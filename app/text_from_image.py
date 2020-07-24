import pytesseract


def extract_text_from_image(image_data, lang='eng'):
    text = pytesseract.image_to_string(image_data, lang=lang)
    return text
