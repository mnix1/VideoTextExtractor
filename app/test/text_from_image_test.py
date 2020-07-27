import unittest
import cv2
from parameterized import parameterized

from app.text_from_image import extract_text_from_image, converter_builder


class TextFromImageTest(unittest.TestCase):
    @parameterized.expand([
        ['3476', 'Te dije que\nevitaras cansarte.'],
        ['3528', 'Te dije que\nevitaras cansarte.'],
        ['3547', 'No te preocupes, mamá.'],
        ['3645', 'Ya estoy mejor.'],
        ['3728', 'No quiero que te canses.\nRecuerda lo que dijo el doctor.'],
        ['3744', 'No quiero que te canses.\nRecuerda lo que dijo el doctor.'],
        ['3969', '¿Seguimos adelante?'],
        ['3988', 'Bernadette está agotada.\nDile que pare.'],
        ['4006', 'Bernadette está agotada.\nDile que pare.'],
        ['4087', 'No, mamá.'],
        ['4218', 'Sube al carro con Justin.\nAhora vamos cuesta abajo.'],
        ['4292', 'No, quiero ayudar.'],
        ['4383', '¿Otra vez de\nmudanza, Francois'],
        ['4510', 'Entren a refrescarse.'],
        ['4600', 'Gracias, pero nos esperan.'],
        ['4680', 'Vamos.'],
        ['4970', 'Son tan pobres\nque los echaron.'],
        ['5112', 'Pobre gente,\ncon cuatro hijos.'],
        ['5249', '¿Con Sajous?'],
        ['5406', ';Dios mio!'],
        ['10242', 'Peor para él.'],
        ['10322', 'No tenemos gachas?'],
        ['10485', 'En tres meses, subió\nde 13 a 27 francos.'],
        ['10702', 'Mañana empiezo en la\npanadería y tendremos'],
        ['10918', 'Antes era su\nmolinero favorito.'],
        ['11331', 'No, Jean Marie, ese es\nel pan de Bernadette.'],
        ['11458', 'No tienes derucho\na comerte su pan.'],
    ])
    def extracts_text_from_image(self, file_name, expected_text):
        image_data = self._load_image(file_name)

        converter = converter_builder(to_black_offset=134, to_white_offset=182)
        converted_image_data = converter(image_data)
        text = extract_text_from_image(converted_image_data, lang='spa')

        self.assertEqual(expected_text, text)

    def _load_image(self, name):
        return cv2.imread('./test_images/{}_cropped.png'.format(name))


if __name__ == '__main__':
    unittest.main()
