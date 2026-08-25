# converge-dashboards
Converge - US stocks &amp; crypto tracking dashboards

## גרפי TradingView

`tv-chart.js` מוסיף גרף TradingView בלחיצה על כל טיקר — בכרטיסים ובטבלאות, בשני הדשבורדים.

**חשוב לעדכון היומי האוטומטי:** הלוגיקה כולה נמצאת ב-`tv-chart.js` ולא בתוך ה-HTML,
אבל שורת ההטמעה חייבת לשרוד כתיבה מחדש של הדשבורדים. ודא ששתי השורות האלה
נשארות לפני `</body>`:

```html
<!-- index.html -->  <script defer src="tv-chart.js" data-market="stocks"></script>
<!-- crypto.html --> <script defer src="tv-chart.js" data-market="crypto"></script>
```

הסקריפט מזהה טיקרים לפי `.ticker` (כרטיסים) ו-`td.tk` (טבלאות), טוען את
`s3.tradingview.com/tv.js` רק בלחיצה הראשונה, ומתאים את ערכת הנושא של הגרף
לזו של הדשבורד.

סמל קריפטו שלא נטען — הוסף אותו ל-`CRYPTO_OVERRIDES` בראש `tv-chart.js`.
