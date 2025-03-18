from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from user_model import User, Role
from authorization.auth import require_permission, get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/roles", tags=["roles"])

def get_role_permission(action: str):
    return require_permission(action, "Role")

@router.get("/")
@get_role_permission("read")
async def list_roles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    """List all roles"""
    try:
        roles = db.query(Role).all()
        return {"roles": [{"id": role.id, "name": role.name} for role in roles]}
    except Exception as e:
        logger.error(f"Error listing roles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
@get_role_permission("manage_roles")
async def create_role(
    name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new role"""
    try:
        # Check if role already exists
        existing_role = db.query(Role).filter(Role.name == name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role already exists")
        
        # Create new role
        role = Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
        return {"id": role.id, "name": role.name}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{role_id}")
@get_role_permission("manage_roles")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Delete a role"""
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent deletion of built-in roles
        if role.name in ["admin", "user"]:
            raise HTTPException(status_code=400, detail="Cannot delete built-in roles")
        
        db.delete(role)
        db.commit()
        return {"message": "Role deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting role: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assign/{user_id}/{role_id}")
@get_role_permission("manage_roles")
async def assign_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Assign a role to a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
        
        return {"message": f"Role {role.name} assigned to user successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/remove/{user_id}/{role_id}")
@get_role_permission("manage_roles")
async def remove_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Remove a role from a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent removing admin role if it's the last one
        if role.name == "admin":
            admin_users = db.query(User).filter(User.roles.any(name="admin")).count()
            if admin_users <= 1 and user.is_admin:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot remove the last admin role"
                )
        
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
        
        return {"message": f"Role {role.name} removed from user successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error removing role: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 