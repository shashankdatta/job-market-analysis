from scrapfly import ScrapflyClient, ScrapeConfig, ScrapflyScrapeError
import os, indeed

SCRAPFLY_KEY = os.getenv("SCRAPFLY_KEY")
SCRAPFLY = ScrapflyClient(key=SCRAPFLY_KEY)
BASE_CONFIG = {
    # Indeed.com requires Anti Scraping Protection bypass feature.
    "asp": True,
    "country": "US",
}

url = "https://www.indeed.com/m/basecamp/viewjob?viewtype=embedded&jk=cc7c17837eb91fba"

result = SCRAPFLY.scrape(ScrapeConfig(url, **BASE_CONFIG))
print(indeed.parse_job_page(result))