import base64
import hashlib
import hmac

from flask_restx import abort

from project.dao.user import UserDAO
from project.exceptions import ItemNotFound
from project.helpers.constant import PWD_HASH_SALT, PWD_HASH_ITERATIONS
from project.schemas.user import UserSchema

from project.services.base import BaseService


class UsersService(BaseService):
    def get_all_users(self):
        """
        Получаем всех пользователей
        """
        users = UserDAO(self._db_session).get_all()
        print(UserSchema(many=True).dump(users))
        return UserSchema(many=True).dump(users)

    def get_item_by_id(self, pk):
        """
        Получаем пользователя по его id
        """
        user = UserDAO(self._db_session).get_by_id(pk)
        if not user:
            raise ItemNotFound
        return UserSchema().dump(user)

    def get_item_by_email(self, email):
        """
        Получаем пользователя по его email
        """
        user = UserDAO(self._db_session).get_by_email(email=email)
        if not user:
            raise ItemNotFound
        return UserSchema().dump(user)

    def create(self, new_pd):
        """
        Метод создания пользователя
        :param new_pd: все данные пользователя -> dict
        """
        user_password = new_pd.get("password")
        if user_password:
            new_pd["password"] = self.generate_password_digest(user_password)  # хешируем пароль
        user = UserDAO(self._db_session).create(new_pd)
        return UserSchema().dump(user)

    def update(self, new_pd):
        """
        Обновляем пользователя
        :param new_pd: передаем нужные поля для обновления -> dict
        """
        user = UserDAO(self._db_session).update(new_pd)
        return UserSchema().dump(user)

    def update_password(self, new_pd):
        """
        Обновление пароля
        :param new_pd: старый, новый пароль и id -> dict
        :return:
        """
        old_password = new_pd.get("old_password")
        new_password = new_pd.get("new_password")

        before_update_user = self.get_item_by_id(new_pd.get("id"))
        if self.generate_password_digest(old_password) == before_update_user.get("password"):  # проверяю совпадают ли пароли
            abort(400)                                                                         #
        if self.compare_passwords(before_update_user.get('password'), new_password):           #
            abort(400, 'Старый и новый пароль совпадают')                                      #

        user_update_date = {
            "id": before_update_user.get("id"),
            "email": before_update_user.get('email'),
            "password": self.generate_password_digest(new_password)
        }

        update_user = UserDAO(self._db_session).update(user_update_date)
        return UserSchema().dump(update_user)

    def generate_password_digest(self, password):
        """
        хешируем пароль
        :param password: пароль -> str

        """
        hash_digest = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password.encode("utf-8"),
            salt=PWD_HASH_SALT,
            iterations=PWD_HASH_ITERATIONS
        )
        return base64.b64encode(hash_digest)

    def compare_passwords(self, password_hash, other_password) -> bool:
        """
        Проверка пароля
        """
        decoded_digest = base64.b64decode(password_hash)

        hash_digest = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=other_password.encode('utf-8'),
            salt=PWD_HASH_SALT,
            iterations=PWD_HASH_ITERATIONS
        )
        return hmac.compare_digest(decoded_digest, hash_digest)

