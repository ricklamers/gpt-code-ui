import threading


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self, wait: bool = False):
        self._stop_event.set()
        if wait:
            self.join()

    def stopped(self, timeout=None):
        if timeout is not None:
            return self._stop_event.wait(timeout)
        else:
            return self._stop_event.is_set()
