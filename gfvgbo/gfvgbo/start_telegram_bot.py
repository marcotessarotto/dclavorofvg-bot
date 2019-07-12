import threading

class TelegramStarter(ModelBase):
    _counter = 0
    _counter_lock = threading.Lock()

    @classmethod
    def increment_counter(cls):
        with cls._counter_lock:
            cls._counter += 1

    def some_action(self):
        # core code
        self.increment_counter()

#https://stackoverflow.com/a/2681834/974287