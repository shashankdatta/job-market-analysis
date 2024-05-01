# Data Scraping Team

This is a job posting scrapper for indeed.com

### Environment Configuration
```linux
conda create -n scrapper python==3.10
conda activate
pip3 install -r requirement.txt
```
Indeed.com has anti scraping protection. This scrapper uses [Scrapfly](https://scrapfly.io/) to bypass it. First you need to sign up for a scrapfly account and get a free API key from your dashboard.

Then set `SCRAPFLY_KEY` as your environment variable.

```linux
export SCRAPFLY_KEY = 'your_api_key'
```

### Start Crawling
```linux
python3 run.py
```

You can define POSITION, LOCATION and PAGES (number of web pages) you want to scrap from indeed.com in `run.py`.
