from class_templates import GenericCVModule


class CVModule(GenericCVModule):

    async def perform(self, img, *args, **kwargs):
        return img
