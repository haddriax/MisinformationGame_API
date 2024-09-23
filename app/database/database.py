import asyncio
import uuid
from contextlib import contextmanager
from typing import Any, Dict, List
from venv import logger

from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker

from database.models.db_model import AdminUser, Comment, Post, Source, Study, Base


def handle_db_query_exceptions(empty_return):
    """
    A decorator to handle database exceptions and log errors.
    :param empty_return: The type of empty collection to return on exception.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SQLAlchemyError as e:
                logger.error(
                    f"SQLAlchemyError error occurred while executing {func.__name__}: {str(e)}"
                )
                return empty_return()
            except DBAPIError as e:
                logger.error(
                    f"DBAPIError error occurred while executing {func.__name__}: {str(e)}"
                )
                return empty_return()
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred in {func.__name__}: {str(e)}"
                )
                return empty_return()

        return wrapper

    return decorator


# @todo: When there is a large amounts of requests planned, might be smart to to that with only ONE sessions object.
class Database:
    def __init__(self, db_url: str):
        # Keeping engine as instance variable rather than creating it each time should allow efficient use of
        # connection pooling.
        self.engine = None
        self.session_maker = None

        try:
            if not db_url:
                raise ValueError("DATABASE_URL variable not set")
            self.engine = create_engine(db_url)

            Base.metadata.create_all(self.engine)

        except Exception as e:
            logger.error("Failed to connect to the database: %s", str(e))
            raise

        try:
            self.session_maker = sessionmaker(
                autocommit=False, autoflush=True, bind=self.engine
            )
        except Exception as e:
            logger.error("Failed to create session maker: %s", str(e))
            raise

        try:
            pass
        except Exception as e:
            logger.error("Failed to create database schema: %s", str(e))

    def __del__(self):
        if self.engine:
            self.engine.dispose()

    @staticmethod
    def generate_uuid():
        """
        Generates a universally unique identifier (UUID) using the uuid4 method.

        :return: A string representation of the generated UUID.
        """
        return str(uuid.uuid4())

    def create_session(self):
        try:
            return scoped_session(self.session_maker)
        except Exception as e:
            logger.error("Failed to create database session: %s", e)
            raise

    @contextmanager
    def session(self, autocommit=False):
        """
        Open a session and yield it for the caller to use.
        Creates a context with an open SQLAlchemy session, ensure that the session is properly closed and returned
        to the pool when it's no longer needed, even in the event of exceptions.

        Transactions are automatically rolled back if any exception occurs.
        Transactions are committed only if no exception occurs.
        Sessions are always closed properly, avoiding potential connection leaks.

        Example: Usable using the with directive:
        with db_session() as db:
            # Database code ...
        :param autocommit: A boolean indicating whether to commit the session automatically. Defaults to False.
        :return: The session object.
        """
        session = self.create_session()

        try:
            yield session
            if autocommit:
                session.commit()
        except KeyError as e:
            logger.error(
                f"Failed to commit session: {str(e)}. Key is invalid. \nExecuting a session rollback..."
            )
            session.rollback()
            raise
        except (DBAPIError, SQLAlchemyError) as e:
            logger.error(
                f"Failed to commit session: {str(e)}. \nExecuting a session rollback..."
            )
            session.rollback()
            raise
        except Exception as e:
            logger.error(
                f"Failed to commit session, unhandled exception {str(e.__class__)}: {str(e)}."
                f"\nExecuting a session rollback..."
            )
            session.rollback()
            raise
        finally:
            # Ensures that the session is always closed, even if an exception occurred, preventing connection leaks.
            session.close()

    async def insert_study(self, study_dict: dict) -> bool:
        """
        Insert a study into the database from a Dictionary containing study foreign keys.

        :param study_dict: A dictionary containing the study details.
        :return: True if the study is successfully inserted, False otherwise.
        """
        assert (
                study_dict is not None
        ), "Study dict cannot be None when inserting a study."

        with self.session(True) as session:
            session.add_all(study_dict["styles"])
            session.add(study_dict["basic_settings"])
            session.add(study_dict["advanced_settings"])
            session.add(study_dict["post_selection_methods"])
            session.add(study_dict["ui_settings"])
            session.add(study_dict["pages_settings"])
            session.add(study_dict["study"])
            session.add_all(study_dict["avatars"])
            session.add_all(study_dict["sources"])
            session.add_all(study_dict["posts"])
            session.add_all(study_dict["comments"])

        del study_dict
        return True

    @handle_db_query_exceptions(empty_return=List)
    async def get_all_studies(self) -> List[Study]:
        """
        Returns a list of all studies with their child objects.
        This contains all the objects and is very costly and heavy in memory.
        Used to be compatible with the legacy application.

        :return: A list of Study objects.
        :rtype: List[Study]
        """
        with self.session() as session:
            studies = (
                session.query(Study)
                .options(
                    joinedload(Study.basic_settings),
                    joinedload(Study.advanced_settings),
                    joinedload(Study.pages_settings),
                    joinedload(Study.ui_settings),
                    joinedload(Study.post_selection_methods),
                    joinedload(Study.opened_by),
                    joinedload(Study.closed_by),
                    joinedload(Study.created_by),
                    joinedload(Study.result_last_download_by),
                )
                .all()
            )
            session.expunge_all()

        return studies

    @handle_db_query_exceptions(empty_return=List)
    async def query_posts_list_by_study(self, study_id: str) -> List[Post]:
        """
        :param study_id: ID of the study to retrieve the posts for.
        :return: List of the Post objects related to the specified study.
        """
        with self.session() as session:
            posts = session.query(Post).filter_by(fk_linked_study=study_id).all()

            session.expunge_all()
        return posts

    @handle_db_query_exceptions(empty_return=dict)
    async def query_posts_list_by_study_as_dict(self, study_id: str) -> dict[str, Post]:
        """
        Get a dictionary of posts by study ID, with keys being the Posts ID for easy O(1) access.

        :param study_id: ID of the study to retrieve the posts for.
        :return: A dictionary where the keys are post IDs and the values are Post objects.
        """

        with self.session() as session:
            posts = (
                session.query(Post)
                .options(joinedload(Post.linked_study))
                .filter_by(fk_linked_study=study_id)
                .all()
            )

            # Detach all objects from the session, means the objects are is no longer managed by the session.
            session.expunge_all()

        # Build the dictionary using list comprehension.
        return {post.id: post for post in posts}

    @handle_db_query_exceptions(empty_return=dict)
    async def query_comments_list_by_study(self, study_id: str) -> List[Comment]:
        """
        :param study_id: The ID of the study to retrieve comments for.
        :return: A list of Comment objects associated with the given study.
        """
        with self.session() as session:
            comments = (
                session.query(Comment)
                .join(Comment.linked_post)
                .filter(Comment.linked_post.has(fk_linked_study=study_id))
                .all()
            )
            session.expunge_all()

        return comments

    @handle_db_query_exceptions(empty_return=List)
    async def query_comments_list_by_post(self, post_id: str) -> List[Post]:
        with self.session() as session:
            comments = session.query(Comment).filter_by(fk_linked_post=post_id).all()
            session.expunge_all()

        return comments

    @handle_db_query_exceptions(empty_return=List)
    async def query_sources_list_by_study(self, study_id: str) -> List[Source]:
        with self.session() as session:
            sources = (
                session.query(Source)
                .options(
                    joinedload(Source.linked_study),
                    joinedload(Source.avatar),
                    joinedload(Source.style),
                )
                .filter_by(fk_linked_study=study_id)
                .all()
            )
            session.expunge_all()

        return sources

    @handle_db_query_exceptions(empty_return=dict)
    async def query_study_comments_and_posts_raw(self, study_id: str) -> Dict[str, Any]:
        """
        Query all the comments, posts, and sources associated with a study.

        :param study_id: The ID of the study.
        :type study_id: str
        :return: A dictionary containing the study's posts, comments, and sources. Keys["posts", "comments", "sources"]

        :rtype: Dict[str, Any]
        """
        posts_task = self.query_posts_list_by_study_as_dict(study_id)
        comments_task = self.query_comments_list_by_study(study_id)
        sources_task = self.query_sources_list_by_study(study_id)

        _posts, _comments, _sources = await asyncio.gather(posts_task, comments_task, sources_task)

        return {"posts": _posts, "comments": _comments, "sources": _sources}

    async def update_study_enabled(self, parameters: dict):
        with self.session(True) as session:
            study_id = parameters["id"]
            study = session.query(Study).filter_by(id=study_id).one_or_none()
            if study:
                study.enabled = parameters["enabled"]
                study.last_modified_time = parameters["last_modified_time"]
                logger.info(
                    f"Study:[{study_id}], has been set to {study.enabled}."
                )
            else:
                logger.warning(
                    f"Trying to update study:[{study_id}], but the entry does not exists int the database."
                )

    def generate_debug_test_user(self):
        with self.session() as session:
            # Specify the model to query
            user = session.query(AdminUser).filter_by(username="test").one_or_none()
            if not user:
                new_user = AdminUser(
                    id=self.generate_uuid(), username="test", email="test@test.com"
                )
                new_user.set_password("test")
                session.add(new_user)
                session.commit()
                logger.info(f"Created new user: {new_user}")
            else:
                logger.info(f"User {user.username} already exists.")

    def delete_study(self, study_id: str):
        # @todo: Foreign key constraints lock the deletion. Probably need a db changes: see backpopulate and cascade delete.
        # @todo: link that to the deletion of images from the Blob storage.
        try:
            with self.session(True) as session:
                logger.info(f"Querying study {study_id}...")
                study = session.query(Study).filter_by(id=study_id).one_or_none()

                if study:
                    logger.info(f"Deleting posts for study {study_id}...")
                    session.query(Post).filter_by(fk_linked_study=study_id).delete(synchronize_session=False)

                    logger.info(f"Deleting comments for study {study_id}...")
                    session.query(Comment).filter(
                        Comment.linked_post.has(fk_linked_study=study_id)
                    ).delete(synchronize_session=False)

                    logger.info(f"Deleting sources for study {study_id}...")
                    session.query(Source).filter_by(fk_linked_study=study_id).delete(synchronize_session=False)

                    logger.info(f"Deleting study {study_id}...")
                    session.delete(study)
                    session.commit()
                    logger.info(f"Study {study_id} has been deleted.")
                else:
                    logger.warning(f"Study {study_id} not found in the database.")
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while deleting study with ID {study_id}: {e}")
            session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            session.rollback()
            raise
