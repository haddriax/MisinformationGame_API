from dataclasses import dataclass
from random import randrange

OPENAI_API_KEY = ""  # DEBUG - NOT FOR PRODUCTION


@dataclass
class PostDetails:
    """
    Data class that holds information about the creation process for a post.
    """

    ai_model: str
    """ AI Model version."""
    no_hashtag: bool
    """ Ensure the generation does not include hashtag at the end of the post."""
    is_info_true: bool
    """ Hint for generated information to be either true or false."""
    force_title: str
    """ Pass a value that will be used as title. If none, a random one will be generated. """
    is_info_true: bool
    """ Filled at object creation, define if the generated post will be true or fake. """
    available_themes = [
        "Health and Wellness",
        "Environmental Awareness",
        "Technology Trends",
        "Historical Facts",
        "Financial Literacy",
        "Science Education",
        "Cultural Diversity",
        "Global Issues",
        "Travel Tips and Destinations",
        "Education Insights",
        "Self-Improvement",
        "Food and Nutrition",
        "Entrepreneurship",
        "Parenting Tips",
        "Art and Creativity",
        "Work-Life Balance",
        "Human Rights Advocacy",
        "Sports and Fitness",
        "Mental Health Awareness",
        "Automotive Enthusiasm",
    ]
    """ List of themes that are used when no theme is specifically precised."""

    def __init__(
            self,
            is_true_percentage,
            no_hashtag,
            forced_title=None,
            specific_theme=None,
            min_char=300,
            max_char=600,
    ):
        self.is_true_percentage = is_true_percentage
        self.no_hashtag = no_hashtag
        self.force_title = forced_title
        self.min_char = min_char
        self.max_char = max_char
        self.ai_model = "gpt-4o"  # "gpt-3.5-turbo"
        self.is_info_true = randrange(100) <= is_true_percentage
        self.theme = (
            specific_theme
            if specific_theme is not None
            else PostDetails.available_themes[
                randrange(len(PostDetails.available_themes) - 1)
            ]
        )


def generate_post_ai(
        open_ai_client, post_details: PostDetails, verbose=False
) -> dict[str, str]:
    # Preparing the title prompt based on our parameters.
    ai_instruction_title = (
        post_details.force_title
        if (post_details.force_title is not None)
        else "Generate the title, and only the title, of a social media post. The content must be \033[1m"
             "{is_true}\033[0m "
             "and be about\033[1m{theme}\033[0m. The post must be informative. Do not generate title like '10 proven "
             "facts' or '10 proven benefits' or '10 proven reasons'.".format(
            is_true="true" if post_details.is_info_true else "fake",
            theme=post_details.theme,
        )
    )

    # Request for creating the title.
    completion_headline = open_ai_client.chat.completions.create(
        model=post_details.ai_model,
        messages=[
            {"role": "user", "content": ai_instruction_title},
        ],
    )
    if verbose:
        print(f"\033[92mTitle prompt:\033[0m\n{ai_instruction_title}")
        print(f"\033[92mHeadline:\n\033[0m\033[1m{completion_headline.choices[0].message.content}\033[0m")

    # Preparing the content prompt based on our parameters and the result of the title prompt.
    ai_instruction_content = (
        "Generate the content of a social media post based on this title: \033[1m{title}\033[0m. The "
        "content must be \033[1m{is_true}\033[0m. The post"
        "must be informative. Limit the size from \033[1m{min_char}\033[0m to \033[1m{max_char}\033[0m characters. Do "
        "not add any"
        "hashtag '#' at the end. Avoid repeating the title in the content."
    ).format(
        title=completion_headline.choices[0].message.content,
        is_true=post_details.is_info_true,
        min_char=post_details.min_char,
        max_char=post_details.max_char,
    )

    # Request for creating the content, based on given title.
    completion_content = open_ai_client.chat.completions.create(
        model=post_details.ai_model,
        messages=[
            {"role": "user", "content": ai_instruction_content},
        ],
    )
    if verbose:
        print(f"\033[96mContent prompt:\033[0m\n{ai_instruction_content}")
        print(f"\033[96mContent:\n\033[0m{completion_content.choices[0].message.content}")

    return {
        "headline": completion_headline.choices[0].message.content,
        "content": completion_content.choices[0].message.content,
        "theme": post_details.theme,
        "is_true": str(post_details.is_info_true),
    }

# Test call of our generation function.
# post = generate_post_ai(
#     PostDetails(
#         is_true_percentage=0,
#         no_hashtag=False,
#         min_char=600,
#         max_char=800,
#         specific_theme=None),
#     verbose=True)
