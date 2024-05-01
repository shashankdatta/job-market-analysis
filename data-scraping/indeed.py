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

# utility function
def _add_url_parameter(url, **kwargs):
    """Add or replace GET parameters in a URL"""
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4])) # url_parts[4] is query parameters string
    query.update(kwargs)
    url_parts[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(url_parts)

def parse_search_page(result):
    """Find hidden web data of search results in Indeed.com search page HTML"""
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', result.content)
    data = json.loads(data[0])
    return {
        "results": data["metaData"]["mosaicProviderJobCardsModel"]["results"],
    }

def parse_job_page(result):
    """Find hidden web data of job details in Indeed.com job page HTML"""
    # extract company name, job title
    data2 = re.findall(r'window.mosaic.providerData\["mosaic-provider-reportcontent"\]=(\{.+?\});', result.content)
    if data2:
        data2 = json.loads(data2[0])

        # extract education and skills
        data1 = re.findall(r'window.mosaic.providerData\["js-match-insights-provider"\]=(\{.+?\});', result.content)
        skills = []
        education = []
        if data1:
            data1 = json.loads(data1[0])
            requirements = data1["requirements"]["list"]
            for item in requirements:
                if item["category"] == "Skills":
                    skills.append(item["displayText"])
                elif item["category"] == "Education":
                    education.append(item["displayText"])

        # extract salary, benefits, experience, responsibilities
        data3 = re.findall(r'window._initialData=(\{.+?\});', result.content)
        benefits = []
        experience = []
        responsibilities = []
        salary = ""
        if data3:
            data3 = json.loads(data3[0])
            # extract salary
            salary_model = data3.get("salaryInfoModel", {})
            if salary_model is not None:
                salary = salary_model.get("salaryText", "0")
            else:
                salary = "0"
            # extract benefits
            benefits_model = data3.get("benefitsModel", {})
            if benefits_model is not None:
                benefits_info = benefits_model.get("benefits", [])
            else:
                benefits_info = []
            for item in benefits_info:
                benefits.append(item["label"])
            # extract experience, responsibilities
            des = data3.get("jobInfoWrapperModel", {}).get("jobInfoModel", {}).get("sanitizedJobDescription", "")
            experience = re.findall(r'<p>Experience.*?<p>\s*<ul>(.+?)</ul>', des, re.DOTALL)
            if experience:
                experience = re.findall(r'<li>(.+?)</li>', experience[0])
            responsibilities = re.findall(r'<p>(?:<b>)?Responsibilities.*?(?:</b>)?</p>\s*<ul>(.+?)</ul>', des, re.DOTALL)
            if responsibilities:
                responsibilities = re.findall(r'<li>(.+?)</li>', responsibilities[0])

        return {
            "company name": data2["companyName"],
            "job title": data2["jobTitle"],
            "salary": salary,
            "skills": skills,
            "education": education,
            "benefits": benefits,
            "experience": experience,
            "responsibilities": responsibilities
        }


# get job keys from search results
async def get_job_keys(url: str, max_pages: int = 5) -> list[str]:
    """Scrape Indeed.com search for job listing previews"""
    result_first_page = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    data_first_page = parse_search_page(result_first_page)

    results = data_first_page["results"]
    other_pages = [
        ScrapeConfig(_add_url_parameter(url, start=offset), **BASE_CONFIG)
        for offset in range(10, max_pages*10, 10)
    ]
    async for result in SCRAPFLY.concurrent_scrape(other_pages):
        if not isinstance(result, ScrapflyScrapeError):
            data = parse_search_page(result)
            results.extend(data["results"])
        else:
            log.error(f"failed to scrape {result.api_response.config['url']}, got: {result.message}")

    # return job keys list
    job_keys = []
    for job in results:
        job_keys.append(job["jobkey"])
    return job_keys


async def scrape_jobs(job_keys: list[str]):
    """scrape job details from job page for given job keys"""
    urls = [f"https://www.indeed.com/m/basecamp/viewjob?viewtype=embedded&jk={job_key}" for job_key in job_keys]
    to_scrape = [ScrapeConfig(url=url, **BASE_CONFIG) for url in urls]
    scraped = []
    async for result in SCRAPFLY.concurrent_scrape(to_scrape):
        scraped.append(parse_job_page(result))
    return scraped