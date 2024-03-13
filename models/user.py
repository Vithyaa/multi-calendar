# models/user.py
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    google_access_token: str
    google_refresh_token: str
