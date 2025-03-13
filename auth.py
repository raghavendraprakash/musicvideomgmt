from passlib.hash import pbkdf2_sha256
from jose import JWTError, jwt
import datetime
import os
from dotenv import load_dotenv
import logging
from logger_config import setup_logger

# Setup logger
logger = setup_logger()

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = "your-fallback-secret-key"  # For development only
    logger.warning("SECRET_KEY not found in .env, using fallback key")

def hash_password(password: str) -> str:
    """
    Hash a password using pbkdf2_sha256
    """
    try:
        return pbkdf2_sha256.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    try:
        return pbkdf2_sha256.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def create_access_token(data: dict) -> str:
    """
    Create a JWT token
    """
    try:
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise

def verify_token(token: str) -> dict:
    """
    Verify a JWT token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError as e:
        logger.error(f"Token verification error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {str(e)}")
        return None

# Optional: Add password validation
def validate_password(password: str) -> bool:
    """
    Validate password strength
    """
    try:
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char.islower() for char in password):
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating password: {str(e)}")
        return False

# Optional: Add token blacklist for logout
token_blacklist = set()

def blacklist_token(token: str):
    """
    Add a token to the blacklist
    """
    try:
        token_blacklist.add(token)
        logger.info(f"Token blacklisted successfully")
    except Exception as e:
        logger.error(f"Error blacklisting token: {str(e)}")

def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted
    """
    return token in token_blacklist