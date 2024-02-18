import requests
import re
import html


URL = ("https://forum.vbulletin.com/forum/vbulletin-3-8/vbulletin-3-8-questions-problems-and-troubleshooting/"
       "414325-www-vs-non-www-url-causing-site-not-to-login")
OUTPUT_FILE_NAME = "vbulletin_posts.txt"


def main():
    """
    Yields posts from `vbulletin` blog
    """

    post_pattern = '<div class="js-post__content-text restore h-wordwrap" itemprop="text">(.*?)<div class="h-flex-spacer'

    page_html = requests.get(URL).text

    all_posts = re.findall(pattern=post_pattern, string=page_html, flags=re.DOTALL)

    for idx, raw_post in enumerate(all_posts):

        post = clean_up_post(raw_post)

        if raw_post != all_posts[-1]:
            yield f'{idx + 1}. [{html.unescape(post.strip())}]\n\n'
        else:
            yield f'{idx + 1}. [{html.unescape(post.strip())}]'


def clean_up_post(post: str) -> str:
    """
    Remove html tags from raw `post` element in order to extract plain text, handle new lines

    :param  post:  Raw post element to be cleaned up
    """

    exclude_patterns = ['<div class="bbcode_postedby">.*?</div>', '<div class="post-signature restore">.*?</span><br />',
                        '<div class="post-signature restore">.*?</a>', '<div class="post-signature restore">.*?>',
                        '<div.*?>', '<a.*?>', '<span.*?>', '<pre.*?>', "<img.*?>"]

    to_remove = []

    # Find patterns to be removed
    for pattern in exclude_patterns:
        text = re.findall(pattern=pattern, string=post, flags=re.DOTALL)

        to_remove.extend(text)

    # Redundant tags
    to_remove.extend(["</div>", "</a>", "</span>", "<br />", "\r", "\t"])

    for tag in to_remove:
        post = post.replace(tag, "")

    # Handle multiple `\n`
    while "\n\n\n" in post.strip():

        post = post.replace("\n\n\n", "\n\n")

    # End of `pre` tag implies new line
    post = post.replace("</pre>", "\n")

    return post


if __name__ == "__main__":

    with open(file=OUTPUT_FILE_NAME, mode="w") as file:

        for post_text in main():
            print(post_text)
            file.write(post_text)
