from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str
    ADMIN_ID: int

config = Config(
    BOT_TOKEN=os.getenv("8789440252:AAE8rDGoechq-drdSi-RAiaMYcpHx1MJsfQ"),
    ADMIN_ID=int(os.getenv("5007698880")) 
)
