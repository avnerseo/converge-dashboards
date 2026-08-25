/*
 * tv-chart.js — גרף TradingView בלחיצה על טיקר
 * ------------------------------------------------------------------
 * משותף ל-index.html (מניות) ול-crypto.html (קריפטו).
 * שימוש:  <script defer src="tv-chart.js" data-market="stocks"></script>
 *         <script defer src="tv-chart.js" data-market="crypto"></script>
 *
 * חשוב: הדשבורדים נכתבים מחדש אוטומטית מדי יום. שורת ה-<script>
 * הזו חייבת לשרוד את הכתיבה מחדש — כל שאר הלוגיקה נמצאת כאן ולא נוגעים בה.
 *
 * הערה על סמלים: TradingView פותר טיקר מנייה חשוף (NVDA) לבד.
 * לקריפטו נדרש קידומת, וברירת המחדל היא CRYPTO:<SYM>USD.
 * סמל שלא נפתר יציג הודעה של TradingView — אפשר לתקן אותו בגרף עצמו
 * (allow_symbol_change), או להוסיף אותו למפה CRYPTO_OVERRIDES למטה.
 */
(function () {
  'use strict';

  var script = document.currentScript ||
    document.querySelector('script[src*="tv-chart.js"]');
  var MARKET = (script && script.dataset.market) || 'stocks';

  /* ---------------------------------------------------------------
   * מפת סמלים — ערוך כאן אם סמל מסוים לא נטען בגרף
   * ------------------------------------------------------------- */
  var CRYPTO_OVERRIDES = {
    // בורסות ייעודיות לטוקנים שאין להם מדד CRYPTO: מאוחד
    KCS: 'KUCOIN:KCSUSDT',
    OKB: 'OKX:OKBUSDT',
    LEO: 'BITFINEX:LEOUSD',
    HYPE: 'BINANCE:HYPEUSDT',
    MORPHO: 'BINANCE:MORPHOUSDT',
    ONDO: 'BINANCE:ONDOUSDT',
    PENDLE: 'BINANCE:PENDLEUSDT',
    SKY: 'BINANCE:SKYUSDT',
    SCRT: 'BINANCE:SCRTUSDT'
  };
  var STOCK_OVERRIDES = {};

  function toTvSymbol(ticker) {
    var t = String(ticker || '').trim().toUpperCase();
    if (!t) return null;
    if (MARKET === 'crypto') {
      return CRYPTO_OVERRIDES[t] || 'CRYPTO:' + t + 'USD';
    }
    return STOCK_OVERRIDES[t] || t;
  }

  /* --------------------------------------------------------------- */

  var TV_SRC = 'https://s3.tradingview.com/tv.js';
  var tvLoading = null;
  var modal, chartHost, titleEl, subtitleEl, externalLink, lastFocus;
  var currentTicker = null, widget = null;

  function loadTradingView() {
    if (window.TradingView && window.TradingView.widget) {
      return Promise.resolve();
    }
    if (tvLoading) return tvLoading;
    tvLoading = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = TV_SRC;
      s.async = true;
      s.onload = resolve;
      s.onerror = function () {
        tvLoading = null;
        reject(new Error('TradingView script failed to load'));
      };
      document.head.appendChild(s);
    });
    return tvLoading;
  }

  function currentTheme() {
    var explicit = document.documentElement.getAttribute('data-theme');
    if (explicit === 'dark' || explicit === 'light') return explicit;
    return window.matchMedia &&
      window.matchMedia('(prefers-color-scheme:dark)').matches
      ? 'dark' : 'light';
  }

  function injectStyles() {
    var css = [
      '.tk,.ticker{cursor:pointer;}',
      '.tk:hover,.ticker:hover{text-decoration:underline;text-underline-offset:3px;}',
      '.tk:focus-visible,.ticker:focus-visible{outline:2px solid var(--series-1,#2a78d6);outline-offset:2px;border-radius:3px;}',

      '.tvm-backdrop{position:fixed;inset:0;z-index:9998;background:rgba(0,0,0,.55);',
      'display:flex;align-items:center;justify-content:center;padding:16px;}',
      '.tvm-backdrop[hidden]{display:none;}',

      '.tvm-panel{background:var(--surface-1,#fff);color:var(--text-primary,#111);',
      'border:1px solid var(--card-border,rgba(0,0,0,.1));border-radius:10px;',
      'box-shadow:var(--shadow,0 12px 40px rgba(0,0,0,.3));',
      'width:min(1100px,96vw);height:min(680px,88vh);display:flex;flex-direction:column;overflow:hidden;}',

      '.tvm-head{display:flex;align-items:center;gap:12px;padding:12px 16px;',
      'border-bottom:1px solid var(--gridline,#e1e0d9);flex:none;}',
      '.tvm-titles{flex:1;min-width:0;}',
      '.tvm-title{font-weight:700;font-size:16px;direction:ltr;unicode-bidi:isolate;}',
      '.tvm-sub{font-size:12px;color:var(--text-secondary,#666);margin-top:2px;',
      'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}',
      '.tvm-link{font-size:12px;color:var(--series-1,#2a78d6);text-decoration:none;',
      'border:1px solid var(--gridline,#e1e0d9);border-radius:6px;padding:5px 10px;flex:none;}',
      '.tvm-link:hover{text-decoration:underline;}',
      '.tvm-close{flex:none;background:none;border:1px solid var(--gridline,#e1e0d9);',
      'border-radius:6px;width:32px;height:32px;font-size:18px;line-height:1;cursor:pointer;',
      'color:var(--text-secondary,#666);}',
      '.tvm-close:hover{color:var(--text-primary,#111);}',
      '.tvm-close:focus-visible,.tvm-link:focus-visible{outline:2px solid var(--series-1,#2a78d6);outline-offset:2px;}',

      '.tvm-body{flex:1;min-height:0;position:relative;}',
      '.tvm-chart{position:absolute;inset:0;}',
      '.tvm-msg{position:absolute;inset:0;display:flex;align-items:center;',
      'justify-content:center;text-align:center;padding:24px;font-size:14px;',
      'color:var(--text-secondary,#666);line-height:1.7;}',
      '.tvm-msg[hidden]{display:none;}',

      '@media (max-width:560px){.tvm-panel{height:92vh;}.tvm-link{display:none;}}'
    ].join('');
    var el = document.createElement('style');
    el.textContent = css;
    document.head.appendChild(el);
  }

  function buildModal() {
    modal = document.createElement('div');
    modal.className = 'tvm-backdrop';
    modal.hidden = true;
    modal.innerHTML =
      '<div class="tvm-panel" role="dialog" aria-modal="true" aria-labelledby="tvm-title">' +
        '<div class="tvm-head">' +
          '<div class="tvm-titles">' +
            '<div class="tvm-title" id="tvm-title"></div>' +
            '<div class="tvm-sub"></div>' +
          '</div>' +
          '<a class="tvm-link" target="_blank" rel="noopener noreferrer">פתח ב-TradingView ↗</a>' +
          '<button class="tvm-close" type="button" aria-label="סגור">&times;</button>' +
        '</div>' +
        '<div class="tvm-body">' +
          '<div class="tvm-chart" id="tvm-chart"></div>' +
          '<div class="tvm-msg" hidden></div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(modal);

    chartHost = modal.querySelector('#tvm-chart');
    titleEl = modal.querySelector('.tvm-title');
    subtitleEl = modal.querySelector('.tvm-sub');
    externalLink = modal.querySelector('.tvm-link');

    modal.querySelector('.tvm-close').addEventListener('click', close);
    modal.addEventListener('mousedown', function (e) {
      if (e.target === modal) close();
    });
  }

  function showMessage(html) {
    var msg = modal.querySelector('.tvm-msg');
    msg.innerHTML = html;
    msg.hidden = false;
  }

  function render(ticker, label) {
    var tvSymbol = toTvSymbol(ticker);
    if (!tvSymbol) return;

    currentTicker = ticker;
    titleEl.textContent = ticker;
    subtitleEl.textContent = label || '';
    externalLink.href = 'https://www.tradingview.com/chart/?symbol=' +
      encodeURIComponent(tvSymbol);

    chartHost.innerHTML = '';
    modal.querySelector('.tvm-msg').hidden = true;

    loadTradingView().then(function () {
      // ייתכן שהמשתמש סגר או החליף סמל בזמן הטעינה
      if (modal.hidden || currentTicker !== ticker) return;
      widget = new window.TradingView.widget({
        container_id: 'tvm-chart',
        symbol: tvSymbol,
        interval: 'D',
        timezone: 'Asia/Jerusalem',
        theme: currentTheme(),
        style: '1',
        locale: 'he_IL',
        autosize: true,
        withdateranges: true,
        allow_symbol_change: true,
        hide_side_toolbar: false,
        save_image: false
      });
    }).catch(function () {
      showMessage(
        'לא הצלחנו לטעון את הגרף מ-TradingView.<br>' +
        'ייתכן שחוסם פרסומות או הרשת חוסמים את <code>s3.tradingview.com</code>.<br>' +
        '<a href="' + externalLink.href + '" target="_blank" rel="noopener noreferrer">' +
        'פתח את הגרף ישירות ב-TradingView ↗</a>'
      );
    });
  }

  function open(ticker, label, trigger) {
    lastFocus = trigger || document.activeElement;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    render(ticker, label);
    modal.querySelector('.tvm-close').focus();
  }

  function close() {
    if (modal.hidden) return;
    modal.hidden = true;
    document.body.style.overflow = '';
    chartHost.innerHTML = '';
    widget = null;
    currentTicker = null;
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  /* --- זיהוי טיקרים בכרטיסים ובטבלאות --- */

  function tickerFrom(el) {
    var node = el.closest && el.closest('.ticker, td.tk');
    if (!node) return null;
    var text = (node.textContent || '').trim().toUpperCase();
    return /^[A-Z0-9.]{1,8}$/.test(text) ? { node: node, ticker: text } : null;
  }

  function labelFor(node) {
    // כרטיס: שם החברה מתחת לטיקר. טבלה: התא הסמוך.
    var card = node.closest('.stock-card');
    if (card) {
      var name = card.querySelector('.company-name');
      if (name) return name.textContent.trim();
    }
    var row = node.closest('tr');
    if (row && node.cellIndex != null && row.cells[node.cellIndex + 1]) {
      return row.cells[node.cellIndex + 1].textContent.trim();
    }
    return '';
  }

  function markInteractive() {
    var nodes = document.querySelectorAll('.ticker, td.tk');
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      if (n.dataset.tvmReady) continue;
      var text = (n.textContent || '').trim();
      if (!/^[A-Za-z0-9.]{1,8}$/.test(text)) continue;
      n.dataset.tvmReady = '1';
      n.setAttribute('role', 'button');
      n.setAttribute('tabindex', '0');
      n.setAttribute('title', 'הצג גרף TradingView');
    }
  }

  function init() {
    injectStyles();
    buildModal();
    markInteractive();

    document.addEventListener('click', function (e) {
      var hit = tickerFrom(e.target);
      if (!hit) return;
      e.preventDefault();
      open(hit.ticker, labelFor(hit.node), hit.node);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { close(); return; }
      if (e.key !== 'Enter' && e.key !== ' ') return;
      var hit = tickerFrom(e.target);
      if (!hit) return;
      e.preventDefault();
      open(hit.ticker, labelFor(hit.node), hit.node);
    });

    // הדשבורדים מסננים ומיינים טבלאות — נסמן טיקרים חדשים שנוספו ל-DOM
    if (window.MutationObserver) {
      new MutationObserver(markInteractive)
        .observe(document.body, { childList: true, subtree: true });
    }

    // החלפת ערכת נושא בזמן שהגרף פתוח — נטען מחדש בערכה הנכונה
    if (window.MutationObserver) {
      new MutationObserver(function () {
        if (!modal.hidden && currentTicker) {
          render(currentTicker, subtitleEl.textContent);
        }
      }).observe(document.documentElement, {
        attributes: true, attributeFilter: ['data-theme']
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
