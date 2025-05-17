from pydantic import BaseModel, Field

class LoginCredentials(BaseModel):
    username: str
    password: str
    