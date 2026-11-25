import src.backend.helpers as helpers
import json

class WikimediaClient:

    def __init__(self):
        self.EMAIL_ADDRESS = helpers.EMAIL_ADDRESS
        self.REQUEST_HEADER = f"User-Agent: PrismaMusic/0.0 ({self.EMAIL_ADDRESS}; https://github.com/noahdiaz658-tech/Prisma)"

    def search(self, artist):

        response = helpers.request_helper("https://wikibase.example/w/rest.php/wikibase/v1/openapi.json", )