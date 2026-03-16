import jwt
from fastapi import HTTPException
from app.db.main import get_session
from app.db.models import User
from sqlmodel import select
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.logger import logger

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class Auth:

    @staticmethod
    def _is_hashed_password(value: str) -> bool:
        # passlib pbkdf2_sha256 hashes look like: "$pbkdf2-sha256$..."
        return isinstance(value, str) and value.startswith("$pbkdf2-sha256$")

    @staticmethod
    def create_access_token(data: dict, expires_delta = None):
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
           
            to_encode.update({ "exp": expire })

            encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

            return encoded_jwt
        except Exception as e:
            logger.error(f'Exception occurred: {e}')
            return None
        
    @staticmethod
    def create_initial_user():
        with get_session() as session:
            try:
                existing_user = session.exec(select(User).where(User.username == "admin")).first()
                if existing_user:
                    return True
                
                user = User(username="admin", password=Auth.hash_password("admin"))
                session.add(user)
                session.commit()
                session.refresh(user)

                return True
            
            except Exception as e:
                logger.error(f'Exception occurred: {e}')
                return False

    @staticmethod
    def get_all_users():
        with get_session() as session:
            try:
                statement = select(User)
                users = session.exec(statement=statement).all()

                return users
            
            except Exception as e:
                logger.error(f'Exception occurred: {e}')
                raise HTTPException(status_code=500, detail="Internal Error, unable to get all users")

    @staticmethod
    def get_serial_number():
        """
            This will red the /proc/cpuinfo and returns the serial number
            if not if will return with None
        """
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("Serial"):
                        return line.strip().split(":")[1].strip()
                    
            return None
        except Exception as e:
            logger.error(f'Exception occurred: {e}')
            return None

    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(original_password, password):
        try:
            if not Auth._is_hashed_password(original_password):
                return original_password == password
            return pwd_context.verify(password, original_password)
        except Exception as e:
            logger.error(f'Exception occurred: {e}')
            return False
        
    @staticmethod
    def get_password(username):
        """
            This will return the password of the given user. 
        """
        with get_session() as session:
            try:
                statement = select(User).where(User.username == username)
                user = session.exec(statement=statement).first()

                return user.password if user else None
            except Exception as e:
                logger.error(f"Error while getting the password: {e}")
                return None
        
    @staticmethod
    def login(username, password):
        # TODO - hash/encrypt the password while sending even though the medium is HTTPS.
        """
            It authenticates the user and returns the user with a JWT
            username - string 
            password - string

            if username is admin and password is serial number of the CPU then it is first time login, return the user a JWT and ask the user to reset the password. 
        """

        if not username or not password:
            raise HTTPException(status_code=400, detail="Username/Password not provided")

        serial_number = Auth.get_serial_number()

        if serial_number is None:
            raise HTTPException(status_code=503, detail="Unable to read device serial number")

        with get_session() as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            is_default_admin_password = (
                username == "admin"
                and (
                    user.password == "admin"
                    or Auth.verify_password(user.password, password="admin")
                )
            )

            # First-time admin flow: require serial number to proceed to reset.
            if is_default_admin_password:
                if password == serial_number:
                    raise HTTPException(status_code=403, detail="Reset your password")
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Normal credential check
            if not Auth.verify_password(user.password, password=password):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Opportunistic migration: if we ever accepted a plaintext password, re-hash it.
            if not Auth._is_hashed_password(user.password):
                user.password = Auth.hash_password(password=password)
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()

            token = Auth.create_access_token({
                "sub": username,
                "role": "admin" if username == "admin" else "user",
                "is_verified": True
            })

            if not token:
                raise HTTPException(status_code=500, detail="Issue in creating the JWT token")
            
            return {
                "token": token,
                "serial_number": serial_number,
            }
        
    @staticmethod
    def reset_password(username, password):
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username/Password not provided")
        
        # check if user is present if not return invalid request.
        # if present then hash the password and add it to the db along with the updated_at. 
        with get_session() as session:
            try:
                user = session.exec(select(User).where(User.username == username)).first()
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                user.password = Auth.hash_password(password=password)
                user.updated_at = datetime.now(timezone.utc)

                session.commit()
                session.refresh(user)

                return {"detail": "Password updated successfully"}
            except Exception as e:
                logger.error(f'Exception occurred: {e}')
                raise HTTPException(status_code=503, detail="Service unavailable") 
