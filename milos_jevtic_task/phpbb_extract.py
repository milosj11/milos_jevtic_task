import requests
import re


URL = "http://www.phpbb.com/community/viewtopic.php?f=46&t=2159437"
OUTPUT_FILE_NAME = "phpbb_posts.txt"


def main():
    """
    Yields posts from `phpbb` blog
    """

    post_pattern = '<div class="content">(.*?)<div id="sig'  # Match all posts
    exclude_pattern = '<img.*?>'  # Redundant tag (in this case -> `Embarrassed` emojy)

    page_html = requests.get(URL).text

    # End of `cite` and `blockquote` tag implies new line
    page_html = page_html.replace("</cite>", "\n")
    page_html = page_html.replace("</blockquote>", "\n")

    # All img tags & Other redundant tags
    to_exclude = re.findall(pattern=exclude_pattern, string=page_html, flags=re.DOTALL)
    to_exclude.extend(["<blockquote>", "<div>", "<cite>", "</div>", "<br>"])

    # Remove img and other redundant tags
    for str_to_exclude in to_exclude:
        page_html = page_html.replace(str_to_exclude, "")

    all_posts = re.findall(pattern=post_pattern, string=page_html, flags=re.DOTALL)

    for idx, post in enumerate(all_posts):

        if post != all_posts[-1]:
            yield f'{idx + 1}. [{post.strip()}]\n\n'
        else:
            yield f'{idx + 1}. [{post.strip()}]'


if __name__ == "__main__":

    with open(file=OUTPUT_FILE_NAME, mode="w") as file:

        for post_text in main():
            print(post_text)
            file.write(post_text)
