import json
import os
import random
import uuid
from time import sleep

from openai import OpenAI

from database.models.json_study_models import (JSONStudyModel, PostModel,
                                               ReactionFullModel)
from generators.OpenAI.post_generator import PostDetails, generate_post_ai


def load_json_template(file_name: str):
    """
    Load a JSON file and return its contents as a dictionary.

    :param file_name: The name of the JSON file to load.
    :return: A dictionary representing the JSON contents.
    """
    try:
        with open(file_name, "r", encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: An error occurred while decoding JSON from the file '{file_name}': {e}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: The file '{file_name}' was not found: {e}")
    except IOError as e:
        print(f"IOError: An I/O error occurred while reading the file '{file_name}': {e}")
    except Exception as e:
        print(f"UnexpectedError: An unexpected error occurred while loading the file '{file_name}': {e}")

    return {}


def create_new_post(open_ai_client: OpenAI):
    """
    :param open_ai_client: The client object of the OpenAI API.
    :return: A new post created using the OpenAI API.

    This method takes in an instance of the OpenAI client and generates a new post using the generate_post_ai method.
    The generated post is then used to create a PostModel object with various properties such as ID, source name,
    content, headline, and reactions. The PostModel object is returned as the result of the method.
    """
    generated_post = generate_post_ai(
        open_ai_client,
        PostDetails(
            is_true_percentage=65,
            no_hashtag=False,
            min_char=50,
            max_char=350,
            specific_theme=None,
        ),
        verbose=False,
    )
    reactions_model = ReactionFullModel(
        mean=0.5, stdDeviation=0.5, skewShape=1, min=-1000, max=1000
    )
    return PostModel(
        id=str(uuid.uuid4()),
        sourceName="Jake",
        content=generated_post["content"],
        headline=generated_post["headline"],
        isTrue=generated_post["is_true"],
        changesToFollowers=PostModel.ChangesToFollowersModel(
            like=reactions_model,
            dislike=reactions_model,
            share=reactions_model,
            flag=reactions_model,
        ),
        changesToCredibility=PostModel.ChangesToCredibilityModel(
            like=reactions_model,
            dislike=reactions_model,
            share=reactions_model,
            flag=reactions_model,
        ),
        numberOfReactions=PostModel.NumberOfReactionsModel(
            like=reactions_model,
            dislike=reactions_model,
            share=reactions_model,
            flag=reactions_model,
        ),
        comments=[],
    )


def create_new_comment(open_ai_client: OpenAI, generated_post: PostModel):
    """
    :param open_ai_client: the OpenAI client object used for communication with the OpenAI API
    :param generated_post: the PostModel object representing the generated post

    :return: None

    This method creates a new comment for the given generated post.

    The comment is generated using the OpenAI client and the content of the generated post. The comment message is obtained by calling the `generate_comment_ai` method from the `comment_generator` module in the OpenAI package.

    The comment is then constructed using the following information:
    - id: a unique identifier generated using the `uuid.uuid4()` function
    - sourceName: a string representing the source of the comment
    - message: the generated comment message obtained from the OpenAI API
    - numberOfReactions: an object representing the number of reactions the comment has, including like, dislike, flag, and share. However, only the like and dislike reactions are set in this method.

    The constructed comment is then appended to the comments list of the generated post.
    """
    from generators.OpenAI.comment_generator import generate_comment_ai

    comment_values = generate_comment_ai(
        open_ai_client, generated_post.headline, generated_post.content
    )

    reactions_model = ReactionFullModel(
        mean=0.5, stdDeviation=0.5, skewShape=1, min=-1000, max=1000
    )
    comment = PostModel.CommentModel(
        id=str(uuid.uuid4()),
        sourceName="S1",
        message=comment_values["message"],
        numberOfReactions=PostModel.CommentModel.NumberOfReactionsLightModel(
            like=reactions_model,
            dislike=reactions_model,
            # flag=reactions_model,
            # share=reactions_model
        ),
    )
    generated_post.comments.append(comment)


def save_json_to_file(json_study: JSONStudyModel, output_dir: str, file_name: str):
    """
    :param json_study: A JSONStudyModel object representing the study to be saved.
    :param output_dir: A string representing the output directory where the file will be saved.
    :param file_name: A string representing the name of the file.
    :return: None

    Save JSON study to file.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "w") as json_file:
        json_string = json_study.json()
        json_object = json.loads(json_string)
        json_file.write(json.dumps(json_object, indent=4))


def generate_study() -> JSONStudyModel:
    """
    :return: The generated JSONStudyModel object representing the study.

    Generate a synthetic study using AI for test purposes.
    Save the generated study as a JSON file name <result.json> in the <./output> directory.
    """
    config = {
        "min_post": 4,
        "max_post": 8,
        "min_comment": 0,
        "max_comment": 5,
    }

    # @todo this only work for local execution, create the object manually using Pydantic.
    json_template = load_json_template("template.json")
    result_json_study = JSONStudyModel(**json_template)
    result_json_study.id = str(uuid.uuid4())
    result_json_study.basicSettings.name = f"synthetic:{result_json_study.id}"
    result_json_study.basicSettings.prompt = (
        "This an auto generated Study using AI for test purposes."
    )
    result_json_study.basicSettings.description = (
        "This an auto generated Study using AI."
    )
    # Clear all existing posts from the loaded template
    result_json_study.posts = []

    # OpenAI also requires an API key in environment variables.
    client = OpenAI()

    number_of_posts = random.randint(config["min_post"], config["max_post"])

    # We keep a minus -1 because the legacy app don't like to use ALL the available posts and throw an error
    result_json_study.basicSettings.length = (
        number_of_posts if (number_of_posts == 1) else (number_of_posts - 1)
    )

    for _ in range(number_of_posts):
        new_post = create_new_post(client)
        result_json_study.posts.append(new_post)
        sleep(1)  # Ensure we don't get timeout by sending to many requests

        # Generate a range up to a random number between 0 and 6
        for _ in range(random.randint(config["min_comment"], config["max_comment"])):
            create_new_comment(client, new_post)
            sleep(1)

    save_json_to_file(result_json_study, "output", "result.json")
    return result_json_study


generate_study()
