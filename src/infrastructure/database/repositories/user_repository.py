"""
User repository implementation
"""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.value_objects.common import EntityId
from ....domain.value_objects.email import Email
from ..models.user_model import UserModel
from ..connection import get_db_session

logger = logging.getLogger(__name__)


class UserRepositoryImpl(UserRepository):
    """SQLAlchemy implementation of user repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        try:
            user_model = UserModel(
                id=user.id.value,
                email=user.email.value,
                username=user.username,
                password_hash=user.password_hash,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_verified=user.is_verified,
                last_login=user.last_login,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)
            
            logger.info(f"Created user: {user.id.value}")
            return self._model_to_entity(user_model)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        try:
            stmt = (
                select(UserModel)
                .options(selectinload(UserModel.roles))
                .where(UserModel.id == user_id)
            )
            
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if user_model:
                return self._model_to_entity(user_model)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            raise
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email"""
        try:
            stmt = (
                select(UserModel)
                .options(selectinload(UserModel.roles))
                .where(UserModel.email == email.value)
            )
            
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if user_model:
                return self._model_to_entity(user_model)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email.value}: {e}")
            raise
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            stmt = (
                select(UserModel)
                .options(selectinload(UserModel.roles))
                .where(UserModel.username == username)
            )
            
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if user_model:
                return self._model_to_entity(user_model)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            raise
    
    async def update(self, user: User) -> User:
        """Update existing user"""
        try:
            stmt = select(UserModel).where(UserModel.id == user.id.value)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                raise ValueError(f"User not found: {user.id.value}")
            
            # Update fields
            user_model.email = user.email.value
            user_model.username = user.username
            user_model.password_hash = user.password_hash
            user_model.first_name = user.first_name
            user_model.last_name = user.last_name
            user_model.is_active = user.is_active
            user_model.is_verified = user.is_verified
            user_model.last_login = user.last_login
            user_model.updated_at = user.updated_at
            
            await self.session.commit()
            await self.session.refresh(user_model, ["roles"])
            
            logger.info(f"Updated user: {user.id.value}")
            return self._model_to_entity(user_model)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update user {user.id.value}: {e}")
            raise
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID"""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return False
            
            await self.session.delete(user_model)
            await self.session.commit()
            
            logger.info(f"Deleted user: {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        role: Optional[str] = None
    ) -> List[User]:
        """List users with optional filters"""
        try:
            stmt = select(UserModel).options(selectinload(UserModel.roles))
            
            # Apply filters
            if is_active is not None:
                stmt = stmt.where(UserModel.is_active == is_active)
            
            if is_verified is not None:
                stmt = stmt.where(UserModel.is_verified == is_verified)
            
            if role:
                stmt = stmt.join(UserModel.roles).where(
                    UserModel.roles.any(name=role)
                )
            
            # Apply pagination
            stmt = stmt.offset(skip).limit(limit)
            stmt = stmt.order_by(UserModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            user_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in user_models]
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise
    
    async def count_users(
        self,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        role: Optional[str] = None
    ) -> int:
        """Count users with optional filters"""
        try:
            stmt = select(func.count(UserModel.id))
            
            # Apply filters
            if is_active is not None:
                stmt = stmt.where(UserModel.is_active == is_active)
            
            if is_verified is not None:
                stmt = stmt.where(UserModel.is_verified == is_verified)
            
            if role:
                stmt = stmt.join(UserModel.roles).where(
                    UserModel.roles.any(name=role)
                )
            
            result = await self.session.execute(stmt)
            return result.scalar()
            
        except Exception as e:
            logger.error(f"Failed to count users: {e}")
            raise
    
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""
        try:
            stmt = select(func.count(UserModel.id)).where(UserModel.email == email.value)
            result = await self.session.execute(stmt)
            count = result.scalar()
            return count > 0
            
        except Exception as e:
            logger.error(f"Failed to check user existence by email {email.value}: {e}")
            raise
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        try:
            stmt = select(func.count(UserModel.id)).where(UserModel.username == username)
            result = await self.session.execute(stmt)
            count = result.scalar()
            return count > 0
            
        except Exception as e:
            logger.error(f"Failed to check user existence by username {username}: {e}")
            raise
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with specific role"""
        try:
            stmt = (
                select(UserModel)
                .options(selectinload(UserModel.roles))
                .join(UserModel.roles)
                .where(UserModel.roles.any(name=role))
                .order_by(UserModel.created_at.desc())
            )
            
            result = await self.session.execute(stmt)
            user_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in user_models]
            
        except Exception as e:
            logger.error(f"Failed to get users by role {role}: {e}")
            raise
    
    async def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name, username, or email"""
        try:
            search_term = f"%{query.lower()}%"
            
            stmt = (
                select(UserModel)
                .options(selectinload(UserModel.roles))
                .where(
                    or_(
                        func.lower(UserModel.username).like(search_term),
                        func.lower(UserModel.email).like(search_term),
                        func.lower(UserModel.first_name).like(search_term),
                        func.lower(UserModel.last_name).like(search_term),
                        func.lower(
                            func.concat(UserModel.first_name, ' ', UserModel.last_name)
                        ).like(search_term)
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(UserModel.created_at.desc())
            )
            
            result = await self.session.execute(stmt)
            user_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in user_models]
            
        except Exception as e:
            logger.error(f"Failed to search users with query '{query}': {e}")
            raise
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert UserModel to User entity"""
        return User(
            id=EntityId(model.id),
            email=Email(model.email),
            username=model.username,
            password_hash=model.password_hash,
            first_name=model.first_name,
            last_name=model.last_name,
            is_active=model.is_active,
            is_verified=model.is_verified,
            last_login=model.last_login,
            roles=model.role_names,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


# Dependency function
def get_user_repository(session: AsyncSession) -> UserRepository:
    """Get user repository instance"""
    return UserRepositoryImpl(session)