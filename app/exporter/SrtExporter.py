import datetime
import math

from app.exporter.Exporter import Exporter


class SrtExporter(Exporter):
    def __init__(self, path):
        self.path = path
        self.index = 1

    def append(self, from_millis, to_millis, body):
        with open(self.path, "a", encoding='UTF-8') as file:
            file.write('{}\n'.format(self.index))
            from_time = str(datetime.timedelta(milliseconds=math.floor(from_millis)))
            to_time = str(datetime.timedelta(milliseconds=math.floor(to_millis)))
            file.write('{} --> {}\n'.format(from_time[0:-3], to_time[0:-3]))
            file.write(body)
            file.write('\n\n')
            self.index = self.index + 1
