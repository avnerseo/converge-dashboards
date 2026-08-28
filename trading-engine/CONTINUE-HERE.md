# מאיפה ממשיכים — קרא את זה קודם

כל סשן חדש (Code, Chat או Cowork) שנוגע במנוע המסחר:
**קרא את `trading-engine/STATE.md` לפני שאתה עושה משהו.**

## איפה כל דבר נמצא

| מה | איפה |
|---|---|
| הקוד החי | `C:\dev\trading-engine` על מחשב Windows (desktop-2mf0j9f) |
| גיבוי הקוד | https://github.com/aifreemeditate-source/trading-engine (פרטי) |
| מצב הפרויקט | `trading-engine/STATE.md` בריפו הזה |
| האפיון המעוצב | https://claude.ai/code/artifact/bcc59036-6635-4732-b6e1-9cc550b59bc2 |
| זיכרון ארוך-טווח | Mem0, project=trading-engine |

## איך משחזרים שיחה שנקטעה ב-Claude Code מקומי

בטרמינל של Windows:

```
cd C:\dev\trading-engine
claude --resume
```

`--resume` פותח בורר של כל השיחות הקודמות בתיקייה הזו. בחר את האחרונה.
`claude -c` ממשיך ישירות את האחרונה בלי בורר.

התמלילים המלאים שמורים כקבצי `.jsonl` כאן:
```
C:\Users\<שם המשתמש>\.claude\projects\C--dev-trading-engine\
```
גם אם הבורר לא מציג את השיחה — הקובץ קיים וניתן לקריאה.

## כלל עבודה קבוע

בסוף כל סשן משמעותי על מנוע המסחר:
1. עדכן את `trading-engine/STATE.md`
2. commit + push
3. כתוב זיכרון Mem0 עם `project: trading-engine` ותאריך

שיחה היא לא מקום אחסון. git ו-Mem0 כן.
