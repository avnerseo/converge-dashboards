# Hebrew source clip — script and segmentation

**Purpose:** the 60–90s Hebrew source asset for brief task 3. It is not a neutral
sample. Every line is loaded with a failure mode that the dubbing pipeline must
survive, so that a pass is informative and a failure is diagnosable.

**Target length:** ~78s at a natural news-read pace (~145 Hebrew words/min).
**Register:** daily market update, single speaker, no music, no background.

## Why these lines

| Stress tested | Where |
|---|---|
| Latin tickers spoken inside Hebrew speech | NVDA, TSLA, AAPL, VIX — the hardest ASR case in the clip |
| Company names transliterated to Hebrew | אנבידיה, טסלה, אפל, לאומי, פועלים |
| Large scale words that do not map 1:1 | טריליון, מיליארד |
| Percentages with decimals, spoken as words | 6 of them, incl. "עשיריות" forms |
| Hebrew gendered number agreement | שלוש מניות / שתי סיבות / שתי הורדות (fem) vs שלושה אחוז / שני אחוז (masc) |
| Two currencies with sub-units | דולר+סנט, שקלים+אגורות |
| Index name containing digits | ת"א 35 |
| A spoken date | שלושים באוגוסט אלפיים עשרים ושש |

## Segments

| # | Start | End | Line |
|---|---|---|---|
| 1 | 0:00 | 0:12 | שלום, כאן העדכון היומי של קונברג' לשלושים באוגוסט אלפיים עשרים ושש. שלוש מניות הזיזו את השוק היום, ואחת מהן בכיוון שאף אחד לא ציפה לו. |
| 2 | 0:12 | 0:25 | אנבידיה, סימול אן־וי־די־איי, עלתה שלושה אחוז ושבע עשיריות ונסגרה על מאה שמונים ותשעה דולר ועשרים וארבעה סנט. שווי השוק שלה חצה את ארבעה טריליון דולר. |
| 3 | 0:25 | 0:38 | מנגד, טסלה, סימול טי־אס־אל־איי, ירדה שני אחוז וחצי. שתי סיבות: דוח מכירות חלש באירופה, ושתי הורדות דירוג משני בתי השקעות. |
| 4 | 0:38 | 0:52 | אפל, סימול איי־איי־פי־אל, כמעט לא זזה — שמונה עשיריות האחוז. אבל היא הודיעה על רכישה עצמית של מניות בהיקף מאה ועשרה מיליארד דולר, הגדולה בתולדות החברה. |
| 5 | 0:52 | 1:05 | בתל אביב, מדד תל אביב שלושים וחמש עלה אחוז ושתי עשיריות. הבנקים הובילו: לאומי פלוס אחוז ושמונה, פועלים פלוס אחוז ושלוש. הדולר נסחר על שלושה שקלים ושבעים ואחת אגורות. |
| 6 | 1:05 | 1:18 | לסיכום: שוק חזק, אבל התנודתיות עלתה. מדד הפחד וי־איי־אקס טיפס לשמונה עשרה נקודות ושש. זה היה העדכון היומי. שיהיה יום מסחר טוב. |

## Note on the numbers

The figures are **illustrative, not real market data**. This clip is a test
fixture for a dubbing pipeline, not content for publication. If it is ever
adapted for a real video, the numbers must be re-pulled live — and note that
`REALTIME_BULK_QUOTES` on the Alpha Vantage key returns fabricated sample data
(see `../../README.md`).
