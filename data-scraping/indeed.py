# http request to indeed.com
import re, json, urllib, os
import requests
import logging
from pathlib import Path

output = Path(__file__).parent / "results"
output.mkdir(exist_ok=True)
URL = "https://www.indeed.com/jobs?q=software+engineer&l=New+York%2C+New+York"

# create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # set the level of logging

# create a file handler
file_handler = logging.FileHandler('my_logs.log')
file_handler.setLevel(logging.INFO)  # set the level of logging for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# add the handler to the logger
logger.addHandler(file_handler)

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
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', page_response)
    if not data:
        print("failed to scrape search page")
        return
    data = json.loads(data[0])
    results = data["metaData"]["mosaicProviderJobCardsModel"]["results"]
    
    job_keys = []
    for job in results:
        job_keys.append(job["jobkey"])
    return job_keys

def parse_job_page(result):
    """Find hidden web data of job details in Indeed.com job page HTML"""
    # extract company name, job title
    data2 = re.findall(r'window.mosaic.providerData\["mosaic-provider-reportcontent"\]=(\{.+?\});', result)
    if data2:
        data2 = json.loads(data2[0])

        # extract education and skills
        data1 = re.findall(r'window.mosaic.providerData\["js-match-insights-provider"\]=(\{.+?\});', result)
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
        data3 = re.findall(r'window._initialData=(\{.+?\});', result)
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


def scrape_jobs(job_keys: list[str]):
    """scrape job details from job page for given job keys"""
    urls = [f"https://www.indeed.com/m/basecamp/viewjob?viewtype=embedded&jk={job_key}" for job_key in job_keys]
    scraped = []
    for url in urls:
        scraped.append(parse_job_page(get_html_response(url)))
    return scraped


def get_html_response(url):
    # Structure payload.
    payload = {
        'source': 'universal',
        'url': url,
    }
    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=(os.getenv('OXY_USERNAME'), 
              os.getenv('OXY_PASSWORD')
        ), 
        json=payload,
    )
    if response.status_code != 200:
        print(f"Failed to get response from {url}")
        return
    return response.json()["results"][0]["content"]

# scrape all job details on a search page
def save_jobs(page_num):
    print(f"scraping page {page_num}")
    logger.info(f"scraping page {page_num}")
    if page_num > 1:
        url = _add_url_parameter(URL, start=(page_num-1)*10)
    else:
        url = URL

    job_keys = extract_job_keys(get_html_response(url))
    if not job_keys:
        print("failed to scrape job keys")
        return
    jobs = scrape_jobs(job_keys)
    output.joinpath(f"job_dataset_{page_num}.json").write_text(json.dumps(jobs, indent=2, ensure_ascii=False))
    print(f"scraped {len(jobs)} jobs saved")
    logger.info(f"scraped {len(jobs)} jobs saved")
