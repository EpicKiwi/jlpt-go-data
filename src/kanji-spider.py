import sys

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re


RADICAL_RE = re.compile("(.) ?\(n°(\d+)\) ?: ?(.+)")

"""
Scrap kanji from JLPT-Go website.

Documentation : http://jlptgo.com/caracteres/kanjis.php
"""
class KanjiSpider(CrawlSpider) :

    id = "kanji-spider"
    name = "Kanji Spider"
    description = "Spider for kanji on JLPT-Go"

    allowed_domains = ["jlptgo.com"]
    start_urls = [
        "http://jlptgo.com/caracteres/kanjis.php"
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.25,
    }

    rules = [
        Rule(LinkExtractor(allow="caracteres/kanjis-.+\.php",)),
        Rule(LinkExtractor(allow="traitements/controleur\.php\?action=kanjis")),
        Rule(LinkExtractor(
            allow="caracteres/kanjis-detail-.+\.html",
            process_value=lambda x: x.replace("traitements","caracteres")),
            callback="parse_kanji")
    ]

    def parse_kanji(self, response):

        item = {
            "kanji": response.css(".caractere_kanji ::text").get(),
            "reading-on": self.parse_reading(response.css("td.detail_kanji_kana:nth-child(3) > a:nth-child(1) ::text").get()),
            "reading-kun": self.parse_reading(response.css("td.detail_kanji_kana:nth-child(2) > a:nth-child(1) ::text").get()),
            "stroke-number": int(response.css(".tableau_detail_kanji > tr:nth-child(3) > td:nth-child(2) ::text").get()),
            "meaning": response.css("div.sous_partie_detail_kanji:nth-child(5) ::text").get(),
            "level-school": response.css(".tableau_detail_kanji > tr:nth-child(4) > td:nth-child(2) ::text").get(),
            "level-jlpt": response.css(".tableau_detail_kanji > tr:nth-child(5) > td:nth-child(2) ::text").get(),
            "source": response.url
        }

        item["related-kanji"] = list(map(lambda x: x.css("::text").get(), response.css(".liens_kanji_proche")))

        try:
            item["frequency"] = int(response.css(".tableau_detail_kanji > tr:nth-child(6) > td:nth-child(2) ::text").get())
        except ValueError:
            print("Kanji {} frequency is not specified ({})".format(item["kanji"], response.url), file=sys.stderr)

        radicalStr = response.css(".tableau_detail_kanji > tr:nth-child(7) > td:nth-child(2) ::text").get()
        radicalMatch = RADICAL_RE.match(radicalStr)

        if(radicalMatch):
            item["radical"] = radicalMatch.group(1)
            item["radical-number"] = radicalMatch.group(2)
            item["radical-meaning"] = radicalMatch.group(3)
        else:
            print("Could not extract radical of {} ({})".format(item["kanji"], response.url), file=sys.stderr)

        return item

    def parse_reading(self, readingStr):
        if readingStr is None or readingStr == "-":
            return []
        return readingStr.split(", ")