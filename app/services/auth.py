"""
Authentication service
"""
from typing import Optional
from app.config import get_settings
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import Token

settings = get_settings()


class AuthService:
    """Authentication service for user login and token management"""

    def __init__(self):
        # In a real application, this would be stored in the database
        # For now, we use hardcoded credentials
        self.admin_username = settings.ADMIN_USERNAME
        self.admin_password = settings.ADMIN_PASSWORD
        self._admin_password_hash = None

        # Visitor account (read-only access)
        self.visitor_username = "visitor"
        self.visitor_password = "visitor123"
        self._visitor_password_hash = None

    @property
    def admin_password_hash(self) -> str:
        """Lazy load admin password hash"""
        if self._admin_password_hash is None:
            self._admin_password_hash = get_password_hash(self.admin_password)
        return self._admin_password_hash

    @property
    def visitor_password_hash(self) -> str:
        """Lazy load visitor password hash"""
        if self._visitor_password_hash is None:
            self._visitor_password_hash = get_password_hash(self.visitor_password)
        return self._visitor_password_hash

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate a user with username and password.

        Args:
            username: The username to authenticate
            password: The plain text password

        Returns:
            True if authentication successful, False otherwise
        """
        # Check admin credentials
        if username == self.admin_username:
            return verify_password(password, self.admin_password_hash)

        # Check visitor credentials
        if username == self.visitor_username:
            return verify_password(password, self.visitor_password_hash)

        return False
    
    def create_token_for_user(self, username: str) -> Token:
        """
        Create a JWT token for an authenticated user.
        
        Args:
            username: The username to create token for
            
        Returns:
            Token object with access_token and token_type
        """
        # Create token data
        token_data = {
            "sub": username,
            "is_admin": (username == self.admin_username)
        }
        
        # Generate JWT token
        access_token = create_access_token(data=token_data)
        
        return Token(access_token=access_token, token_type="bearer")
    
    def login(self, username: str, password: str) -> Optional[Token]:
        """
        Authenticate user and return token if successful.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            Token object if authentication successful, None otherwise
        """
        if self.authenticate_user(username, password):
            return self.create_token_for_user(username)
        return None


# Singleton instance
auth_service = AuthService()

