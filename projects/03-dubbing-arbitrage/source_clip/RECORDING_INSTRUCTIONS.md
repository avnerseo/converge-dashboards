# Recording the Hebrew source clip

The fixture needs a **real human Hebrew recording**. There is a synthetic
placeholder in `build/source_he_synthetic.wav`, built with espeak-ng — it exists
only to prove the harness runs end to end. **Do not send it to a vendor.**
espeak-ng is a formant synthesiser; it would fail vendor ASR for reasons that
say nothing about how those tools handle real Hebrew speech, and a failure from
it would be a meaningless result.

## What to record

Read `script_he.md`, segments 1 through 6, in order.

- **Length:** ~88 seconds. Measured from the synthesised read, which is an upper
  bound — a human will likely come in a little under.
- **Pace:** a normal market-update read. Do not slow down for the numbers. The
  whole point is to see whether the tools handle Hebrew numbers at natural speed.
- **Pauses:** a short breath (~0.3s) between segments. Do not pause mid-segment.
- **Delivery:** flat and clear, one speaker, no music, no background.

## Recording quality

Vendor ASR quality is sensitive to input quality, and a bad recording would
produce a failure that blames the tool for your microphone.

- Quiet room, no fan, no open window.
- Phone voice memo at arm's length is fine. A headset mic is better.
- WAV or M4A. Avoid heavy compression and avoid any "voice enhancement" mode.
- Listen back before sending. If you can hear room echo, record again.

## The numbers must be read exactly as written

This is the part that matters most. The fixture's value is in its critical
tokens, and the ground truth assumes they were spoken as scripted.

- Tickers are written spelled-out in Hebrew letters — `אן־וי־די־איי`. Read them
  as letters, the way you would say them out loud. Do **not** say "NVIDIA"
  instead.
- Read `שלושה אחוז ושבע עשיריות`, not "3.7 אחוז". The whole test is whether
  spoken Hebrew numbers survive; reading digits would defeat it.
- Keep the gendered forms exactly: `שלוש מניות`, `שתי סיבות`, `שתי הורדות`
  (feminine) against `שלושה אחוז` (masculine).

If you deviate anywhere, note what you actually said — the ground truth has to
be corrected to match, or every score after it is wrong.

## Then

```bash
python3 tools/build_clip.py --from-recording /path/to/your/recording.m4a
```

This normalises the audio, checks the length, and emits the timecoded MP4, the
transcript and the SRT that vendors accept. It will tell you if the length is
far enough off the script that the segment boundaries need re-deriving before
timing drift can be scored.

## A note on what this clip is

It is a **test fixture, not content**. The figures in it are illustrative and
not real market data. It should never be published. If anything from it is ever
adapted for a real video, the numbers must be re-pulled live — and note that
`REALTIME_BULK_QUOTES` on the Alpha Vantage key returns fabricated sample data
(see `../../README.md`).
