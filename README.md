# JLPT-Go Data

> Scrapper for the JLPT-Go Website

## Install

Make sure you have Python 3.8+ and using it to run JLPT-Go Data.

Install all dependancies

```sh-session
pip install -r requirements.txt
```

## Get Data

Get kanji from JLPT-Go

```sh-session
scrapy runspider src/kanji-spider.py --output=kanji.json
```