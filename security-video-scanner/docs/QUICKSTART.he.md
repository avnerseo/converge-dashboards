# מדריך הפעלה — שלב אחר שלב

המדריך הזה מניח שאין לך שום דבר מותקן, ושיש לך תיקייה עם סרטונים שאתה רוצה
לבדוק. יש שלושה מסלולים — תבחר אחד לפי מה שאתה רוצה עכשיו:

| מסלול | מתי | כמה זמן |
|---|---|---|
| **א׳ — שורת פקודה** | לבדוק במהירות אם הסרטונים שלך בכלל ניתנים לחיפוש | ~10 דקות |
| **ב׳ — ממשק web על המחשב שלך** | לראות את המוצר כמו שלקוח יראה אותו, בלי דוקר | +2 דקות אחרי א׳ |
| **ג׳ — דוקר** | התקנה אצל לקוח, על שרת | ~20 דקות |

---

## שלב 0 (משותף לכולם): להוריד את הקוד

הקוד יושב בענף `claude/security-video-scanner-ox5p4z` במאגר
`avnerseo/converge-dashboards`.

**עם git:**

```bash
git clone --branch claude/security-video-scanner-ox5p4z \
  https://github.com/avnerseo/converge-dashboards.git
cd converge-dashboards/security-video-scanner
```

**בלי git:** בגיטהאב, בוחרים את הענף `claude/security-video-scanner-ox5p4z`
בתפריט הענפים → כפתור **Code** → **Download ZIP** → לפתוח את הקובץ.
התיקייה שעובדים בה היא `security-video-scanner`.

כל הפקודות בהמשך רצות **מתוך התיקייה `security-video-scanner`**.

---

## הדרך הקצרה (מומלץ) — סקריפט התקנה

במקום שלבים 1–3 ידניים, יש סקריפט שעושה הכל: בודק אם Python ו‑ffmpeg מותקנים,
מתקין אותם אם לא, בונה סביבה מבודדת, מתקין את vscan ומוריד את המודלים.

**Windows (PowerShell):**

```powershell
cd C:\path\to\security-video-scanner
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

**macOS / Linux:**

```bash
cd /path/to/security-video-scanner
bash scripts/setup.sh
```

אפשר להריץ שוב ושוב — הוא מדלג על מה שכבר מותקן. בסוף הוא מדפיס את הפקודה
הבאה להרצה. אם משהו נכשל, אפשר לעשות את אותם שלבים ידנית לפי ההמשך.

---

## מסלול א׳ — שורת פקודה (ידני)

### שלב 1: להתקין Python ו‑ffmpeg

ffmpeg הוא מה שפותח את קבצי הווידאו. בלעדיו כלום לא יעבוד.

**macOS** (צריך [Homebrew](https://brew.sh)):

```bash
brew install python ffmpeg
```

**Windows** (PowerShell):

```powershell
winget install --id Python.Python.3.12 -e
winget install --id Gyan.FFmpeg -e
```

חשוב: לסגור ולפתוח מחדש את חלון ה‑PowerShell אחרי ההתקנה, אחרת המערכת עדיין
לא מכירה את `ffmpeg`.

**Ubuntu / Debian:**

```bash
sudo apt update && sudo apt install -y python3 python3-venv ffmpeg
```

בדיקה שהכול תפס:

```bash
ffmpeg -version      # אמור להדפיס גרסה
python3 --version    # 3.10 ומעלה. בווינדוס: py --version
```

### שלב 2: להתקין את vscan

**macOS / Linux:**

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[server,ask]"
```

**Windows:**

```powershell
py -m venv .venv
.\.venv\Scripts\pip.exe install -e ".[server,ask]"
```

זה מתקין לתוך תיקיית `.venv` בלבד ולא נוגע בפייתון של המערכת.

### שלב 3: להוריד את מודלי הזיהוי

```bash
.venv/bin/vscan models fetch                 # ווינדוס: .\.venv\Scripts\vscan.exe models fetch
```

כ‑140MB, פעם אחת למחשב. נשמר ב‑`~/.cache/vscan/models`.

### שלב 4: לבדוק אם הסרטון בכלל ניתן לחיפוש

**זו הפקודה שכדאי להתחיל ממנה תמיד:**

```bash
.venv/bin/vscan doctor "/נתיב/לסרטון.mp4"
```

בווינדוס:

```powershell
.\.venv\Scripts\vscan.exe doctor "C:\videos\cam1.mp4"
```

מה שיוצא:

```
cam1.mp4
  01:00:00  1920x1080  25.0 fps  h264
  sampled 60 frames, analysed at 1280 px wide

what is in the picture
  movement              23% of sampled frames
  brightness         mean 96/255
  frames with faces    14 / 60   width p50 31 px, p90 44 px
  frames with people   38 / 60   height p50 165 px, p90 240 px

verdict
  [ok ] face search will work, but only sometimes
         half the faces are under 40 px (31 px median)...
  [ok ] appearance search will work
         median person height 165 px...

suggested command
  vscan index "cam1.mp4" --fps 2 --width 1280 --objects --appearance
  then search faces with --threshold 0.3
```

איך קוראים את זה:

- **`frames with faces` + `width p50`** — אם רוחב הפנים החציוני מתחת ל‑24 פיקסלים,
  זיהוי פנים לא יעבוד על המצלמה הזאת. מעל 40 — יעבוד טוב.
- **`height p50` של אנשים** — מעל 64 פיקסלים, חיפוש לפי מראה יעבוד.
- **`movement`** — כמה מהחומר בכלל מעניין. אחוז נמוך = אינדוקס מהיר וזול.
- **`suggested command`** — זו הפקודה להריץ בשלב הבא. פשוט להעתיק.

### שלב 5: לאנדקס

מריצים בדיוק את מה שה‑doctor הציע:

```bash
.venv/bin/vscan index "/נתיב/לסרטון.mp4" --fps 2 --width 1280 --objects --appearance
```

אפשר גם תיקייה שלמה: `.venv/bin/vscan index /נתיב/לתיקייה -r --objects --appearance`

האינדקס נשמר בתיקייה `vscan-index` שנוצרת במקום שממנו הרצת. אפשר לשנות עם
`--index /נתיב/אחר`.

### שלב 6: לחפש

```bash
# מי בכלל מופיע בחומר? (מקבץ את כל הפנים לאנשים)
.venv/bin/vscan cluster --min-size 3 --report faces.html

# לתת שם לאשכול, ואז למצוא מתי הוא הגיע
.venv/bin/vscan label --cluster 0 --name "דוד"
.venv/bin/vscan find --person "דוד" --arrivals --report david.html

# מי עוד נראה כמו האדם שנמצא בדקה 3:12 (עובד גם בלי פנים)
.venv/bin/vscan similar --video cam1 --at 00:03:12 --report similar.html

# מתי בכלל היה מישהו / רכב
.venv/bin/vscan objects --labels person car --arrivals --report objects.html
```

כל `--report` מייצר קובץ HTML שנפתח בדפדפן, עם תמונות ממוזערות של כל אירוע.
`--clips ./clips` יחתוך קטע וידאו לכל אירוע.

---

## מסלול ב׳ — הממשק המלא, בלי דוקר

**Windows** — פקודה אחת, פותחת גם את הדפדפן:

```powershell
.\scripts\start-server.ps1 -Footage "C:\videos"
```

אם לא תיתן סיסמה, הסקריפט ייצר אחת ויציג אותה על המסך. אפשר גם
`-Password "..."` ו‑`-Port 8090`.

**macOS / Linux** — אחרי שלבים 1–3 של מסלול א׳:

```bash
VSCAN_FOOTAGE_DIRS=/נתיב/לתיקיית/הסרטונים \
VSCAN_ADMIN_PASSWORD=בחר-סיסמה-חזקה \
.venv/bin/vscan-server
```

אותו דבר בווינדוס בלי הסקריפט — שימו לב שכל משתנה בשורה נפרדת:

```powershell
$env:VSCAN_FOOTAGE_DIRS="C:\videos"
$env:VSCAN_ADMIN_PASSWORD="בחר-סיסמה-חזקה"
.\.venv\Scripts\vscan-server.exe
```

לפתוח בדפדפן: **http://localhost:8080** — שם משתמש `admin` והסיסמה שהגדרת.

בממשק: לשונית **הקלטות** → לסמן קבצים → לסמן **זיהוי אובייקטים** ו**וקטורי מראה**
→ **התחל אינדוקס**. אחר כך **פנים שנמצאו** לקיבוץ, **חיפוש** לחיפוש, וכפתור
**מי עוד נראה ככה** על כל תוצאה.

לעצור: `Ctrl+C` בחלון.

---

## מסלול ג׳ — דוקר (התקנה אצל לקוח)

### שלב 1: להתקין דוקר

- **Windows / macOS:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux:** `curl -fsSL https://get.docker.com | sh`

### שלב 2: להגדיר

```bash
cd security-video-scanner/docker
cp .env.example .env
```

לפתוח את `.env` בעורך טקסט ולשנות שתי שורות:

```ini
VSCAN_ADMIN_PASSWORD=סיסמה-חזקה-כאן
VSCAN_FOOTAGE_PATH=/נתיב/לתיקיית/הסרטונים
```

בווינדוס הנתיב נכתב עם לוכסנים רגילים: `VSCAN_FOOTAGE_PATH=C:/videos`

### שלב 3: להרים

```bash
docker compose up -d --build
```

הבנייה הראשונה לוקחת 5–15 דקות (מורידה בסיס פייתון, ffmpeg והמודלים). אחר כך
העליות הבאות הן שניות.

לראות מה קורה: `docker compose logs -f vscan`
לעצור: `docker compose down` — האינדקס והמשתמשים נשמרים.

### שלב 4: להיכנס

**http://localhost:8080** — משתמש `admin` והסיסמה מה‑`.env`.

הסרטונים כבר מחוברים לקונטיינר לקריאה בלבד תחת `/footage`, אז בלשונית
**הקלטות** הם פשוט יופיעו ברשימה.

---

## תקלות נפוצות

| מה קורה | למה ומה עושים |
|---|---|
| `ffmpeg not found` | ffmpeg לא מותקן או שהטרמינל נפתח לפניו. לסגור ולפתוח מחדש את הטרמינל |
| `no video files found` | הנתיב שגוי או הסיומת לא נתמכת. לשים את הנתיב בגרשיים, במיוחד אם יש בו רווחים |
| הפקודה `vscan` לא מוכרת | להריץ דרך הנתיב המלא: `.venv/bin/vscan` (או `.\.venv\Scripts\vscan.exe`) |
| `VSCAN_FOOTAGE_DIRS=... is not recognized` | זו פקודה בתחביר של מק/לינוקס שהודבקה ל‑PowerShell. בווינדוס משתמשים ב‑`$env:VAR="..."` בשורה נפרדת, או פשוט ב‑`.\scripts\start-server.ps1` |
| `http://localhost:8080 is not recognized` | כתובת אתר נפתחת בדפדפן, לא בטרמינל. ב‑PowerShell אפשר `start http://localhost:8080` |
| `running scripts is disabled on this system` | להריץ בצורה הזו: `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1` |
| doctor אומר שאין פנים | המצלמה גבוהה או רחוקה מדי. לאנדקס עם `--appearance` ולחפש לפי מראה |
| האינדוקס איטי מאוד | להוריד `--fps` ל‑1, או לוותר על `--objects` |
| בממשק לא רואים את הסרטונים | `VSCAN_FOOTAGE_DIRS` לא מצביע על התיקייה הנכונה |
| הווידאו לא מתנגן בדפדפן | ה‑ffmpeg שלך בלי libx264. להוסיף `VSCAN_PREVIEW_CODEC=vp9` |
| `port already in use` | פורט 8080 תפוס. להוסיף `VSCAN_PORT=8090` ולפתוח את `localhost:8090` |

---

## מה כדאי לשלוח בחזרה

אחרי `doctor` על 2–3 מצלמות שונות: את הפלט המלא של הפקודה. משם אפשר לדעת אם
צריך לכוונן ספים, אם ה‑Re‑ID מספיק בזוויות שלך, ואם מסנן התנועה מדלג על אירועים
אמיתיים.

```bash
.venv/bin/vscan doctor cam1.mp4 cam2.mp4 --json report.json
```
