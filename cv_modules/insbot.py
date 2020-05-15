import aiohttp

from class_templates import GenericCVModule, FuniaGeneratorNotFoundError


class CVModule(GenericCVModule):

    generator = True

    async def perform(self, _, *args, **kwargs):

        async with aiohttp.ClientSession() as session:
            async with session.get("https://inspirobot.me/api?generate=true") as resp:
                if resp.status != 200:
                    return None
                link = await resp.text()
                idd = self.util.generate_uuid()
                return await self.util.download_png(idd, link)
