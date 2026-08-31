'use strict';
/* vscan operator console. No build step: this file is the whole front end. */

const S = {
  user: null, caps: {}, lang: localStorage.getItem('vscan.lang') || 'he',
  tab: 'overview', videos: [], persons: [], zones: [], lines: [], clusters: [],
  settings: {},
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
    model: 'מודל לחיפוש חופשי', cost: 'עלות', requests: 'בקשות',
    estimate: 'אומדן',
    costHint: 'העלות בפועל של החיפוש האחרון, לפי מספר הטוקנים שנצרכו.',
    whyPerson: 'רשום במערכת, אז זה חיפוש פנים',
    whyObjects: 'נמדד כבר באינדוקס — חיפוש מקומי, בלי עלות',
    thatMoved: 'שזז', thatStayed: 'שלא זז',
    whyDescriptive: 'מתאר מראה או תנועה, לא עצם שהגלאי מזהה',
    whyUnknown: 'לא משהו שהגלאי המקומי מכיר',
    whyNotMeasurable: 'מתאר משהו שהגלאים המקומיים לא יודעים למדוד',
    zones: 'אזורים', zoneNew: 'סימון אזור חדש', zoneName: 'שם האזור',
    zoneNamePh: 'למשל: דלת כניסה', zoneMode: 'מה לחפש', sensitivity: 'רגישות',
    zoneModeChange: 'שונה מהרגיל — דלת שנפתחה, חפץ שנעלם, רכב שחנה',
    zoneModeMotion: 'רגע השינוי — הדלת נעה, מישהו חצה את האזור',
    zoneDraw: 'גררו עם העכבר על התמונה כדי לסמן אזור',
    zoneSave: 'שמירת האזור', zoneNone: 'עדיין לא סומנו אזורים.',
    zoneEveryVideo: 'לעקוב אחרי המלבן הזה בכל הסרטונים (מצלמה קבועה)',
    zoneScope: 'תחולה', zoneSearch: 'חיפוש באזור', zoneDeleteConfirm: 'למחוק את האזור?',
    zoneUsualChange: 'שינוי רגיל באזור', zoneSuggested: 'רגישות מומלצת',
    zoneFlat: 'האזור הזה כמעט לא משתנה לאורך ההקלטה — ודאו שסימנתם את המקום הנכון.',
    zoneHint: 'דלת אינה "עצם" שגלאי מזהה, ולכן אי אפשר לחפש אותה כמו רכב. במקום זה מסמנים פעם אחת את המלבן שבו הדלת נמצאת, ומאז אפשר לשאול מתי הוא לא נראה כרגיל. הבדיקה רצה על התמונות הממוזערות שנשמרו באינדוקס — מקומית, בלי עלות, גם על הקלטה של 12 שעות.',
    zoneAtMoment: 'פריים מתוך הסרטון', zoneNamedAlready: 'כבר קיים אזור בשם הזה',
    modeZone: 'לפי אזור', whyZone: 'אזור במעקב — משווים את הפינה הזו לאיך שהיא נראית בדרך כלל',
    framesExamined: 'פריימים נבדקו', zoneNoVideos: 'צריך לאנדקס הקלטה אחת לפחות כדי לסמן אזור.',
    zoneScanning: 'סורק את האזור', zoneChanged: 'שינוי באזור',
    lines: 'קווי חצייה', kindArea: 'אזור (מלבן)', kindLine: 'קו חצייה',
    lineDraw: 'גררו קו במקום שבו אנשים עוברים — פתח דלת, שער, מסדרון',
    lineNone: 'עדיין לא סומנו קווים.', lineSearch: 'כל החציות',
    lineNew: 'סימון קו חצייה חדש', lineSave: 'שמירת הקו',
    lineNamePh: 'למשל: שער כניסה',
    lineEveryVideo: 'לספור על הקו הזה בכל הסרטונים (מצלמה קבועה)',
    lineHint: 'גלאי יודע לומר שאדם נמצא בנקודה מסוימת, אבל לא שהנקודה הזאת היא פתח, ולא אם האדם נכנס או יצא. מותחים קו פעם אחת במקום שבו עוברים, והמערכת סופרת כל חצייה עם הכיוון שלה — מתוך המסלולים שכבר נשמרו באינדוקס, מקומית ובלי עלות.',
    lineWhich: 'מה נספר', flipDirection: 'החלף כיוון',
    inArrow: 'החץ מסמן איזה כיוון נחשב "נכנס". לחיצה על "החלף כיוון" הופכת אותו.',
    directionIn: 'נכנס', directionOut: 'יצא',
    modeLine: 'לפי קו חצייה',
    whyLine: 'קו חצייה — מדווח מי חצה אותו, ולאיזה כיוון',
    crossings: 'חציות',
    noCrossingsThatWay: 'לא נמצאו חציות בכיוון הזה. בכיוון ההפוך כן נמצאו:',
    markUnknown: 'אני לא יודע איפה', markIt: 'סמן לי על התמונה',
    markTitle: 'סימון', markAndSearch: 'שמור וחפש', markReady: 'מסומן. אפשר לשמור ולחפש.',
    markAsArea: 'סמנו את המלבן שבו זה נמצא, ומאותו רגע אפשר לשאול עליו — מקומית, בלי עלות.',
    markAsLine: 'מתחו קו במקום שבו עוברים, ומאותו רגע אפשר לשאול מי נכנס ומי יצא — מקומית, בלי עלות.',
    lineName: 'שם הקו',
    inYourFootage: 'מה שיש בהקלטות שלך',
    noSuchObject: 'לא נמצא דבר כזה בהקלטות שאונדקסו. מה שכן נמצא בהן:',
    noSuchColour: 'לא נמצא בצבע הזה. הצבעים שנמצאו בפועל:',
    noColourData: 'ההקלטות האלה אונדקסו לפני שהמערכת מדדה צבעים. כדי לחפש לפי צבע צריך לאנדקס אותן מחדש (לשונית הקלטות ← לסמן "לאנדקס מחדש").',
    noSuchMotion: 'לא נמצא במצב התנועה הזה. אפשר לחפש בלי התנאי:', noFacesButPeople: 'לא נמצאו פנים ברורות בהקלטה הזאת — אפשר עדיין לחפש אנשים לפי מראה ולפי צבע בגדים',
    whatNow: 'מה עכשיו', goSearch: 'למסך החיפוש',
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
    model: 'Instruction-search model', cost: 'cost', requests: 'requests',
    estimate: 'estimate',
    costHint: 'What the last search actually cost, from the tokens it used.',
    whyPerson: 'is enrolled, so this is a face search',
    whyObjects: 'measured when the footage was indexed - local, and free',
    thatMoved: 'that moved', thatStayed: 'that stayed put',
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
    zones: 'Zones', zoneNew: 'Mark a new zone', zoneName: 'Zone name',
    zoneNamePh: 'e.g. front door', zoneMode: 'What to look for',
    sensitivity: 'Sensitivity',
    zoneModeChange: 'Different from usual - a door left open, something gone, a car parked',
    zoneModeMotion: 'The moment it changed - the door swinging, someone crossing',
    zoneDraw: 'Drag across the picture to mark an area',
    zoneSave: 'Save zone', zoneNone: 'No zones marked yet.',
    zoneEveryVideo: 'Watch this rectangle in every video (fixed camera)',
    zoneScope: 'Applies to', zoneSearch: 'Search this zone',
    zoneDeleteConfirm: 'Delete this zone?', zoneUsualChange: 'Everyday change here',
    zoneSuggested: 'Suggested sensitivity',
    zoneFlat: 'This area barely changes across the recording - check you framed the right spot.',
    zoneHint: 'A door is not an object any detector knows, so it cannot be searched for like a car. Mark the rectangle it sits in once, and from then on you can ask when that rectangle stopped looking like itself. The scan runs over the thumbnails written during indexing - locally, at no cost, even across twelve hours.',
    zoneAtMoment: 'Frame from the video', zoneNamedAlready: 'a zone with that name already exists',
    modeZone: 'by zone', whyZone: 'is a watched zone - this compares that corner against how it usually looks',
    framesExamined: 'frames examined', zoneNoVideos: 'Index at least one recording before marking a zone.',
    zoneScanning: 'Scanning the zone', zoneChanged: 'Changed by',
    lines: 'Counting lines', kindArea: 'Area (rectangle)', kindLine: 'Counting line',
    lineDraw: 'Drag a line where people pass - a doorway, a gate, an aisle',
    lineNone: 'No lines drawn yet.', lineSearch: 'All crossings',
    lineNew: 'Draw a new counting line', lineSave: 'Save line',
    lineNamePh: 'e.g. front gate',
    lineEveryVideo: 'Count on this line in every video (fixed camera)',
    lineHint: 'A detector can say a person is at these pixels, but not that those pixels are a doorway, nor whether the person was going in or out. Draw the line once where people pass, and every crossing is counted with its direction - read off the tracks already stored during indexing, locally and at no cost.',
    lineWhich: 'What is counted', flipDirection: 'Flip direction',
    inArrow: 'The arrow shows which way counts as "in". Flip direction reverses it.',
    directionIn: 'in', directionOut: 'out',
    modeLine: 'by counting line',
    whyLine: 'is a counting line - it reports who crossed it, and which way',
    crossings: 'crossings',
    noCrossingsThatWay: 'no crossings that way. In the other direction there were:',
    markUnknown: 'I do not know where', markIt: 'Show me on the picture',
    markTitle: 'Marking', markAndSearch: 'Save and search', markReady: 'Marked. Save and search.',
    markAsArea: 'Draw the rectangle it sits in, and from then on it can be asked about - locally, at no cost.',
    markAsLine: 'Draw a line where people pass, and from then on you can ask who came in and who went out - locally, at no cost.',
    lineName: 'Line name',
    inYourFootage: 'In your footage',
    noSuchObject: 'nothing like that in the indexed footage. What is in it:',
    noSuchColour: 'nothing in that colour. The colours actually found:',
    noColourData: 'this footage was indexed before colours were measured. Re-index it to search by colour (Footage tab, tick "Re-index").',
    noSuchMotion: 'nothing moving that way. Search without that condition:', noFacesButPeople: 'no face was clear enough in this recording - people can still be found by appearance and by clothing colour',
    whatNow: 'What now', goSearch: 'Go to search',
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
const COLOURS_HE = {
  white: 'לבן', black: 'שחור', gray: 'אפור', red: 'אדום', orange: 'כתום',
  yellow: 'צהוב', green: 'ירוק', cyan: 'תכלת', blue: 'כחול', purple: 'סגול',
  pink: 'ורוד', brown: 'חום',
};
/* Hebrew adjectives agree with the noun: a shirt is feminine, a car is not.
   "אדם בחולצה אדום" is the kind of thing that tells an operator this product
   was not written for them. */
const COLOURS_HE_F = {
  white: 'לבנה', black: 'שחורה', gray: 'אפורה', red: 'אדומה', orange: 'כתומה',
  yellow: 'צהובה', green: 'ירוקה', cyan: 'תכלת', blue: 'כחולה',
  purple: 'סגולה', pink: 'ורודה', brown: 'חומה',
};
const labelName = (label) => (S.lang === 'he' && LABELS_HE[label]) || label;
const colourName = (colour) => (S.lang === 'he' && COLOURS_HE[colour]) || colour;

/* "white car, moving" in the reader's own language and word order. */
function describeIntent(intent) {
  const parts = [];
  if (S.lang === 'he') {
    parts.push(labelList(intent.labels));
    if (intent.colours && intent.colours.length) {
      parts.push(intent.colours.map(colourName).join(', '));
    }
  } else {
    if (intent.colours && intent.colours.length) {
      parts.push(intent.colours.map(colourName).join(', '));
    }
    parts.push(labelList(intent.labels));
  }
  if (intent.moving === true) parts.push(t('thatMoved'));
  if (intent.moving === false) parts.push(t('thatStayed'));
  return parts.filter(Boolean).join(' ');
}
const labelList = (labels) => (labels || []).map(labelName).join(', ');

/* Turn what the index actually holds into a sentence the search box accepts,
   so every suggestion offered is a search that returns something. */
function contentPhrase(label, colour) {
  if (!colour) return labelName(label);
  if (S.lang === 'he') {
    return label === 'person'
      ? `אדם בחולצה ${COLOURS_HE_F[colour] || colourName(colour)}`
      : `${labelName(label)} ${colourName(colour)}`;
  }
  return label === 'person' ? `a person in a ${colour} shirt` : `${colour} ${label}`;
}

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
  ['people', 'viewer'], ['zones', 'viewer'], ['faces', 'viewer'], ['jobs', 'viewer'],
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
  const [videos, persons, zones, lines, stats] = await Promise.all([
    api('/api/videos').catch(() => ({ videos: [] })),
    api('/api/persons').catch(() => ({ persons: [] })),
    api('/api/zones').catch(() => ({ zones: [] })),
    api('/api/lines').catch(() => ({ lines: [] })),
    api('/api/stats').catch(() => null),
  ]);
  S.videos = videos.videos; S.persons = persons.persons; S.zones = zones.zones;
  S.lines = lines.lines; S.stats = stats || S.stats;
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
  const stats = S.stats || await api('/api/stats');
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

  /* Suggestions taken from the index itself. An empty search box in front of
     twelve hours of footage is a riddle; "person in a red shirt (15)" is an
     answer you can click, and every chip here is known to return something. */
  const chip = (text, count) => el('button', {
    class: 'btn ghost small', onclick: () => { box.value = text; runButton.click(); },
  }, text, count ? el('span', { class: 'muted' }, ' ', bdi(count)) : null);

  async function run(forceMode) {
    const query = box.value.trim();
    if (!query) return;
    clear(interpretation);
    clear(resultsBox);
    const data = await api('/api/search', { method: 'POST',
      body: { query, ...filters(), force_mode: forceMode || null } });
    showInterpretation(data);
    const offer = (data.intent || {}).mode === 'ask' ? markCard(data.intent) : null;
    if (offer) resultsBox.append(offer);
    if (data.job_id) {
      const zone = (data.intent || {}).mode === 'zone';
      S.lastAskFrames = filters().max_frames;
      resultsBox.append(jobProgress(data.job_id, resultsBox, query,
        zone ? { estimate: false, title: t('zoneScanning') } : { estimate: true }));
    } else if (data.needs) {
      resultsBox.append(missingCard(data));
    } else {
      showResults(resultsBox, data.events, query);
      if (!data.count) {
        const note = (data.intent || {}).mode === 'line'
          ? emptyCrossings(data) : emptyNote(data.intent || {});
        if (note) resultsBox.append(note);
      }
    }
  }

  /* Nobody went out through that door - but four people came in, and that is
     the answer the operator is one click away from. */
  function emptyCrossings(data) {
    const intent = data.intent || {};
    const tally = data.tally || {};
    const other = intent.direction === 'in' ? 'out' : 'in';
    if (intent.direction === 'both' || !tally[other]) return null;
    return el('div', { class: 'card' },
      el('p', {}, t('noCrossingsThatWay')),
      el('div', { class: 'row' }, el('button', {
        class: 'btn', onclick: guard(async () => {
          const again = await api('/api/search/line', { method: 'POST',
            body: { line_id: intent.line_id, direction: other } });
          showResults(resultsBox, again.events, intent.line_name || '');
        }),
      }, `${other === 'in' ? t('directionIn') : t('directionOut')} · `,
         bdi(tally[other]))));
  }

  /* A zero is not an answer. We know exactly what is in the index, so when a
     local search finds nothing, say what is there instead - "no white shirts;
     there are 15 red ones" - with each alternative one click away. */
  function emptyNote(intent) {
    if (intent.mode !== 'objects') return null;
    const contents = (S.stats && S.stats.contents) || {};
    const labels = contents.labels || [];
    const combos = contents.combos || [];
    if (!labels.length) return null;

    const wanted = intent.labels || [];
    const present = labels.filter((l) => wanted.includes(l.label));
    if (wanted.length && !present.length) {
      return el('div', { class: 'card' },
        el('p', {}, t('noSuchObject')),
        el('div', { class: 'row' },
          ...labels.slice(0, 8).map((l) => chip(contentPhrase(l.label, null), l.count))));
    }
    if ((intent.colours || []).length) {
      const alternatives = combos.filter((c) => wanted.includes(c.label));
      if (!combos.length) {
        // Indexed by a version that did not measure colour yet.
        return el('div', { class: 'card' }, el('p', { class: 'legal' }, t('noColourData')));
      }
      if (alternatives.length) {
        return el('div', { class: 'card' },
          el('p', {}, t('noSuchColour')),
          el('div', { class: 'row' },
            ...alternatives.slice(0, 8).map((c) =>
              chip(contentPhrase(c.label, c.colour), c.count))));
      }
    }
    if (intent.moving !== null && intent.moving !== undefined && present.length) {
      return el('div', { class: 'card' },
        el('p', {}, t('noSuchMotion')),
        el('div', { class: 'row' },
          ...present.slice(0, 8).map((l) => chip(contentPhrase(l.label, null), l.count))));
    }
    return null;
  }

  function reasonText(intent) {
    const key = { person_enrolled: 'whyPerson', objects_known: 'whyObjects',
                  zone_watched: 'whyZone', line_watched: 'whyLine',
                  descriptive_word: 'whyDescriptive',
                  unknown_word: 'whyUnknown',
                  not_measurable: 'whyNotMeasurable' }[intent.reason_code];
    if (!key) return intent.reason || '';
    const word = intent.reason_code === 'objects_known'
      ? describeIntent(intent) : intent.reason_word;
    return word ? `"${word}" ${t(key)}` : t(key);
  }

  function showInterpretation(data) {
    const intent = data.intent || {};
    const label = { person: t('modePerson'), zone: t('modeZone'),
                    line: t('modeLine'), objects: t('modeObjects'),
                    ask: t('modeAsk') }[intent.mode] || '';
    const why = reasonText(intent);
    clear(interpretation).append(
      el('span', {}, `${t('searchedAs')}: `),
      el('b', {}, label),
      why ? el('span', {}, ' — ') : null,
      why ? el('span', { dir: 'auto' }, why) : null);
    // let the operator overrule us in one click
    const others = ['person', 'zone', 'line', 'objects', 'ask'].filter((m) =>
      m !== intent.mode
      && (m !== 'person' || S.persons.length)
      && (m !== 'zone' || intent.zone_id)
      && (m !== 'line' || intent.line_id));
    for (const mode of others) {
      interpretation.append(' ', el('button', {
        class: 'btn ghost small', onclick: guard(() => run(mode)),
      }, { person: t('modePerson'), zone: t('modeZone'), line: t('modeLine'),
           objects: t('modeObjects'), ask: t('modeAsk') }[mode]));
    }
  }

  /* The question named a place we have never been shown. Rather than explain
     that the detector has no class for gates, offer the one action that makes
     the question answerable - and then run it. */
  function markCard(intent) {
    const suggest = intent.suggest;
    if (!suggest || !can('analyst') || !S.videos.length) return null;
    const what = suggest.kind === 'line' ? t('markAsLine') : t('markAsArea');
    return el('div', { class: 'card' },
      el('h3', {}, `${t('markUnknown')} “${suggest.name}”`),
      el('p', {}, what),
      el('button', { class: 'btn', onclick: () => {
        markItModal(suggest, filters().video_ids ? filters().video_ids[0] : null,
          async () => { await run(null); });
      } }, t('markIt')));
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

  const contents = (S.stats && S.stats.contents) || {};
  const seen = new Set();
  const found = [];
  for (const combo of (contents.combos || []).slice(0, 5)) {
    const text = contentPhrase(combo.label, combo.colour);
    if (!seen.has(text)) { seen.add(text); found.push(chip(text, combo.count)); }
  }
  for (const entry of (contents.labels || []).slice(0, 4)) {
    const text = contentPhrase(entry.label, null);
    if (!seen.has(text)) { seen.add(text); found.push(chip(text, entry.count)); }
  }
  for (const person of S.persons.slice(0, 3)) found.push(chip(person.name));
  for (const zone of S.zones.slice(0, 3)) found.push(chip(zone.name));
  for (const line of S.lines.slice(0, 3)) found.push(chip(line.name));

  const examples = el('div', { class: 'row', style: 'margin-top:10px' },
    el('span', { class: 'small muted' },
      `${found.length ? t('inYourFootage') : t('examples')}:`),
    ...(found.length ? found
      : (S.lang === 'he'
        ? ['מתי הרכב הלבן זז', 'איש עם חולצה לבנה', 'רכב', 'מישהו משאיר תיק']
        : ['when did the white car move', 'a man in a white shirt', 'car',
           'someone leaving a bag']).map((text) => chip(text))));

  wrap.append(el('div', { class: 'card' },
    el('div', { class: 'row' }, el('div', { class: 'grow' }, box), runButton,
      advancedToggle),
    interpretation, examples, advanced), resultsBox);
  return wrap;
};

/* A grid of nine frames is about 3.4k input tokens; a confirmation on a full
   frame about 1.4k. Enough to warn someone before they spend, not accounting. */
function estimateCost(frames) {
  const model = S.settings.ask_model || 'claude-opus-5';
  const [inRate, outRate] = (S.settings.ask_pricing || {})[model] || [5, 25];
  const grids = Math.ceil(frames / 9);
  const confirms = Math.round(grids * 0.4);
  const input = grids * 3400 + confirms * 1500;
  const output = grids * 450 + confirms * 250;
  return { requests: grids + confirms,
           usd: (input * inRate + output * outRate) / 1e6 };
}

function askProgress(jobId, container, label) {
  return jobProgress(jobId, container, label, { estimate: true });
}

/* One progress card for every search that runs as a job. Only the ones that
   spend money get a price on them. */
function jobProgress(jobId, container, label, opts = {}) {
  const bar = el('i', { style: 'width:2%' });
  const message = el('div', { class: 'small muted' }, '…');
  const estimate = opts.estimate ? estimateCost(Number(S.lastAskFrames || 400)) : null;
  const card = el('div', { class: 'card' },
    el('h3', {}, `${opts.title || t('modeAsk')} #${jobId}`),
    el('div', { class: 'bar' }, bar), message,
    estimate ? el('div', { class: 'small muted' },
      `${t('estimate')}: ~${estimate.requests} ${t('requests')} · ~$${estimate.usd.toFixed(2)}`)
      : null);
  const timer = setInterval(async () => {
    try {
      const { job } = await api(`/api/jobs/${jobId}`);
      bar.style.width = `${Math.round((job.progress || 0) * 100)}%`;
      message.textContent = job.message || job.status;
      if (['done', 'failed', 'cancelled'].includes(job.status)) {
        clearInterval(timer);
        if (job.status === 'done') {
          showResults(container, job.result.events, label);
          const spent = job.result.cost_usd
            ? ` · ${t('cost')} $${Number(job.result.cost_usd).toFixed(2)}` : '';
          const work = job.result.requests !== undefined
            ? `${job.result.requests} ${t('requests')}`
            : `${job.result.frames_examined || 0} ${t('framesExamined')}`;
          toast(`${job.result.events.length} ${t('results')} · ${work}${spent}`, 'ok');
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
  const zoneHit = !!(event.meta && event.meta.zone);
  const crossed = !!(event.meta && event.meta.direction);
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
      zoneHit ? el('div', { class: 'small muted' },
        `${t('zoneChanged')}: `, bdi(`${Math.round(event.meta.changed * 100)}%`)) : null,
      crossed ? el('div', { class: 'small' },
        el('b', {}, event.meta.direction === 'in' ? t('directionIn') : t('directionOut')),
        ' · ', labelName(event.meta.label),
        event.meta.colour ? ` · ${colourName(event.meta.colour)}` : '') : null,
      // "who else looks like this" reads an appearance vector out of a person
      // box; a rectangle on a wall has none, so it is not offered there.
      (zoneHit || crossed) ? null : el('button', {
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

/* --------------------------------------------------- places on the picture
   Two questions no detector can answer, because both are about a place rather
   than a thing: a rectangle that stops looking like itself is a door that
   opened, and a line somebody stepped over is a person who came in or went
   out. Both need the operator to point at their own picture once - so the
   pointing happens where the question was asked, not in a tab they have to
   find first. */

/* One drawing surface, shared by the Places tab and the one-click prompt that
   appears under a search we could not answer. */
function drawSurface(options = {}) {
  const state = { kind: options.kind || 'area', area: null, line: null,
                  flipped: false };
  const videoPick = el('select', {}, ...S.videos.map((v) =>
    el('option', { value: v.id, selected: v.id === options.videoId }, v.name)));
  const at = el('input', { type: 'range', min: '0', max: '100', value: '35',
    style: 'width:100%' });
  const img = el('img', { alt: '', draggable: false });
  const rect = el('div', { class: 'zone-rect hidden' });
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', 'zone-line hidden');
  const canvas = el('div', { class: 'zone-canvas' }, img, rect, svg);

  const video = () => S.videos.find((v) => String(v.id) === videoPick.value) || S.videos[0];
  function loadFrame() {
    const v = video();
    if (!v) return;
    const seconds = (Number(at.value) / 100) * (v.duration || 0);
    img.src = `/api/media/frame/${v.id}?t=${seconds.toFixed(2)}&width=960`;
  }
  videoPick.addEventListener('change', () => { reset(); loadFrame(); });
  at.addEventListener('change', loadFrame);
  img.addEventListener('load', paint);

  function reset() { state.area = null; state.line = null; paint(); }

  function paintArea() {
    if (!state.area) { rect.classList.add('hidden'); return; }
    rect.classList.remove('hidden');
    rect.style.left = `${state.area.x * 100}%`;
    rect.style.top = `${state.area.y * 100}%`;
    rect.style.width = `${state.area.w * 100}%`;
    rect.style.height = `${state.area.h * 100}%`;
  }

  /* The arrow is the whole user interface for direction: rather than explain
     which side of a vector counts as "in", show it and let them flip it. */
  function paintLine() {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (!state.line) { svg.classList.add('hidden'); return; }
    svg.classList.remove('hidden');
    const w = img.clientWidth || 960;
    const h = img.clientHeight || 540;
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    const p1 = { x: state.line.x1 * w, y: state.line.y1 * h };
    const p2 = { x: state.line.x2 * w, y: state.line.y2 * h };
    const draw = (tag, attrs) => {
      const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
      for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
      svg.append(node);
    };
    draw('line', { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y, class: 'wire' });
    const dx = p2.x - p1.x, dy = p2.y - p1.y;
    const length = Math.hypot(dx, dy) || 1;
    const sign = state.flipped ? -1 : 1;
    const nx = (-dy / length) * sign, ny = (dx / length) * sign;
    const mid = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };
    const tip = { x: mid.x + nx * 42, y: mid.y + ny * 42 };
    draw('line', { x1: mid.x, y1: mid.y, x2: tip.x, y2: tip.y, class: 'arrow' });
    draw('polygon', { class: 'arrow head', points: [
      `${tip.x + nx * 9},${tip.y + ny * 9}`,
      `${tip.x - ny * 7 - nx * 4},${tip.y + nx * 7 - ny * 4}`,
      `${tip.x + ny * 7 - nx * 4},${tip.y - nx * 7 - ny * 4}`,
    ].join(' ') });
  }

  function paint() { paintArea(); paintLine(); }

  /* Drag to draw. Coordinates are fractions of the picture, so the same mark
     fits a 4CIF camera and a 4K one. */
  let origin = null;
  const point = (event) => {
    const area = img.getBoundingClientRect();
    return { x: Math.min(1, Math.max(0, (event.clientX - area.left) / area.width)),
             y: Math.min(1, Math.max(0, (event.clientY - area.top) / area.height)) };
  };
  canvas.addEventListener('pointerdown', (event) => {
    origin = point(event); reset();
    canvas.setPointerCapture(event.pointerId);
    event.preventDefault();
  });
  canvas.addEventListener('pointermove', (event) => {
    if (!origin) return;
    const now = point(event);
    if (state.kind === 'area') {
      state.area = { x: Math.min(origin.x, now.x), y: Math.min(origin.y, now.y),
                     w: Math.abs(now.x - origin.x), h: Math.abs(now.y - origin.y) };
    } else {
      state.line = { x1: origin.x, y1: origin.y, x2: now.x, y2: now.y };
    }
    paint();
  });
  canvas.addEventListener('pointerup', () => {
    origin = null;
    const done = surface.shape();
    if (!done) { reset(); return; }
    if (options.onShape) options.onShape(done);
  });

  const surface = {
    node: el('div', {},
      el('div', { class: 'row', style: 'margin-top:10px' },
        el('div', { style: 'min-width:240px' }, field(t('videos'), videoPick)),
        el('div', { class: 'grow', style: 'min-width:200px' },
          field(t('zoneAtMoment'), at))),
      canvas),
    canvas,
    videoId: () => (video() ? video().id : null),
    kind: () => state.kind,
    setKind(kind) { state.kind = kind; reset(); },
    flip() { state.flipped = !state.flipped; paint(); },
    reset,
    shape() {
      if (state.kind === 'area') {
        if (!state.area || state.area.w < 0.01 || state.area.h < 0.01) return null;
        const a = state.area;
        return { kind: 'area', box: [a.x, a.y, a.w, a.h] };
      }
      if (!state.line) return null;
      const l = state.line;
      if (Math.hypot(l.x2 - l.x1, l.y2 - l.y1) < 0.03) return null;
      return { kind: 'line', line: [l.x1, l.y1, l.x2, l.y2], flipped: state.flipped };
    },
  };
  loadFrame();
  return surface;
}

/* Save whatever was drawn, under the name the operator already typed. */
async function savePlace(name, shape, videoId, extra = {}) {
  if (shape.kind === 'area') {
    return api('/api/zones', { method: 'POST', body: {
      name, box: shape.box, video_id: videoId,
      mode: extra.mode || 'change',
      sensitivity: extra.sensitivity || 0.15 } });
  }
  return api('/api/lines', { method: 'POST', body: {
    name, line: shape.line, video_id: videoId, flipped: shape.flipped } });
}

/* The whole point: a question we could not answer becomes answerable in one
   step, in the place it was asked. No tab to find, no vocabulary to learn. */
function markItModal(suggest, videoId, onSaved) {
  const kind = suggest.kind === 'line' ? 'line' : 'area';
  const name = el('input', { type: 'text', dir: 'auto', value: suggest.name || '' });
  const hint = el('div', { class: 'small muted', style: 'margin-top:6px' },
    kind === 'line' ? t('lineDraw') : t('zoneDraw'));
  const save = el('button', { class: 'btn', disabled: true }, t('markAndSearch'));
  const surface = drawSurface({ kind, videoId, onShape: () => {
    save.disabled = false;
    clear(hint).append(kind === 'line' ? t('inArrow') : t('markReady'));
  } });
  const flip = el('button', { class: 'btn ghost', onclick: () => surface.flip() },
    t('flipDirection'));

  // One line, not the essay from the Places tab: somebody who got here was in
  // the middle of asking a question, not reading about the product.
  const box = modal(`${t('markTitle')} “${suggest.name || ''}”`,
    el('p', { class: 'small muted' },
      kind === 'line' ? t('markAsLine') : t('markAsArea')),
    surface.node, hint,
    el('div', { class: 'row', style: 'margin-top:12px' },
      el('div', { class: 'grow', style: 'min-width:200px' },
        field(kind === 'line' ? t('lineName') : t('zoneName'), name)),
      kind === 'line' ? flip : null, save));

  save.onclick = guard(async () => {
    const shape = surface.shape();
    if (!shape) { toast(t('zoneDraw'), 'bad'); return; }
    if (!name.value.trim()) { toast(t('zoneName'), 'bad'); return; }
    save.disabled = true;
    await savePlace(name.value.trim(), shape, surface.videoId());
    box.remove();
    toast(t('saved'), 'ok');
    await refreshCore();
    await onSaved(name.value.trim());
  });
  return box;
}

VIEWS.zones = async () => {
  const wrap = el('div');
  if (!S.videos.length) {
    return el('div', { class: 'card' }, el('p', {}, t('zoneNoVideos')),
      el('button', { class: 'btn', onclick: () => { S.tab = 'footage'; renderTabs(); renderTab(); } },
        t('addFootage')));
  }
  if (can('analyst')) wrap.append(zoneEditor());
  wrap.append(await zoneList(), await lineList());
  return wrap;
};

function zoneEditor() {
  const name = el('input', { type: 'text', dir: 'auto', placeholder: t('zoneNamePh') });
  const readout = el('div', { class: 'small muted', style: 'margin-top:6px' },
    t('zoneDraw'));
  const sensitivity = el('input', { type: 'number', value: '0.15', min: '0.01',
    max: '1', step: '0.01' });
  const mode = el('select', {},
    el('option', { value: 'change' }, t('zoneModeChange')),
    el('option', { value: 'motion' }, t('zoneModeMotion')));
  const everywhere = checkbox('z-all', t('zoneEveryVideo'), false);

  const surface = drawSurface({ onShape: (shape) => {
    if (shape.kind === 'area') measure(shape).catch(() => {});
    else clear(readout).append(t('inArrow'));
  } });

  async function measure(shape) {
    readout.textContent = '…';
    const stats = await api('/api/zones/preview', { method: 'POST',
      body: { video_id: surface.videoId(), box: shape.box } });
    sensitivity.value = stats.suggested_sensitivity || 0.15;
    clear(readout).append(
      el('span', {}, `${t('zoneUsualChange')}: `),
      bdi(`${Math.round((stats.median_change || 0) * 100)}%`),
      el('span', {}, ` · ${t('zoneSuggested')}: `),
      bdi(stats.suggested_sensitivity),
      el('span', {}, ` · ${stats.sampled || 0} ${t('frames')}`));
    if ((stats.max_change || 0) < 0.05) {
      readout.append(el('div', { class: 'legal', style: 'margin-top:6px' }, t('zoneFlat')));
    }
  }

  const heading = el('h2', {}, t('zoneNew'));
  const hint = el('p', { class: 'legal' }, t('zoneHint'));
  const scopeLabel = everywhere.querySelector('label') || everywhere;
  const flipButton = el('button', { class: 'btn ghost', onclick: () => surface.flip() },
    t('flipDirection'));
  const areaFields = el('div', { class: 'row', style: 'margin-top:12px' },
    el('div', { style: 'min-width:280px' }, field(t('zoneMode'), mode)),
    el('div', { style: 'min-width:120px' }, field(t('sensitivity'), sensitivity)));
  const lineFields = el('div', { class: 'row hidden', style: 'margin-top:12px' },
    flipButton);
  const save = el('button', { class: 'btn' }, t('zoneSave'));

  /* Every word on this card belongs to one of the two shapes. Leaving it
     talking about rectangles while an operator draws a line is how a tool
     starts to feel like it was built for somebody else. */
  function relabel() {
    const line = surface.kind() === 'line';
    heading.textContent = line ? t('lineNew') : t('zoneNew');
    hint.textContent = line ? t('lineHint') : t('zoneHint');
    name.placeholder = line ? t('lineNamePh') : t('zoneNamePh');
    save.textContent = line ? t('lineSave') : t('zoneSave');
    scopeLabel.textContent = line ? t('lineEveryVideo') : t('zoneEveryVideo');
    areaFields.classList.toggle('hidden', line);
    lineFields.classList.toggle('hidden', !line);
    clear(readout).append(line ? t('lineDraw') : t('zoneDraw'));
  }

  save.onclick = guard(async () => {
    const shape = surface.shape();
    if (!shape) { toast(surface.kind() === 'line' ? t('lineDraw') : t('zoneDraw'), 'bad'); return; }
    if (!name.value.trim()) { toast(t('zoneName'), 'bad'); return; }
    await savePlace(name.value.trim(), shape,
      everywhere.querySelector('input').checked ? null : surface.videoId(),
      { mode: mode.value, sensitivity: Number(sensitivity.value) });
    toast(t('saved'), 'ok');
    name.value = ''; surface.reset();
    await refreshCore(); await renderTab();
  });

  const kindPick = el('div', { class: 'row' },
    ...[['area', t('kindArea')], ['line', t('kindLine')]].map(([value, text]) =>
      el('button', {
        class: value === surface.kind() ? 'btn small' : 'btn ghost small',
        onclick: (event) => {
          surface.setKind(value);
          for (const button of event.target.parentNode.children) {
            button.className = 'btn ghost small';
          }
          event.target.className = 'btn small';
          relabel();
        },
      }, text)));

  relabel();
  return el('div', { class: 'card' },
    heading, hint, kindPick, surface.node, readout, areaFields, lineFields,
    el('div', { class: 'row', style: 'margin-top:12px' },
      el('div', { style: 'min-width:220px' }, field(t('zoneName'), name)),
      everywhere, save));
}

function scopeName(videoId) {
  const video = S.videos.find((v) => v.id === videoId);
  return video ? bdi(video.name) : t('allVideos');
}

async function zoneList() {
  const card = el('div', { class: 'card' }, el('h2', {}, t('zones')));
  if (!S.zones.length) {
    card.append(el('p', { class: 'muted' }, t('zoneNone')));
    return card;
  }
  const rows = S.zones.map((zone) => el('tr', {},
    el('td', { dir: 'auto' }, el('b', {}, zone.name)),
    el('td', { class: 'small' }, scopeName(zone.video_id)),
    el('td', { class: 'small' },
      zone.mode === 'motion' ? t('zoneModeMotion') : t('zoneModeChange')),
    el('td', { class: 'mono small' }, bdi(Number(zone.sensitivity).toFixed(2))),
    el('td', {}, el('div', { class: 'row' },
      el('button', { class: 'btn small', onclick: guard(() => searchZone(zone)) },
        t('zoneSearch')),
      can('analyst') ? el('button', { class: 'btn ghost small danger',
        onclick: guard(async () => {
          if (!confirm(t('zoneDeleteConfirm'))) return;
          await api(`/api/zones/${zone.id}`, { method: 'DELETE' });
          toast(t('deleted'), 'ok');
          await refreshCore(); await renderTab();
        }) }, t('remove')) : null))));
  card.append(el('table', {},
    el('thead', {}, el('tr', {}, el('th', {}, t('name')), el('th', {}, t('zoneScope')),
      el('th', {}, t('zoneMode')), el('th', {}, t('sensitivity')), el('th', {}, ''))),
    el('tbody', {}, ...rows)));
  return card;
}

async function lineList() {
  const card = el('div', { class: 'card' }, el('h2', {}, t('lines')));
  if (!S.lines.length) {
    card.append(el('p', { class: 'muted' }, t('lineNone')));
    return card;
  }
  const rows = S.lines.map((line) => el('tr', {},
    el('td', { dir: 'auto' }, el('b', {}, line.name)),
    el('td', { class: 'small' }, scopeName(line.video_id)),
    el('td', { class: 'small' }, labelList(line.labels)),
    el('td', {}, el('div', { class: 'row' },
      el('button', { class: 'btn small',
        onclick: guard(() => searchLine(line, 'both')) }, t('lineSearch')),
      el('button', { class: 'btn ghost small',
        onclick: guard(() => searchLine(line, 'in')) }, t('directionIn')),
      el('button', { class: 'btn ghost small',
        onclick: guard(() => searchLine(line, 'out')) }, t('directionOut')),
      can('analyst') ? el('button', { class: 'btn ghost small danger',
        onclick: guard(async () => {
          if (!confirm(t('zoneDeleteConfirm'))) return;
          await api(`/api/lines/${line.id}`, { method: 'DELETE' });
          toast(t('deleted'), 'ok');
          await refreshCore(); await renderTab();
        }) }, t('remove')) : null))));
  card.append(el('table', {},
    el('thead', {}, el('tr', {}, el('th', {}, t('name')), el('th', {}, t('zoneScope')),
      el('th', {}, t('lineWhich')), el('th', {}, ''))),
    el('tbody', {}, ...rows)));
  return card;
}

/* Searching from this tab lands on the Search tab, so results, clips and
   exports all live in one place. */
async function showOnSearchTab(label, render) {
  S.tab = 'search'; renderTabs();
  await renderTab();
  const host = document.querySelector('#view > div');
  const box = el('div');
  host.append(box);
  render(box, label);
}

async function searchZone(zone) {
  const data = await api('/api/search/zone', { method: 'POST',
    body: { zone_id: zone.id, gap: 5 } });
  await showOnSearchTab(zone.name, (box, label) => {
    if (data.job_id) {
      box.append(jobProgress(data.job_id, box, label, { estimate: false,
        title: `${t('zoneScanning')}: ${label}` }));
    } else {
      showResults(box, data.events, label);
      toast(`${data.count} ${t('results')} · ${data.frames_examined} ${t('framesExamined')}`,
        data.count ? 'ok' : '');
    }
  });
}

async function searchLine(line, direction) {
  const data = await api('/api/search/line', { method: 'POST',
    body: { line_id: line.id, direction: direction || 'both' } });
  await showOnSearchTab(line.name, (box, label) => {
    showResults(box, data.events, label);
    const tally = data.tally || {};
    toast(`${t('directionIn')}: ${tally.in || 0} · ${t('directionOut')}: ${tally.out || 0}`,
      data.count ? 'ok' : '');
  });
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
        ? exportLinks(job)
        : job.kind === 'index' && job.status === 'done'
          // The jobs table is a dead end otherwise: indexing finished, and
          // nothing on screen says where to go with it.
          ? el('button', { class: 'btn small', onclick: async () => {
              S.tab = 'search'; renderTabs(); await refreshCore(); await renderTab();
            } }, t('goSearch'))
          : null));
}

function jobSummary(job) {
  const result = job.result || {};
  if (job.kind === 'index' && result.totals) {
    const totals = result.totals;
    const line = `${totals.frames} ${t('frames')} · `
      + `${totals.faces} ${t('facesFound')} · `
      + `${totals.objects ?? 0} ${t('objects')} · `
      + `${totals.appearances ?? 0} ${t('byAppearance')}`;
    const diagnosed = (result.videos || []).filter((v) => v.diagnosis);
    if (diagnosed.length) {
      const why = diagnosed[0].diagnosis.map((d) => d.headline).join(' · ');
      return `${line} — ${t('nothingFound')}: ${why}`;
    }
    // Faces are the one thing an operator expects and often does not get:
    // too small, turned away, too dark. Say so, instead of leaving a zero.
    if (!totals.faces && (totals.objects || totals.appearances)) {
      return `${line} — ${t('noFacesButPeople')}`;
    }
    return line;
  }
  if (job.kind === 'ask' && result.events) {
    const cost = result.cost_usd
      ? ` · ${t('cost')} $${Number(result.cost_usd).toFixed(2)}` : '';
    return `${result.events.length} ${t('results')} · `
      + `${result.requests} ${t('requests')}${cost}`;
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
    const askModel = el('select', { onchange: guard(async (e) => {
      await api('/api/settings', { method: 'PATCH',
        body: { ask_model: e.target.value } });
      toast(t('saved'), 'ok');
    }) }, ...(S.settings.ask_models || []).map((m) => el('option',
      { value: m, selected: m === S.settings.ask_model }, m)));
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
        el('div', { style: 'min-width:200px' }, field(t('model'), askModel)),
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
      el('p', { class: 'small muted' }, `${t('apiKeyHint')} ${t('costHint')}`),
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
