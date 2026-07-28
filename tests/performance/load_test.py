import threading
import time
import requests

URL = "http://127.0.0.1:8000/api/v1/screener/?min_roe=15"

times = []


def call_api():
    start = time.perf_counter()

    response = requests.get(URL)
    assert response.status_code == 200

    elapsed = time.perf_counter() - start
    times.append(elapsed)


threads = []

overall_start = time.perf_counter()

for _ in range(10):
    t = threading.Thread(target=call_api)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

overall = time.perf_counter() - overall_start

print(f"Total Time : {overall:.2f} sec")
print(f"Average API: {sum(times)/len(times):.3f} sec")
print(f"Fastest    : {min(times):.3f} sec")
print(f"Slowest    : {max(times):.3f} sec")