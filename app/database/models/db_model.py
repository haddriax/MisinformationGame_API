from datetime import datetime
from enum import Enum

import bcrypt
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy import JSON, TIMESTAMP, Boolean, Column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (Mapped, declarative_base, mapped_column,
                            relationship)

Base = declarative_base()

# Size of the Varchar primary key, applied to every database entries.
primary_key_size = 36


class Status(Enum):
    """
    Enumeration class representing the possible status values of a database entry.

    Each instance of the Status class represents a specific status value. The available status values are:
    - ACTIVE:
        Represents an active status - regular state.
    - ARCHIVED:
        Represents an archived status - inactive but stored, can be used to exclude archived entries form queries.
    - MARKED_FOR_DELETION:
        Represents a status marked for deletion, use it to implements a soft-delete mechanic for admin user.

    Attributes:
        ACTIVE (Status): The active status value.
        ARCHIVED (Status): The archived status value.
        MARKED_FOR_DELETION (Status): The status marked for deletion value.
    """

    ACTIVE = "active"
    ARCHIVED = "archived"
    MARKED_FOR_DELETION = "marked_for_deletion"


class Reactions(Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    SHARE = "share"
    FLAG = "flag"


class DatabaseBaseClass(Base):
    """
    This class is the base class for all database models.
    It provides common properties and attributes for database objects.

    Attributes:
        id (str): The primary key of the database object.
        created_at (datetime): The timestamp representing the time at which the database object was inserted.
        entry_status (SQLEnum(Status)): The status of the database object.

    """

    __abstract__ = True

    id: Mapped[str] = mapped_column(String(primary_key_size), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now,
        nullable=False,
        doc="Time at which the row entry was inserted.",
    )
    entry_status = Column(SQLEnum(Status), default=Status.ACTIVE)


class StudyUiSettings(DatabaseBaseClass):
    """
    Represents the settings for the Study UI.

    This class inherits from the DatabaseBaseClass.

    Attributes:
        display_posts_in_feed (bool): Indicates whether to display posts in the feed or not.
        display_followers (bool): Indicates whether to display followers or not.
        display_credibility (bool): Indicates whether to display credibility or not.
        display_progress (bool): Indicates whether to display progress or not.
        display_number_of_reactions (bool): Indicates whether to display the number of reactions or not.
        allow_multiple_reactions (bool): Indicates whether multiple reactions are allowed or not.

        comment_enable_reaction_like (bool): Indicates whether to enable liking a comment or not.
        comment_enable_reaction_dislike (bool): Indicates whether to enable disliking a comment or not.

        post_enable_reaction_like (bool): Indicates whether to enable liking a post or not.
        post_enable_reaction_dislike (bool): Indicates whether to enable disliking a post or not.
        post_enable_reaction_share (bool): Indicates whether to enable sharing a post or not.
        post_enable_reaction_flag (bool): Indicates whether to enable flagging a post or not.
        post_enable_reaction_skip (bool): Indicates whether to enable skipping a post or not.
    """

    __tablename__ = "study_ui_settings"

    display_posts_in_feed: Mapped[bool] = mapped_column(Boolean)
    display_followers: Mapped[bool] = mapped_column(Boolean)
    display_credibility: Mapped[bool] = mapped_column(Boolean)
    display_progress: Mapped[bool] = mapped_column(Boolean)
    display_number_of_reactions: Mapped[bool] = mapped_column(Boolean)
    allow_multiple_reactions: Mapped[bool] = mapped_column(Boolean)

    comment_enable_reaction_like: Mapped[bool] = mapped_column(Boolean)
    comment_enable_reaction_dislike: Mapped[bool] = mapped_column(Boolean)

    post_enable_reaction_like: Mapped[bool] = mapped_column(Boolean)
    post_enable_reaction_dislike: Mapped[bool] = mapped_column(Boolean)
    post_enable_reaction_share: Mapped[bool] = mapped_column(Boolean)
    post_enable_reaction_flag: Mapped[bool] = mapped_column(Boolean)
    post_enable_reaction_skip: Mapped[bool] = mapped_column(Boolean)


class StudyBasicSettings(DatabaseBaseClass):
    """
    This class represents the basic settings for a study in the database.

    :class:`StudyBasicSettings` inherits from `DatabaseBaseClass`, which provides functionality for interacting with the database.

    Attributes:
        __tablename__ (str): The name of the database table for storing study basic settings.
        name (Mapped[str]): The name of the study (maximum length: 64 characters).
        description (Mapped[str]): The description of the study.
        prompt (Mapped[str]): The prompt for the study.
        length (Mapped[int]): The length of the study.
        require_comments (Mapped[str]): Flag indicating whether comments are required for the study.
        require_reactions (Mapped[bool]): Flag indicating whether reactions are required for the study.
        require_identification (Mapped[bool]): Flag indicating whether identification is required for the study.
    """

    __tablename__ = "study_basic_settings"

    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    prompt: Mapped[str] = mapped_column(Text)
    length: Mapped[int] = mapped_column(Integer)
    require_comments: Mapped[str] = mapped_column(String(16))
    require_reactions: Mapped[bool] = mapped_column(Boolean)
    require_identification: Mapped[bool] = mapped_column(Boolean)


class StudyAdvancedSettings(DatabaseBaseClass):
    """Represents the advanced settings for a study.

    :ivar minimum_comment_length: The minimum length required for a comment.
    :vartype minimum_comment_length: int

    :ivar prompt_delay_seconds: The delay in seconds before a prompt is shown.
    :vartype prompt_delay_seconds: float

    :ivar react_delay_seconds: The delay in seconds before a reaction is required.
    :vartype react_delay_seconds: float

    :ivar gen_completion_code: Whether to generate completion codes.
    :vartype gen_completion_code: bool

    :ivar completion_code_digits: The number of digits in the completion code.
    :vartype completion_code_digits: int

    :ivar gen_random_default_avatars: Whether to generate random default avatars.
    :vartype gen_random_default_avatars: bool
    """

    __tablename__ = "study_advanced_settings"

    minimum_comment_length: Mapped[int] = mapped_column(Integer)
    prompt_delay_seconds: Mapped[float] = mapped_column(Float)
    react_delay_seconds: Mapped[float] = mapped_column(Float)
    gen_completion_code: Mapped[bool] = mapped_column(Boolean)
    completion_code_digits: Mapped[int] = mapped_column(Integer)
    gen_random_default_avatars: Mapped[bool] = mapped_column(Boolean)


class StudyPagesSettings(DatabaseBaseClass):
    """

    This class represents the settings for a study pages in a database.

    :class:`~StudyPagesSettings` is a subclass of :class:`~DatabaseBaseClass` and is mapped to the "study_pages_settings" table in the database.

    Attributes:
        pre_intro (str): The content of the pre-introduction page.
        pre_intro_delay_seconds (int): The delay in seconds before the pre-introduction page is shown.
        rules (str): The content of the rules page.
        rules_delay_seconds (float): The delay in seconds before the rules page is shown.
        post_intro (str): The content of the post-introduction page.
        post_intro_delay_seconds (float): The delay in seconds before the post-introduction page is shown.
        debrief (str): The content of the debrief page.

    Note:
        This class does not include example code, author information, or version information.

    """

    __tablename__ = "study_pages_settings"
    pre_intro: Mapped[str] = mapped_column(Text)
    pre_intro_delay_seconds: Mapped[int] = mapped_column(Integer)
    rules: Mapped[str] = mapped_column(Text)
    rules_delay_seconds: Mapped[float] = mapped_column(Float)
    post_intro: Mapped[str] = mapped_column(Text)
    post_intro_delay_seconds: Mapped[float] = mapped_column(Float)
    debrief: Mapped[str] = mapped_column(Text)


class AdminUser(DatabaseBaseClass):
    """Represents an admin user in the system.

    Inherits from the DatabaseBaseClass.

    Attributes:
        first_name (str): The first name of the admin user.
        last_name (str): The last name of the admin user.
        username (str): The username of the admin user.
        email (str): The email address of the admin user.
        password_hash (str): The hashed password of the admin user.
        active (bool): Indicates if the admin user is active or not.

    Methods:
        __repr__(): Returns a string representation of the admin user.
        is_active(): Returns whether the admin user is active or not.
        set_password(password): Sets the password for the admin user.
        check_password(password): Checks if the provided password matches the admin user's password.

    """

    __tablename__ = "admin_users"

    first_name = mapped_column(String(100))
    last_name = mapped_column(String(100))
    username = mapped_column(String(64), unique=True, index=True)
    email = mapped_column(String(120), unique=True, index=True)
    password_hash = mapped_column(String(512))
    active = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def is_active(self):
        return self.active

    def set_password(self, password):
        self.password_hash = str(
            bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt()), "utf-8"
        )

    def check_password(self, password):
        return bcrypt.checkpw(
            bytes(password, "utf-8"), bytes(self.password_hash, "utf-8")
        )


class PostSelectionMethod(DatabaseBaseClass):
    """
    The PostSelectionMethod class is a subclass of the DatabaseBaseClass and represents a post-selection method. It defines the necessary attributes and methods for interacting with the "post_selection_methods" table in the database.

    Attributes:
        __tablename__ (str): The name of the table in the database.
        type (Mapped[str]): The type of the post-selection method.
        linear_relationship_slope (Mapped[float]): The slope of the linear relationship associated with the method.
        linear_relationship_intercept (Mapped[float]): The intercept of the linear relationship associated with the method.
    """

    __tablename__ = "post_selection_methods"
    type: Mapped[str] = mapped_column(String(32), default="credibility")
    linear_relationship_slope: Mapped[float] = mapped_column(Float)
    linear_relationship_intercept: Mapped[float] = mapped_column(Float)


class Study(DatabaseBaseClass):
    """
    Represents a study in the database.

    Attributes:
        __tablename__ (str): The name of the table for studies.
        fk_ui_settings (Mapped[str]): The foreign key to the UI settings table.
        fk_basic_settings (Mapped[str]): The foreign key to the basic settings table.
        fk_advanced_settings (Mapped[str]): The foreign key to the advanced settings table.
        fk_pages_settings (Mapped[str]): The foreign key to the pages settings table.
        fk_opened_by (Mapped[str]): The foreign key to the opened by user table.
        fk_closed_by (Mapped[str]): The foreign key to the closed by user table.
        fk_created_by (Mapped[str]): The foreign key to the created by user table.
        fk_post_selection_methods (Mapped[str]): The foreign key to the post selection methods table.
        enabled (Mapped[bool]): Indicates if the study is enabled.
        opened_at (Mapped[datetime]): The timestamp when the study was opened.
        closed_at (Mapped[datetime]): The timestamp when the study was closed.
        last_modified_time (Mapped[int]): The last modified time of the study.
        result_last_download_time (Mapped[int]): The last download time of the study result.
        fk_result_last_download_by (Mapped[str]): The foreign key to the user who downloaded the study result.

    Relationships:
        basic_settings (relationship): The relationship to the basic settings table.
        advanced_settings (relationship): The relationship to the advanced settings table.
        pages_settings (relationship): The relationship to the pages settings table.
        ui_settings (relationship): The relationship to the UI settings table.
        post_selection_methods (relationship): The relationship to the post selection methods table.
        opened_by (relationship): The relationship to the user who opened the study.
        closed_by (relationship): The relationship to the user who closed the study.
        created_by (relationship): The relationship to the user who created the study.
        result_last_download_by (relationship): The relationship to the user who last downloaded the study result.

    Methods:
        get_by_id(session, study_id): Retrieves a study by its ID from the database.

    """

    __tablename__ = "studies"

    fk_ui_settings: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(StudyUiSettings.__tablename__)),
    )
    fk_basic_settings: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(StudyBasicSettings.__tablename__)),
    )
    fk_advanced_settings: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(StudyAdvancedSettings.__tablename__)),
    )
    fk_pages_settings: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(StudyPagesSettings.__tablename__)),
        nullable=True,
    )
    fk_opened_by: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(AdminUser.__tablename__)),
        nullable=True,
        default=None,
    )
    fk_closed_by: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(AdminUser.__tablename__)),
        nullable=True,
        default=None,
    )
    fk_created_by: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(AdminUser.__tablename__)),
        nullable=True,
        default=None,
    )
    fk_post_selection_methods: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(PostSelectionMethod.__tablename__)),
    )
    enabled: Mapped[bool] = mapped_column(Boolean)
    opened_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True, default=None)
    closed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True, default=None)
    last_modified_time: Mapped[int] = mapped_column(
        Integer, nullable=True, default=None
    )
    result_last_download_time: Mapped[int] = mapped_column(
        Integer, nullable=True, default=None
    )
    fk_result_last_download_by: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(AdminUser.__tablename__)),
        nullable=True,
        default=None,
    )

    basic_settings = relationship(
        StudyBasicSettings.__name__, foreign_keys=fk_basic_settings
    )
    advanced_settings = relationship(
        StudyAdvancedSettings.__name__, foreign_keys=fk_advanced_settings
    )
    pages_settings = relationship(
        StudyPagesSettings.__name__, foreign_keys=fk_pages_settings
    )
    ui_settings = relationship(StudyUiSettings.__name__, foreign_keys=fk_ui_settings)
    post_selection_methods = relationship(
        PostSelectionMethod.__name__, foreign_keys=fk_post_selection_methods
    )
    opened_by = relationship(AdminUser.__name__, foreign_keys=fk_opened_by)
    closed_by = relationship(AdminUser.__name__, foreign_keys=fk_closed_by)
    created_by = relationship(AdminUser.__name__, foreign_keys=fk_created_by)
    result_last_download_by = relationship(
        AdminUser.__name__, foreign_keys=fk_result_last_download_by
    )

    @staticmethod
    def get_by_id(session, study_id):
        try:
            query_object = (
                session.query(Study)
                .filter(Study.id == study_id)
                .join(StudyBasicSettings)
                .join(StudyAdvancedSettings)
                .join(StudyUiSettings)
                .join(StudyPagesSettings)
                .join(AdminUser, onclause=Study.fk_created_by == AdminUser.id)
            )
        except SQLAlchemyError as e:
            error = str(e)
            print(error)
            return None
        return query_object.first()


class Avatar(DatabaseBaseClass):
    """

    :class: Avatar

    The Avatar class represents an avatar in the database.

    Inherits From:
        - DatabaseBaseClass

    Attributes:
        - `__tablename__` (str): The name of the database table for avatars.
        - `type` (str): The type of the avatar.

    """

    __tablename__ = "avatar"
    type: Mapped[str] = mapped_column(String(6))


class SourceStyle(DatabaseBaseClass):
    """
    Represents a source style in the database.

    :cvar __tablename__: The name of the database table.
    :type __tablename__: str

    :ivar background_color: The background color of the source style.
    :vartype background_color: str
    """

    __tablename__ = "source_style"
    background_color: Mapped[str] = mapped_column(String(8))


class Source(DatabaseBaseClass):
    """This class represents a source in the database.

    Attributes:
        name (str): The name of the source.
        file_name (str): The name of the file associated with the source.
        max_posts (int): The maximum number of posts allowed for the source.
        true_post_percentage (int): The percentage of true posts for the source.
        fk_avatar (str): The foreign key that references the avatar associated with the source.
        fk_linked_study (str): The foreign key that references the linked study associated with the source.
        followers (int): The number of followers for the source.
        followers_mean (int): The mean value of followers for the source.
        followers_std_deviation (float): The standard deviation of followers for the source.
        followers_skew_shape (int): The skew shape of followers for the source.
        followers_min (int): The minimum number of followers for the source.
        followers_maw (int): The maximum number of followers allowed for the source.
        credibility (int): The credibility score of the source.
        credibility_mean (int): The mean value of credibility score for the source.
        credibility_std_deviation (float): The standard deviation of credibility score for the source.
        credibility_skew_shape (int): The skew shape of credibility score for the source.
        credibility_min (int): The minimum credibility score for the source.
        credibility_maw (int): The maximum credibility score allowed for the source.
        fk_style (str): The foreign key that references the source style associated with the source.
        avatar (Avatar): The avatar associated with the source.
        linked_study (Study): The linked study associated with the source.
        style (SourceStyle): The source style associated with the source.
    """

    __tablename__ = "sources"
    name: Mapped[str] = mapped_column(String(64))
    file_name: Mapped[str] = mapped_column(String(64), nullable=True, default=None)
    max_posts: Mapped[int] = mapped_column(Integer, default=-1)
    true_post_percentage: Mapped[int] = mapped_column(Integer)
    fk_avatar: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(Avatar.__tablename__)),
        nullable=True,
    )
    fk_linked_study: Mapped[str] = mapped_column(
        String(primary_key_size), ForeignKey("{}.id".format(Study.__tablename__))
    )

    followers: Mapped[int] = mapped_column(Integer, default=0)
    followers_mean: Mapped[int] = mapped_column(Integer)
    followers_std_deviation: Mapped[float] = mapped_column(Float, default=0.5)
    followers_skew_shape: Mapped[int] = mapped_column(Integer)
    followers_min: Mapped[int] = mapped_column(Integer, default=0)
    followers_maw: Mapped[int] = mapped_column(Integer, default=250)
    credibility: Mapped[int] = mapped_column(Integer, default=0)
    credibility_mean: Mapped[int] = mapped_column(Integer)
    credibility_std_deviation: Mapped[float] = mapped_column(Float, default=0.5)
    credibility_skew_shape: Mapped[int] = mapped_column(Integer)
    credibility_min: Mapped[int] = mapped_column(Integer, default=0)
    credibility_maw: Mapped[int] = mapped_column(Integer, default=100)

    fk_style: Mapped[str] = mapped_column(
        String(primary_key_size), ForeignKey("{}.id".format(SourceStyle.__tablename__))
    )

    avatar = relationship(Avatar.__name__)
    linked_study = relationship(Study.__name__)
    style = relationship(SourceStyle.__name__)


class Participant(DatabaseBaseClass):
    """
    Participant represents a participant in a study.

    Attributes:
        ms_id (str): The unique ID of the participant in the system.
        session_id (str): The ID of the session that the participant is a part of.
        username (str): The username of the participant.
        nb_follower (int): The number of followers the participant has.
        credibility_score (int): The credibility score of the participant.
        game_start_time (datetime): The start time of the participant's game session.
        game_finish_time (datetime): The finish time of the participant's game session.
        fk_linked_study (str): The foreign key linking the participant to a study.
        fk_avatar (str): The foreign key linking the participant to an avatar.

    Relationships:
        linked_study (Study): The study that the participant is linked to.
        avatar (Avatar): The avatar that the participant is linked to.
    """

    __tablename__ = "participants"

    ms_id: Mapped[str] = mapped_column(String(32))
    session_id: Mapped[str] = mapped_column(String(16))
    username: Mapped[str] = mapped_column(String(32))
    nb_follower: Mapped[int] = mapped_column(Integer)
    credibility_score: Mapped[int] = mapped_column(Integer)
    game_start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=True, default=None
    )
    game_finish_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=True, default=None
    )

    fk_linked_study: Mapped[str] = mapped_column(
        String(primary_key_size), ForeignKey("{}.id".format(Study.__tablename__))
    )
    fk_avatar: Mapped[str] = mapped_column(
        String(primary_key_size),
        ForeignKey("{}.id".format(Avatar.__tablename__)),
        nullable=True,
    )

    linked_study = relationship(Study.__name__)
    avatar = relationship(Avatar.__name__)


class Post(DatabaseBaseClass):
    """
    Represents a post in the database.

    Attributes:
        fk_linked_study (str): Foreign key linking the post to a study.
        headline (str): The headline of the post.
        content (str): The content of the post.
        is_true (bool): Indicates if the post is true.

        changes_to_follower_on_like_mean (float): Mean of changes to follower count when a post is liked.
        changes_to_follower_on_like_std_deviation (float): Standard deviation of changes to follower count
        when a post is liked.
        changes_to_follower_on_like_skewShape (int): Skew shape of changes to follower count distribution
        when a post is liked.
        changes_to_follower_on_like_min (int): Minimum changes to follower count when a post is liked.
        changes_to_follower_on_like_max (int): Maximum changes to follower count when a post is liked.

        changes_to_follower_on_dislike_mean (float): Mean of changes to follower count when a post is disliked.
        changes_to_follower_on_dislike_std_deviation (float): Standard deviation of changes to follower count
        when a post is disliked.
        changes_to_follower_on_dislike_skewShape (int): Skew shape of changes to follower count distribution
        when a post is disliked.
        changes_to_follower_on_dislike_min (int): Minimum changes to follower count when a post is disliked.
        changes_to_follower_on_dislike_max (int): Maximum changes to follower count when a post is disliked.

        changes_to_follower_on_share_mean (float): Mean of changes to follower count when a post is shared.
        changes_to_follower_on_share_std_deviation (float): Standard deviation of changes to follower count
        when a post is shared.
        changes_to_follower_on_share_skewShape (int): Skew shape of changes to follower count distribution
        when a post is shared.
        changes_to_follower_on_share_min (int): Minimum changes to follower count when a post is shared.
        changes_to_follower_on_share_max (int): Maximum changes to follower count when a post is shared.

        changes_to_follower_on_flag_mean (float): Mean of changes to follower count when a post is flagged.
        changes_to_follower_on_flag_std_deviation (float): Standard deviation of changes to follower count
        when a post is flagged.
        changes_to_follower_on_flag_skewShape (int): Skew shape of changes to follower count distribution
        when a post is flagged.
        changes_to_follower_on_flag_min (int): Minimum changes to follower count when a post is flagged.
        changes_to_follower_on_flag_max (int): Maximum changes to follower count when a post is flagged.

        changes_to_credibility_on_like_mean (float): Mean of changes to credibility score when a post is liked.
        changes_to_credibility_on_like_std_deviation (float): Standard deviation of changes to credibility score
        when a post is liked.
        changes_to_credibility_on_like_skewShape (int): Skew shape of changes to credibility score distribution
        when a post is liked.
        changes_to_credibility_on_like_min (int): Minimum changes to credibility score when a post is liked.
        changes_to_credibility_on_like_max (int): Maximum changes to credibility score when a post is liked.

        changes_to_credibility_on_dislike_mean (float): Mean of changes to credibility score when a post is disliked.
        changes_to_credibility_on_dislike_std_deviation (float): Standard deviation of changes to credibility score
        when a post is disliked.
        changes_to_credibility_on_dislike_skewShape (int): Skew shape of changes to credibility score distribution
        when a post is disliked.
        changes_to_credibility_on_dislike_min (int): Minimum changes to credibility score when a post is disliked.
        changes_to_credibility_on_dislike_max (int): Maximum changes to credibility score when a post is disliked.

        changes_to_credibility_on_share_mean (float): Mean of changes to credibility score when a post is shared.
        changes_to_credibility_on_share_std_deviation (float): Standard deviation of changes to credibility score
        when a post is shared.
        changes_to_credibility_on_share_skewShape (int): Skew shape of changes to credibility score distribution
        when a post is shared.
        changes_to_credibility_on_share_min (int): Minimum changes to credibility score when a post is shared.
        changes_to_credibility_on_share_max (int): Maximum changes to credibility score when a post is shared.

        changes_to_credibility_on_flag_mean (float): Mean of changes to credibility score when a post is flagged.
        changes_to_credibility_on_flag_std_deviation (float): Standard deviation of changes to"""

    __tablename__ = "posts"

    fk_linked_study: Mapped[str] = mapped_column(
        String(primary_key_size), ForeignKey("{}.id".format(Study.__tablename__))
    )
    headline: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    is_true: Mapped[bool] = mapped_column(Boolean)

    changes_to_follower_on_like_mean: Mapped[float] = mapped_column(Float, default=1.0)
    changes_to_follower_on_like_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    changes_to_follower_on_like_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_follower_on_like_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_follower_on_like_max: Mapped[int] = mapped_column(
        Integer, default=100
    )

    changes_to_follower_on_dislike_mean: Mapped[float] = mapped_column(
        Float, default=-1
    )
    changes_to_follower_on_dislike_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    changes_to_follower_on_dislike_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_follower_on_dislike_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_follower_on_dislike_max: Mapped[int] = mapped_column(
        Integer, default=100
    )

    changes_to_follower_on_share_mean: Mapped[float] = mapped_column(Float, default=5)
    changes_to_follower_on_share_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    changes_to_follower_on_share_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_follower_on_share_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_follower_on_share_max: Mapped[int] = mapped_column(
        Integer, default=100
    )

    changes_to_follower_on_flag_mean: Mapped[float] = mapped_column(Float, default=-5)
    changes_to_follower_on_flag_std_deviation: Mapped[float] = mapped_column(
        Float, default=0
    )
    changes_to_follower_on_flag_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_follower_on_flag_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_follower_on_flag_max: Mapped[int] = mapped_column(
        Integer, default=100
    )

    changes_to_credibility_on_like_mean: Mapped[float] = mapped_column(
        Float, default=1.0
    )
    changes_to_credibility_on_like_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    changes_to_credibility_on_like_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_credibility_on_like_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_credibility_on_like_max: Mapped[int] = mapped_column(
        Integer, default=100
    )

    changes_to_credibility_on_dislike_mean: Mapped[float] = mapped_column(
        Float, default=-1
    )
    changes_to_credibility_on_dislike_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    changes_to_credibility_on_dislike_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_credibility_on_dislike_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_credibility_on_dislike_max: Mapped[int] = mapped_column(
        Integer, default=100
    )

    changes_to_credibility_on_share_mean: Mapped[float] = mapped_column(
        Float, default=5
    )
    changes_to_credibility_on_share_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    changes_to_credibility_on_share_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_credibility_on_share_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_credibility_on_share_max: Mapped[int] = mapped_column(
        Integer, default=100
    )

    changes_to_credibility_on_flag_mean: Mapped[float] = mapped_column(
        Float, default=-5
    )
    changes_to_credibility_on_flag_std_deviation: Mapped[float] = mapped_column(
        Float, default=0
    )
    changes_to_credibility_on_flag_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    changes_to_credibility_on_flag_min: Mapped[int] = mapped_column(
        Integer, default=-100
    )
    changes_to_credibility_on_flag_max: Mapped[int] = mapped_column(
        Integer, default=100
    )
    number_of_reactions_on_like_mean: Mapped[float] = mapped_column(
        Float, default=1.0
    )
    number_of_reactions_on_like_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    number_of_reactions_on_like_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    number_of_reactions_on_like_min: Mapped[int] = mapped_column(
        Integer, default=-1000
    )
    number_of_reactions_on_like_max: Mapped[int] = mapped_column(
        Integer, default=1000
    )
    number_of_reactions_on_dislike_mean: Mapped[float] = mapped_column(
        Float, default=-1
    )
    number_of_reactions_on_dislike_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    number_of_reactions_on_dislike_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    number_of_reactions_on_dislike_min: Mapped[int] = mapped_column(
        Integer, default=-10000
    )
    number_of_reactions_on_dislike_max: Mapped[int] = mapped_column(
        Integer, default=1000
    )
    number_of_reactions_on_share_mean: Mapped[float] = mapped_column(
        Float, default=5
    )
    number_of_reactions_on_share_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    number_of_reactions_on_share_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    number_of_reactions_on_share_min: Mapped[int] = mapped_column(
        Integer, default=-1000
    )
    number_of_reactions_on_share_max: Mapped[int] = mapped_column(
        Integer, default=1000
    )
    number_of_reactions_on_flag_mean: Mapped[float] = mapped_column(
        Float, default=-5
    )
    number_of_reactions_on_flag_std_deviation: Mapped[float] = mapped_column(
        Float, default=0
    )
    number_of_reactions_on_flag_skewShape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    number_of_reactions_on_flag_min: Mapped[int] = mapped_column(
        Integer, default=-1000
    )
    number_of_reactions_on_flag_max: Mapped[int] = mapped_column(
        Integer, default=1000
    )

    linked_study = relationship(Study.__name__)


class Comment(DatabaseBaseClass):
    """
    Class Comment

    This class represents a comment in the database.

    Attributes:
        sourceName (Mapped[str]): The source name of the comment.
        message (Mapped[str]): The message of the comment.
        number_of_reaction_like_mean (Mapped[float]): The mean number of likes for the comment.
        number_of_reaction_like_std_deviation (Mapped[float]): The standard deviation of the number of likes.
        number_of_reaction_like_skewShape (Mapped[int]): The skewness shape of the number of likes.
        number_of_reaction_like_min (Mapped[int]): The minimum number of likes.
        number_of_reaction_like_max (Mapped[int]): The maximum number of likes.
        number_of_reaction_dislike_mean (Mapped[float]): The mean number of dislikes.
        number_of_reaction_dislike_std_deviation (Mapped[float]): The standard deviation of the number of dislikes.
        number_of_reaction_dislike_skew_shape (Mapped[int]): The skewness shape of the number of dislikes.
        number_of_reaction_dislike_min (Mapped[int]): The minimum number of dislikes.
        number_of_reaction_dislike_max (Mapped[int]): The maximum number of dislikes.
        number_of_reaction_share_mean (Mapped[float]): The mean number of shares.
        number_of_reaction_share_std_deviation (Mapped[float]): The standard deviation of the number of shares.
        number_of_reaction_share_skew_shape (Mapped[int]): The skewness shape of the number of shares.
        number_of_reaction_share_min (Mapped[int]): The minimum number of shares.
        number_of_reaction_share_max (Mapped[int]): The maximum number of shares.
        number_of_reaction_flags_mean (Mapped[float]): The mean number of flags.
        number_of_reaction_flags_std_deviation (Mapped[float]): The standard deviation of the number of flags.
        number_of_reaction_flags_skew_shape (Mapped[int]): The skewness shape of the number of flags.
        number_of_reaction_flags_min (Mapped[int]): The minimum number of flags.
        number_of_reaction_flags_max (Mapped[int]): The maximum number of flags.
        fk_linked_post (Mapped[str]): The foreign key of the linked post.
        linked_post: The linked post object associated with the comment.

    """

    __tablename__ = "comments"

    sourceName: Mapped[str] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text)
    number_of_reaction_like_mean: Mapped[float] = mapped_column(Float, default=0)
    number_of_reaction_like_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    number_of_reaction_like_skewShape: Mapped[int] = mapped_column(Integer, default=0)
    number_of_reaction_like_min: Mapped[int] = mapped_column(Integer, default=0)
    number_of_reaction_like_max: Mapped[int] = mapped_column(Integer, default=0)

    number_of_reaction_dislike_mean: Mapped[float] = mapped_column(Float, default=0)
    number_of_reaction_dislike_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    number_of_reaction_dislike_skew_shape: Mapped[int] = mapped_column(
        Integer, default=0
    )
    number_of_reaction_dislike_min: Mapped[int] = mapped_column(Integer, default=0)
    number_of_reaction_dislike_max: Mapped[int] = mapped_column(Integer, default=0)

    number_of_reaction_share_mean: Mapped[float] = mapped_column(Float, default=0)
    number_of_reaction_share_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    number_of_reaction_share_skew_shape: Mapped[int] = mapped_column(Integer, default=0)
    number_of_reaction_share_min: Mapped[int] = mapped_column(Integer, default=0)
    number_of_reaction_share_max: Mapped[int] = mapped_column(Integer, default=0)

    number_of_reaction_flags_mean: Mapped[float] = mapped_column(Float, default=0)
    number_of_reaction_flags_std_deviation: Mapped[float] = mapped_column(
        Float, default=0.5
    )
    number_of_reaction_flags_skew_shape: Mapped[int] = mapped_column(Integer, default=0)
    number_of_reaction_flags_min: Mapped[int] = mapped_column(Integer, default=0)
    number_of_reaction_flags_max: Mapped[int] = mapped_column(Integer, default=0)

    fk_linked_post: Mapped[str] = mapped_column(
        String(primary_key_size), ForeignKey("{}.id".format(Post.__tablename__))
    )

    linked_post = relationship(Post.__name__)


# class PostInteraction(DatabaseBaseClass):
#     """
#
#     :Description: This class represents a database table for storing interactions between participants and posts.
#
#     Attributes:
#         order (int): The order of the interaction.
#         fk_participant_id (str): The foreign key to the participant's ID.
#         fk_post_id (str): The foreign key to the post's ID.
#         reaction_type (str): The type of reaction.
#         flagged (bool): Indicates if the interaction is flagged.
#         shared (bool): Indicates if the interaction is shared.
#         fk_comment_id (str): The foreign key to the comment's ID (nullable).
#         first_time_to_interact_ms (int): The timestamp of the first interaction (in milliseconds).
#         last_interaction_time_ms (int): The timestamp of the last interaction (in milliseconds).
#         user_follower_before (int): The number of followers the participant had before the interaction.
#         user_follower_after (int): The number of followers the participant had after the interaction.
#         user_credibility_before (int): The credibility score of the participant before the interaction.
#         user_credibility_after (int): The credibility score of the participant after the interaction.
#
#     Relationships:
#         participant (:class:`Participant`): The relationship with the :class:`Participant` entity.
#         post (:class:`Post`): The relationship with the :class:`Post` entity.
#         comment (:class:`Comment`): The relationship with the :class:`Comment` entity.
#
#     """
#
#     __tablename__ = "posts_interactions"
#
#     order: Mapped[int] = mapped_column(Integer)
#     fk_participant_id: Mapped[str] = mapped_column(
#         String(primary_key_size), ForeignKey("{}.id".format(Participant.__tablename__))
#     )
#     fk_post_id: Mapped[str] = mapped_column(
#         String(primary_key_size), ForeignKey("{}.id".format(Post.__tablename__))
#     )
#     reaction_type: Mapped[str] = mapped_column(String(8))
#     flagged: Mapped[bool] = mapped_column(Boolean)
#     shared: Mapped[bool] = mapped_column(Boolean)
#     fk_comment_id: Mapped[str] = mapped_column(
#         String(primary_key_size),
#         ForeignKey("{}.id".format(Comment.__tablename__)),
#         nullable=True,
#         default=None,
#     )
#     first_time_to_interact_ms: Mapped[int] = mapped_column(Integer, default=-1)
#     last_interaction_time_ms: Mapped[int] = mapped_column(Integer, default=-1)
#     user_follower_before: Mapped[int] = mapped_column(Integer)
#     user_follower_after: Mapped[int] = mapped_column(Integer)
#     user_credibility_before: Mapped[int] = mapped_column(Integer)
#     user_credibility_after: Mapped[int] = mapped_column(Integer)
#
#     participant = relationship(Participant.__name__)
#     post = relationship(Post.__name__)
#     comment = relationship(Comment.__name__)
#
#
# class CommentInteraction(DatabaseBaseClass):
#     """
#     The `CommentInteraction` class represents a relationship between a comment and a participant in a database.
#
#     Attributes:
#         fk_comment_id (Mapped[str]): The foreign key of the comment.
#         fk_participant_id (Mapped[str]): The foreign key of the participant.
#         reaction_type (Mapped[str]): The type of reaction.
#         first_time_to_interact_ms (Mapped[int]): The timestamp of the first interaction in milliseconds.
#         last_interaction_time_ms (Mapped[int]): The timestamp of the last interaction in milliseconds.
#         comment (Relationship): The relationship to the Comment class.
#         participant (Relationship): The relationship to the Participant class.
#
#     """
#
#     __tablename__ = "comments_interactions"
#
#     fk_comment_id: Mapped[str] = mapped_column(
#         String(primary_key_size), ForeignKey("{}.id".format(Comment.__tablename__))
#     )
#     fk_participant_id: Mapped[str] = mapped_column(
#         String(primary_key_size), ForeignKey("{}.id".format(Participant.__tablename__))
#     )
#     reaction_type: Mapped[str] = mapped_column(String(8))
#     first_time_to_interact_ms: Mapped[int] = mapped_column(Integer)
#     last_interaction_time_ms: Mapped[int] = mapped_column(Integer)
#
#     comment = relationship(Comment.__name__)
#     participant = relationship(Participant.__name__)


class StudyResultFile(DatabaseBaseClass):
    """
    Represents a study result, storing the legacy result as JSON.
    Additional fields are redundant with the JSON, but are useful for sorting and querying the entries without loading
    a whole file.

    Attributes:
        fk_study_ID (Mapped[str]): The foreign key representing the ID of the associated study.
        study_ID: The relationship to the Study class.
        study_mod_time (Mapped[int]): The modification time of the study.
        session_ID (Mapped[str]): The session ID of the study result file.
        study_start_time (Mapped[int]): The start time of the study.
        study_end_time (Mapped[int]): The end time of the study.
        data (Mapped[dict]): The JSON object containing the study result data.
    """

    __tablename__ = "study_results_file"

    fk_study_ID: Mapped[str] = mapped_column(
        String(primary_key_size), ForeignKey("{}.id".format(Study.__tablename__))
    )
    study_ID = relationship(Study.__name__)
    study_mod_time: Mapped[int] = mapped_column(Integer)
    session_ID: Mapped[str] = mapped_column(String(primary_key_size))
    study_start_time: Mapped[int] = mapped_column(Integer)
    study_end_time: Mapped[int] = mapped_column(Integer)

    data: Mapped[dict] = mapped_column(JSON)
