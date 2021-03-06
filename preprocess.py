import argparse
import io

from google.cloud import vision
from google.cloud.vision import types
import cv2
import base64
import os

class DataHelper:
    def __init__(self):
        self.colors = {"k":(255,0,0,0.5),"c":(0,255,0,0.5), "j":(0,0,255,0.5)}

    def process_data(self):
        for key,color in self.colors.items():
            images = self.find_files(key)
            count = 0
            for image in images:
                self.draw_hint(image, key + str(count) + ".jpg", color)
                count += 1

    def get_crop_hint(self,path):
        """Detect crop hints on a single image and return the first result."""
        client = vision.ImageAnnotatorClient()

        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

        crop_hints_params = types.CropHintsParams(aspect_ratios=[0.3])
        image_context = types.ImageContext(crop_hints_params=crop_hints_params)

        response = client.crop_hints(image=image, image_context=image_context)
        hints = response.crop_hints_annotation.crop_hints

        try:
            vertices = hints[0].bounding_poly.vertices
        except:
            raise AssertionError("the image doesn't exist")
        return vertices

    def draw_hint(self, image_file, out_file, color):
        vects = self.get_crop_hint(image_file)

        img = cv2.imread(image_file)
        output = cv2.imread(image_file)

        cv2.rectangle(
            img,
            (vects[0].x, vects[0].y),
            (vects[2].x, vects[2].y),
            color,
            -1
        )
        alpha = 0.4
        cv2.addWeighted(img, alpha, output, 1 - alpha, 0, output)
        output = cv2.resize(output, (64,64))
        cv2.imwrite(os.path.join('data',out_file), output)

    def find_files(self, key):
        files = []
        current = os.path.join(os.getcwd(),'images')

        for i in os.listdir(current):
            real_file = i.split('.')[0]
            if key in real_file:
                files.append(os.path.join('images',i))
        return files

def get_color(image, vects):
    width = image.shape[1]
    if(vects[0].x < 0.33 * width):
        color = (255,0,0,0.5)
    elif(0.33*width <= vects[0].x < 0.67 * width):
        color = (0,255,0,0.5)
    else:
        color = (0,0,255,0.5)
    return color

def process_image(image_file,dataHelper):
    vects = dataHelper.get_crop_hint(image_file)
    img = cv2.imread(image_file)
    output = cv2.imread(image_file)
    color = get_color(img, vects)

    cv2.rectangle(
        img,
        (vects[0].x, vects[0].y),
        (vects[2].x, vects[2].y),
        color,
        -1
    )

    alpha = 0.4
    cv2.addWeighted(img, alpha, output, 1 - alpha,0, output)
    output = cv2.resize(output, (64,64))
    return output


if __name__ == '__main__':
    same = DataHelper()
    same.process_data()
