# USDT/USD census. Alpha Vantage's USDT history begins 2024-12-23 (verified: the
# monthly series starts 2025-01 and the daily series' oldest bar is 2024-12-23;
# USDT/EUR starts even later, 2025-10). 615 daily bars were examined in-session.
#
# Rigorous filter: a day with close<=0.99 must have low<=0.99, hence must sit in a
# month whose MONTHLY low <=0.99. So the 20 monthly lows bound the search exactly.
ENTRY=0.9900
monthly_low = {  # every month of the available history, from DIGITAL_CURRENCY_MONTHLY
 '2025-01':0.99608,'2025-02':0.99813,'2025-03':0.98974,'2025-04':0.99872,
 '2025-05':0.99926,'2025-06':0.99010,'2025-07':0.99929,'2025-08':0.99801,
 '2025-09':0.99908,'2025-10':0.98091,'2025-11':0.98800,'2025-12':0.99500,
 '2026-01':0.99104,'2026-02':0.98750,'2026-03':0.98597,'2026-04':0.99809,
 '2026-05':0.98000,'2026-06':0.98300,'2026-07':0.99200,'2026-08':0.99150}
cand=[m for m,l in monthly_low.items() if l<=ENTRY]
print("months that COULD contain a qualifying day:", sorted(cand))
print("months excluded by monthly low > 0.99      :", len(monthly_low)-len(cand))

# All daily bars inside those candidate months with low<=0.99 (date, low, close):
qualifying_low = [
 ('2025-03-02',0.98974,1.00008),('2025-10-06',0.98091,1.00040),
 ('2025-11-18',0.98800,0.99974),('2026-02-06',0.98750,0.99917),
 ('2026-03-30',0.98597,0.99924),('2026-05-26',0.98000,0.99865),
 ('2026-06-08',0.98300,0.99961),('2026-06-30',0.98800,0.99850)]
# cross-check: every candidate month's monthly low is matched by one of these days
matched={d[:7] for d,l,c in qualifying_low}
assert matched=={m for m in cand}, (matched, set(cand))
for m in cand:
    assert min(l for d,l,c in qualifying_low if d[:7]==m)==monthly_low[m], m
print("cross-check PASSED: every candidate month's low is attributed to a named day\n")

days=365+240  # 2024-12-23 .. 2026-08-28
yrs=615/365.25
exe=[q for q in qualifying_low if q[2]<=ENTRY]
print(f"coverage 2024-12-23 .. 2026-08-28  615 bars  {yrs:.2f} years")
print(f"EXECUTABLE (close<=0.99) : {len(exe)} episodes = {len(exe)/yrs:.2f}/yr")
print(f"UPPER BOUND (low<=0.99)  : {len(qualifying_low)} episodes = {len(qualifying_low)/yrs:.2f}/yr  (all isolated days)")
mn=0.99789  # min close over the whole series, 2025-01-01
print(f"min CLOSE {mn} on 2025-01-01 -> max gross to par {100*(1/mn-1):.4f}%  vs 0.50% round-trip cost")
