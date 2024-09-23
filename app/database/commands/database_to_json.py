"""This module provides functions to convert various database models related to a study into corresponding JSON
models using Pydantic for validation. It includes detailed logging to capture and report validation and conversion
errors."""

import logging
from datetime import datetime
from typing import Tuple

from pydantic import ValidationError

from database.models.db_model import (AdminUser, Comment, Post,
                                      PostSelectionMethod, Source, Study,
                                      StudyAdvancedSettings,
                                      StudyBasicSettings, StudyPagesSettings,
                                      StudyUiSettings)
from database.models.json_study_models import (AdvancedSettingsModel,
                                               BasicSettingsModel,
                                               JSONStudyModel, List,
                                               PagesSettingsModel, PostModel,
                                               ReactionFullModel,
                                               SourcePostSelectionMethodModel,
                                               SourcesModel, UiSettingsModel)

logger = logging.getLogger("conversion_logger")


def convert_basic_settings_to_json(
        basic_settings: StudyBasicSettings,
) -> BasicSettingsModel:
    try:
        basic_settings_json = BasicSettingsModel(
            name=basic_settings.name,
            description=basic_settings.description,
            prompt=basic_settings.prompt,
            length=basic_settings.length,
            requireComments=basic_settings.require_comments,
            requireReactions=basic_settings.require_reactions,
            requireIdentification=basic_settings.require_identification,
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_basic_settings_to_json: {e}")
        raise
    else:
        return basic_settings_json


def convert_ui_settings_to_json(ui_settings: StudyUiSettings) -> UiSettingsModel:
    try:
        ui_settings_json = UiSettingsModel(
            displayPostsInFeed=ui_settings.display_posts_in_feed,
            displayFollowers=ui_settings.display_followers,
            displayCredibility=ui_settings.display_credibility,
            displayProgress=ui_settings.display_progress,
            displayNumberOfReactions=ui_settings.display_number_of_reactions,
            allowMultipleReactions=ui_settings.allow_multiple_reactions,
            postEnabledReactions=UiSettingsModel.PostEnabledReactionsModel(
                like=ui_settings.post_enable_reaction_like,
                dislike=ui_settings.post_enable_reaction_dislike,
                share=ui_settings.post_enable_reaction_share,
                flag=ui_settings.post_enable_reaction_flag,
                skip=ui_settings.post_enable_reaction_skip,
            ),
            commentEnabledReactions=UiSettingsModel.CommentEnabledReactionsModel(
                like=ui_settings.comment_enable_reaction_like,
                dislike=ui_settings.comment_enable_reaction_dislike,
            ),
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_ui_settings_to_json: {e}")
        raise
    else:
        return ui_settings_json


def convert_study_advanced_settings(
        advanced_settings: StudyAdvancedSettings,
) -> AdvancedSettingsModel:
    try:
        advanced_settings_json = AdvancedSettingsModel(
            minimumCommentLength=advanced_settings.minimum_comment_length,
            promptDelaySeconds=advanced_settings.prompt_delay_seconds,
            reactDelaySeconds=advanced_settings.react_delay_seconds,
            genCompletionCode=advanced_settings.gen_completion_code,
            completionCodeDigits=advanced_settings.completion_code_digits,
            genRandomDefaultAvatars=advanced_settings.gen_random_default_avatars,
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_study_advanced_settings: {e}")
        raise
    else:
        return advanced_settings_json


def convert_study_pages_settings(
        pages_settings: StudyPagesSettings,
) -> PagesSettingsModel:
    try:
        pages_settings_json = PagesSettingsModel(
            preIntro=pages_settings.pre_intro,
            preIntroDelaySeconds=pages_settings.pre_intro_delay_seconds,
            rules=pages_settings.rules,
            rulesDelaySeconds=pages_settings.rules_delay_seconds,
            postIntro=pages_settings.post_intro,
            postIntroDelaySeconds=pages_settings.post_intro_delay_seconds,
            debrief=pages_settings.debrief,
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_study_pages_settings: {e}")
        raise
    else:
        return pages_settings_json


def convert_admin_user(admin_user: AdminUser) -> str:
    try:
        if admin_user is None:
            return "Unknown"
        return admin_user.username
    except Exception as e:
        logger.error(f"Error converting admin user: {e}")
        return "Unknown"


def convert_comment(comment: Comment) -> PostModel.CommentModel:
    try:
        if (
                comment.sourceName is None
                or comment.message is None
                or comment.number_of_reaction_like_mean is None
        ):
            raise ValueError("One of the required fields is None.")
        comment_json = PostModel.CommentModel(
            sourceName=comment.sourceName,
            message=comment.message,
            numberOfReactions=PostModel.CommentModel.NumberOfReactionsLightModel(
                like=ReactionFullModel(
                    mean=comment.number_of_reaction_like_mean,
                    stdDeviation=comment.number_of_reaction_like_std_deviation,
                    skewShape=comment.number_of_reaction_like_skewShape,
                    min=comment.number_of_reaction_like_min,
                    max=comment.number_of_reaction_like_max,
                ),
                dislike=ReactionFullModel(
                    mean=comment.number_of_reaction_dislike_mean,
                    stdDeviation=comment.number_of_reaction_dislike_std_deviation,
                    skewShape=comment.number_of_reaction_dislike_skew_shape,
                    min=comment.number_of_reaction_dislike_min,
                    max=comment.number_of_reaction_dislike_max,
                ),
            ),
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_comment: {e}")
        raise
    except ValueError as e:
        logger.error(f"Value error in convert_comment: {e}")
        raise
    else:
        return comment_json


def convert_one_post(post_comment: Tuple[Post, List[Comment]]) -> PostModel:
    """
    Takes a tuple that contains a Post object and a list of Comment objects.
    It converts the Post object and its associated comments into a PostModel object.

    Parameters:
        post_comment: Tuple[Post, List[Comment]]
            A tuple containing a Post object and the list its Comment.

    Returns:
        PostModel: JSON format object representing the converted Post.

    Raises:
        ValidationError: If a ValidationError occurs during conversion, it will be logged and re-raised.
    """
    try:
        post = post_comment[0]
        comments = post_comment[1]

        post_content: PostModel.ContentModel
        # Set the 'content' to a ContentModel if the entry contains "type=". This means we upload an object.
        # This is not an ideal solution but was needed to stay compatible with the legacy application.
        if "type=" in post.content:
            # We create the object, and set the type to the file extension by removing the "type=" part.
            post_content = PostModel.ContentModel(type=post.content.split("=")[1])
            # Sanitize string not keeping '.
            post_content.type = post_content.type.replace("'", "")
            # Sanitize string not keeping space.
            post_content.type = post_content.type.replace(" ", "")
        # Otherwise the content is a string.
        else:
            # noinspection PyTypeChecker
            post_content = post.content

        post_json = PostModel(
            id=post.id,
            headline=post.headline,
            content=post_content,
            isTrue=post.is_true,
            changesToFollowers=PostModel.ChangesToFollowersModel(
                like=ReactionFullModel(
                    mean=post.changes_to_follower_on_like_mean,
                    stdDeviation=post.changes_to_follower_on_like_std_deviation,
                    skewShape=post.changes_to_follower_on_like_skewShape,
                    min=post.changes_to_follower_on_like_min,
                    max=post.changes_to_follower_on_like_max
                ),
                dislike=ReactionFullModel(
                    mean=post.changes_to_follower_on_dislike_mean,
                    stdDeviation=post.changes_to_follower_on_dislike_std_deviation,
                    skewShape=post.changes_to_follower_on_dislike_skewShape,
                    min=post.changes_to_follower_on_dislike_min,
                    max=post.changes_to_follower_on_dislike_max
                ),
                share=ReactionFullModel(
                    mean=post.changes_to_follower_on_share_mean,
                    stdDeviation=post.changes_to_follower_on_share_std_deviation,
                    skewShape=post.changes_to_follower_on_share_skewShape,
                    min=post.changes_to_follower_on_share_min,
                    max=post.changes_to_follower_on_share_max
                ),
                flag=ReactionFullModel(
                    mean=post.changes_to_follower_on_flag_mean,
                    stdDeviation=post.changes_to_follower_on_flag_std_deviation,
                    skewShape=post.changes_to_follower_on_flag_skewShape,
                    min=post.changes_to_follower_on_flag_min,
                    max=post.changes_to_follower_on_flag_max
                ),
            ),
            changesToCredibility=PostModel.ChangesToCredibilityModel(
                like=ReactionFullModel(
                    mean=post.changes_to_credibility_on_like_mean,
                    stdDeviation=post.changes_to_credibility_on_like_std_deviation,
                    skewShape=post.changes_to_credibility_on_like_skewShape,
                    min=post.changes_to_credibility_on_like_min,
                    max=post.changes_to_credibility_on_like_max
                ),
                dislike=ReactionFullModel(
                    mean=post.changes_to_credibility_on_dislike_mean,
                    stdDeviation=post.changes_to_credibility_on_dislike_std_deviation,
                    skewShape=post.changes_to_credibility_on_dislike_skewShape,
                    min=post.changes_to_credibility_on_dislike_min,
                    max=post.changes_to_credibility_on_dislike_max
                ),
                share=ReactionFullModel(
                    mean=post.changes_to_credibility_on_share_mean,
                    stdDeviation=post.changes_to_credibility_on_share_std_deviation,
                    skewShape=post.changes_to_credibility_on_share_skewShape,
                    min=post.changes_to_credibility_on_share_min,
                    max=post.changes_to_credibility_on_share_max
                ),
                flag=ReactionFullModel(
                    mean=post.changes_to_credibility_on_flag_mean,
                    stdDeviation=post.changes_to_credibility_on_flag_std_deviation,
                    skewShape=post.changes_to_credibility_on_flag_skewShape,
                    min=post.changes_to_credibility_on_flag_min,
                    max=post.changes_to_credibility_on_flag_max
                ),
            ),
            numberOfReactions=PostModel.NumberOfReactionsModel(
                like=ReactionFullModel(
                    mean=post.number_of_reactions_on_like_mean,
                    stdDeviation=post.number_of_reactions_on_like_std_deviation,
                    skewShape=post.number_of_reactions_on_like_skewShape,
                    min=post.number_of_reactions_on_like_min,
                    max=post.number_of_reactions_on_like_max
                ),
                dislike=ReactionFullModel(
                    mean=post.number_of_reactions_on_dislike_mean,
                    stdDeviation=post.number_of_reactions_on_dislike_std_deviation,
                    skewShape=post.number_of_reactions_on_dislike_skewShape,
                    min=post.number_of_reactions_on_dislike_min,
                    max=post.number_of_reactions_on_dislike_max
                ),
                share=ReactionFullModel(
                    mean=post.number_of_reactions_on_share_mean,
                    stdDeviation=post.number_of_reactions_on_share_std_deviation,
                    skewShape=post.number_of_reactions_on_share_skewShape,
                    min=post.number_of_reactions_on_share_min,
                    max=post.number_of_reactions_on_share_max
                ),
                flag=ReactionFullModel(
                    mean=post.number_of_reactions_on_share_mean,
                    stdDeviation=post.number_of_reactions_on_share_std_deviation,
                    skewShape=post.number_of_reactions_on_share_skewShape,
                    min=post.number_of_reactions_on_share_min,
                    max=post.number_of_reactions_on_share_max
                ),
            ),
            comments=[convert_comment(c) for c in comments],
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_one_post: {e}")
        raise
    else:
        return post_json


def convert_post_selection_method(
        post_selection_method: PostSelectionMethod,
) -> SourcePostSelectionMethodModel:
    """
    Convert a PostSelectionMethod from the database into a SourcePostSelectionMethodModel
    """
    try:
        sps_method = SourcePostSelectionMethodModel(
            type=post_selection_method.type,
            linearRelationship=SourcePostSelectionMethodModel.LinearRelationshipModel(
                slope=post_selection_method.linear_relationship_slope,
                intercept=post_selection_method.linear_relationship_intercept,
            ),
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_post_selection_method: {e}")
        raise
    else:
        return sps_method


def convert_sources(sources: List[Source], study: Study) -> List[SourcesModel]:
    """
    Convert a list of sources to a list of SourcesModel objects.

    Parameters:
        sources: List[Source]
            List of Source objects to convert.
        study: Study
           The study related to the sources list.

    Returns:
        List of converted SourcesModel objects.

    Raises:
        ValidationError: If there is a validation error during conversion.
    """
    try:
        res = []
        source_id: int = 0
        for source in sources:
            source_id = source_id + 1
            source_json = SourcesModel(
                id=f"S{source_id}",  # source.id,
                linked_study_id=study.id,
                file_name=source.file_name,
                name=source.name,
                avatar=SourcesModel.AvatarModel(type=source.avatar.type)
                if source.avatar is not None
                else None,
                style=SourcesModel.StyleModel(
                    backgroundColor="#8fd186",
                )
                if source.avatar is not None
                else None,
                maxPosts=source.max_posts if source.max_posts > 0 else -1,
                followers=SourcesModel.FollowersModel(
                    mean=source.followers_mean,
                    stdDeviation=source.followers_std_deviation,
                    skewShape=source.followers_skew_shape,
                    min=0,
                    max=250,
                ),
                credibility=SourcesModel.CredibilityModel(
                    mean=source.credibility_mean,
                    stdDeviation=source.credibility_std_deviation,
                    skewShape=source.credibility_skew_shape,
                    min=0,
                    max=100,
                ),
                truePostPercentage=source.true_post_percentage,
            )
            res.append(source_json)
    except ValidationError as e:
        logger.error(f"Validation error in convert_sources: {e}")
        raise
    else:
        return res


def convert_study(
        study: Study,
        posts_comments: dict[str, Tuple[Post, List[Comment]]],
        sources: List[Source],
        study_version=1,
) -> JSONStudyModel:
    try:
        post_id: int = 0
        converted_posts = []
        for elem in posts_comments.values():
            post_id = post_id + 1
            elem[0].id = f"P{post_id}"
            converted_posts.append(convert_one_post(elem))

        converted_sources = convert_sources(sources, study)

        study_json = JSONStudyModel(
            id=study.id,
            version=study_version,
            authorID=study.fk_created_by if study.fk_created_by is not None else "None",
            authorName=convert_admin_user(study.created_by)
            if study.fk_created_by is not None
            else "None",
            lastModifiedTime=int(datetime.now().timestamp()),
            enabled=study.enabled,
            basicSettings=convert_basic_settings_to_json(study.basic_settings),
            uiSettings=convert_ui_settings_to_json(study.ui_settings),
            advancedSettings=convert_study_advanced_settings(study.advanced_settings),
            pagesSettings=convert_study_pages_settings(study.pages_settings),
            sourcePostSelectionMethod=convert_post_selection_method(
                study.post_selection_methods
            ),
            sources=converted_sources,
            posts=converted_posts,
        )
    except ValidationError as e:
        logger.error(f"Validation error in convert_study: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in convert_study: {e}")
        raise
    else:
        return study_json
