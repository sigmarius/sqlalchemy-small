from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Boolean,
    create_engine,
)

from sqlalchemy.orm import mapper

# echo=True => распечатывает все запросы к БД в консоль
engine = create_engine("sqlite:///example-02.db", echo=True)
metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(32), unique=True, nullable=False, default=""),
    # server_default="0" => sqlite БД (данные в виде строки), postgres => False
    Column("is_staff", Boolean, nullable=False, default=False, server_default="0")
)


class User:
    def __init__(self, id, username, is_staff):
        self.id = id
        self.username = username
        self.is_staff = is_staff


mapper(User, users_table)


if __name__ == '__main__':
    # создаем таблицу с помощью engine
    metadata.create_all(bind=engine)
