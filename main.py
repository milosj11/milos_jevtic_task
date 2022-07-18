import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

option = webdriver.ChromeOptions()
option.add_argument('headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

web_sites = dict(
    versoix=dict(target_website="https://www.versoix.ch/news/commune/", s1="block-card-txt", s2="a", s3="a", s4="href",
                 s5="time", s6="main-content-txt", s7="p", s8="a", s9="a", s10="href", website_name="versoix"),
    collex_bossy=dict(target_website="https://collex-bossy.ch/fr/actualites/", s1="article", s2="h2",s3="a", s4="href",
                      s5="span", s6="content-main", s7="p", s8="a", s9="a", s10="href", website_name="collex_bossy")

)


class SeleniumGenericScraper:

    def __init__(self, web_driver, target_website, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, website_name):

        self.website_name = website_name
        self.target_url = target_website
        self.driver = web_driver

        self.headlines, self.urls, self.dates = self.first_page_data(s1, s2, s3, s4, s5, website_name)

        self.body, self.pdf_links = self.data_from_article_page(s6, s7, s8, s9, s10)

    def first_page_data(self, s1, s2, s3, s4, s5, website_name):

        # fetch data from first page
        self.driver.get(self.target_url)
        if website_name == "collex_bossy":  # in this isolated areas it's not needed to use css selectors from input
            headlines_urls_dates = self.driver.find_elements(by=By.TAG_NAME, value=s1)
        else:
            headlines_urls_dates = self.driver.find_elements(by=By.CLASS_NAME, value=s1)

        headlines = [headline.find_element(By.TAG_NAME, s2).text for headline in headlines_urls_dates]

        urls = [url.find_element(By.TAG_NAME, s3).get_attribute(s4) for url in headlines_urls_dates]
        dates = [date.find_element(By.TAG_NAME, s5).text for date in headlines_urls_dates]

        return headlines, urls, dates

    def data_from_article_page(self, s6, s7, s8, s9, s10):
        # fetch body data from each article
        body = list()
        pdf_links = list()
        for url in self.urls:
            self.driver.get(url=url)
            # body
            body_raw = self.driver.find_element(by=By.CLASS_NAME, value=s6)
            paragraphs = [p.text for p in body_raw.find_elements(by=By.TAG_NAME, value=s7)]
            # create one string from list of paragraphs
            article_body = " ".join(paragraphs) if len(paragraphs) > 1 else paragraphs[0]
            body.append(article_body)

            # links
            article_pdf_links = list()
            article_urls = [p for p in body_raw.find_elements(by=By.TAG_NAME, value=s8)]  # extract urls from body

            if article_urls != 0:
                for a in body_raw.find_elements(by=By.TAG_NAME, value=s9):
                    if "pdf" in a.get_attribute("outerHTML"):  # check is `pdf` word exists in html element
                        article_pdf_links.append(a.get_attribute(s10))

            pdf_links.append(article_pdf_links)

        return body, pdf_links

    def create_output_file(self):
        # construct final result
        result = [dict(domain=self.target_url[:22], link=self.urls[i], headline=self.headlines[i], body=self.body[i],
                       date=self.dates[i], pdf_links=self.pdf_links[i]) for i in range(len(self.urls))]

        with open(f"{self.website_name}.json", "w", encoding="utf8") as file:

            data = json.dumps(result, indent=2, ensure_ascii=False)
            file.write(data)


if __name__ == "__main__":

    for k in web_sites:

        scraper = SeleniumGenericScraper(web_driver=driver, **web_sites.get(k))
        scraper.create_output_file()
