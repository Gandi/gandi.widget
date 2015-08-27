# -*- coding: utf-8 -*-
import threading
from Queue import Queue

from gi.repository import GObject

_lock = threading.Lock()


def log(*args):
    with _lock:
        print("%s %s" % (threading.current_thread(), " ".join(map(str, args))))


class Async:
    def __init__(self):
        self._task_id = 0
        self._queue = Queue(maxsize=100)  # NOTE: GUI blocks if queue is full
        for _ in range(5):
            t = threading.Thread(target=self._work)
            t.daemon = True
            t.start()

    def _work(self):
        # executed in background thread
        for task_id, callback, args in iter(self._queue.get, None):
            method, menu_item = args
            log('received task', task_id, method, menu_item)
            result = method()

            # signal task completion; run callback() in the main thread
            GObject.idle_add(callback, menu_item, result)

    def add_task(self, callback, *args):
        # executed in the main thread
        self._task_id += 1
        log('sending task ', self._task_id)
        self._queue.put((self._task_id, callback, args))
