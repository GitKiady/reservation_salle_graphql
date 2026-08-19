import jwt
from datetime import datetime, timedelta, timezone

import os
from dotenv import load_dotenv
load_dotenv()

def create_access_token(email: str) -> str:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES"))

    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)

    to_encode = {
        "email": email,
        "exp": expire
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    try:
        result = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return result
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token expiré.")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Token invalide.")
