import time

class Logging(object):
    def __init__(self, theme="default", log_text_color=None):
        self.theme = theme

    def info(self, msg):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] {msg}")

    def error(self, msg):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] {msg}")

    def warning(self, msg):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [WARNING] {msg}")

    def debug(self, msg):
        pass
