import cv2

from class_templates import GenericCVModule


class CVModule(GenericCVModule):

    async def perform(self, img, *args, **kwargs):

        hor_rel = 50
        vert_rel = 50

        if len(args) == 1:
            hor_rel = int(args[0])
            vert_rel = int(args[0])
        elif len(args) == 2:
            hor_rel = int(args[0])
            vert_rel = int(args[1])

        hor_rel /= 200
        vert_rel /= 200

        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) != 1:
            return
        x1, y1, cw, ch = faces[0]
        x2 = x1 + cw
        y2 = y1 + ch
        offset_hor = int(cw * hor_rel)
        offset_vert = int(cw * vert_rel)
        x1 -= offset_hor
        x2 += offset_hor
        y1 -= offset_vert
        y2 += offset_vert
        ih, iw, _ = img.shape

        def limit(x, m):
            return max(0, min(x, m))
        x1 = limit(x1, iw)
        x2 = limit(x2, iw)
        y1 = limit(y1, ih)
        y2 = limit(y2, ih)
        return img[y1:y2, x1:x2]
