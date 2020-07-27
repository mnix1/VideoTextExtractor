import cv2
import numpy as np
import pytesseract


def extract_text_from_image(image_data, lang='eng', converter=None):
    if converter is not None:
        image_data = converter(image_data)
    text = pytesseract.image_to_string(image_data, lang=lang)
    return text


def crop_image(image_data, video_text_appearance_box):
    x = video_text_appearance_box['x']
    y = video_text_appearance_box['y']
    w = video_text_appearance_box['width']
    h = video_text_appearance_box['height']
    crop = image_data[y:y + h, x:x + w]
    return crop


def to_gray(image_data):
    return cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)


def converter_builder(video_text_appearance_box=None, to_black_offset=None, to_white_offset=None):
    def converter(image_data):
        if video_text_appearance_box is not None:
            image_data = crop_image(image_data, video_text_appearance_box)

        if to_black_offset is not None:
            image_data[np.where(image_data <= [to_black_offset])] = [0]

        if to_white_offset is not None:
            image_data[np.where(image_data >= [to_white_offset])] = [255]

        return image_data

    return converter
