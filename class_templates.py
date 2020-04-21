

class GenericCommand:

    async def run(self, args, message):
        pass

    def __init__(self, client, util):
        self.client = client
        self.util = util


class GenericCVModule:

    def perform(self, img, *args, **kwargs):
        pass

    def __init__(self, util):
        self.util = util


class FuniaGeneratorNotFoundError(Exception):
    pass


class ImageNotFoundLocallyError(Exception):
    pass
