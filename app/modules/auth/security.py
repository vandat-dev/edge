import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Union

import jwt

from app.modules.user.model import User


class TokenService:
    def __init__(
            self,
            secret_key: str,
            algorithm: str,
            access_token_expires_in_minutes: int,
            refresh_token_expires_in_days: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expires_in_minutes = access_token_expires_in_minutes
        self.refresh_token_expires_in_days = refresh_token_expires_in_days

    def generate_access_token(self, user: User) -> str:
        """
        Generate an access token for a user.

        Args:
            user (User): A User model instance containing user details.

        Returns:
            str: The generated access token.
        """
        now = datetime.now(tz=timezone.utc)
        exp_time = now + timedelta(minutes=self.access_token_expires_in_minutes)

        payload = {
            "sub": str(user.id),  # Subject (user ID) - MUST be string
            "username": user.username,  # Username
            "email": user.email,  # Email
            "role": user.role,  # Role for the user
            "iat": int(now.timestamp()),  # Issued at - UNIX timestamp
            "jti": str(uuid.uuid4()),  # JWT ID (unique identifier for the token)
            "exp": int(exp_time.timestamp()),  # Expiration time - UNIX timestamp
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def generate_refresh_token(self, user: User) -> str:
        """
        Generate a refresh token for a user.

        Args:
            user (User): A User model instance containing user details.

        Returns:
            str: The generated refresh token.
        """
        now = datetime.now(tz=timezone.utc)
        exp_time = now + timedelta(days=self.refresh_token_expires_in_days)

        payload = {
            "sub": str(user.id),  # Subject (user ID) - MUST be string
            "iat": int(now.timestamp()),  # Issued at - UNIX timestamp
            "jti": str(uuid.uuid4()),  # JWT ID (unique identifier for the token)
            "exp": int(exp_time.timestamp()),  # Expiration time - UNIX timestamp
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def validate_token(self, token: str) -> Union[Dict[str, Any], None]:
        """
        Validate a given token (access or refresh).

        Args:
            token (str): The token to validate.

        Returns:
            dict | None: Decoded token payload if valid; None if invalid or expired.
        """
        try:
            decoded_token = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            return decoded_token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def generate_token_pair(self, user: User) -> Dict[str, str]:
        """
        Generate both access and refresh tokens.

        Args:
            user (User): A User model instance containing user details.

        Returns:
            dict: A dictionary containing both access and refresh tokens.
        """
        access_token = self.generate_access_token(user)
        refresh_token = self.generate_refresh_token(user)
        return {"access_token": access_token, "refresh_token": refresh_token}

    def get_token_payload(self, token: str) -> Union[Dict[str, Any], None]:
        """
        Get token payload without verification (for debugging).
        WARNING: Only use for debugging, not for production validation!

        Args:
            token (str): The token to decode.

        Returns:
            dict | None: Decoded payload or None if invalid format.
        """
        try:
            # Decode the token without verifying signature
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None
