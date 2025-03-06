
# ----- rate_limiter.py -----
import time
from threading import Lock


class TokenBucketLimiter:
    def __init__(self, rate_per_second):
        self.rate = rate_per_second
        self.tokens = rate_per_second
        self.last_update = time.time()
        self.lock = Lock()

    def __enter__(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens += elapsed * self.rate
            self.tokens = min(self.tokens, self.rate)

            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                time.sleep(sleep_time)
                self.tokens = self.rate
            else:
                self.tokens -= 1

            self.last_update = time.time()

    def __exit__(self, *args):
        pass

