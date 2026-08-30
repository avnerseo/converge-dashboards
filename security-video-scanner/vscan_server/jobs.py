"""A small persistent job queue.

Indexing hours of footage and asking Claude about hundreds of frames are both
too slow for a request/response cycle, so they run here: rows in the jobs
table, worked by a fixed pool of threads, with progress the UI can poll and a
cooperative cancel flag.
"""
from __future__ import annotations

import queue
import threading
import traceback
from dataclasses import dataclass
from typing import Any, Callable

from .store import Store

# vscan's SQLite index tolerates concurrent readers, but two indexers writing at
# once just fight over the same tables - so write-heavy jobs take this lock.
INDEX_WRITE_LOCK = threading.RLock()


class JobCancelled(Exception):
    """Raised inside a handler when the operator asks for a cancel."""


@dataclass
class JobContext:
    job_id: int
    store: Store
    user_id: int | None

    def progress(self, fraction: float | None = None, message: str | None = None) -> None:
        self.store.update_job(self.job_id, fraction, message)
        self.check_cancel()

    def check_cancel(self) -> None:
        if self.store.cancel_requested(self.job_id):
            raise JobCancelled()

    @property
    def cancelled(self) -> bool:
        return self.store.cancel_requested(self.job_id)


Handler = Callable[[JobContext, dict], Any]


class JobRunner:
    def __init__(self, store: Store, workers: int = 2):
        self.store = store
        self.workers = max(1, workers)
        self._queue: queue.Queue[int | None] = queue.Queue()
        self._handlers: dict[str, Handler] = {}
        self._threads: list[threading.Thread] = []
        self._running = False

    def register(self, kind: str, handler: Handler) -> None:
        self._handlers[kind] = handler

    def start(self) -> None:
        if self._running:
            return
        stale = self.store.requeue_stale_jobs()
        if stale:
            # Nothing survives a restart mid-job; say so rather than hanging.
            self.store.audit("jobs.recovered", detail={"failed": stale})
        self._running = True
        for i in range(self.workers):
            thread = threading.Thread(target=self._work, name=f"vscan-worker-{i}",
                                      daemon=True)
            thread.start()
            self._threads.append(thread)

    def stop(self, timeout: float = 5.0) -> None:
        if not self._running:
            return
        self._running = False
        for _ in self._threads:
            self._queue.put(None)
        for thread in self._threads:
            thread.join(timeout=timeout)
        self._threads.clear()

    def submit(self, kind: str, title: str, params: dict,
               user_id: int | None = None) -> int:
        if kind not in self._handlers:
            raise KeyError(f"no handler registered for job kind {kind!r}")
        job_id = self.store.create_job(kind, title, params, user_id)
        self._queue.put(job_id)
        return job_id

    # -- worker ------------------------------------------------------------
    def _work(self) -> None:
        while True:
            job_id = self._queue.get()
            try:
                if job_id is None:
                    return
                self._run_one(job_id)
            finally:
                self._queue.task_done()

    def _run_one(self, job_id: int) -> None:
        job = self.store.job(job_id)
        if job is None:
            return
        if job["cancel"]:
            self.store.finish_job(job_id, "cancelled")
            return
        handler = self._handlers.get(job["kind"])
        if handler is None:
            self.store.finish_job(job_id, "failed",
                                  error=f"unknown job kind {job['kind']!r}")
            return

        self.store.start_job(job_id)
        ctx = JobContext(job_id, self.store, job.get("created_by"))
        try:
            result = handler(ctx, job.get("params") or {})
            self.store.finish_job(job_id, "done", result=result)
        except JobCancelled:
            self.store.finish_job(job_id, "cancelled")
        except Exception as exc:
            detail = f"{type(exc).__name__}: {exc}"
            self.store.finish_job(job_id, "failed", error=detail)
            self.store.audit("job.failed", detail={
                "job_id": job_id, "kind": job["kind"], "error": detail,
                "trace": traceback.format_exc(limit=4)})
