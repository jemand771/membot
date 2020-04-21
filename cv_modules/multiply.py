import cv2
import numpy as np

from class_templates import GenericCVModule


class CVModule(GenericCVModule):

    async def perform(self, img, *args, **kwargs):

        hor = True
        vert = True
        if args:
            if args[0].lower() in ("h", "hor", "horizontal"):
                vert = False
            if args[0].lower() in ("v", "vert", "vertical"):
                hor = False

        if hor:
            img = np.concatenate((img, img), axis=1)
        if vert:
            img = np.concatenate((img, img), axis=0)

        return img
