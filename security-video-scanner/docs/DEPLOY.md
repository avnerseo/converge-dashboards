# Deploying vscan on-premise

vscan ships as a single container that runs inside the customer's network. The
recordings are mounted read-only; the index, accounts and audit trail live in
one Docker volume. Nothing leaves the site unless natural-language search is
explicitly switched on.

---

## 1. What the box needs

| | Minimum | Comfortable |
|---|---|---|
| CPU | 4 cores | 8+ cores (indexing is CPU-bound and scales with cores) |
| RAM | 4 GB | 8 GB |
| Disk | footage + ~1 GB per 20 h of indexed footage | plus room for exported clips |
| OS | any Linux with Docker Engine 24+ and the compose plugin | |
| GPU | not used | not used |

Rough indexing throughput per worker, measured on 4 cores with 1080p input at
2 sampled frames per second: **~13× realtime** with face detection only,
**~3× realtime** with object detection as well. The motion gate skips frames
where nothing changed, so real CCTV usually runs far faster than that. One
`VSCAN_WORKERS` slot needs roughly one core.

## 2. Install

```bash
git clone <your-distribution-of-this-repo> vscan && cd vscan/docker
cp .env.example .env
$EDITOR .env                     # set VSCAN_ADMIN_PASSWORD and VSCAN_FOOTAGE_PATH
docker compose up -d --build
docker compose logs -f vscan     # wait for "vscan server ... ready"
```

Open `http://<host>:8080` and sign in with the administrator from `.env`.
If you left `VSCAN_ADMIN_PASSWORD` empty, the first start generates a password,
prints it to the log and writes it to `/data/initial-admin-password.txt`
inside the volume — change it on first login and delete that file.

The image builds the ONNX models in, so the running container needs **no
internet access at all** (unless you enable natural-language search).

### Footage

Mount whatever holds the recordings at `/footage`, read-only:

```yaml
volumes:
  - /mnt/nvr/exports:/footage:ro          # a share from the NVR
  - vscan-data:/data
```

Several roots are allowed — separate them with `:` in `VSCAN_FOOTAGE_DIRS`.
Paths outside those roots are rejected by the API, so an operator cannot browse
the host filesystem through the web UI.

## 3. Accounts and roles

| Role | Can |
|---|---|
| `viewer` | search, watch results, see footage and jobs |
| `analyst` | + import and index footage, enrol people, group faces, run instruction search, export clips |
| `admin` | + manage users, settings, retention purges, read the audit log |

Sessions are cookie-based and expire after `VSCAN_SESSION_HOURS` (12 by
default). Changing a password or deactivating a user drops that user's sessions
immediately. Five failed sign-ins for the same username from the same address
within 15 minutes trigger a temporary `429` brake.

## 4. Putting TLS in front

The container speaks plain HTTP and binds to `127.0.0.1` by default. Terminate
TLS in front of it and set `VSCAN_SECURE_COOKIE=true` so the session cookie is
marked `Secure`.

nginx:

```nginx
server {
  listen 443 ssl;
  server_name vscan.example.com;
  ssl_certificate     /etc/ssl/vscan.crt;
  ssl_certificate_key /etc/ssl/vscan.key;
  client_max_body_size 64m;               # photo uploads

  location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;                  # video streams and job polling
    proxy_read_timeout 3600s;
  }
}
```

Caddy:

```
vscan.example.com {
  reverse_proxy 127.0.0.1:8080
  request_body { max_size 64MB }
}
```

The app trusts `X-Forwarded-For` for the address it records in the audit log,
so only expose it behind a proxy you control.

## 5. Natural-language search (optional, off by default)

`VSCAN_ASK_ENABLED=true` plus an `ANTHROPIC_API_KEY` turns on the third search
mode. It is the only feature that sends anything off the machine: selected
frames (as JPEG contact sheets) go to the Claude API. Nothing else — no
recordings, no face vectors, no names.

Tell the customer this plainly before enabling it, and keep it off where the
footage cannot legally leave the premises. Admins can flip it in
**Settings**, and every instruction search is written to the audit log with the
text of the query and the user who ran it.

Cost scales with the number of frames reviewed: the triage pass sends one
request per 9 frames, then one request per candidate frame for confirmation.
`--max-frames`/**Max frames** is the budget dial; narrow the time range first.

## 6. Retention and purging

Face crops and 128-dimension face vectors are personal data under GDPR and
comparable regimes. The product gives you three controls:

- `VSCAN_RETENTION_DAYS` (or **Settings → Retention**) records the policy.
- **Settings → Purge old data** deletes every video indexed before that cutoff,
  along with its frames, faces, crops and object rows.
- **Settings → Wipe the index** removes all indexed data *and* every enrolled
  person. Accounts and the audit log survive, so the record of who did what
  remains.

Purges are themselves audited. There is no scheduler in v1 — run the purge from
the UI, or hit `POST /api/maintenance/purge` from cron with an admin session.

## 7. Backup, restore, upgrade

Everything mutable is in the `vscan-data` volume: `app.db` (accounts, jobs,
audit), `index/` (the search index, thumbnails and face crops), `exports/`,
`previews/`, `secret.key`.

```bash
# backup
docker compose stop vscan
docker run --rm -v vscan-data:/data -v "$PWD:/backup" alpine \
  tar czf /backup/vscan-$(date +%F).tar.gz -C /data .
docker compose start vscan

# restore
docker run --rm -v vscan-data:/data -v "$PWD:/backup" alpine \
  sh -c "rm -rf /data/* && tar xzf /backup/vscan-2026-08-30.tar.gz -C /data"
```

Upgrading is `git pull && docker compose up -d --build`. The schema is created
and migrated on start; the data volume is not touched.

## 8. Data map (for a DPIA)

| Where | What | Deleted by |
|---|---|---|
| `/footage` (read-only) | the customer's recordings | never written or deleted by vscan |
| `/data/index/index.db` | frame times, face boxes, face vectors, object boxes | purge, or removing a video |
| `/data/index/thumbs`, `crops` | frame thumbnails and face crops (JPEG) | same |
| `/data/index/clusters.json` | face grouping results | overwritten on each grouping run |
| `/data/app.db` | accounts, sessions, jobs, audit log | account deletion; the audit log is kept |
| `/data/previews`, `exports` | transcoded playback windows, exported clips | previews self-prune; exports are manual |

## 9. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| A job fails with "interrupted by a server restart" | the container restarted mid-job; re-run it |
| Video shows "the source file is not reachable" | the `/footage` mount changed or the file moved; re-index |
| Preview fails to transcode | this ffmpeg build lacks the encoder; set `VSCAN_PREVIEW_CODEC=vp9` |
| Indexing is slow | lower **Frames per second**, turn off object detection, raise `VSCAN_WORKERS` if cores allow |
| No faces are ever found | the camera is too far or too high; faces need to be ~24 px wide. Use object search instead |
| Instruction search returns 403 | it is switched off, or the user is not an analyst |

Server logs: `docker compose logs -f vscan`. Every user action worth reviewing
is in **Audit log**, and every job keeps its parameters, progress and error.

## 10. What is not in the threat model (v1)

Be straight with buyers about this list; it is short and each item is a known
choice, not an oversight.

- **No TLS inside the container.** Terminate it in front (section 4).
- **No SSO/LDAP.** Local accounts only. SAML/OIDC is the usual first request
  from larger buyers.
- **No per-camera authorisation.** A viewer can search everything indexed.
- **No live camera ingest.** v1 indexes recorded files, not RTSP streams.
- **No scheduled retention job.** The purge is manual or cron-driven.
- **Audit log is append-only by convention, not by storage.** An admin with
  shell access to the volume can edit `app.db`. Ship the volume to a WORM
  store if the customer needs tamper evidence.
