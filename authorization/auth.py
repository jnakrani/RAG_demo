from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from oso import Oso
from pathlib import Path
from functools import wraps
from typing import Optional, Callable, Any
from user_model import User, Role
from utils.auth_utils import get_current_active_user
import logging

logger = logging.getLogger(__name__)

# Initialize security scheme
security = HTTPBearer()

# Create a fresh Oso instance
oso = Oso()

def initialize_oso():
    """Initialize Oso with our policy file and register classes"""
    try:
        # Create a fresh instance
        global oso
        oso = Oso()
        
        # Register classes
        oso.register_class(User)
        oso.register_class(Role)
        
        # Load policy file
        policy_path = Path(__file__).parent / "policy.polar"
        oso.load_files([str(policy_path)])
    except Exception as e:
        raise Exception(f"Failed to initialize Oso: {str(e)}")

# Initialize Oso when the module is imported
initialize_oso()

def require_permission(action: str, resource_type: Optional[str] = None):
    """Function that can be used both as a dependency and a decorator for permission checking"""
    def check_permission(user: User) -> bool:
        try:
            # For admin users, allow all actions
            if user.is_admin:
                return True

            if resource_type:
                oso.authorize(user, action, resource_type)
            else:
                oso.authorize(user, action, None)
            return True
        except Exception as e:
            logger.error(f"Authorization error: {str(e)}")
            return False

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if check_permission(current_user):
            return current_user
        raise HTTPException(
            status_code=403,
            detail=f"Not authorized to perform {action}"
        )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), **kwargs):
            if check_permission(current_user):
                return await func(*args, current_user=current_user, **kwargs)
            raise HTTPException(
                status_code=403,
                detail=f"Not authorized to perform {action}"
            )
        return wrapper

    # Return the decorator directly
    return decorator

def check_permission(user: User, action: str, resource: Any) -> bool:
    """Check if a user has permission to perform an action on a resource"""
    try:
        oso.authorize(user, action, resource)
        return True
    except Exception:
        return False 