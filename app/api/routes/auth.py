from fastapi import APIRouter, Form, Body
from app.core.auth import Auth

router = APIRouter()

@router.get("/")
async def get_all_users():
    # TODO - Remove this API route if not required
    """
        returns all the user details. 
    """

    return Auth.get_all_users()

@router.post("/")
async def login(username=Form("", description="Username to login"), password=Form("", description="Password to login")):
    """
        logins the user if valid username & password if not returns 401.
    """

    return Auth.login(username=username, password=password)

@router.post("/reset-password")
async def login(username=Form("", description="Username to login"), password=Form("", description="Password to login")):
    """
        reset the password for the given username
    """

    return Auth.reset_password(username=username, password=password)

