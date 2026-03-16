from fastapi import APIRouter, Depends
from app.core.auth import Auth
from app.api.routes.models import LoginCredentials
from app.core.utils.auth_utils import verify_token
router = APIRouter()

@router.get("/")
async def get_all_users(_: dict = Depends(verify_token)):
    # TODO - Remove this API route if not required
    """
        returns all the user details. 
    """

    return Auth.get_all_users()

@router.post("/")
async def login(loginCredentials: LoginCredentials):
    """
        logins the user if valid username & password if not returns 401.
    """

    return Auth.login(username=loginCredentials.username, password=loginCredentials.password)

@router.post("/reset-password", status_code=201)
async def reset_password(loginCredentials: LoginCredentials):
    """
        reset the password for the given username
    """

    return Auth.reset_password(username=loginCredentials.username, password=loginCredentials.password)
