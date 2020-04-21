import cv2

from class_templates import GenericCVModule


class CVModule(GenericCVModule):

    async def perform(self, img, *args, **kwargs):

        flip = 1
        if args:
            d = args[0]
            if d.lower() in ("h", "hor", "horizontal"):
                flip = 0
            if d.lower() in ("x", "both"):
                flip = -1
        return cv2.flip(img, flip)
