from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, models
from .database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .config import setting
SECRET_KEY = setting.secret_key
ALGORITHM = setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = setting.access_token_expire_min
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    """
    The function `create_access_token` generates a JWT access token with an expiration time based on the
    input data.
    
    :param data: The `data` parameter in the `create_access_token` function is a dictionary containing
    the information that you want to encode into the access token. This data could include things like
    user ID, username, roles, or any other relevant information that you want to include in the token
    :type data: dict
    :return: The function `create_access_token` returns an encoded JSON Web Token (JWT) containing the
    data provided in the `data` dictionary along with an expiration time set to a specific number of
    minutes from the current time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """
    The function `verify_token` decodes a JWT token using a secret key and algorithm, extracts the user
    ID from the payload, and returns token data or raises a credentials exception if the user ID is
    missing or if there is a JWT error.
    
    :param token: A JWT token that needs to be verified
    :type token: str
    :param credentials_exception: The `credentials_exception` parameter is typically an exception that
    is raised when there is an issue with the user's credentials or authentication. In the context of
    the `verify_token` function you provided, it seems to be used to handle cases where the token
    verification fails or the user ID is not found in
    :return: the `token_data` object containing the user ID extracted from the decoded token payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    The function `get_current_user` retrieves the current user based on the provided token and database
    session.
    
    :param token: The `token` parameter is a string that represents the authentication token used to
    verify the user's identity and access rights. In this case, it is obtained as a dependency using the
    `oauth2_scheme` and is used to validate the user's credentials
    :type token: str
    :param db: The `db` parameter in the `get_current_user` function is of type `Session` and is
    obtained by calling the `get_db` dependency. This parameter is used to interact with the database
    within the function
    :type db: Session
    :return: The function `get_current_user` is returning the user object retrieved from the database
    based on the user ID extracted from the token.
    """
    credentials_exception = HTTPException(status_code=401, 
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user