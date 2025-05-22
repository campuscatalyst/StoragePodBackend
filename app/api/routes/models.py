from pydantic import BaseModel, Field

class LoginCredentials(BaseModel):
    username: str
    password: str
    
class CreateFolderPayload(BaseModel):
    path: str
    folder_name: str