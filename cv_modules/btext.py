import cv2
import numpy as np

from class_templates import GenericCVModule


class CVModule(GenericCVModule):

    generator = True

    async def perform(self, _, *args, **kwargs):
        text = "sample text" if not args else " ".join(args)
        img = np.zeros((512, 512, 3), np.uint8)

        cv2.putText(img, text,
                    (10, 250),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2)

        return img
