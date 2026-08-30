/* Converge daily scene — deterministic renderer.
 *
 * Contract with the capture harness (scripts/capture.py):
 *   SCENE.init(payload)  build the DOM once, from data only
 *   SCENE.duration       total seconds
 *   SCENE.seek(t)        set every visual property as a pure function of t
 *
 * seek(t) must be pure: same t -> same pixels, in any order, any number of
 * times. That rules out Date/performance/Math.random/rAF/CSS animation, all of
 * which the harness actively traps. See notes/determinism.md.
 */
(function () {
  "use strict";

  // ---------- timing helpers (pure) ----------
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  // progress of a segment starting at `start` lasting `dur`
  const seg = (t, start, dur) => clamp((t - start) / dur, 0, 1);
  const easeOut = p => 1 - Math.pow(1 - p, 3);
  const easeInOut = p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);

  /* Fade a block in, hold, fade out. Returns {o, y} — opacity and px offset. */
  function beat(t, start, dur, opts) {
    const inD = (opts && opts.in) || 0.45;
    const outD = (opts && opts.out) || 0.35;
    const rise = (opts && opts.rise) !== undefined ? opts.rise : 46;
    if (t < start - 0.001 || t > start + dur) return { o: 0, y: rise, p: 0 };
    const local = t - start;
    const pIn = easeOut(clamp(local / inD, 0, 1));
    const pOut = 1 - easeInOut(clamp((local - (dur - outD)) / outD, 0, 1));
    return { o: clamp(pIn * pOut, 0, 1), y: (1 - pIn) * rise, p: clamp(local / dur, 0, 1) };
  }

  // ---------- text helpers ----------
  /* Every Latin/numeric run becomes its own LTR island. Doing this in code
     rather than in the payload means a customer's feed cannot break BiDi. */
  function ltr(text, cls) {
    const s = document.createElement("span");
    s.className = "ltr" + (cls ? " " + cls : "");
    s.dir = "ltr";
    s.textContent = text;
    return s;
  }
  function money(v) {
    return "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function pct(v) {
    // U+2212 for the minus: typographically right, and safe now that every
    // number sits inside a .ltr island.
    if (Math.abs(v) < 0.005) return "0.00%";   // flat is not a gain
    return (v < 0 ? "−" : "+") + Math.abs(v).toFixed(2) + "%";
  }
  // "up" / "down" / neither — a 0% day must not be painted green
  function dir(v) {
    return Math.abs(v) < 0.005 ? "flat" : v < 0 ? "down" : "up";
  }
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // ---------- timeline ----------
  const T = {
    intro: { at: 0.0, dur: 3.0 },
    kpi: { at: 2.7, dur: 2.6 },
    card: { at: 5.1, dur: 2.35, gap: 2.2 }, // per featured row
    movers: null, // filled in init once we know the card count
    outro: null
  };

  const SCENE = {
    duration: 0,
    payload: null,
    _nodes: null,

    init(payload) {
      this.payload = payload;
      const frames = document.getElementById("frames");
      frames.textContent = "";

      // Brand comes from the payload, not the markup. A second customer is a
      // second JSON file, not a second copy of the scene.
      document.getElementById("wordmark").textContent = payload.brand.name;
      document.getElementById("tagline").textContent = payload.brand.tagline || "";
      document.documentElement.style.setProperty(
        "--accent", payload.brand.accent || "#3d7bff");
      document.getElementById("datepill").textContent = fmtDate(payload.date);
      document.getElementById("disclaimer").textContent = payload.disclaimer || "";

      const nodes = { cards: [], movers: [], kpis: [] };

      // --- intro ---
      const intro = el("div", "frame");
      intro.appendChild(ltr(payload.brand.name + " · Daily"));
      intro.lastChild.className = "kicker ltr";
      intro.appendChild(el("div", "headline", payload.title));
      intro.appendChild(el("div", "sub", payload.subtitle));
      intro.appendChild(el("div", "rule"));
      frames.appendChild(intro);
      nodes.intro = intro;
      nodes.introRule = intro.querySelector(".rule");

      // --- kpi ---
      const kpiFrame = el("div", "frame");
      const row = el("div", "kpi-row");
      const kpiSpec = [
        [payload.kpi.tier1_count, "מניות בשכבה 1"],
        [payload.kpi.universe, "מניות שנבדקו היום"],
        [payload.kpi.risk_count, "בשכבת סיכון גבוה"]
      ];
      for (const [value, label] of kpiSpec) {
        const box = el("div", "kpi");
        const v = el("div", "kpi-value ltr");
        v.dir = "ltr";
        box.appendChild(v);
        box.appendChild(el("div", "kpi-label", label));
        row.appendChild(box);
        nodes.kpis.push({ node: box, valueNode: v, target: value });
      }
      kpiFrame.appendChild(row);
      frames.appendChild(kpiFrame);
      nodes.kpi = kpiFrame;

      // --- featured cards ---
      payload.featured.forEach((r, i) => {
        const f = el("div", "frame");
        f.appendChild(ltr("#" + (i + 1) + " / " + payload.featured.length)).className =
          "rank ltr";
        const card = el("div", "card");

        const head = el("div", "card-head");
        const left = el("div");
        const tk = el("div", "tk ltr");
        tk.dir = "ltr";
        tk.textContent = r.ticker;
        left.appendChild(tk);
        left.appendChild(el("div", "co", r.name));
        const right = el("div", "px-wrap");
        const px = el("div", "px ltr");
        px.dir = "ltr";
        px.textContent = money(r.price);
        const chg = el("div", "chg ltr " + dir(r.change_pct));
        chg.dir = "ltr";
        chg.textContent = pct(r.change_pct);
        right.appendChild(px);
        right.appendChild(chg);
        head.appendChild(left);
        head.appendChild(right);
        card.appendChild(head);

        const bar = el("div", "bar");
        const fill = el("div", "bar-fill " + dir(r.change_pct));
        bar.appendChild(fill);
        card.appendChild(bar);

        const meta = el("div", "meta");
        if (r.chip) meta.appendChild(el("span", "chip", r.chip));
        if (r.sector) meta.appendChild(el("span", "chip sector", r.sector));
        card.appendChild(meta);

        f.appendChild(card);
        frames.appendChild(f);

        // width is proportional to move size, capped at 5% so one wild day
        // does not flatten every other bar
        const width = clamp(Math.abs(r.change_pct) / 5, 0.06, 1);
        nodes.cards.push({ node: f, card, fill, width, at: T.card.at + i * T.card.gap });
      });

      const nCards = payload.featured.length;
      T.movers = { at: T.card.at + nCards * T.card.gap + 0.1, dur: 3.4 };

      // --- movers ---
      const mf = el("div", "frame");
      mf.appendChild(el("div", "frame-title", "התנועות החדות של היום"));
      payload.movers.forEach(m => {
        const rowEl = el("div", "mover");
        const a = el("div", "m-tk ltr");
        a.dir = "ltr";
        a.textContent = m.ticker;
        const b = el("div", "m-chg ltr " + dir(m.change_pct));
        b.dir = "ltr";
        b.textContent = pct(m.change_pct);
        rowEl.appendChild(a);
        rowEl.appendChild(b);
        mf.appendChild(rowEl);
        nodes.movers.push(rowEl);
      });
      frames.appendChild(mf);
      nodes.moversFrame = mf;

      // --- outro ---
      T.outro = { at: T.movers.at + T.movers.dur - 0.3, dur: 2.8 };
      const of_ = el("div", "frame");
      const lock = el("div", "outro-lock");
      lock.appendChild(el("div", "outro-mark"));
      const w = el("div", "outro-word ltr");
      w.dir = "ltr";
      w.textContent = payload.brand.name;
      lock.appendChild(w);
      lock.appendChild(
        el("div", "outro-note", "מעודכן כל בוקר אוטומטית מתוך הדאטה של " + payload.brand.name)
      );
      of_.appendChild(lock);
      frames.appendChild(of_);
      nodes.outro = of_;
      nodes.outroMark = of_.querySelector(".outro-mark");

      this._nodes = nodes;
      this.duration = Math.round((T.outro.at + T.outro.dur) * 100) / 100;
      this.seek(0);
      return this.duration;
    },

    seek(t) {
      const n = this._nodes;
      if (!n) throw new Error("SCENE.seek called before init");

      const put = (node, b, extra) => {
        node.style.opacity = b.o.toFixed(4);
        node.style.transform =
          "translate3d(0," + b.y.toFixed(2) + "px,0)" + (extra || "");
      };

      // intro
      const bIntro = beat(t, T.intro.at, T.intro.dur, { in: 0.7, out: 0.4, rise: 40 });
      put(n.intro, bIntro);
      n.introRule.style.transform =
        "scaleX(" + easeOut(seg(t, T.intro.at + 0.5, 0.9)).toFixed(4) + ")";

      // kpi — counters are a function of t, so scrubbing backwards works too
      const bKpi = beat(t, T.kpi.at, T.kpi.dur, { in: 0.5, out: 0.35 });
      put(n.kpi, bKpi);
      const countP = easeOut(seg(t, T.kpi.at + 0.15, 1.15));
      n.kpis.forEach((k, i) => {
        k.valueNode.textContent = String(Math.round(k.target * countP));
        const rise = beat(t, T.kpi.at + i * 0.1, T.kpi.dur, { in: 0.5, out: 0.35, rise: 34 });
        k.node.style.transform = "translate3d(0," + rise.y.toFixed(2) + "px,0)";
      });

      // featured cards
      n.cards.forEach(c => {
        const b = beat(t, c.at, T.card.dur, { in: 0.42, out: 0.34, rise: 54 });
        put(c.node, b);
        const grow = easeOut(seg(t, c.at + 0.18, 0.85));
        c.fill.style.width = (c.width * grow * 100).toFixed(3) + "%";
        const s = 0.965 + 0.035 * easeOut(seg(t, c.at, 0.5));
        c.card.style.transform = "scale(" + s.toFixed(4) + ")";
      });

      // movers
      const bMov = beat(t, T.movers.at, T.movers.dur, { in: 0.5, out: 0.4 });
      put(n.moversFrame, bMov);
      n.movers.forEach((m, i) => {
        const p = easeOut(seg(t, T.movers.at + 0.25 + i * 0.18, 0.6));
        m.style.opacity = p.toFixed(4);
        m.style.transform = "translate3d(0," + ((1 - p) * 40).toFixed(2) + "px,0)";
      });

      // outro
      const bOut = beat(t, T.outro.at, T.outro.dur, { in: 0.6, out: 0.5, rise: 30 });
      put(n.outro, bOut);
      const ms = 0.8 + 0.2 * easeOut(seg(t, T.outro.at, 0.8));
      n.outroMark.style.transform = "scale(" + ms.toFixed(4) + ")";

      // progress bar
      const p = clamp(t / this.duration, 0, 1);
      document.getElementById("progressFill").style.width = (p * 100).toFixed(3) + "%";
    }
  };

  function fmtDate(iso) {
    // Formatted from the payload string only — never from a Date/clock.
    const [y, m, d] = iso.split("-");
    return Number(d) + "." + Number(m) + "." + y;
  }

  window.SCENE = SCENE;
})();
