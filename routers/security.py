from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException

from config import config
from app import dao


SECRET_KEY = config.crypt_key
ALGORITHM = "HS256"
EXPIRE_SEC = 300
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    created: datetime
    email: str | None = None
    fullname: str | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_user(username: str, password: str):
    user = await dao.UserDAO.find_one_or_none(username=username)
    if not user or not verify_password(password, user['password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()

    # add expire
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else None
    to_encode.update({"exp": expire})

    # encode
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    creds_exception = HTTPException(401, detail="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise creds_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise creds_exception

    user = await dao.UserDAO.find_one_or_none(username=token_data.username)
    if user is None:
        raise creds_exception
    return user


router = APIRouter(tags=['security'])

@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(seconds=EXPIRE_SEC)
    access_token = create_access_token(data={'sub': user['username']}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post('/users/me', response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


