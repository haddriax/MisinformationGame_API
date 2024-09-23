"""This module provides functions to generate study settings and components from a JSON representation
(JSONStudyModel). The generated components can be used to construct a Study object and its related objects such as
posts, comments, sources, avatars, and styles. This Study object can then be inserted in the database"""

from typing import List, Union

from database.database import Database
from database.models.db_model import (Avatar, Comment, Post,
                                      PostSelectionMethod, Source, SourceStyle,
                                      Study, StudyAdvancedSettings,
                                      StudyBasicSettings, StudyPagesSettings,
                                      StudyUiSettings)
from database.models.json_study_models import JSONStudyModel, PostModel


def generate_basic_settings_from_json(study_json: JSONStudyModel) -> StudyBasicSettings:
    """
    :param study_json: JSONStudyModel object containing study configuration in JSON format
    :return: StudyBasicSettings object containing basic settings extracted from the study_json
    """
    basic_settings = StudyBasicSettings(
        id=Database.generate_uuid(),
        name=study_json.basicSettings.name,
        description=study_json.basicSettings.description,
        prompt=study_json.basicSettings.prompt,
        length=study_json.basicSettings.length,
        require_comments=study_json.basicSettings.requireComments,
        require_reactions=study_json.basicSettings.requireReactions,
        require_identification=study_json.basicSettings.requireIdentification,
    )
    return basic_settings


def generate_advanced_settings_from_json(
        study_json: JSONStudyModel,
) -> StudyAdvancedSettings:
    """
    :param study_json: The JSON study model.
    :type study_json: JSONStudyModel
    :return: The advanced settings generated from the JSON study model.
    :rtype: StudyAdvancedSettings
    """
    advanced_settings = StudyAdvancedSettings(
        id=Database.generate_uuid(),
        minimum_comment_length=study_json.advancedSettings.minimumCommentLength,
        prompt_delay_seconds=study_json.advancedSettings.promptDelaySeconds,
        react_delay_seconds=study_json.advancedSettings.reactDelaySeconds,
        gen_completion_code=study_json.advancedSettings.genCompletionCode,
        completion_code_digits=study_json.advancedSettings.completionCodeDigits,
        gen_random_default_avatars=study_json.advancedSettings.genRandomDefaultAvatars,
    )
    return advanced_settings


def generate_ui_settings_from_json(study_json: JSONStudyModel) -> StudyUiSettings:
    """
    :param study_json: A JSONStudyModel object representing the study data
    :return: A StudyUiSettings object generated from the study_json
    """
    ui_settings = StudyUiSettings(
        id=Database.generate_uuid(),
        display_posts_in_feed=study_json.uiSettings.displayPostsInFeed,
        display_followers=study_json.uiSettings.displayFollowers,
        display_credibility=study_json.uiSettings.displayCredibility,
        display_progress=study_json.uiSettings.displayProgress,
        display_number_of_reactions=study_json.uiSettings.displayNumberOfReactions,
        allow_multiple_reactions=study_json.uiSettings.allowMultipleReactions,
        comment_enable_reaction_like=study_json.uiSettings.commentEnabledReactions.like,
        comment_enable_reaction_dislike=study_json.uiSettings.commentEnabledReactions.dislike,
        post_enable_reaction_like=study_json.uiSettings.postEnabledReactions.like,
        post_enable_reaction_dislike=study_json.uiSettings.postEnabledReactions.dislike,
        post_enable_reaction_share=study_json.uiSettings.postEnabledReactions.share,
        post_enable_reaction_flag=study_json.uiSettings.postEnabledReactions.flag,
        post_enable_reaction_skip=study_json.uiSettings.postEnabledReactions.skip,
    )
    return ui_settings


def generate_pages_settings_from_json(study_json: JSONStudyModel) -> StudyPagesSettings:
    """
    :param study_json: JSONStudyModel object containing study settings
    :return: StudyPagesSettings object generated from study_json
    """
    pages_settings = StudyPagesSettings(
        id=Database.generate_uuid(),
        pre_intro=study_json.pagesSettings.preIntro,
        pre_intro_delay_seconds=study_json.pagesSettings.preIntroDelaySeconds,
        rules=study_json.pagesSettings.rules,
        rules_delay_seconds=study_json.pagesSettings.rulesDelaySeconds,
        post_intro=study_json.pagesSettings.postIntro,
        post_intro_delay_seconds=study_json.pagesSettings.postIntroDelaySeconds,
        debrief=study_json.pagesSettings.debrief,
    )
    return pages_settings


def generate_posts_selection_methods_from_json(
        study_json: JSONStudyModel,
) -> PostSelectionMethod:
    """
    :param study_json: A JSONStudyModel object containing the study information.
    :return: A PostSelectionMethods object generated from the study_json.

    """
    post_selection_methods = PostSelectionMethod(
        id=Database.generate_uuid(),
        type=study_json.sourcePostSelectionMethod.type,
        linear_relationship_slope=study_json.sourcePostSelectionMethod.linearRelationship.slope,
        linear_relationship_intercept=study_json.sourcePostSelectionMethod.linearRelationship.intercept,
    )
    return post_selection_methods


def generate_study_with_fk(
        study_json: JSONStudyModel,
        basic_settings: StudyBasicSettings,
        advanced_settings: StudyAdvancedSettings,
        post_selection_methods: PostSelectionMethod,
        ui_settings: StudyUiSettings,
        pages_settings: StudyPagesSettings,
) -> Study:
    """
    Generate a study object with foreign key relationships, creating the empty object and linking the foreign keys by ID

    :param study_json: The JSON representation of the study.
    :param basic_settings: The basic settings of the study.
    :param advanced_settings: The advanced settings of the study.
    :param post_selection_methods: The post selection methods of the study.
    :param ui_settings: The UI settings of the study.
    :param pages_settings: The pages settings of the study.
    :return: The generated study object.
    """
    study = Study(
        id=study_json.id,
        enabled=study_json.enabled,
        fk_basic_settings=basic_settings.id,
        fk_advanced_settings=advanced_settings.id,
        fk_post_selection_methods=post_selection_methods.id,
        fk_ui_settings=ui_settings.id,
        fk_pages_settings=pages_settings.id,
    )
    return study


def generate_avatar(source_avatar):
    return Avatar(
        id=Database.generate_uuid(),
        type=source_avatar.type,
    )


def generate_style(source_style):
    return SourceStyle(
        id=Database.generate_uuid(),
        background_color=source_style.backgroundColor,
    )


def get_avatar_id_for_source():
    return Database.generate_uuid()


def generate_sources_as_dict(
        study_json: JSONStudyModel,
) -> List[dict[str, Union[Source, Avatar, SourceStyle]]]:
    """
    Generate all the sources from the JSONStudyModel object.
    Create new avatar and new style for each of them.
    ID of avatar and style are generated and inserted into each source as Foreign Key.
    :param study_json: A JSON model representing a study.
    :return: A list of dictionaries containing information about each source, including the source itself, its avatar,
    and style. {'source', 'avatar', 'style'}
    """
    result = []

    for source in study_json.sources:
        avatar = generate_avatar(source.avatar)
        style = generate_style(source.style)
        s = Source(
            id=Database.generate_uuid(),
            name=source.name,
            max_posts=source.maxPosts,
            true_post_percentage=source.truePostPercentage,
            followers=500,
            followers_mean=source.followers.mean,
            followers_std_deviation=source.followers.stdDeviation,
            followers_skew_shape=source.followers.skewShape,
            credibility=500,
            credibility_mean=source.credibility.mean,
            credibility_std_deviation=source.credibility.stdDeviation,
            credibility_skew_shape=source.credibility.skewShape,
            fk_avatar=avatar.id,
            fk_style=style.id,
        )
        result.append({"source": s, "avatar": avatar, "style": style})

    return result


def generate_sources_as_lists(
        study_json: JSONStudyModel, linked_study: Study
) -> {List[Source], List[Avatar], List[SourceStyle]}:
    avatars = []
    sources = []
    source_styles = []
    for source in study_json.sources:
        # We generate avatar and style here, because we need their ID.
        avatar = generate_avatar(source.avatar) if source.avatar is not None else None

        style = generate_style(source.style)

        s = Source(
            id=Database.generate_uuid(),
            file_name=source.id,
            name=source.name,
            max_posts=source.maxPosts,
            true_post_percentage=source.truePostPercentage,
            followers=500,
            followers_mean=source.followers.mean,
            followers_std_deviation=source.followers.stdDeviation,
            followers_skew_shape=source.followers.skewShape,
            credibility=500,
            credibility_mean=source.credibility.mean,
            credibility_std_deviation=source.credibility.stdDeviation,
            credibility_skew_shape=source.credibility.skewShape,
            fk_avatar=avatar.id if avatar is not None else None,
            fk_style=style.id,
            fk_linked_study=linked_study.id,
        )
        sources.append(s)
        avatars.append(avatar)
        source_styles.append(style)

    return {"sources": sources, "avatars": avatars, "styles": source_styles}


def build_one_post(post: PostModel, linked_study_id: str) -> Post:
    """
    Build a database Posts object with the provided Pydantic Object.

    :param post: The PostsModel Pydantic object containing the data for the new Post.
    :param linked_study_id: ID of the linked study.
    :return: The newly created database Posts object.
    """

    # We need to check the type, because legacy app use either an object for image,
    # or str for text in the same field. Plus the field can be Optional.
    if post.content is None:
        p_content = ""
    else:
        p_content = (
            str(post.content.type)
            if isinstance(post.content, PostModel)
            else str(post.content)
        )

    return Post(
        id=Database.generate_uuid(),
        fk_linked_study=linked_study_id,
        headline=post.headline,
        content=p_content,
        is_true=post.isTrue,
        changes_to_follower_on_like_mean=post.changesToFollowers.like.mean,
        changes_to_follower_on_like_std_deviation=post.changesToFollowers.like.stdDeviation,
        changes_to_follower_on_like_skewShape=post.changesToFollowers.like.skewShape,
        changes_to_follower_on_like_min=post.changesToFollowers.like.min,
        changes_to_follower_on_like_max=post.changesToFollowers.like.max,
        changes_to_follower_on_dislike_mean=post.changesToFollowers.dislike.mean,
        changes_to_follower_on_dislike_std_deviation=post.changesToFollowers.dislike.stdDeviation,
        changes_to_follower_on_dislike_skewShape=post.changesToFollowers.dislike.skewShape,
        changes_to_follower_on_dislike_max=post.changesToFollowers.dislike.max,
        changes_to_follower_on_share_mean=post.changesToFollowers.share.mean,
        changes_to_follower_on_share_std_deviation=post.changesToFollowers.share.stdDeviation,
        changes_to_follower_on_share_skewShape=post.changesToFollowers.share.skewShape,
        changes_to_follower_on_share_min=post.changesToFollowers.share.min,
        changes_to_follower_on_share_max=post.changesToFollowers.share.max,
        changes_to_follower_on_flag_mean=post.changesToFollowers.flag.mean,
        changes_to_follower_on_flag_std_deviation=post.changesToFollowers.flag.stdDeviation,
        changes_to_follower_on_flag_skewShape=post.changesToFollowers.flag.skewShape,
        changes_to_follower_on_flag_min=post.changesToFollowers.flag.min,
        changes_to_follower_on_flag_max=post.changesToFollowers.flag.max,
        changes_to_credibility_on_like_mean=post.changesToCredibility.like.mean,
        changes_to_credibility_on_like_std_deviation=post.changesToCredibility.like.stdDeviation,
        changes_to_credibility_on_like_skewShape=post.changesToCredibility.like.skewShape,
        changes_to_credibility_on_like_min=post.changesToCredibility.like.min,
        changes_to_credibility_on_like_max=post.changesToCredibility.like.max,
        changes_to_credibility_on_dislike_mean=post.changesToCredibility.dislike.mean,
        changes_to_credibility_on_dislike_std_deviation=post.changesToCredibility.dislike.stdDeviation,
        changes_to_credibility_on_dislike_skewShape=post.changesToCredibility.dislike.skewShape,
        changes_to_credibility_on_dislike_min=post.changesToCredibility.dislike.min,
        changes_to_credibility_on_dislike_max=post.changesToCredibility.dislike.max,
        changes_to_credibility_on_share_mean=post.changesToCredibility.share.mean,
        changes_to_credibility_on_share_std_deviation=post.changesToCredibility.share.stdDeviation,
        changes_to_credibility_on_share_skewShape=post.changesToCredibility.share.skewShape,
        changes_to_credibility_on_share_min=post.changesToCredibility.share.min,
        changes_to_credibility_on_share_max=post.changesToCredibility.share.max,
        changes_to_credibility_on_flag_mean=post.changesToCredibility.flag.mean,
        changes_to_credibility_on_flag_std_deviation=post.changesToCredibility.flag.stdDeviation,
        changes_to_credibility_on_flag_skewShape=post.changesToCredibility.flag.skewShape,
        changes_to_credibility_on_flag_min=post.changesToCredibility.flag.min,
        changes_to_credibility_on_flag_max=post.changesToCredibility.flag.max,
        number_of_reactions_on_like_mean=post.numberOfReactions.like.mean,
        number_of_reactions_on_like_std_deviation=post.numberOfReactions.like.stdDeviation,
        number_of_reactions_on_like_skewShape=post.numberOfReactions.like.skewShape,
        number_of_reactions_on_like_min=post.numberOfReactions.like.min,
        number_of_reactions_on_like_max=post.numberOfReactions.like.max,
        number_of_reactions_on_dislike_mean=post.numberOfReactions.dislike.mean,
        number_of_reactions_on_dislike_std_deviation=post.numberOfReactions.dislike.stdDeviation,
        number_of_reactions_on_dislike_skewShape=post.numberOfReactions.dislike.skewShape,
        number_of_reactions_on_dislike_min=post.numberOfReactions.dislike.min,
        number_of_reactions_on_dislike_max=post.numberOfReactions.dislike.max,
        number_of_reactions_on_share_mean=post.numberOfReactions.share.mean,
        number_of_reactions_on_share_std_deviation=post.numberOfReactions.share.stdDeviation,
        number_of_reactions_on_share_skewShape=post.numberOfReactions.share.skewShape,
        number_of_reactions_on_share_min=post.numberOfReactions.share.min,
        number_of_reactions_on_share_max=post.numberOfReactions.share.max,
        number_of_reactions_on_flag_mean=post.numberOfReactions.flag.mean,
        number_of_reactions_on_flag_std_deviation=post.numberOfReactions.flag.stdDeviation,
        number_of_reactions_on_flag_skewShape=post.numberOfReactions.flag.skewShape,
        number_of_reactions_on_flag_min=post.numberOfReactions.flag.min,
        number_of_reactions_on_flag_max=post.numberOfReactions.flag.max,
    )


def build_one_comment(
        comment_model: PostModel.CommentModel, linked_post: Post
) -> Comment:
    """
    Build a comment instance based on the given comment Pydantic object and linked database post object.

    :param comment_model: The comment model to build the comment from.
    :type comment_model: CommentsModel
    :param linked_post: The linked post to associate the comment with.
    :type linked_post: Post
    :return: The built comment instance.
    :rtype: Comment
    """
    return Comment(
        id=Database.generate_uuid(),
        sourceName=comment_model.sourceName,
        message=comment_model.message,
        number_of_reaction_like_mean=comment_model.numberOfReactions.like.mean,
        number_of_reaction_like_std_deviation=comment_model.numberOfReactions.like.stdDeviation,
        number_of_reaction_like_skewShape=comment_model.numberOfReactions.like.skewShape,
        number_of_reaction_like_min=comment_model.numberOfReactions.like.min,
        number_of_reaction_like_max=comment_model.numberOfReactions.like.max,
        number_of_reaction_dislike_mean=comment_model.numberOfReactions.dislike.mean,
        number_of_reaction_dislike_std_deviation=comment_model.numberOfReactions.dislike.stdDeviation,
        number_of_reaction_dislike_skew_shape=comment_model.numberOfReactions.dislike.skewShape,
        number_of_reaction_dislike_min=comment_model.numberOfReactions.dislike.min,
        number_of_reaction_dislike_max=comment_model.numberOfReactions.dislike.max,
        number_of_reaction_flags_mean=comment_model.numberOfReactions.flag.mean
        if comment_model.numberOfReactions.flag is not None
        else 0,
        number_of_reaction_flags_std_deviation=comment_model.numberOfReactions.flag.stdDeviation
        if comment_model.numberOfReactions.flag is not None
        else 0,
        number_of_reaction_flags_skew_shape=comment_model.numberOfReactions.flag.skewShape
        if comment_model.numberOfReactions.flag is not None
        else 0,
        number_of_reaction_flags_min=comment_model.numberOfReactions.flag.min
        if comment_model.numberOfReactions.flag is not None
        else 0,
        number_of_reaction_flags_max=comment_model.numberOfReactions.flag.max
        if comment_model.numberOfReactions.flag is not None
        else 0,
        number_of_reaction_share_mean=comment_model.numberOfReactions.share.mean
        if comment_model.numberOfReactions.share is not None
        else 0,
        number_of_reaction_share_std_deviation=comment_model.numberOfReactions.share.stdDeviation
        if comment_model.numberOfReactions.share is not None
        else 0,
        number_of_reaction_share_min=comment_model.numberOfReactions.share.min
        if comment_model.numberOfReactions.share is not None
        else 0,
        number_of_reaction_share_max=comment_model.numberOfReactions.share.max
        if comment_model.numberOfReactions.share is not None
        else 0,
        fk_linked_post=linked_post.id,  # Set the Foreign Key to the owning Post
    )


def generate_posts_and_comments_as_dict(
        study_json: JSONStudyModel, linked_study: Study
) -> List[dict[str, Union[Post, List[Comment]]]]:
    """
    :param study_json: JSONStudyModel object containing study information
    :param linked_study: Studies object representing linked study
    :return: list of dictionaries, each containing a post and its associated comments
    The function returns a list of dictionaries, where each dictionary contains a post and its associated comments.
    The structure of each dictionary is as follows:
    {
        'post': <Post object>,
        'comments': [<Comment object>, <Comment object>, ...]
    }
    """
    result = []

    for post in study_json.posts:
        db_post = build_one_post(post, linked_study.id)
        comments = []
        for comment in post.comments:
            comments.append(build_one_comment(comment, db_post))

        result.append({"post": post, "comments": comments})

    return result


def generate_posts_and_comments_as_lists(
        study_json: JSONStudyModel, linked_study: Study
) -> {List[Post], List[Comment]}:
    """
    Processes the study JSON and generates lists of posts and comments, ready to be inserted into the database.

    :param study_json: The JSONStudyModel object representing the study JSON.
    :param linked_study: The Studies object representing the linked study.
    :return: A dictionary containing two lists: 'posts' and 'comments'.
    :rtype: dict
    """
    posts = []
    comments = []
    for post in study_json.posts:
        db_post = build_one_post(post, linked_study.id)
        posts.append(db_post)

        for comment in post.comments:
            comments.append(build_one_comment(comment, db_post))

    return {"posts": posts, "comments": comments}


def build_study_from_json(study_json: JSONStudyModel):
    """
    Takes a JSONStudyModel object and returns a Study object as well as its related objects.

    Parameters:
    study_json (database.models.db_mode.JSONStudyModel): The JSONStudyModel object representing a study.

    Returns:
    Studies: The database.models.database.Studies object generated from the study_json.

    Example:
    study_json = JSONStudyModel(...)
    study = build_study_from_json(study_json)
    """

    # Generate the settings from the JSON.
    basic_settings = generate_basic_settings_from_json(study_json)
    advanced_settings = generate_advanced_settings_from_json(study_json)
    post_selection_methods = generate_posts_selection_methods_from_json(study_json)
    ui_settings = generate_ui_settings_from_json(study_json)
    pages_settings = generate_pages_settings_from_json(study_json)

    # Generate the Study object and link it to its future foreign keys.
    study = generate_study_with_fk(
        study_json,
        basic_settings,
        advanced_settings,
        post_selection_methods,
        ui_settings,
        pages_settings,
    )

    # Generate a Dict of: {List[Sources], List[Avatar], List[SourceStyle]} of all sources.
    # We generate the avatar at the same time to get their ID into the source
    sources = generate_sources_as_lists(study_json, study)

    posts_and_comments = generate_posts_and_comments_as_lists(study_json, study)

    return {
        "basic_settings": basic_settings,
        "advanced_settings": advanced_settings,
        "post_selection_methods": post_selection_methods,
        "ui_settings": ui_settings,
        "pages_settings": pages_settings,
        "study": study,
        "sources": sources["sources"],
        "styles": sources["styles"],
        "avatars": sources["avatars"],
        "posts": posts_and_comments["posts"],
        "comments": posts_and_comments["comments"],
    }


async def get_study_by_id(database: Database, study_id: str) -> Study:
    with database.session() as session:
        from sqlalchemy.orm import joinedload

        result = (
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
            .filter(Study.id == study_id)
            .first()
        )
    return result
