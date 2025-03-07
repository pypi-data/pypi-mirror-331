import time

from PIL import Image


class Encryptor:
    def __init__(self, image_path, text):
        self.image_path = image_path
        self.text = text

    def text_to_binary(self):
        binary = ''.join(format(byte, '08b') for byte in self.text.encode('utf-8'))
        return binary

    def binary_to_rgb(self, binary):
        rgb_values = []
        for i in range(0, len(binary), 24):
            r = int(binary[i:i + 8], 2) if i + 8 <= len(binary) else 0
            g = int(binary[i + 8:i + 16], 2) if i + 16 <= len(binary) else 0
            b = int(binary[i + 16:i + 24], 2) if i + 24 <= len(binary) else 0
            rgb_values.append((r, g, b))
        return rgb_values

    def create_image(self):
        binary = self.text_to_binary()
        text_length = len(self.text.encode('utf-8'))
        length_binary = format(text_length, '032b')  # 32-bit binary length
        binary = length_binary + binary  # Prepend length information
        rgb_values = self.binary_to_rgb(binary)

        image = Image.open(self.image_path)
        pixels = list(image.getdata())

        if len(rgb_values) > len(pixels):
            raise ValueError("The image is too small to hold the message.")

        for i in range(len(rgb_values)):
            pixels[i] = rgb_values[i]

        image.putdata(pixels)
        return image

    def save_image(self, filename):
        image = self.create_image()
        image.save(filename)


class Decryptor:
    def __init__(self, image_path):
        self.image_path = image_path

    def extract_text(self):
        image = Image.open(self.image_path)
        pixels = list(image.getdata())

        binary = ''
        for pixel in pixels:
            for value in pixel:
                binary += format(value, '08b')

        length_binary = binary[:32]
        text_length = int(length_binary, 2)
        text_binary = binary[32:32 + text_length * 8]

        text = ''
        for i in range(0, len(text_binary), 8):
            byte = text_binary[i:i + 8]
            text += chr(int(byte, 2))

        return text


if __name__ == '__main__':
    start_time = time.time()

    text = (
        "Steganography is a technique used to hide information within other non-secret data. In encryption, text"
        " is converted into binary and embedded into an image's pixel values. The image size is adjusted to"
        " accommodate the data. For decryption, the binary data is extracted from the image and converted back to"
        " text. This method ensures that the hidden message is not easily detectable, providing an additional layer"
        " of security."
    )

    image_path = '../../images/hide_to_image_pro_input.png'
    encryptor = Encryptor(image_path, text)
    encryptor.save_image('../../images/hide_to_image_pro_output.png')

    decryptor = Decryptor('../../images/hide_to_image_pro_output.png')
    extracted_text = decryptor.extract_text()
    end_time = time.time()

    print(extracted_text)
    print(f"Execution time: {end_time - start_time} seconds")
