# http request to indeed.com
import re, json, urllib
from loguru import logger as log
import requests
from pprint import pprint
from pathlib import Path

output = Path(__file__).parent / "results"
output.mkdir(exist_ok=True)

# Structure payload.
payload = {
    'source': 'universal_ecommerce',
    'url': 'https://www.indeed.com/jobs?q=software+engineer&l=New+York%2C+New+York',
}

# Get response.
response = requests.request(
    'POST',
    'https://realtime.oxylabs.io/v1/queries',
    auth=('user', 'pass1'),
    json=payload,
)

# Instead of response with job status and results url, this will return the
# JSON response with the result.
pprint(response.json())

# utility function
def _add_url_parameter(url, **kwargs):
    """Add or replace GET parameters in a URL"""
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4])) # url_parts[4] is query parameters string
    query.update(kwargs)
    url_parts[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(url_parts)

def extract_job_keys(page_response):
    """Extract job keys from Indeed.com search page HTML"""
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', page_response.content)
    if not data:
        print("failed to scrape search page")
        return
    data = json.loads(data[0])
    results = data["metaData"]["mosaicProviderJobCardsModel"]["results"],
    
    job_keys = []
    for job in results:
        job_keys.append(job["jobkey"])
    return job_keys

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
async def get_job_keys(url: str, start_page: int = 1, end_page: int = 5) -> list[str]:
    """Scrape Indeed.com search for job listing previews"""
    if start_page == 1:
        result_first_page = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
        data_first_page = parse_search_page(result_first_page)
        print("scrapped page 1")

        if data_first_page is None:
            return
        # get job keys from first page
        results = data_first_page["results"]
        jobs = await indeed.scrape_jobs(job_keys)
        output.joinpath("job_dataset.json").write_text(json.dumps(jobs, indent=2, ensure_ascii=False))
        other_pages = [
            ScrapeConfig(_add_url_parameter(url, start=offset), **BASE_CONFIG)
            for offset in range(10, (end_page-1)*10+1, 10)
        ]

        pages = 2
        async for result in SCRAPFLY.concurrent_scrape(other_pages):
            if not isinstance(result, ScrapflyScrapeError):
                data = parse_search_page(result)
                print("scrapped page ", pages)
                results.extend(data["results"])
            else:
                log.error(f"failed to scrape {result.api_response.config['url']}, got: {result.message}")
            pages += 1
    else:
        results = []
        other_pages = [
            ScrapeConfig(_add_url_parameter(url, start=offset), **BASE_CONFIG)
            for offset in range((start_page-1)*10, (end_page-1)*10+1, 10)
        ]

        pages = 2
        async for result in SCRAPFLY.concurrent_scrape(other_pages):
            if not isinstance(result, ScrapflyScrapeError):
                data = parse_search_page(result)
                print("scrapped page ", pages)
                results.extend(data["results"])
            else:
                log.error(f"failed to scrape {result.api_response.config['url']}, got: {result.message}")
            pages += 1

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

# scrape all job details on a search page
async def save_jobs(page):
    if page > 1:
        payload["url"] = f"https://www.indeed.com/jobs?q=software+engineer&l=New+York%2C+New+York&start={(page-1)*10}"

    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=('user', 'pass1'),
        json=payload,
    )
    job_keys = extract_job_keys(response.json()["results"])
    if not job_keys:
        print("failed to scrape job keys")
        return
    jobs = await scrape_jobs(job_keys)
    output.joinpath(f"job_dataset_{page}.json").write_text(json.dumps(jobs, indent=2, ensure_ascii=False))
