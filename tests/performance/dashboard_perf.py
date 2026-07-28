import time
import requests

tickers = [
    "TCS",
    "INFY",
    "RELIANCE",
    "HDFCBANK",
    "ICICIBANK"
]

for ticker in tickers:

    start = time.perf_counter()

    r = requests.get(
        f"http://127.0.0.1:8000/api/v1/companies/{ticker}"
    )

    elapsed = time.perf_counter() - start

    print(
        ticker,
        round(elapsed, 3),
        "seconds",
        r.status_code
    )