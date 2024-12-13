from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
from typing import Optional, Dict, List
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import func, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_email_service, get_settings
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from app.services.email_service import EmailService

import logging

settings = get_settings()
logger = logging.getLogger(__name__)


class UserService:
    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        query = select(User).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> Optional[User]:
        try:
            validated_data = UserCreate(**user_data).model_dump()
            existing_user = await cls.get_by_email(session, validated_data['email'])
            if existing_user:
                logger.error("User with given email already exists.")
                return {"detail": "Email exists already.", "status": 409}

            validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            new_user = User(**validated_data)
            new_user.nickname = await cls._generate_unique_nickname(session)
            new_user.role = await cls._assign_role(session, validated_data.get('role'))
            new_user.verification_token = None if new_user.role == UserRole.ADMIN else generate_verification_token()
            new_user.email_verified = new_user.role == UserRole.ADMIN

            session.add(new_user)
            await session.commit()

            if not new_user.email_verified:
                await email_service.send_verification_email(new_user)

            return new_user
        except ValidationError as e:
            logger.error(f"Validation error during user creation: {e}")
            return None

    @classmethod
    async def update(cls, session: AsyncSession, email_id: str, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        try:
            validated_data = UserUpdate(**update_data).model_dump(exclude_unset=True)

            # Check for duplicate email
            if email_id:
                existing_user = await cls.get_by_email(session, email_id)
                if existing_user and existing_user.id != user_id:
                    logger.error("User with given email already exists.")
                    return {"detail": "Email exists already.", "status": 409}

            # Update password if provided
            if "password" in validated_data:
                validated_data["hashed_password"] = hash_password(validated_data.pop("password"))

            # Execute update query
            query = (
                update(User)
                .where(User.id == user_id)
                .values(**validated_data)
                .execution_options(synchronize_session="fetch")
            )
            await cls._execute_query(session, query)

            # Refresh and return the updated user
            updated_user = await cls.get_by_id(session, user_id)
            if updated_user:
                session.refresh(updated_user)
                logger.info(f"User {user_id} updated successfully.")
                return updated_user
            else:
                logger.error(f"User {user_id} not found after update attempt.")
                return None
        except Exception as e:
            logger.error(f"Error during user update: {e}")
            return None

    @classmethod
    async def _generate_unique_nickname(cls, session: AsyncSession) -> str:
        new_nickname = generate_nickname()
        while await cls.get_by_email(session, new_nickname):
            new_nickname = generate_nickname()
        return new_nickname

    @classmethod
    async def _assign_role(cls, session: AsyncSession, role: Optional[UserRole]) -> UserRole:
        user_count = await cls.count(session)
        return UserRole.ADMIN if user_count == 0 or role == UserRole.ADMIN else UserRole.ANONYMOUS

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        return result.scalar() or 0
