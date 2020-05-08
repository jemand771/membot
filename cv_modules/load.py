import os

import cv2

from class_templates import GenericCVModule, LoadImageLocallyOrFromUrlError


class CVModule(GenericCVModule):

    generator = True

    async def perform(self, img, *args, **kwargs):

        if len(args) == 1:
            name = args[0]
            for folder in (self.util.TEMP_FOLDER,
                           self.util.SAVED_FOLDER + self.util.get_folder_id_from_message(kwargs["message"]) + "/",
                           self.util.LIBRARY_FOLDER):
                file = folder + name + ".png"
                if os.path.exists(file):
                    await kwargs["message"].channel.send(
                        "loaded " + name + ".png (size: " + str(
                            round(os.path.getsize(file) / 1024 / 1024, self.util.MB_ROUND)) + "mb)")
                    return cv2.imread(file)

            # not found locally, trying to download
            idd = self.util.generate_uuid()
            try:
                await self.util.download_png(idd, name)
            except Exception:
                raise LoadImageLocallyOrFromUrlError()
            return cv2.imread(self.util.TEMP_FOLDER + idd + ".png")
