from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    create_engine,
    func,
    ForeignKey,
    or_
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, joinedload

# echo=True => распечатывает все запросы к БД в консоль
engine = create_engine("sqlite:///example-04.db", echo=True)
Base = declarative_base(bind=engine)

# создаем сессию, привязываем к engine
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False, default="", server_default="")
    is_staff = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    
    # user - поле для связки из класса Post
    posts = relationship("Post", back_populates="user")

    # user - поле для связки из класса UserProfile, uselist=False => связь один к одному
    profile = relationship("UserProfile", back_populates="user", uselist=False)

    def __str__(self):
        return f"User #{self.id} username:{self.username}"

    def __repr__(self):
        return str(self)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(120), nullable=False, default="", server_default="")
    last_name = Column(String(120), nullable=False, default="", server_default="")
    
    # связь с таблицей users 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # поле для обратной связи таблиц => берем из класса User, по полю user_id
    user = relationship(User, back_populates="profile")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(90), nullable=False, default="", server_default="")

    # user_id = Column(Integer, ForeignKey(User.id))
    # лучше передавать имя таблицы, чтобы можно было использовать модульность
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # поле для связки таблиц => берем из поста username, на который указывает user_id
    user = relationship(User, back_populates="posts")

    def __str__(self):
        return f"{self.title} by #{self.user_id}"

    def __repr__(self):
        return str(self)


def create_users():
    # создали сессию (необязательно, выполняется автоматом)
    session = Session()

    user = User(username="admin", is_staff=True)
    mark = User(username="mark")

    # начали отслеживание пользователей в сессии
    session.add(user)
    session.add(mark)

    # записали изменения в БД
    session.commit()

    # закрыли сессию
    session.close()


def add_profiles():
    session = Session()

    mark = session.query(User).filter_by(username="mark").one_or_none()

    profile = UserProfile(user=mark, first_name="Mark", last_name="Two")
    # profile = UserProfile(user_id=user.id)

    session.add(profile)
    session.commit()
    session.close()


def show_users_with_related():
    session = Session()

    # объектная нотация для подсказок в print
    admin: User = session.query(User).filter_by(username="admin").one_or_none()
    mark: User = session.query(
        User,
    ).filter_by(
        username="mark",
    ).options(
        joinedload(User.profile),
        joinedload(User.posts)
    ).one()

    print("admin with profile and posts", admin, admin.profile, admin.posts)
    print("mark with profile and posts", mark, mark.profile, mark.posts)

    session.close()


def create_posts():
    session = Session()

    # объектная нотация для подсказок в print
    admin: User = session.query(User).filter_by(username="admin").one_or_none()
    mark: User = session.query(User).filter_by(username="mark").one_or_none()

    post_django = Post(title="Django lesson", user=admin)
    post_flask = Post(title="Flask lesson", user=mark)
    post_fast_api = Post(title="FastAPI lesson", user=mark)

    session.add(post_django)
    session.add(post_flask)
    session.add(post_fast_api)
    session.commit()

    print("admin with posts", admin, admin.posts)
    print("mark with posts", mark,  mark.posts)

    session.close()


def demo_filtering():
    marks = Session.query(User).join(UserProfile).filter(
        # ilike => case insensitive
        UserProfile.first_name.ilike("mark")
    ).all()

    # pure SQL
    res = Session.execute("SELECT * FROM USERS;")

    print("marks: ", marks)
    print("pure SQL: ", list(res))

    Session.close()


def demo_filtering2():
    users_flask_or_django = Session.query(
        User, Post
    ).join(
        Post,
    ).filter(
        # or => выполняется что-то одно
        or_(
            Post.title.ilike("%flask%"),
            Post.title.ilike("%django%")
        )
    ).options(
        joinedload(User.profile),
    ).all()

    print("users with flask or django posts: ")
    for user, post in users_flask_or_django:
        print("user", user)
        print("his matched posts:", post)

    Session.close()


def main():
    # # создаем таблицу с помощью engine
    # Base.metadata.create_all()
    # # создали пользователей
    # create_users()
    # # добавили профили
    # add_profiles()
    # create_posts()
    # show_users_with_related()
    # demo_filtering()
    demo_filtering2()


if __name__ == '__main__':
    main()
