import os

from src import mooseBot
from dotenv import load_dotenv
from g4f.cookies import set_cookies

# Driver Code:
if __name__ == '__main__':
    set_cookies(".google.com", {
        "__Secure-1PSID": str(os.getenv("GOOGLE_PSID"))
    })

    mooseBot.run_discord_bot()