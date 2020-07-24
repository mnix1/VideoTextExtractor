import string

import cv2

from app.exporter.SrtExporter import SrtExporter
from app.subtitle.SimpleSubtitleCreator import SimpleSubtitleCreator
from app.text_from_image import extract_text_from_image
from app.video_to_image_frames import convert_video_to_image_frames


def video_subtitles_generator(video_path, subtitle_creator, lang='eng', video_text_appearance_box=None):
    def handle_video_frame_extracted(image_data, frame_index, frame_timestamp):
        converted_image_data = convert_image(image_data, video_text_appearance_box)
        text = extract_text_from_image(converted_image_data, lang=lang)
        subtitle_creator.handle_next_frame(frame_index, frame_timestamp, text)
        # cv2.imwrite('temp/{}.png'.format(frame_index), image_data)
        # cv2.imwrite('temp/gray_{}.png'.format(frame_index), converted_image_data)

    def crop_image(image_data, video_text_appearance_box):
        x = video_text_appearance_box['x']
        y = video_text_appearance_box['y']
        w = video_text_appearance_box['width']
        h = video_text_appearance_box['height']
        crop = image_data[y:y + h, x:x + w]
        return crop

    def convert_image(image_data, video_text_appearance_box):
        if video_text_appearance_box is not None:
            image_data = crop_image(image_data, video_text_appearance_box)
        image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        return image_data

    convert_video_to_image_frames(video_path,
                                  on_video_frame_extracted=handle_video_frame_extracted,
                                  from_frame=3000,
                                  frame_increase=1)


def init_stopwords(lang):
    try:
        from nltk.corpus import stopwords

        return stopwords.words(lang)
    except:
        import nltk

        nltk.download('stopwords')
        from nltk.corpus import stopwords

        return stopwords.words(lang)


stopwords = init_stopwords('spanish')


def string_cleaner(text):
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stopwords])
    return text


video_text_appearance_box = {
    'x': 10,
    'y': 277,
    'width': 450,
    'height': 75
}
srt_exporter = SrtExporter('D:/movie.srt')
video_subtitles_generator('D:/movie.mp4',
                          SimpleSubtitleCreator(srt_exporter, string_cleaner),
                          lang='spa',
                          video_text_appearance_box=video_text_appearance_box)
