from database.database import Database
from database.models.db_model import AdminUser


def select_user_by_username(database: Database, username: str) -> AdminUser:
    with database.session() as session:
        return session.query(AdminUser).filter(AdminUser.username == username).first()


def select_user_by_id(database: Database, id: str) -> AdminUser:
    with database.session() as session:
        return session.query(AdminUser).filter(AdminUser.id == id).first()
