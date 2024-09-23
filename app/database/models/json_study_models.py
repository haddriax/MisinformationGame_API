from typing import List, Optional, Union

from pydantic import BaseModel, Field


class ReactionFullModel(BaseModel):
    """
    Attributes:
        mean (Optional[float]): Defaults to 0.5.
        stdDeviation (Optional[float]): Defaults to 0.5.
        skewShape (Optional[int]): Defaults to 1.
        min (Optional[int]): Defaults to 0.
        max (Optional[int]): Defaults to 1000.
    """
    mean: Optional[float] = Field(default=0.5)
    stdDeviation: Optional[float] = Field(default=0.5)
    skewShape: Optional[int] = Field(default=1)
    min: Optional[int] = Field(default=0)
    max: Optional[int] = Field(default=1000)


class PostModel(BaseModel):
    """
    Attributes:
        id (str)
        headline (str, optional)
        content (str or ContentModel, optional):
            It can be a string or a ContentModel object. Defaults to None.
        isTrue (bool)
        changesToFollowers (ChangesToFollowersModel)
        changesToCredibility (ChangesToCredibilityModel)
        numberOfReactions (NumberOfReactionsModel)
        comments (list of CommentModel, optional): Defaults to None
    """

    class ContentModel(BaseModel):
        """
        Attributes:
            type (Optional[str]): Defaults to None.
        """

        type: Optional[str] = None

    class CommentModel(BaseModel):
        """
        Attributes:
            sourceName (str)
            message (str)
            numberOfReactions (NumberOfReactionsLightModel)
        """

        class NumberOfReactionsLightModel(BaseModel):
            """
            Attributes:
                like (ReactionFullModel)
                dislike (ReactionFullModel)
                flag (Optional[ReactionFullModel]): Defaults to None
                share (Optional[ReactionFullModel]):  Defaults to None
            """

            like: ReactionFullModel
            dislike: ReactionFullModel
            flag: Optional[ReactionFullModel] = None
            share: Optional[ReactionFullModel] = None

        sourceName: str
        message: str
        numberOfReactions: NumberOfReactionsLightModel

    # ___ end CommentModel ___

    class NumberOfReactionsModel(BaseModel):
        """
        Attributes:
            like (ReactionFullModel)
            dislike (ReactionFullModel)
            share (ReactionFullModel)
            flag (ReactionFullModel)
        """

        like: ReactionFullModel
        dislike: ReactionFullModel
        share: ReactionFullModel
        flag: ReactionFullModel

    class ChangesToCredibilityModel(BaseModel):
        """
        Attributes:
            like (ReactionFullModel)
            dislike (ReactionFullModel)
            share (ReactionFullModel)
            flag (ReactionFullModel)
        """

        like: ReactionFullModel
        dislike: ReactionFullModel
        share: ReactionFullModel
        flag: ReactionFullModel

    class ChangesToFollowersModel(BaseModel):
        """
        Attributes:
            like (ReactionFullModel)
            dislike (ReactionFullModel)
            share (ReactionFullModel)
            flag (ReactionFullModel)
        """

        like: ReactionFullModel
        dislike: ReactionFullModel
        share: ReactionFullModel
        flag: ReactionFullModel

    id: str
    headline: Optional[str]
    content: Optional[Union[str, ContentModel]]
    isTrue: bool
    changesToFollowers: ChangesToFollowersModel
    changesToCredibility: ChangesToCredibilityModel
    numberOfReactions: NumberOfReactionsModel
    comments: Optional[List[CommentModel]] = None


class SourcePostSelectionMethodModel(BaseModel):
    """
    Attributes:
        type (str)
        linearRelationship (LinearRelationshipModel)
    """

    class LinearRelationshipModel(BaseModel):
        """
        Represents a linear relationship between two variables.
        The model is defined by its slope and intercept.

        Attributes:
            slope (float)
            intercept (int)
        """

        slope: float
        intercept: int

    type: str
    linearRelationship: LinearRelationshipModel


class SourcesModel(BaseModel):
    """
    Attributes:
        id (str)
        linked_study_id (Optional[str]):  Defaults to None
        file_name (Optional[str]):  Defaults to None
        name (str)
        avatar (Optional[AvatarModel])
        style (StyleModel)
        maxPosts (Optional[int])
        followers (FollowersModel)
        credibility (CredibilityModel)
        truePostPercentage (int)
    """

    class AvatarModel(BaseModel):
        """
        Attributes:
            type (str)
        """

        type: str

    class StyleModel(BaseModel):
        """
        Attributes:
            backgroundColor (str)
        """

        backgroundColor: str

    class FollowersModel(BaseModel):
        """
        Attributes:
            mean (int)
            stdDeviation (int)
            skewShape (int)
            min (int)
            max (int)
        """

        mean: int
        stdDeviation: int
        skewShape: int
        min: int
        max: int

    class CredibilityModel(BaseModel):
        """
        Attributes:
            mean (int)
            stdDeviation (int)
            skewShape (int)
            min (int)
            max (int)
        """

        mean: int
        stdDeviation: int
        skewShape: int
        min: int
        max: int

    id: str
    linked_study_id: Optional[str] = None
    file_name: Optional[str] = None
    name: str
    avatar: Optional[AvatarModel]
    style: StyleModel
    maxPosts: Optional[int]
    followers: FollowersModel
    credibility: CredibilityModel
    truePostPercentage: int


class PagesSettingsModel(BaseModel):
    """
    Attributes:
        preIntro (str)
        preIntroDelaySeconds (int)
        rules (str)
        rulesDelaySeconds (int)
        postIntro (str)
        postIntroDelaySeconds (int)
        debrief (str)
    """

    preIntro: str
    preIntroDelaySeconds: int
    rules: str
    rulesDelaySeconds: int
    postIntro: str
    postIntroDelaySeconds: int
    debrief: str


class AdvancedSettingsModel(BaseModel):
    """
    Model class for advanced settings.

    Attributes:
        minimumCommentLength (int)
        promptDelaySeconds (float)
        reactDelaySeconds (float)
        genCompletionCode (bool)
        completionCodeDigits (int)
        genRandomDefaultAvatars (bool)
    """

    minimumCommentLength: int
    promptDelaySeconds: float
    reactDelaySeconds: float
    genCompletionCode: bool
    completionCodeDigits: int
    genRandomDefaultAvatars: bool


class UiSettingsModel(BaseModel):
    """
    Attributes:
        displayPostsInFeed (bool)
        displayFollowers (bool)
        displayCredibility (bool)
        displayProgress (bool)
        displayNumberOfReactions (bool)
        allowMultipleReactions (bool)
        postEnabledReactions (PostEnabledReactionsModel)
        commentEnabledReactions (CommentEnabledReactionsModel)

    """

    class CommentEnabledReactionsModel(BaseModel):
        """
        Attributes:
            like (bool)
            dislike (bool)
        """
        like: bool
        dislike: bool

    class PostEnabledReactionsModel(BaseModel):
        """
         Attributes:
             like (bool)
             dislike (bool)
             share (bool)
             flag (bool)
             skip (bool)
         """
        like: bool
        dislike: bool
        share: bool
        flag: bool
        skip: bool

    displayPostsInFeed: bool
    displayFollowers: bool
    displayCredibility: bool
    displayProgress: bool
    displayNumberOfReactions: bool
    allowMultipleReactions: bool
    postEnabledReactions: PostEnabledReactionsModel
    commentEnabledReactions: CommentEnabledReactionsModel


class BasicSettingsModel(BaseModel):
    """
    Attributes:
        name (str)
        description (str)
        prompt (str)
        length (int)
        requireComments (str)
        requireReactions (bool)
        requireIdentification (bool)

    """
    name: str
    description: str
    prompt: str
    length: int
    requireComments: str
    requireReactions: bool
    requireIdentification: bool


class JSONStudyModel(BaseModel):
    """
    Class representing the JSON from the API endpoint as a Python object extending Pydantic.BaseModel.

    Attributes:
        id Optional[str]: Defaults to None
        version (int)
        authorID (str)
        authorName (str)
        lastModifiedTime (int)
        enabled (bool)
        basicSettings (BasicSettingsModel)
        uiSettings (UiSettingsModel)
        advancedSettings (AdvancedSettingsModel)
        pagesSettings (PagesSettingsModel)
        sourcePostSelectionMethod (SourcePostSelectionMethodModel)
        sources (List[SourcesModel])
        posts (List[PostsModel])
    """

    id: Optional[str] = None
    version: int
    authorID: str
    authorName: str
    lastModifiedTime: int
    enabled: bool
    basicSettings: BasicSettingsModel
    uiSettings: UiSettingsModel
    advancedSettings: AdvancedSettingsModel
    pagesSettings: PagesSettingsModel
    sourcePostSelectionMethod: SourcePostSelectionMethodModel
    sources: Optional[List[SourcesModel]]
    posts: Optional[List[PostModel]]


class JSONStudyLightModel(BaseModel):
    """
    Represents a JSON object that contains a Study WITHOUT storing Posts are Sources.
    This should be used when only an overview of the Study is needed, or when we want to simply work on settings.
    At this time, this has no uses in the application, but should be envisaged quickly.
    """

    id: str
    version: int
    authorID: str
    authorName: str
    lastModifiedTime: int
    enabled: bool
    basicSettings: BasicSettingsModel
    uiSettings: UiSettingsModel
    advancedSettings: AdvancedSettingsModel
    pagesSettings: PagesSettingsModel
    sourcePostSelectionMethod: SourcePostSelectionMethodModel
