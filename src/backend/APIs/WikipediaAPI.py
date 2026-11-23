import wikipediaapi
import src.backend.helpers as helpers


wiki = wikipediaapi.Wikipedia(
    user_agent= f"PrismaMusic/v0.1 ({helpers.EMAIL_ADDRESS})",
    language= "en"
)

page = wiki.page("Rauw Alejandro")
print(page.summary)