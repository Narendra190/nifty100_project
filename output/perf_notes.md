# Sprint 6 – Day 43 Performance Notes

## Load Test

- Concurrent Requests: 10
- Total Execution Time: 0.17 seconds
- Average Response Time: 0.150 seconds
- Fastest Response: 0.135 seconds
- Slowest Response: 0.166 seconds
- Result: PASS

## Dashboard Performance

| Company | Load Time |
|----------|-----------|
| TCS | 0.054 sec |
| INFY | 0.005 sec |
| RELIANCE | 0.003 sec |
| HDFCBANK | 0.004 sec |
| ICICIBANK | 0.004 sec |

Result: PASS (All under 3 seconds)

## End-to-End Integration

- FastAPI running on port 8000
- Streamlit running on port 8501
- No port conflicts observed
- Dashboard successfully consumed API endpoints

## Bottlenecks

No significant performance bottlenecks identified during testing.

## SQLite Optimization

Indexes added on:
- company_id
- year

to improve query execution on large financial tables.