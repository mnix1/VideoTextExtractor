import string

from app.exporter.ImportantFramesExporter import ImportantFramesExporter
from app.exporter.SrtExporter import SrtExporter
from app.subtitle.SimpleSubtitleCreator import SimpleSubtitleCreator
from app.text_from_image import extract_text_from_image, converter_builder
from app.video_to_image_frames import convert_video_to_image_frames


def video_subtitles_generator(video_path, subtitle_creator, lang='eng', important_frames_exporter=None, converter=None):
    def handle_video_frame_extracted(image_data, frame_index, frame_timestamp):
        converted_image_data = image_data
        if converter is not None:
            converted_image_data = converter(converted_image_data)
        text = extract_text_from_image(converted_image_data, lang=lang)
        frame_contains_text = subtitle_creator.handle_next_frame(frame_index, frame_timestamp, text)
        if important_frames_exporter is not None:
            if frame_contains_text:
                important_frames_exporter.handle_frame_important(frame_index)
            else:
                important_frames_exporter.handle_frame_not_important(frame_index)

    convert_video_to_image_frames(video_path,
                                  on_video_frame_extracted=handle_video_frame_extracted,
                                  from_frame=3400,
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
    text = ''.join(
        [word for word in text if word in string.ascii_letters or word in string.digits or word in string.whitespace])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stopwords])
    if len(text) <= 4:
        return ''
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
                          important_frames_exporter=ImportantFramesExporter('D:/frames.txt'),
                          converter=converter_builder(video_text_appearance_box,
                                                      to_black_offset=134,
                                                      to_white_offset=182))
