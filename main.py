import datetime
import os
import math
import cv2
import pytesseract
from PIL import Image


def video_to_image_frames(video_path, on_video_frame_extracted=None, from_frame=0, to_frame=None, frame_increase=1,
                          output_path='temp'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    video = cv2.VideoCapture(video_path)
    frames_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    if from_frame >= frames_count:
        raise RuntimeError('start_frame lower than frames_count')
    frame_index = from_frame
    if to_frame is None:
        to_frame = frames_count - 1
    while video.isOpened() and frame_index <= to_frame:
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        successfully_read, frame_data = video.read()
        if not successfully_read:
            raise RuntimeError('Error when reading video frame {}'.format(frame_index))
        # else:
        #     print('Extracted frame {} from {}'.format(frame_index, video_path))
        frame_output_path = output_path + '/' + str(frame_index) + '.png'
        cv2.imwrite(frame_output_path, frame_data)
        frame_index = frame_index + frame_increase
        if on_video_frame_extracted is not None:
            on_video_frame_extracted(frame_output_path, frame_index, video.get(cv2.CAP_PROP_POS_MSEC))
    video.release()
    cv2.destroyAllWindows()


def extract_text_from_image(image_path, lang='eng'):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=lang)
    return text


class Srt:
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


class FramesToSubtitle:
    def handle_next_frame(self, frame_index, frame_timestamp, srt):
        pass


class SimpleFramesToSubtitle(FramesToSubtitle):
    def __init__(self, output_srt):
        self.last_text = None
        self.in_transaction = False
        self.output_srt = output_srt
        self.min_entry_duration = 1000

    def _begin_entry(self, frame_timestamp, text):
        self.entry_from_timestamp = frame_timestamp
        self.entry_text = text
        self.in_transaction = True

    def _commit_entry(self, frame_timestamp, text):
        self.output_srt.append(self.entry_from_timestamp, frame_timestamp, text)
        self.last_text = None
        self.in_transaction = False

    def _rollback_entry(self):
        self.in_transaction = False

    def _is_entry_duration_valid(self, to_timestamp):
        return to_timestamp - self.entry_from_timestamp > self.min_entry_duration

    def handle_next_frame(self, frame_index, frame_timestamp, text):
        text = text.strip()
        if self.last_text == text:
            return
        self.last_text = text
        if len(text) == 0:
            if self.in_transaction:
                if self._is_entry_duration_valid(frame_timestamp):
                    self._commit_entry(frame_timestamp, self.entry_text)
                else:
                    self._rollback_entry()
            return
        if not self.in_transaction:
            self._begin_entry(frame_timestamp, text)
            return
        if self._is_entry_duration_valid(frame_timestamp):
            self._commit_entry(frame_timestamp - 1, self.entry_text)
            self._begin_entry(frame_timestamp, text)


def video_subtitles_generator(video_path, frames_to_subtitle, lang='spa'):
    def handle_video_frame_extracted(image_path, frame_index, frame_timestamp):
        text = extract_text_from_image(image_path, lang=lang)
        os.remove(image_path)
        frames_to_subtitle.handle_next_frame(frame_index, frame_timestamp, text)

    video_to_image_frames(video_path,
                          on_video_frame_extracted=handle_video_frame_extracted,
                          from_frame=43000,
                          to_frame=44000,
                          frame_increase=2)


output_srt = Srt('D:/movie.srt')
video_subtitles_generator('D:/movie.mp4', frames_to_subtitle=SimpleFramesToSubtitle(output_srt))
