from random import randint


def generate_comment_ai(open_ai_client, post_headline, post_content) -> dict[str, str]:
    """
    Generate a comment using an AI model.

    :param open_ai_client: The OpenAI client for making API calls.
    :param post_headline: The title of the social media post.
    :param post_content: The content of the social media post.
    :return: A dictionary containing the generated comment as the value of the "message" key.
    """

    ai_instruction = (
        f"Write a short comment (1 sentence, maximum 280 characters) on this social media post "
        f"of title {post_headline} "
        f"and content {post_content}."
        f"Make sure the comment seems realistic and related to the post."
        f"On a scale of 1 to 100, you are {randint(0, 100)} agree with what that particular post say."
    )
    completion = open_ai_client.chat.completions.create(
        model="gpt-4o",  # "gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a young social media user scrolling content for enjoyment.",
            },
            {"role": "user", "content": ai_instruction},
        ],
        timeout=60,
        max_tokens=256,
    )

    return {"message": completion.choices[0].message.content}
