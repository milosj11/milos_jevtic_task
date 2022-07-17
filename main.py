import argparse
import csv
import json
import logging
import os
import re
import sys
import unicodedata

import requests
from bs4 import BeautifulSoup
from dateparser import parse

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s: %(message)s")

# optional arguments that can be passed from cli
parser = argparse.ArgumentParser(
    description="Determines which website will be object of scraping and output file format")
parser.add_argument("-s", "--site", help="Website from with data will be scraped.",
                    choices=["troinex", "plan_les_ouates", "ge"], required=False)
parser.add_argument("-f", "--format", help="File format in which result will be saved", choices=["json", "csv"],
                    default="json", required=False)
args = vars(parser.parse_args())

# css selectors and other required parameters specific for every website
sites = dict(
    troinex=dict(s1="h3", s2="card-title", s3="div", s4="card-subtitle my-2 text-muted font-light", s5="div",
                 s6="my-3", web_site_url="https://troinex.ch", target_url="https://troinex.ch/actualites/",
                 url_regex=r"(https?://\S+/)", file_name="troinex"),

    plan_les_ouates=dict(s1="h2", s2="field-content", s3="div", s4="views-field views-field-created", s5="div",
                         s6="field-type-text-with-summary", web_site_url="https://www.plan-les-ouates.ch",
                         target_url="https://www.plan-les-ouates.ch/actualites", file_name="plan_les_ouates"),

    ge=dict(s1="div", s2="publications-listing", s3="div", s4="item-data", s5="div", s6="field--name-body",
            web_site_url="https://www.ge.ch", target_url="https://www.ge.ch/publication", file_name="ge")
)


def collect_the_data(s1, s2, s3, s4, s5, s6, web_site_url, target_url, file_name, url_regex=None,
                     file_format=args["format"]):
    """
    Collect the data using bs4 and saves them into external file
    """

    logging.info(f"Scraping started from web page: {target_url}")

    try:
        site = requests.get(url=target_url).text
    except requests.exceptions.RequestException as err:
        raise Exception(err)

    soup = BeautifulSoup(markup=site, features="html.parser")
    headlines_and_urls = soup.find_all(name=s1, class_=s2)

    urls = []
    headlines = []
    body = []
    pdf_links_ = []

    # fetching article urls
    if url_regex:  # in this case RegEx is used for demonstration purposes, it is not really necessary
        urls = [re.findall(url_regex, str(title))[0] for title in headlines_and_urls]

    else:
        for title in headlines_and_urls:
            values = title.find_all(name="a")
            for value in values:
                urls.append(
                    f"{web_site_url}{value['href']}"
                )  # concatenate domain and url

    logging.info("Article urls - collected.")

    # fetching headlines
    for title_tag in headlines_and_urls:
        title = title_tag.find_all(name="a")
        for value in title:
            headlines.append(value.text.strip())

    # fetching dates
    dates_raw = soup.find_all(name=s3, class_=s4)
    dates = [date.text.split("-")[0].strip() for date in dates_raw]
    iso_dates = [parse(date, settings={'TIMEZONE': 'UTC+2'}).date().isoformat() for date in dates]

    logging.info("Article dates - collected.")

    # body and pdf links
    for target_url in urls:
        # fetching news article body
        article = requests.get(target_url).text  # noqa
        article_soup = BeautifulSoup(markup=article, features="html.parser")

        article_text = article_soup.find(name=s5, class_=s6).text

        article_text = unicodedata.normalize("NFKC", article_text).strip().replace("\n", " ")

        body.append(article_text)

        # fetching pdf links
        pdf_links_in_article = []
        all_links_in_article = article_soup.find_all(name="a")
        for link in all_links_in_article:
            if "pdf" in str(link):  # if `pdf` word exists in tag, we grab the url
                url = f'{web_site_url}{link["href"]}' if link["href"].startswith("/") else link["href"]
                pdf_links_in_article.append(url)
        pdf_links_.append(pdf_links_in_article)  # append empty list as well, to not cause index error later

    logging.info("Article content and pdf links - collected.")

    if not (len(urls) == len(headlines) == len(body) == len(dates)):  # basic check is collected data valid
        sys.exit("Length of lists is not matched")

    # put all data together and return them as json or csv file
    result = [dict(domain=web_site_url, link=urls[i], headline=headlines[i], body=body[i], date=iso_dates[i],
                   pdf_links=pdf_links_[i]) for i in range(len(urls))]

    if not os.path.exists("results"):
        os.mkdir("results")

    with open(f"results/{file_name}.{file_format}", "w", encoding="utf8") as file:
        if file_format == "csv":
            keys = result[0].keys()

            dict_writer = csv.DictWriter(file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(result)
        else:
            data = json.dumps(result, indent=2, ensure_ascii=False)
            file.write(data)

        logging.info(f"{file.name} - created.")


if __name__ == "__main__":
    if args["site"]:
        collect_the_data(**sites.get(args["site"]))

    else:
        for k in sites:
            collect_the_data(**sites.get(k))
