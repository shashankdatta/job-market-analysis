# http request to indeed.com
from scrapfly import ScrapflyClient, ScrapeConfig, ScrapflyScrapeError
import re, json, urllib, math, os
from loguru import logger as log

SCRAPFLY_KEY = os.getenv("SCRAPFLY_KEY")

SCRAPFLY = ScrapflyClient(key=SCRAPFLY_KEY)
BASE_CONFIG = {
    # Indeed.com requires Anti Scraping Protection bypass feature.
    "asp": True,
    "country": "US",
}

# parse response to get job information
def parse_search_page(result):
    """Find hidden web data of search results in Indeed.com search page HTML"""
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', result.content)
    data = json.loads(data[0])
    return {
        "results": data["metaData"]["mosaicProviderJobCardsModel"]["results"],
        "meta": data["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"],
    }

# change the url parameter, parse response from following consecutive pages
def _add_url_parameter(url, **kwargs):
    """Add or replace GET parameters in a URL"""
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4])) # url_parts[4] is query parameters string
    query.update(kwargs)
    url_parts[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(url_parts)

# get max 1000 jobs
async def scrape_search(url: str, max_results: int = 1000) -> list[dict]:
    """Scrape Indeed.com search for job listing previews"""
    log.info(f"scraping search: {url}")
    result_first_page = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    data_first_page = parse_search_page(result_first_page)

    results = data_first_page["results"]
    total_results = sum(category["jobCount"] for category in data_first_page["meta"])
    if total_results > max_results:
        total_results = max_results

    print(f"scraping remaining {(total_results - 10) / 10} pages")
    other_pages = [
        ScrapeConfig(_add_url_parameter(url, start=offset), **BASE_CONFIG)
        for offset in range(10, total_results + 10, 10)
    ]
    log.info("found total pages {} search pages", math.ceil(total_results / 10))
    async for result in SCRAPFLY.concurrent_scrape(other_pages):
        if not isinstance(result, ScrapflyScrapeError):
            data = parse_search_page(result)
            results.extend(data["results"])
        else:
            log.error(f"failed to scrape {result.api_response.config['url']}, got: {result.message}")
    return clean_results(results)

def clean_results(results):
    """Clean up job results"""
    clean_results = []
    for job in results:
        for requirement in job["jobCardRequirementsModel"]["jobOnlyRequirements"]:
            requirement.pop("attrId", None)
            requirement.pop("attrSuid", None)
            requirement.pop("qstLabel", None)
            requirement.pop("qstType", None)
            requirement.pop("value", None)
        clean_results.append({
            "position title": job["title"],
            "company name": job["company"],
            "salary range": '$'+str(int(job["extractedSalary"]["min"]//1000))+'K-$'+str(int(job["extractedSalary"]["min"]//1000))+'K' if "extractedSalary" in job else None,
            "requirements": job["jobCardRequirementsModel"]["jobOnlyRequirements"],
            "job types": job["jobTypes"],
        })
    return clean_results