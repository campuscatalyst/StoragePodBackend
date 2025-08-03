from fastapi import APIRouter, Form, Body
from app.core.auth import Auth
from app.api.routes.models import LoginCredentials
router = APIRouter()

@router.get("/")
async def get_all_users():
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

@router.post("/reset-password")
async def reset_password(loginCredentials: LoginCredentials):
    """
        reset the password for the given username
    """

    return Auth.reset_password(username=loginCredentials.username, password=loginCredentials.password)

