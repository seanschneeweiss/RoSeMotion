import time
from threading import Thread


class LogWatcher:
    def __init__(self):
        self.active = True
        self.t = None
        self.filename = None

    def follow(self, thefile):
        thefile.seek(0,2) # Go to the end of the file
        while self.active:
            line = thefile.readline()
            if not line:
                time.sleep(0.1) # Sleep briefly
                continue
            yield line

    def run(self):
        logfile = open(self.filename)
        print(logfile.read())
        loglines = self.follow(logfile)
        for line in loglines:
            print(line, end='')

    def start(self, filename):
        self.filename = filename
        self.t = Thread(target=self.run)
        self.t.start()

    def stop(self):
        self.active = False
        self.t.join()


log_watcher = LogWatcher()
