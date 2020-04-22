import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

from class_templates import GenericCVModule


class CVModule(GenericCVModule):

    generator = True

    async def perform(self, img, *args, **kwargs):

        offset_x1 = 50
        offset_x2 = 80
        offset_x3 = 70
        offset_y = 50
        padding_x = 20
        padding_y = 0
        texts = " ".join(args).split(";")[:2]
        if len(texts) != 2:
            return None

        # create some font objects
        fontpath = "static/arialbd.ttf"
        font = ImageFont.truetype(fontpath, 256)
        img_pil = Image.fromarray(np.zeros((200, 400, 3), np.uint8))
        draw = ImageDraw.Draw(img_pil)

        # get text sizes
        text_width0, text_height0 = draw.textsize(texts[0], font=font)
        text_width1, text_height1 = draw.textsize(texts[1], font=font)
        text_height = 320

        # actually create image
        img = np.zeros(
            (text_height + 2 * offset_y,
             text_width0 + text_width1 + offset_x1 + offset_x2 + offset_x3, 3),
            np.uint8)

        img = self.add_rounded_rectangle(
            img,
            offset_x1 + offset_x2 + text_width0, offset_y,
            text_width1, text_height,
            padding_x, padding_y)

        # draw text
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((offset_x1, offset_y), texts[0], font=font, fill="white")
        draw.text((offset_x1 + offset_x2 + text_width0, offset_y), texts[1], font=font, fill="black")

        # font_scale = 5
        # font_th = 2
        # white = (255, 255, 255)
        # cv2.putText(img, texts[0], (offset_x1, offset_y + text_height0), cvfont, font_scale, white, font_th)
        # cv2.putText(img, texts[1], (offset_x1 + offset_x2 + text_width0, offset_y + text_height1), cvfont, font_scale, white, font_th)
        img = np.array(img_pil)
        return img

    @staticmethod
    def add_rounded_rectangle(img, x, y, width, height, padding_x, padding_y):

        x -= padding_x
        y -= padding_y
        width += 2 * padding_x
        height += 2 * padding_y

        color = (0, 153, 255)
        radius = 30
        img = cv2.circle(img, (x + radius, y + radius), radius, color, -1)
        img = cv2.circle(img, (x - radius + width, y + radius), radius, color, -1)
        img = cv2.circle(img, (x + radius, y + height - radius), radius, color, -1)
        img = cv2.circle(img, (x - radius + width, y + height - radius), radius, color, -1)
        img = cv2.rectangle(img, (x, y + radius), (x + width, y + height - radius), color, -1)
        img = cv2.rectangle(img, (x + radius, y), (x + width - radius, y + height), color, -1)

        return img
