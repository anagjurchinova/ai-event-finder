from typing import List, Dict, Any

from app.error_handler.exceptions import (
    DuplicateEmailException,
    UserSaveException,
    UserDeleteException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.util.logging_util import log_calls
from app.util.transaction_util import transactional, retry_conflicts
from app.util.user_util import return_not_found_by_name_message, return_not_found_by_email_message, \
    return_not_found_by_id_message
from app.util.validation_util import validate_user


@log_calls("app.services")
class UserServiceImpl(UserService):
    """
        Concrete implementation of UserService that uses a UserRepository.
        Adds transaction management, retries on conflicts, and validation/exception handling.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @transactional
    def get_by_id(self, user_id: int, session=None) -> User:
        user = self.user_repository.get_by_id(user_id, session)
        validate_user(user, return_not_found_by_id_message(user_id))
        return user

    @transactional
    def get_by_email(self, email: str, session=None) -> User:
        user = self.user_repository.get_by_email(email, session)
        validate_user(user, return_not_found_by_email_message(email))
        return user

    @transactional
    def get_by_name(self, name: str, session=None) -> User:
        user = self.user_repository.get_by_name(name, session)
        validate_user(user, return_not_found_by_name_message(name))
        return user

    @transactional
    def get_all(self, session=None) -> List[User]:
        return self.user_repository.get_all(session)

    @retry_conflicts(max_retries=3, backoff_sec=0.1)
    @transactional
    def save(self, user: User, session=None) -> User:
        """
        Save a new user to the database.

        Raises:
            DuplicateEmailException: If a user with the same email already exists.
            UserSaveException: If saving fails for other reasons.
        """

        if self.user_repository.get_by_email(user.email, session):
            raise DuplicateEmailException(email=user.email)
        try:
            return self.user_repository.save(user, session)
        except Exception as e:
            raise UserSaveException(original_exception=e)

    @retry_conflicts(max_retries=3, backoff_sec=0.1)
    @transactional
    def update(self, email: str, data: Dict[str, Any], session=None) -> User:
        """
       Update an existing user by email.

       Raises:
           UserSaveException: If the update fails.
        """

        user = self.user_repository.get_by_email(email, session)
        validate_user(user, return_not_found_by_email_message(email))

        if "name" in data and data["name"] is not None:
            user.name = data["name"]
        if "surname" in data and data["surname"] is not None:
            user.surname = data["surname"]
        if "password" in data and data["password"]:
            user.password = data["password"]
        try:
            return self.user_repository.save(user, session)
        except Exception as e:
            raise UserSaveException(original_exception=e)

    @retry_conflicts(max_retries=3, backoff_sec=0.1)
    @transactional
    def delete_by_id(self, user_id: int, session=None) -> None:
        """
        Delete a user by ID.

        Raises:
            UserDeleteException: If deletion fails.
        """
        user = self.user_repository.get_by_id(user_id, session)
        validate_user(user, return_not_found_by_id_message(user_id))

        try:
            self.user_repository.delete_by_id(user_id, session)
        except Exception as e:
            raise UserDeleteException(user_id=user_id, original_exception=e)

    @transactional
    def exists_by_id(self, user_id: int, session=None) -> bool:
        user = self.user_repository.get_by_id(user_id, session)
        validate_user(user, return_not_found_by_id_message(user_id))
        return True

    @transactional
    def exists_by_name(self, name: str, session=None) -> bool:
        user = self.user_repository.get_by_name(name, session)
        validate_user(user, return_not_found_by_name_message(name))
        return True
