import jwt
from fastapi import HTTPException
from app.db.main import get_session
from app.db.models import User
from sqlmodel import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class Auth:

    @staticmethod
    def create_access_token(data: dict, expires_delta = None):
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
           
            to_encode.update({ "exp": expire })

            encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

            return encoded_jwt
        except Exception as e:
            print(e)
            return None
        
    @staticmethod
    def create_initial_user():
        try:
            session = get_session()

            existing_user = session.exec(select(User).where(User.username == "admin")).first()
            if existing_user:
                 print("Admin user already exists.")
                 return True
            
            user = User(username="admin", password="admin")
            session.add(user)
            session.commit()
            session.refresh(user)

            return True
        
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_all_users():
        try:
            session = get_session()
            statement = select(User)
            users = session.exec(statement=statement).all()

            return users
        
        except Exception as e:
            print(e)
            return HTTPException(status_code=500, detail="Internal Error, unable to get all users")

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
            print(e)
            return None

    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(original_password, password):
        try:
            return pwd_context.verify(password, original_password)
        except Exception as e:
            print(e)
            return False
    @staticmethod
    def get_password(username):
        """
            This will return the password of the given user. 
        """
        try:
            session = get_session()
            statement = select(User).where(User.username == username)
            user = session.exec(statement=statement).first()

            return user.password
        except:
            print("Error while getting the password")
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
            return HTTPException(status_code=400, detail="Username/Password not provided")

        # for testing added = bc72285ee4b8686b, uncomment below line in prod.
        serial_number = "bc72285ee4b8686b"
        # serial_number = Auth.get_serial_number()

        if serial_number is None:
            return HTTPException(status_code=503)
        
        # get the hashed password and the given password and verify if they are same, if so then create a jwt and return.
        original_password = Auth.get_password(username=username)

        if username == "admin" and password == serial_number and original_password == "admin":
            return HTTPException(status_code=403, detail="Reset your password")

        if original_password is None:
            return HTTPException(status_code=503)

        #verify the password 
        if Auth.verify_password(original_password, password=password):
            token = Auth.create_access_token({
                "sub": username,
                "role": "admin",
                "is_verified": True
            })

            if not token:
                return HTTPException(status_code=500, detail="Issue in creating the JWT token")
            
            return dict({
                "status_code": 200,
                "token": token
            })
        else:
            # password is wrong.
            return HTTPException(status_code=401)
        
    @staticmethod
    def reset_password(username, password):
        if not username or not password:
            return HTTPException(status_code=400, detail="Username/Password not provided")
        
        # check if user is present if not return invalid request.
        # if present then hash the password and add it to the db along with the updated_at. 
        try:
            session = get_session()
            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user.password = Auth.hash_password(password=password)
            user.updated_at = datetime.utcnow()

            session.commit()
            session.refresh(user)

            return HTTPException(status_code=201, detail="Password updated successfully")
        except Exception as e:
            print(e) 
            return HTTPException(status_code=503) 