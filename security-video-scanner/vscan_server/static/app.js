'use strict';
/* vscan operator console. No build step: this file is the whole front end. */

const S = {
  user: null, caps: {}, lang: localStorage.getItem('vscan.lang') || 'he',
  tab: 'overview', videos: [], persons: [], clusters: [], settings: {},
  results: [], resultsLabel: '', jobs: [], pollTimer: null,
};

/* ----------------------------------------------------------------- i18n */
const STR = {
  he: {
    overview: 'סקירה', footage: 'הקלטות', search: 'חיפוש', people: 'אנשים',
    faces: 'פנים שנמצאו', jobs: 'משימות', audit: 'יומן ביקורת', settings: 'הגדרות',
    signIn: 'כניסה', signOut: 'יציאה', username: 'שם משתמש', password: 'סיסמה',
    videos: 'סרטונים', frames: 'פריימים', facesFound: 'פנים', objects: 'אובייקטים',
    persons: 'אנשים רשומים', hours: 'שעות הקלטה', running: 'רצות', queued: 'בהמתנה',
    addFootage: 'הוספת הקלטות', browse: 'עיון בקבצים', selected: 'נבחרו',
    startIndexing: 'התחל אינדוקס', indexed: 'אונדקס', duration: 'אורך', name: 'שם',
    remove: 'מחיקה', confirmRemove: 'למחוק מהאינדקס?', options: 'אפשרויות',
    sampleFps: 'פריימים לשנייה', width: 'רוחב ניתוח', motion: 'סף תנועה',
    detectObjects: 'זיהוי אובייקטים', force: 'לאנדקס מחדש', startTime: 'שעת התחלה',
    searchMode: 'סוג חיפוש', byPerson: 'לפי אדם', byObject: 'לפי אובייקט',
    byInstruction: 'לפי הוראה חופשית', byAppearance: 'לפי מראה',
    person: 'אדם', threshold: 'סף התאמה',
    onlyArrivals: 'רק הגעות', absence: 'היעדרות (שניות)', gap: 'מרווח איחוד (שניות)',
    from: 'מ', to: 'עד', allVideos: 'כל הסרטונים', run: 'חפש', labels: 'תוויות',
    minScore: 'ציון מינימלי', query: 'מה לחפש', maxFrames: 'מקסימום פריימים',
    confirmPass: 'אימות בפריים מלא', effort: 'עומק חשיבה', results: 'תוצאות',
    noResults: 'אין תוצאות', exportClips: 'ייצוא קטעים', downloadJson: 'הורדת JSON',
    addPerson: 'הוספת אדם', personName: 'שם', uploadPhotos: 'העלאת תמונות',
    references: 'תמונות ייחוס', enrollFromVideo: 'רישום מתוך סרטון',
    atTimecode: 'בזמן (HH:MM:SS)', groupFaces: 'קיבוץ פנים', nameThis: 'תן שם',
    clusterSize: 'מספר פנים', firstSeen: 'נראה לראשונה', lastSeen: 'לאחרונה',
    status: 'סטטוס', progress: 'התקדמות', cancel: 'ביטול', created: 'נוצר',
    action: 'פעולה', user: 'משתמש', when: 'מתי', detail: 'פרטים',
    users: 'משתמשים', role: 'תפקיד', addUser: 'הוספת משתמש', active: 'פעיל',
    changePassword: 'שינוי סיסמה', currentPassword: 'סיסמה נוכחית',
    newPassword: 'סיסמה חדשה', retention: 'שמירת מידע (ימים)', purge: 'מחיקת מידע ישן',
    purgeAll: 'מחיקת כל האינדקס', askEnabled: 'חיפוש בהוראה חופשית מופעל',
    siteName: 'שם המערכת', save: 'שמירה', close: 'סגירה', open: 'פתיחה',
    loginNote: 'גישה למערכת מתועדת ביומן הביקורת.',
    legal: 'זיהוי פנים הוא עיבוד מידע ביומטרי. השתמשו רק בהקלטות שמותר לכם לעבד, ומחקו מידע שאינו נחוץ.',
    nothingIndexed: 'עדיין לא אונדקסו הקלטות.', noPersons: 'עדיין לא נרשמו אנשים.',
    noClusters: 'אין קיבוצי פנים. הריצו קיבוץ פנים אחרי אינדוקס.',
    jobStarted: 'המשימה התחילה', saved: 'נשמר', deleted: 'נמחק',
    videoUnavailable: 'קובץ המקור אינו זמין בשרת', hits: 'זיהויים',
    score: 'ציון', note: 'הערה', clip: 'קטע', download: 'הורדה',
    findSimilar: 'מי עוד נראה ככה', similarTo: 'דומים ל',
    appearanceRefs: 'תמונות מראה', addAppearance: 'רישום מראה מתוך סרטון',
    appearanceHint: 'מראה = בגדים ומבנה גוף. עובד גם כשלא רואים פנים, אבל חלש יותר מזיהוי פנים ומשתנה בין ימים.',
    noAppearance: 'הסרטון לא אונדקס עם מראה. הוסיפו --appearance / סמנו את התיבה באינדוקס.',
    detectAppearance: 'וקטורי מראה (Re-ID)',
    dropHere: 'גררו לכאן קובץ וידאו',
    dropHint: 'או לחצו כדי לבחור קובץ מהמחשב. הקובץ נשמר על השרת ומתחיל להתאנדקס מיד.',
    uploading: 'מעלה', uploadDone: 'ההעלאה הסתיימה, האינדוקס התחיל',
    orPickFromServer: 'או לבחור מתוך התיקיות שמחוברות לשרת',
    askNeedsKey: 'חיפוש בהוראה חופשית דורש מפתח API של Claude. מנהל יכול להוסיף אותו בלשונית הגדרות.',
    askNeedsKeyAdmin: 'צריך מפתח API של Claude. אפשר להוסיף אותו למטה בהגדרות ← מפתח Claude API.',
    apiKey: 'מפתח Claude API', apiKeySet: 'מפתח מוגדר', apiKeyNone: 'לא הוגדר מפתח',
    apiKeyHint: 'המפתח נשמר על השרת שלכם ומשמש רק לחיפוש בהוראה חופשית. הוא לא מוצג שוב אחרי השמירה.',
    askExample: 'למשל: מישהו משאיר תיק ליד הכניסה והולך',
    uploaded: 'הועלה', nothingFound: 'לא נמצא כלום',
    confirmRemoveUpload: 'למחוק מהאינדקס וגם את הקובץ מהשרת?',
    searchPlaceholder: 'מה לחפש? למשל: מתי הרכב הלבן זז, דוד, מישהו משאיר תיק',
    searchedAs: 'חיפשתי', modePerson: 'לפי פנים', modeObjects: 'לפי אובייקט',
    modeAsk: 'לפי הוראה חופשית', advanced: 'סינון', examples: 'דוגמאות',
    cannotAnswerYet: 'לזה עוד אי אפשר לענות',
    meanwhile: 'בינתיים אפשר לחפש מקומית',
    askNeedsAnalyst: 'חיפוש בהוראה חופשית דורש הרשאת אנליסט.',
    askSwitchedOff: 'חיפוש בהוראה חופשית כבוי בהגדרות.',
    testKey: 'בדיקה ושמירה', keyOk: 'המפתח תקין ונשמר',
    whyPerson: 'רשום במערכת, אז זה חיפוש פנים',
    whyObjects: 'הגלאי המקומי מכיר את זה ישירות',
    whyDescriptive: 'מתאר מראה או תנועה, לא עצם שהגלאי מזהה',
    whyUnknown: 'לא משהו שהגלאי המקומי מכיר',
    whyNotMeasurable: 'מתאר משהו שהגלאים המקומיים לא יודעים למדוד',
  },
  en: {
    overview: 'Overview', footage: 'Footage', search: 'Search', people: 'People',
    faces: 'Faces found', jobs: 'Jobs', audit: 'Audit log', settings: 'Settings',
    signIn: 'Sign in', signOut: 'Sign out', username: 'Username', password: 'Password',
    videos: 'Videos', frames: 'Frames', facesFound: 'Faces', objects: 'Objects',
    persons: 'Enrolled people', hours: 'Hours of footage', running: 'Running',
    queued: 'Queued', addFootage: 'Add footage', browse: 'Browse files',
    selected: 'selected', startIndexing: 'Start indexing', indexed: 'Indexed',
    duration: 'Length', name: 'Name', remove: 'Remove',
    confirmRemove: 'Remove this video from the index?',
    confirmRemoveUpload: 'Remove from the index and delete the uploaded file?',
    uploaded: 'uploaded',
    nothingFound: 'nothing detected',
    searchPlaceholder: 'What are you looking for? e.g. when did the white car move, David, someone leaving a bag',
    searchedAs: 'Searched as', modePerson: 'by face', modeObjects: 'by object',
    modeAsk: 'by instruction', advanced: 'Filters', examples: 'Examples',
    cannotAnswerYet: 'This cannot be answered yet',
    meanwhile: 'In the meantime, searchable locally',
    askNeedsAnalyst: 'Instruction search needs the analyst role.',
    askSwitchedOff: 'Instruction search is switched off in Settings.',
    testKey: 'Test and save', keyOk: 'the key works and was saved',
    whyPerson: 'is enrolled, so this is a face search',
    whyObjects: 'the local detector knows this directly',
    whyDescriptive: 'describes appearance or movement, not an object',
    whyUnknown: 'is not something the local detector knows',
    whyNotMeasurable: 'describes something the local detectors cannot measure', options: 'Options',
    sampleFps: 'Frames per second', width: 'Analysis width', motion: 'Motion threshold',
    detectObjects: 'Detect objects', force: 'Re-index', startTime: 'Wall-clock start',
    searchMode: 'Search type', byPerson: 'By person', byObject: 'By object',
    byInstruction: 'By instruction', byAppearance: 'By appearance',
    person: 'Person', threshold: 'Match threshold',
    onlyArrivals: 'Arrivals only', absence: 'Absence (seconds)',
    gap: 'Merge gap (seconds)', from: 'From', to: 'To', allVideos: 'All videos',
    run: 'Search', labels: 'Labels', minScore: 'Min score', query: 'What to look for',
    maxFrames: 'Max frames', confirmPass: 'Confirm on full frame', effort: 'Effort',
    results: 'Results', noResults: 'No matches', exportClips: 'Export clips',
    downloadJson: 'Download JSON', addPerson: 'Add person', personName: 'Name',
    uploadPhotos: 'Upload photos', references: 'Reference faces',
    enrollFromVideo: 'Enrol from a video', atTimecode: 'At (HH:MM:SS)',
    groupFaces: 'Group faces', nameThis: 'Name this person', clusterSize: 'Faces',
    firstSeen: 'First seen', lastSeen: 'Last seen', status: 'Status',
    progress: 'Progress', cancel: 'Cancel', created: 'Created', action: 'Action',
    user: 'User', when: 'When', detail: 'Detail', users: 'Users', role: 'Role',
    addUser: 'Add user', active: 'Active', changePassword: 'Change password',
    currentPassword: 'Current password', newPassword: 'New password',
    retention: 'Retention (days)', purge: 'Purge old data', purgeAll: 'Wipe the index',
    askEnabled: 'Instruction search enabled', siteName: 'Site name', save: 'Save',
    close: 'Close', open: 'Open', loginNote: 'Access to this system is recorded in the audit log.',
    legal: 'Face recognition processes biometric data. Use it only on footage you are authorised to process, and delete what you no longer need.',
    nothingIndexed: 'No footage indexed yet.', noPersons: 'Nobody enrolled yet.',
    noClusters: 'No face groups yet - run face grouping after indexing.',
    jobStarted: 'Job started', saved: 'Saved', deleted: 'Deleted',
    videoUnavailable: 'The source file is not reachable from the server',
    hits: 'detections', score: 'Score', note: 'Note', clip: 'Clip', download: 'Download',
    findSimilar: 'Who else looks like this', similarTo: 'Similar to',
    appearanceRefs: 'Appearance references', addAppearance: 'Add appearance from a video',
    appearanceHint: 'Appearance means clothing and build. It works when no face is visible, but it is weaker than a face match and changes between days.',
    noAppearance: 'This video was indexed without appearance vectors. Re-index with the appearance option.',
    detectAppearance: 'Appearance vectors (re-id)',
    dropHere: 'Drop a video file here',
    dropHint: 'or click to choose one. It is stored on the server and indexing starts immediately.',
    uploading: 'Uploading', uploadDone: 'Upload finished, indexing started',
    orPickFromServer: 'or pick from the folders mounted on the server',
    askNeedsKey: 'Instruction search needs a Claude API key. An admin can add one under Settings.',
    askNeedsKeyAdmin: 'Needs a Claude API key - add one below under Settings > Claude API key.',
    apiKey: 'Claude API key', apiKeySet: 'a key is configured', apiKeyNone: 'no key configured',
    apiKeyHint: 'Stored on your own server and used only for instruction search. It is never shown again after saving.',
    askExample: 'e.g. someone leaving a bag by the entrance and walking away',
  },
};
const t = (k) => (STR[S.lang] && STR[S.lang][k]) || STR.en[k] || k;

/* The detector speaks COCO; the operator does not. */
const LABELS_HE = {
  person: 'אדם', car: 'רכב', truck: 'משאית', bus: 'אוטובוס',
  motorcycle: 'אופנוע', bicycle: 'אופניים', dog: 'כלב', cat: 'חתול',
  handbag: 'תיק', backpack: 'תרמיל', suitcase: 'מזוודה', umbrella: 'מטרייה',
  'cell phone': 'טלפון', laptop: 'מחשב נייד', bird: 'ציפור', train: 'רכבת',
  boat: 'סירה', bench: 'ספסל', bottle: 'בקבוק', chair: 'כיסא',
};
const labelName = (label) => (S.lang === 'he' && LABELS_HE[label]) || label;
const labelList = (labels) => (labels || []).map(labelName).join(', ');

/* ------------------------------------------------------------- helpers */
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') node.className = v;
    else if (k === 'html') node.innerHTML = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else if (k === 'dataset') Object.assign(node.dataset, v);
    else if (v === true) node.setAttribute(k, '');
    else node.setAttribute(k, v);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}
const $ = (sel) => document.querySelector(sel);
const clear = (node) => { while (node.firstChild) node.removeChild(node.firstChild); return node; };

function tc(seconds) {
  const s = Math.max(0, Math.floor(Number(seconds) || 0));
  return [Math.floor(s / 3600), Math.floor(s / 60) % 60, s % 60]
    .map((n) => String(n).padStart(2, '0')).join(':');
}
function parseTc(text) {
  if (!text) return 0;
  const parts = String(text).trim().split(':').map(Number);
  if (parts.some(Number.isNaN)) return 0;
  return parts.reduce((acc, n) => acc * 60 + n, 0);
}
function bytes(n) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let v = Number(n) || 0, i = 0;
  while (v >= 1024 && i < units.length - 1) { v /= 1024; i += 1; }
  return `${v < 10 && i ? v.toFixed(1) : Math.round(v)}${units[i]}`;
}
/* Latin data (timecodes, paths, timestamps) inside an RTL page must be
   bidi-isolated or the browser reorders it - "00:00:03 - 00:00:07" would
   render backwards. <bdi> keeps the text LTR without breaking the layout. */
const bdi = (text, dir = 'ltr') => el('bdi', { dir }, text === null || text === undefined ? '' : text);

function localTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} `
       + `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function toast(message, kind = '') {
  const node = el('div', { class: `toast ${kind}` }, message);
  $('#toasts').append(node);
  setTimeout(() => node.remove(), kind === 'bad' ? 8000 : 4000);
}

async function api(path, { method = 'GET', body, form } = {}) {
  const opts = { method, credentials: 'same-origin', headers: {} };
  if (form) opts.body = form;
  else if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const response = await fetch(path, opts);
  if (response.status === 401 && S.user) { showLogin(); throw new Error('signed out'); }
  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = { detail: text }; }
  if (!response.ok) {
    const detail = (data && (data.detail || data.message)) || response.statusText;
    const error = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    error.status = response.status;
    throw error;
  }
  return data;
}
const guard = (fn) => async (...args) => {
  try { return await fn(...args); } catch (err) { toast(err.message, 'bad'); }
};

function modal(title, ...content) {
  const backdrop = el('div', { class: 'modal-backdrop', onclick: (e) => {
    if (e.target === backdrop) backdrop.remove();
  } });
  const box = el('div', { class: 'modal' },
    el('div', { class: 'spread' }, el('h2', {}, title),
      el('button', { class: 'btn ghost small', onclick: () => backdrop.remove() }, t('close'))),
    ...content);
  backdrop.append(box);
  $('#modal-root').append(backdrop);
  return backdrop;
}

function field(labelText, input) {
  return el('label', { class: 'field' }, el('span', {}, labelText), input);
}
function checkbox(id, labelText, checked = false) {
  return el('label', { class: 'row', style: 'gap:6px' },
    el('input', { type: 'checkbox', id, checked }), el('span', {}, labelText));
}

/* --------------------------------------------------------------- session */
async function boot() {
  applyLang();
  try {
    const me = await api('/api/auth/me');
    S.user = me.user; S.caps = me.capabilities;
    await showApp();
  } catch { showLogin(); }
}

function showLogin() {
  S.user = null;
  if (S.pollTimer) { clearInterval(S.pollTimer); S.pollTimer = null; }
  $('#app').classList.add('hidden');
  $('#login').classList.remove('hidden');
}

async function showApp() {
  $('#login').classList.add('hidden');
  $('#app').classList.remove('hidden');
  $('#whoami').textContent = `${S.user.username} · ${S.user.role}`;
  try {
    const me = await api('/api/auth/me');
    S.user = me.user; S.caps = me.capabilities;
  } catch { /* keep what we have */ }
  try { S.settings = (await api('/api/settings')).settings; } catch { S.settings = {}; }
  $('#site-name').textContent = S.settings.site_name || 'vscan';
  renderTabs();
  await refreshCore();
  await renderTab();
  if (!S.pollTimer) S.pollTimer = setInterval(pollJobs, 2500);
}

const TABS = [
  ['overview', 'viewer'], ['footage', 'viewer'], ['search', 'viewer'],
  ['people', 'viewer'], ['faces', 'viewer'], ['jobs', 'viewer'],
  ['audit', 'admin'], ['settings', 'viewer'],
];
const RANK = { viewer: 0, analyst: 1, admin: 2 };
const can = (role) => RANK[S.user.role] >= RANK[role];

function renderTabs() {
  const nav = clear($('#tabs'));
  for (const [key, role] of TABS) {
    if (!can(role)) continue;
    nav.append(el('button', {
      class: S.tab === key ? 'active' : '',
      onclick: () => { S.tab = key; renderTabs(); renderTab(); },
    }, t(key)));
  }
}

async function refreshCore() {
  const [videos, persons] = await Promise.all([
    api('/api/videos').catch(() => ({ videos: [] })),
    api('/api/persons').catch(() => ({ persons: [] })),
  ]);
  S.videos = videos.videos; S.persons = persons.persons;
}

const VIEWS = {};
async function renderTab() {
  const view = clear($('#view'));
  const render = VIEWS[S.tab] || VIEWS.overview;
  view.append(el('div', { class: 'muted small' }, ''));
  try {
    const node = await render();
    clear(view).append(node);
  } catch (err) {
    clear(view).append(el('div', { class: 'card' }, err.message));
  }
}

/* -------------------------------------------------------------- overview */
VIEWS.overview = async () => {
  const stats = await api('/api/stats');
  const wrap = el('div');
  const tiles = [
    [t('videos'), stats.index.videos], [t('hours'), stats.footage_hours],
    [t('frames'), stats.index.frames], [t('facesFound'), stats.index.faces],
    [t('byAppearance'), stats.index.appearances ?? 0],
    [t('objects'), stats.index.objects], [t('persons'), stats.index.persons],
    [t('running'), stats.jobs.running], [t('queued'), stats.jobs.queued],
  ];
  wrap.append(el('div', { class: 'cards stats' },
    tiles.map(([label, value]) => el('div', { class: 'card stat' },
      el('div', { class: 'muted small' }, label),
      el('div', { class: 'n mono' }, bdi(value))))));
  wrap.append(el('div', { class: 'card' }, el('p', { class: 'legal' }, t('legal'))));
  if (!S.videos.length) {
    wrap.append(el('div', { class: 'card' }, el('p', {}, t('nothingIndexed')),
      el('button', { class: 'btn', onclick: () => { S.tab = 'footage'; renderTabs(); renderTab(); } },
        t('addFootage'))));
  }
  return wrap;
};

/* --------------------------------------------------------------- footage */
VIEWS.footage = async () => {
  const wrap = el('div');
  if (can('analyst')) wrap.append(await footageImportCard());

  const rows = S.videos.map((v) => el('tr', {},
    el('td', {}, el('div', {}, bdi(v.name)),
      el('div', { class: 'small muted' }, bdi(v.path)),
      v.uploaded ? el('span', { class: 'pill' }, t('uploaded')) : null,
      v.available ? null : el('span', { class: 'pill bad' }, t('videoUnavailable'))),
    el('td', { class: 'mono' }, bdi(v.duration_tc)),
    el('td', { class: 'mono' }, bdi(`${v.width}×${v.height}`)),
    el('td', { class: 'mono' }, bdi(v.frames)),
    el('td', { class: 'mono' }, bdi(v.faces)),
    el('td', { class: 'mono' }, bdi(v.objects)),
    el('td', { class: 'small' }, bdi(localTime(v.indexed_at))),
    el('td', {}, can('analyst') ? el('button', {
      class: 'btn ghost small danger', onclick: guard(async () => {
        if (!confirm(v.uploaded ? t('confirmRemoveUpload') : t('confirmRemove'))) return;
        await api(`/api/videos/${v.id}`, { method: 'DELETE' });
        toast(t('deleted'), 'ok'); await refreshCore(); renderTab();
      }),
    }, t('remove')) : null)));

  wrap.append(el('div', { class: 'card' }, el('h2', {}, t('footage')),
    S.videos.length ? el('table', {},
      el('thead', {}, el('tr', {}, [t('name'), t('duration'), '', t('frames'),
        t('facesFound'), t('objects'), t('indexed'), ''].map((h) => el('th', {}, h)))),
      el('tbody', {}, rows)) : el('p', { class: 'muted' }, t('nothingIndexed'))));
  return wrap;
};

function uploadVideo(file, options, onProgress) {
  // XHR rather than fetch: it reports upload progress, and a recording can be
  // gigabytes - the operator needs to see it moving.
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append('file', file);
    form.append('objects', String(options.objects));
    form.append('appearance', String(options.appearance));
    form.append('sample_fps', String(options.sample_fps));
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/videos/upload');
    xhr.withCredentials = true;
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) onProgress(e.loaded / e.total);
    });
    xhr.addEventListener('load', () => {
      let data = null;
      try { data = JSON.parse(xhr.responseText); } catch { data = null; }
      if (xhr.status >= 200 && xhr.status < 300) resolve(data);
      else reject(new Error((data && data.detail) || `HTTP ${xhr.status}`));
    });
    xhr.addEventListener('error', () => reject(new Error('network error')));
    xhr.send(form);
  });
}

function uploadCard(getOptions, toggles) {
  const input = el('input', { type: 'file', accept: 'video/*', class: 'hidden' });
  const zone = el('div', { class: 'dropzone' },
    el('div', { class: 'big' }, t('dropHere')),
    el('div', { class: 'hint' }, t('dropHint')));
  const progress = el('div', {});

  async function send(files) {
    for (const file of [...files]) {
      const bar = el('i', { style: 'width:0%' });
      const row = el('div', { class: 'upload-row' },
        el('span', { class: 'name' }, el('bdi', { dir: 'ltr' }, file.name)),
        el('span', { class: 'small muted mono' }, bytes(file.size)),
        el('div', { class: 'bar', style: 'flex:1' }, bar));
      progress.append(row);
      try {
        const result = await uploadVideo(file, getOptions(),
          (fraction) => { bar.style.width = `${Math.round(fraction * 100)}%`; });
        bar.style.width = '100%';
        toast(`${t('uploadDone')}: ${result.name}`, 'ok');
        row.append(el('span', { class: 'pill ok small' }, `#${result.job_id}`));
      } catch (err) {
        toast(`${file.name}: ${err.message}`, 'bad');
        row.append(el('span', { class: 'pill bad small' }, err.message));
      }
    }
    await refreshCore();
  }

  zone.addEventListener('click', () => input.click());
  input.addEventListener('change', guard(() => send(input.files)));
  ['dragenter', 'dragover'].forEach((name) => zone.addEventListener(name, (e) => {
    e.preventDefault(); zone.classList.add('over');
  }));
  ['dragleave', 'drop'].forEach((name) => zone.addEventListener(name, (e) => {
    e.preventDefault(); zone.classList.remove('over');
  }));
  zone.addEventListener('drop', guard((e) => send(e.dataTransfer.files)));

  return el('div', {}, zone, input,
    toggles ? el('div', { class: 'row', style: 'margin-top:10px' }, ...toggles) : null,
    progress);
}

async function footageImportCard() {
  const selected = new Set();
  const chosen = el('div', { class: 'small muted' }, `0 ${t('selected')}`);
  const list = el('div', { class: 'filebrowser' });

  async function loadDir(path) {
    const data = await api(`/api/sources/browse?path=${encodeURIComponent(path || '')}`);
    clear(list);
    if (data.parent) {
      list.append(el('div', { class: 'entry', onclick: guard(() => loadDir(data.parent)) },
        el('span', {}, '⬆'), el('span', {}, '..')));
    }
    for (const dir of data.dirs) {
      list.append(el('div', { class: 'entry', onclick: guard(() => loadDir(dir.path)) },
        el('span', {}, '📁'), el('span', {}, dir.name)));
    }
    for (const file of data.files) {
      const box = el('input', { type: 'checkbox', checked: selected.has(file.path) });
      box.addEventListener('change', () => {
        if (box.checked) selected.add(file.path); else selected.delete(file.path);
        chosen.textContent = `${selected.size} ${t('selected')}`;
      });
      list.append(el('div', { class: 'entry', onclick: (e) => {
        if (e.target !== box) { box.checked = !box.checked; box.dispatchEvent(new Event('change')); }
      } }, box, el('span', {}, '🎬'), el('span', { class: 'grow' }, file.name),
        el('span', { class: 'small muted mono' }, bytes(file.bytes))));
    }
  }

  const fps = el('input', { type: 'number', value: '2', step: '0.5', min: '0.1' });
  const width = el('input', { type: 'number', value: '1280', step: '160', min: '320' });
  const motion = el('input', { type: 'number', value: '0.004', step: '0.001', min: '0' });
  const startTime = el('input', { type: 'text', dir: 'ltr',
    placeholder: '2026-08-30 14:00:00' });
  const objectsBox = checkbox('opt-objects', t('detectObjects'), true);
  const appearanceBox = checkbox('opt-appearance', t('detectAppearance'), true);
  const forceBox = checkbox('opt-force', t('force'), false);

  const card = el('div', { class: 'card' },
    el('h2', {}, t('addFootage')),
    uploadCard(() => ({
      objects: objectsBox.querySelector('input').checked,
      appearance: appearanceBox.querySelector('input').checked,
      sample_fps: Number(fps.value),
    }), [objectsBox, appearanceBox]),
    el('h3', { style: 'margin-top:18px' }, t('orPickFromServer')),
    el('div', { class: 'row' },
      ...(S.caps.footage_dirs || []).map((dir) => el('button', {
        class: 'btn ghost small', onclick: guard(() => loadDir(dir)),
      }, dir)),
      chosen),
    list,
    el('h3', { style: 'margin-top:14px' }, t('options')),
    el('div', { class: 'row' },
      el('div', { style: 'min-width:150px' }, field(t('sampleFps'), fps)),
      el('div', { style: 'min-width:150px' }, field(t('width'), width)),
      el('div', { style: 'min-width:150px' }, field(t('motion'), motion)),
      el('div', { style: 'min-width:210px' }, field(t('startTime'), startTime)),
      forceBox),
    el('button', { class: 'btn', onclick: guard(async () => {
      if (!selected.size) { toast(t('selected') + ': 0', 'bad'); return; }
      const response = await api('/api/videos/index', { method: 'POST', body: {
        paths: [...selected],
        force: forceBox.querySelector('input').checked,
        start_time: startTime.value.trim() || null,
        options: {
          sample_fps: Number(fps.value), width: Number(width.value),
          motion: Number(motion.value),
          objects: objectsBox.querySelector('input').checked,
          appearance: appearanceBox.querySelector('input').checked,
        },
      } });
      toast(`${t('jobStarted')} #${response.job_id}`, 'ok');
      selected.clear(); chosen.textContent = `0 ${t('selected')}`;
      S.tab = 'jobs'; renderTabs(); renderTab();
    }) }, t('startIndexing')));

  if ((S.caps.footage_dirs || []).length) await loadDir(S.caps.footage_dirs[0]).catch(() => {});
  return card;
}

/* ---------------------------------------------------------------- search */
VIEWS.search = async () => {
  const wrap = el('div');
  const box = el('input', { type: 'search', autocomplete: 'off',
    placeholder: t('searchPlaceholder'), style: 'font-size:17px; padding:12px 14px' });
  const interpretation = el('div', { class: 'small muted', style: 'margin-top:8px' });
  const resultsBox = el('div');

  // filters, folded away: most searches need none of them
  const videoPick = el('select', {}, el('option', { value: '' }, t('allVideos')),
    ...S.videos.map((v) => el('option', { value: v.id }, v.name)));
  const from = el('input', { type: 'text', dir: 'ltr', placeholder: '00:00:00' });
  const to = el('input', { type: 'text', dir: 'ltr', placeholder: '' });
  const gap = el('input', { type: 'number', value: '5', min: '0', step: '1' });
  const arrivalsBox = checkbox('f-arrivals', t('onlyArrivals'), false);
  const absence = el('input', { type: 'number', value: '300', min: '10', step: '10' });
  const maxFrames = el('input', { type: 'number', value: '400', step: '50', min: '9' });
  const advanced = el('div', { class: 'hidden' },
    el('div', { class: 'row', style: 'margin-top:12px' },
      el('div', { style: 'min-width:200px' }, field(t('videos'), videoPick)),
      el('div', { style: 'min-width:120px' }, field(t('from'), from)),
      el('div', { style: 'min-width:120px' }, field(t('to'), to)),
      el('div', { style: 'min-width:130px' }, field(t('gap'), gap)),
      el('div', { style: 'min-width:150px' }, field(t('absence'), absence)),
      el('div', { style: 'min-width:150px' }, field(t('maxFrames'), maxFrames)),
      arrivalsBox));
  const advancedToggle = el('button', { class: 'btn ghost small', onclick: () => {
    advanced.classList.toggle('hidden');
  } }, t('advanced'));

  const filters = () => ({
    video_ids: videoPick.value ? [Number(videoPick.value)] : null,
    start: parseTc(from.value), end: to.value ? parseTc(to.value) : null,
    gap: Number(gap.value), arrivals: arrivalsBox.querySelector('input').checked,
    absence: Number(absence.value), max_frames: Number(maxFrames.value),
  });

  async function run(forceMode) {
    const query = box.value.trim();
    if (!query) return;
    clear(interpretation);
    clear(resultsBox);
    const data = await api('/api/search', { method: 'POST',
      body: { query, ...filters(), force_mode: forceMode || null } });
    showInterpretation(data);
    if (data.job_id) {
      resultsBox.append(askProgress(data.job_id, resultsBox, query));
    } else if (data.needs) {
      resultsBox.append(missingCard(data));
    } else {
      showResults(resultsBox, data.events, query);
    }
  }

  function reasonText(intent) {
    const key = { person_enrolled: 'whyPerson', objects_known: 'whyObjects',
                  descriptive_word: 'whyDescriptive', unknown_word: 'whyUnknown',
                  not_measurable: 'whyNotMeasurable' }[intent.reason_code];
    if (!key) return intent.reason || '';
    const word = intent.reason_code === 'objects_known'
      ? labelList((intent.reason_word || '').split(', ').filter(Boolean))
      : intent.reason_word;
    return word ? `"${word}" ${t(key)}` : t(key);
  }

  function showInterpretation(data) {
    const intent = data.intent || {};
    const label = { person: t('modePerson'), objects: t('modeObjects'),
                    ask: t('modeAsk') }[intent.mode] || '';
    const why = reasonText(intent);
    clear(interpretation).append(
      el('span', {}, `${t('searchedAs')}: `),
      el('b', {}, label),
      why ? el('span', {}, ' — ') : null,
      why ? el('span', { dir: 'auto' }, why) : null);
    // let the operator overrule us in one click
    const others = ['person', 'objects', 'ask'].filter((m) => m !== intent.mode
      && (m !== 'person' || S.persons.length));
    for (const mode of others) {
      interpretation.append(' ', el('button', {
        class: 'btn ghost small', onclick: guard(() => run(mode)),
      }, { person: t('modePerson'), objects: t('modeObjects'),
           ask: t('modeAsk') }[mode]));
    }
  }

  function missingCard(data) {
    const needs = data.needs || {};
    const intent = data.intent || {};
    const card = el('div', { class: 'card' },
      el('h3', {}, t('cannotAnswerYet')),
      el('p', { class: 'legal' },
        needs.role ? t('askNeedsAnalyst')
          : needs.key ? (can('admin') ? t('askNeedsKeyAdmin') : t('askNeedsKey'))
            : t('askSwitchedOff')));
    if (intent.fallback && intent.fallback.labels.length) {
      card.append(el('p', {}, t('meanwhile')),
        el('button', { class: 'btn', onclick: guard(() => run('objects')) },
          `${t('modeObjects')}: ${labelList(intent.fallback.labels)}`));
    }
    if (needs.key && can('admin')) {
      card.append(' ', el('button', { class: 'btn ghost', onclick: () => {
        S.tab = 'settings'; renderTabs(); renderTab();
      } }, t('settings')));
    }
    return card;
  }

  const runButton = el('button', { class: 'btn', onclick: guard(async () => {
    runButton.disabled = true;
    try { await run(null); } finally { runButton.disabled = false; }
  }) }, t('run'));
  box.addEventListener('keydown', (e) => { if (e.key === 'Enter') runButton.click(); });

  const examples = el('div', { class: 'row', style: 'margin-top:10px' },
    el('span', { class: 'small muted' }, `${t('examples')}:`),
    ...(S.lang === 'he'
      ? ['מתי הרכב הלבן זז', 'איש עם חולצה לבנה', 'רכב', 'מישהו משאיר תיק']
      : ['when did the white car move', 'a man in a white shirt', 'car',
         'someone leaving a bag'])
      .map((text) => el('button', { class: 'btn ghost small', onclick: () => {
        box.value = text; runButton.click();
      } }, text)),
    ...S.persons.slice(0, 3).map((person) => el('button', {
      class: 'btn ghost small', onclick: () => { box.value = person.name; runButton.click(); },
    }, person.name)));

  wrap.append(el('div', { class: 'card' },
    el('div', { class: 'row' }, el('div', { class: 'grow' }, box), runButton,
      advancedToggle),
    interpretation, examples, advanced), resultsBox);
  return wrap;
};

function askProgress(jobId, container, label) {
  const bar = el('i', { style: 'width:2%' });
  const message = el('div', { class: 'small muted' }, '…');
  const card = el('div', { class: 'card' }, el('h3', {}, `${t('byInstruction')} #${jobId}`),
    el('div', { class: 'bar' }, bar), message);
  const timer = setInterval(async () => {
    try {
      const { job } = await api(`/api/jobs/${jobId}`);
      bar.style.width = `${Math.round((job.progress || 0) * 100)}%`;
      message.textContent = job.message || job.status;
      if (['done', 'failed', 'cancelled'].includes(job.status)) {
        clearInterval(timer);
        if (job.status === 'done') {
          showResults(container, job.result.events, label);
          toast(`${job.result.events.length} ${t('results')} · ${job.result.requests} API calls`, 'ok');
        } else {
          message.textContent = job.error || job.status;
        }
      }
    } catch (err) { clearInterval(timer); toast(err.message, 'bad'); }
  }, 1500);
  return card;
}

function showResults(container, events, label) {
  S.results = events || []; S.resultsLabel = label || '';
  clear(container);
  const header = el('div', { class: 'spread' },
    el('h2', {}, `${t('results')}: ${S.results.length}`),
    el('div', { class: 'row' },
      can('analyst') && S.results.length ? el('button', {
        class: 'btn ghost small', onclick: guard(async () => {
          const started = await api('/api/export/clips', { method: 'POST', body: {
            events: S.results, pad: 3 } });
          toast(`${t('jobStarted')} #${started.job_id}`, 'ok');
          S.tab = 'jobs'; renderTabs(); renderTab();
        }),
      }, t('exportClips')) : null,
      S.results.length ? el('button', { class: 'btn ghost small', onclick: () => {
        const blob = new Blob([JSON.stringify({ label: S.resultsLabel, events: S.results }, null, 2)],
          { type: 'application/json' });
        const link = el('a', { href: URL.createObjectURL(blob), download: 'vscan-results.json' });
        document.body.append(link); link.click(); link.remove();
      } }, t('downloadJson')) : null));

  const grid = el('div', { class: 'cards' }, ...S.results.map(resultCard));
  container.append(el('div', { class: 'card' }, header,
    S.results.length ? grid : el('p', { class: 'muted' }, t('noResults'))));
}

async function findSimilar(event) {
  // A face hit carries a face box, which is the wrong crop for appearance
  // search - let the server pick the person box indexed nearest that moment.
  const box = event.meta && event.meta.table === 'appearances' ? event.meta.box : null;
  const data = await api('/api/search/similar', { method: 'POST', body: {
    video_id: event.video_id, t: event.best_t, box, gap: 5 } });
  S.tab = 'search'; renderTabs();
  await renderTab();
  const host = document.querySelector('#view > div');
  const box2 = el('div');
  host.append(box2);
  showResults(box2, data.events, `${t('similarTo')} ${tc(event.best_t)}`);
  toast(`${data.events.length} ${t('results')}`, data.events.length ? 'ok' : '');
}

function resultCard(event) {
  const thumb = event.best_thumb
    ? `/api/media/thumb?path=${encodeURIComponent(event.best_thumb)}`
    : `/api/media/frame/${event.video_id}?t=${event.best_t}&width=480`;
  return el('div', { class: 'result', onclick: () => openEvent(event) },
    el('img', { src: thumb, loading: 'lazy', alt: '' }),
    el('div', { class: 'body' },
      el('div', { class: 'tc' }, bdi(`${tc(event.start)} – ${tc(event.end)}`)),
      event.wall_start
        ? el('div', { class: 'small muted' }, bdi(localTime(event.wall_start))) : null,
      el('div', { class: 'small muted' },
        bdi(event.video_path.split('/').pop()), ' · ',
        bdi(event.hits), ` ${t('hits')} · ${t('score')} `, bdi(Number(event.best_score).toFixed(2))),
      event.meta && event.meta.note ? el('div', { class: 'small', dir: 'auto' }, event.meta.note) : null,
      el('button', {
        class: 'btn ghost small', style: 'margin-top:8px',
        onclick: guard(async (e) => { e.stopPropagation(); await findSimilar(event); }),
      }, t('findSimilar'))));
}

const PREVIEW_PAD = 3;

function openEvent(event) {
  const start = Math.max(0, event.start - PREVIEW_PAD);
  const duration = Math.min(180, (event.end - event.start) + PREVIEW_PAD * 2 + 2);
  const status = el('div', { class: 'small muted' }, '');
  const video = el('video', { controls: true, autoplay: true, preload: 'auto',
    src: `/api/media/preview/${event.video_id}`
       + `?start=${start.toFixed(2)}&duration=${duration.toFixed(2)}` });
  video.addEventListener('error', () => {
    status.textContent = t('videoUnavailable');
    status.className = 'small';
    status.style.color = 'var(--bad)';
  });

  const details = el('table', {}, el('tbody', {},
    el('tr', {}, el('th', {}, t('from')), el('td', { class: 'mono' }, bdi(tc(event.start)))),
    el('tr', {}, el('th', {}, t('to')), el('td', { class: 'mono' }, bdi(tc(event.end)))),
    event.wall_start ? el('tr', {}, el('th', {}, t('when')),
      el('td', {}, bdi(localTime(event.wall_start)))) : null,
    el('tr', {}, el('th', {}, t('score')),
      el('td', { class: 'mono' }, bdi(Number(event.best_score).toFixed(3)))),
    el('tr', {}, el('th', {}, t('hits')), el('td', { class: 'mono' }, bdi(event.hits))),
    event.meta && event.meta.note
      ? el('tr', {}, el('th', {}, t('note')), el('td', { dir: 'auto' }, event.meta.note)) : null,
    el('tr', {}, el('th', {}, t('videos')),
      el('td', { class: 'small' }, bdi(event.video_path)))));

  const box = modal(`${event.label || ''} ${tc(event.start)}`, video, status, details,
    el('div', { class: 'row', style: 'margin-top:10px' },
      el('a', { class: 'small', href: `/api/media/video/${event.video_id}`,
        target: '_blank', rel: 'noopener' }, t('open')),
      el('button', { class: 'btn ghost small', onclick: guard(async () => {
        box.remove(); await findSimilar(event);
      }) }, t('findSimilar')),
      can('analyst') ? el('button', { class: 'btn ghost small', onclick: guard(async () => {
        const started = await api('/api/export/clips', { method: 'POST', body: {
          events: [event], pad: PREVIEW_PAD } });
        toast(`${t('jobStarted')} #${started.job_id}`, 'ok');
      }) }, t('exportClips')) : null));
}

/* ---------------------------------------------------------------- people */
VIEWS.people = async () => {
  const wrap = el('div');
  if (can('analyst')) {
    const nameInput = el('input', { type: 'text' });
    wrap.append(el('div', { class: 'card' }, el('h2', {}, t('addPerson')),
      el('div', { class: 'row' }, el('div', { style: 'min-width:240px' },
        field(t('personName'), nameInput)),
        el('button', { class: 'btn', onclick: guard(async () => {
          if (!nameInput.value.trim()) return;
          await api('/api/persons', { method: 'POST', body: { name: nameInput.value.trim() } });
          nameInput.value = ''; toast(t('saved'), 'ok');
          await refreshCore(); renderTab();
        }) }, t('addPerson')))));
  }

  const cards = S.persons.map((person) => el('div', { class: 'face' },
    el('img', { src: person.thumb
      ? `/api/media/thumb?path=${encodeURIComponent(person.thumb)}`
      : 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"/>', alt: '' }),
    el('div', { class: 'body' },
      el('div', { style: 'font-weight:600' }, person.name),
      el('div', { class: 'small muted' },
        `${person.face_references ?? person.references} ${t('references')}`
        + (person.appearance_references
            ? ` · ${person.appearance_references} ${t('appearanceRefs')}` : '')),
      el('div', { class: 'row', style: 'justify-content:center;margin-top:6px' },
        el('button', { class: 'btn ghost small', onclick: () => {
          S.tab = 'search'; renderTabs(); renderTab().then(() => {
            const select = $('#view select'); if (select) select.value = 'person';
          });
        } }, t('search')),
        can('analyst') ? el('button', { class: 'btn ghost small',
          onclick: () => personModal(person) }, t('open')) : null))));

  wrap.append(el('div', { class: 'card' }, el('h2', {}, t('people')),
    S.persons.length ? el('div', { class: 'face-grid' }, ...cards)
      : el('p', { class: 'muted' }, t('noPersons'))));
  return wrap;
};

function personModal(person) {
  const fileInput = el('input', { type: 'file', accept: 'image/*', multiple: true });
  const videoPick = el('select', {}, ...S.videos.map((v) => el('option', { value: v.id }, v.name)));
  const at = el('input', { type: 'text', placeholder: '00:03:12' });
  const appearanceVideo = el('select', {},
    ...S.videos.map((v) => el('option', { value: v.id }, v.name)));
  const appearanceAt = el('input', { type: 'text', placeholder: '00:03:12' });
  const box = modal(person.name,
    el('h3', {}, t('uploadPhotos')),
    fileInput,
    el('button', { class: 'btn small', style: 'margin-top:8px', onclick: guard(async () => {
      if (!fileInput.files.length) return;
      const form = new FormData();
      for (const file of fileInput.files) form.append('files', file);
      const result = await api(`/api/persons/${person.id}/faces/upload`,
        { method: 'POST', form });
      toast(`+${result.added} ${t('references')}`, result.added ? 'ok' : 'bad');
      (result.skipped || []).forEach((s) => toast(s, 'bad'));
      await refreshCore(); box.remove(); renderTab();
    }) }, t('uploadPhotos')),
    el('h3', { style: 'margin-top:18px' }, t('addAppearance')),
    el('p', { class: 'small muted', style: 'margin-top:0' }, t('appearanceHint')),
    el('div', { class: 'row' },
      el('div', { style: 'min-width:220px' }, field(t('videos'), appearanceVideo)),
      el('div', { style: 'min-width:150px' }, field(t('atTimecode'), appearanceAt)),
      el('button', { class: 'btn small', onclick: guard(async () => {
        const result = await api(`/api/persons/${person.id}/appearance`,
          { method: 'POST', body: { video_id: Number(appearanceVideo.value),
            t: parseTc(appearanceAt.value) } });
        toast(`+1 ${t('appearanceRefs')} (${result.appearance_references})`, 'ok');
        await refreshCore(); box.remove(); renderTab();
      }) }, t('save'))),
    el('h3', { style: 'margin-top:18px' }, t('enrollFromVideo')),
    el('div', { class: 'row' },
      el('div', { style: 'min-width:220px' }, field(t('videos'), videoPick)),
      el('div', { style: 'min-width:150px' }, field(t('atTimecode'), at)),
      el('button', { class: 'btn small', onclick: guard(async () => {
        const result = await api(`/api/persons/${person.id}/faces/from-video`,
          { method: 'POST', body: { video_id: Number(videoPick.value),
            times: [parseTc(at.value)] } });
        toast(`+${result.added} ${t('references')}`, result.added ? 'ok' : 'bad');
        await refreshCore(); box.remove(); renderTab();
      }) }, t('save'))),
    el('hr', { style: 'margin:18px 0;border:0;border-top:1px solid var(--line)' }),
    el('button', { class: 'btn danger small', onclick: guard(async () => {
      if (!confirm(`${t('remove')} ${person.name}?`)) return;
      await api(`/api/persons/${person.id}`, { method: 'DELETE' });
      toast(t('deleted'), 'ok'); box.remove(); await refreshCore(); renderTab();
    }) }, t('remove')));
}

/* ----------------------------------------------------------------- faces */
VIEWS.faces = async () => {
  const wrap = el('div');
  const data = await api('/api/clusters');
  if (can('analyst')) {
    const minSize = el('input', { type: 'number', value: '3', min: '1' });
    const threshold = el('input', { type: 'number', value: '0.45', step: '0.01' });
    wrap.append(el('div', { class: 'card' }, el('h2', {}, t('groupFaces')),
      el('div', { class: 'row' },
        el('div', { style: 'min-width:150px' }, field(t('clusterSize'), minSize)),
        el('div', { style: 'min-width:150px' }, field(t('threshold'), threshold)),
        el('button', { class: 'btn', onclick: guard(async () => {
          const started = await api('/api/cluster', { method: 'POST', body: {
            min_size: Number(minSize.value), threshold: Number(threshold.value) } });
          toast(`${t('jobStarted')} #${started.job_id}`, 'ok');
          S.tab = 'jobs'; renderTabs(); renderTab();
        }) }, t('groupFaces')))));
  }

  const cards = (data.clusters || []).map((cluster) => el('div', { class: 'face' },
    el('img', { src: cluster.crop
      ? `/api/media/thumb?path=${encodeURIComponent(cluster.crop)}`
      : `/api/media/frame/${(cluster.videos[0] || {}).id || 0}?t=${cluster.first_seen || 0}`,
      loading: 'lazy', alt: '' }),
    el('div', { class: 'body' },
      el('div', { style: 'font-weight:600' }, `#${cluster.id}`),
      el('div', { class: 'small muted mono' },
        bdi(`${cluster.size} · ${tc(cluster.first_seen)}–${tc(cluster.last_seen)}`)),
      can('analyst') ? el('button', { class: 'btn ghost small', style: 'margin-top:6px',
        onclick: guard(async () => {
          const name = prompt(t('nameThis'));
          if (!name) return;
          const person = await api('/api/persons', { method: 'POST', body: { name } });
          const result = await api(`/api/persons/${person.person.id}/faces/from-cluster`,
            { method: 'POST', body: { cluster_id: cluster.id } });
          toast(`${name}: +${result.added} ${t('references')}`, 'ok');
          await refreshCore(); renderTab();
        }) }, t('nameThis')) : null)));

  wrap.append(el('div', { class: 'card' }, el('h2', {}, t('faces')),
    cards.length ? el('div', { class: 'face-grid' }, ...cards)
      : el('p', { class: 'muted' }, t('noClusters'))));
  return wrap;
};

/* ------------------------------------------------------------------ jobs */
const JOB_PILL = { done: 'ok', running: 'run', queued: '', failed: 'bad', cancelled: 'bad' };

VIEWS.jobs = async () => {
  const { jobs } = await api('/api/jobs?limit=40');
  S.jobs = jobs;
  return el('div', { class: 'card' }, el('h2', {}, t('jobs')),
    el('table', {}, el('thead', {}, el('tr', {},
      ['#', t('action'), t('status'), t('progress'), t('created'), ''].map((h) => el('th', {}, h)))),
      el('tbody', { id: 'jobs-body' }, ...jobs.map(jobRow))));
};

function jobRow(job) {
  const summary = job.status === 'failed' ? job.error
    : job.status === 'done' ? jobSummary(job) : (job.message || '');
  return el('tr', {},
    el('td', { class: 'mono' }, bdi(job.id)),
    el('td', {}, el('div', {}, job.title || job.kind),
      el('div', { class: 'small muted', dir: 'auto' }, summary || '')),
    el('td', {}, el('span', { class: `pill ${JOB_PILL[job.status] || ''}` }, job.status)),
    el('td', { style: 'min-width:120px' },
      el('div', { class: 'bar' }, el('i', { style: `width:${Math.round((job.progress || 0) * 100)}%` }))),
    el('td', { class: 'small' }, bdi(localTime(job.created_at))),
    el('td', {}, ['queued', 'running'].includes(job.status) && can('analyst')
      ? el('button', { class: 'btn ghost small', onclick: guard(async () => {
          await api(`/api/jobs/${job.id}/cancel`, { method: 'POST' });
          toast(t('cancel'), 'ok');
        }) }, t('cancel'))
      : job.kind === 'export' && job.status === 'done'
        ? exportLinks(job) : null));
}

function jobSummary(job) {
  const result = job.result || {};
  if (job.kind === 'index' && result.totals) {
    const line = `${result.totals.frames} ${t('frames')} · `
      + `${result.totals.faces} ${t('facesFound')} · `
      + `${result.totals.appearances ?? 0} ${t('byAppearance')}`;
    const diagnosed = (result.videos || []).filter((v) => v.diagnosis);
    if (!diagnosed.length) return line;
    const why = diagnosed[0].diagnosis.map((d) => d.headline).join(' · ');
    return `${line} — ${t('nothingFound')}: ${why}`;
  }
  if (job.kind === 'ask' && result.events) {
    return `${result.events.length} ${t('results')} · ${result.requests} API calls`;
  }
  if (job.kind === 'cluster') return `${result.clusters || 0} × ${t('faces')}`;
  if (job.kind === 'export') return `${(result.files || []).length} ${t('clip')}`;
  return '';
}

function exportLinks(job) {
  const files = (job.result || {}).files || [];
  return el('div', { class: 'row' }, ...files.slice(0, 20).map((file) => el('a', {
    class: 'small', href: `/api/export/file?path=${encodeURIComponent(file.path)}`,
  }, file.name)));
}

async function pollJobs() {
  if (!S.user) return;
  try {
    const { jobs } = await api('/api/jobs?limit=40');
    const active = jobs.some((j) => ['queued', 'running'].includes(j.status));
    const body = document.getElementById('jobs-body');
    if (body && S.tab === 'jobs') clear(body).append(...jobs.map(jobRow));
    const before = S.jobs.filter((j) => ['queued', 'running'].includes(j.status)).length;
    S.jobs = jobs;
    if (before && !active && ['footage', 'overview', 'faces'].includes(S.tab)) {
      await refreshCore(); renderTab();
    }
  } catch { /* transient - the next tick tries again */ }
}

/* ----------------------------------------------------------------- audit */
VIEWS.audit = async () => {
  const search = el('input', { type: 'search', placeholder: t('action') });
  const body = el('tbody', {});
  async function load() {
    const { entries } = await api(`/api/audit?limit=300${search.value
      ? `&action=${encodeURIComponent(search.value)}` : ''}`);
    clear(body).append(...entries.map((entry) => el('tr', {},
      el('td', { class: 'small' }, bdi(localTime(entry.ts))),
      el('td', {}, entry.username || '—'),
      el('td', {}, el('span', { class: 'pill' }, entry.action)),
      el('td', { class: 'small mono', dir: 'auto' },
        entry.detail ? JSON.stringify(entry.detail) : ''),
      el('td', { class: 'small mono' }, bdi(entry.ip || '')))));
  }
  search.addEventListener('input', guard(load));
  await load();
  return el('div', { class: 'card' }, el('div', { class: 'spread' },
    el('h2', {}, t('audit')), el('div', { style: 'max-width:260px' }, search)),
    el('table', {}, el('thead', {}, el('tr', {},
      [t('when'), t('user'), t('action'), t('detail'), 'IP'].map((h) => el('th', {}, h)))), body));
};

/* -------------------------------------------------------------- settings */
VIEWS.settings = async () => {
  const wrap = el('div');
  const data = await api('/api/settings');
  S.settings = data.settings;

  const current = el('input', { type: 'password', autocomplete: 'current-password' });
  const next = el('input', { type: 'password', autocomplete: 'new-password' });
  wrap.append(el('div', { class: 'card' }, el('h2', {}, t('changePassword')),
    el('div', { class: 'row' },
      el('div', { style: 'min-width:220px' }, field(t('currentPassword'), current)),
      el('div', { style: 'min-width:220px' }, field(t('newPassword'), next)),
      el('button', { class: 'btn', onclick: guard(async () => {
        await api('/api/auth/password', { method: 'POST', body: {
          current_password: current.value, new_password: next.value } });
        toast(t('saved'), 'ok'); showLogin();
      }) }, t('save')))));

  if (can('admin')) {
    const siteName = el('input', { type: 'text', value: S.settings.site_name || 'vscan' });
    const retention = el('input', { type: 'number', min: '0',
      value: S.settings.retention_days || 0 });
    const askBox = checkbox('set-ask', t('askEnabled'), !!S.settings.ask_enabled);
    const apiKey = el('input', { type: 'password', autocomplete: 'off',
      placeholder: S.settings.ask_key_set ? '••••••••••••  (' + t('apiKeySet') + ')' : 'sk-ant-...' });
    wrap.append(el('div', { class: 'card' }, el('h2', {}, t('settings')),
      el('div', { class: 'row' },
        el('div', { style: 'min-width:220px' }, field(t('siteName'), siteName)),
        el('div', { style: 'min-width:180px' }, field(t('retention'), retention)),
        askBox,
        el('button', { class: 'btn', onclick: guard(async () => {
          await api('/api/settings', { method: 'PATCH', body: {
            site_name: siteName.value, retention_days: Number(retention.value),
            ask_enabled: askBox.querySelector('input').checked } });
          toast(t('saved'), 'ok'); await showApp();
        }) }, t('save'))),
      el('div', { class: 'row', style: 'margin-top:14px' },
        el('div', { style: 'min-width:280px' }, field(t('apiKey'), apiKey)),
        el('button', { class: 'btn ghost', onclick: guard(async () => {
          const key = apiKey.value.trim();
          if (!key) return;
          await api('/api/settings/test-key', { method: 'POST', body: { api_key: key } });
          await api('/api/settings', { method: 'PATCH',
            body: { anthropic_api_key: key, ask_enabled: true } });
          apiKey.value = ''; toast(t('keyOk'), 'ok'); await showApp(); renderTab();
        }) }, t('testKey')),
        el('span', { class: 'small muted' },
          S.settings.ask_key_set
            ? `${t('apiKeySet')} (${S.settings.ask_key_source})` : t('apiKeyNone'))),
      el('p', { class: 'small muted' }, t('apiKeyHint')),
      el('div', { class: 'row', style: 'margin-top:12px' },
        el('button', { class: 'btn ghost small', onclick: guard(async () => {
          const result = await api('/api/maintenance/purge', { method: 'POST', body: {} });
          toast(`${t('purge')}: ${result.count}`, 'ok'); await refreshCore(); renderTab();
        }) }, t('purge')),
        el('button', { class: 'btn danger small', onclick: guard(async () => {
          if (!confirm(`${t('purgeAll')}?`)) return;
          const result = await api('/api/maintenance/purge',
            { method: 'POST', body: { everything: true } });
          toast(`${t('purgeAll')}: ${result.count}`, 'ok'); await refreshCore(); renderTab();
        }) }, t('purgeAll'))),
      el('p', { class: 'legal', style: 'margin-top:12px' }, t('legal')),
      el('p', { class: 'small muted' },
        `${data.deployment.data_dir} · ${data.deployment.workers} workers`)));
    wrap.append(await usersCard());
  }
  return wrap;
};

async function usersCard() {
  const { users, roles } = await api('/api/users');
  const name = el('input', { type: 'text' });
  const password = el('input', { type: 'password', autocomplete: 'new-password' });
  const role = el('select', {}, ...roles.map((r) => el('option', { value: r }, r)));
  const rows = users.map((user) => el('tr', {},
    el('td', {}, user.username),
    el('td', {}, el('select', { onchange: guard(async (e) => {
      await api(`/api/users/${user.id}`, { method: 'PATCH', body: { role: e.target.value } });
      toast(t('saved'), 'ok');
    }) }, ...roles.map((r) => el('option', { value: r, selected: r === user.role }, r)))),
    el('td', {}, el('input', { type: 'checkbox', checked: user.active,
      onchange: guard(async (e) => {
        await api(`/api/users/${user.id}`, { method: 'PATCH', body: { active: e.target.checked } });
        toast(t('saved'), 'ok');
      }) })),
    el('td', { class: 'small' }, bdi(localTime(user.last_login))),
    el('td', {}, el('button', { class: 'btn ghost small danger', onclick: guard(async () => {
      if (!confirm(`${t('remove')} ${user.username}?`)) return;
      await api(`/api/users/${user.id}`, { method: 'DELETE' });
      toast(t('deleted'), 'ok'); renderTab();
    }) }, t('remove')))));

  return el('div', { class: 'card' }, el('h2', {}, t('users')),
    el('table', {}, el('thead', {}, el('tr', {},
      [t('username'), t('role'), t('active'), t('signIn'), ''].map((h) => el('th', {}, h)))),
      el('tbody', {}, ...rows)),
    el('h3', { style: 'margin-top:16px' }, t('addUser')),
    el('div', { class: 'row' },
      el('div', { style: 'min-width:180px' }, field(t('username'), name)),
      el('div', { style: 'min-width:180px' }, field(t('password'), password)),
      el('div', { style: 'min-width:140px' }, field(t('role'), role)),
      el('button', { class: 'btn', onclick: guard(async () => {
        await api('/api/users', { method: 'POST', body: {
          username: name.value.trim(), password: password.value, role: role.value } });
        toast(t('saved'), 'ok'); name.value = ''; password.value = ''; renderTab();
      }) }, t('addUser'))));
}

/* ------------------------------------------------------------------ wire */
function applyLang() {
  document.documentElement.lang = S.lang;
  document.documentElement.dir = S.lang === 'he' ? 'rtl' : 'ltr';
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  const toggle = document.getElementById('lang-toggle');
  if (toggle) toggle.textContent = S.lang === 'he' ? 'EN' : 'עב';
}

document.getElementById('lang-toggle').addEventListener('click', () => {
  S.lang = S.lang === 'he' ? 'en' : 'he';
  localStorage.setItem('vscan.lang', S.lang);
  applyLang();
  if (S.user) { renderTabs(); renderTab(); }
});

document.getElementById('logout').addEventListener('click', guard(async () => {
  await api('/api/auth/logout', { method: 'POST' });
  showLogin();
}));

document.getElementById('login-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const error = document.getElementById('login-error');
  error.classList.add('hidden');
  try {
    await api('/api/auth/login', { method: 'POST', body: {
      username: document.getElementById('login-user').value,
      password: document.getElementById('login-pass').value } });
    document.getElementById('login-pass').value = '';
    const me = await api('/api/auth/me');
    S.user = me.user; S.caps = me.capabilities;
    await showApp();
  } catch (err) {
    error.textContent = err.message;
    error.classList.remove('hidden');
  }
});

boot();
