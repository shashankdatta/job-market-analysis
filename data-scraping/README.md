# Data Scraping Team

This is a scraper for **software engineer** job postings on indeed.com in **New York City**.

### Environment Configuration
```linux
conda create -n scrapper python==3.10
conda activate
pip3 install -r requirements.txt
```
Indeed.com has anti scraping protection. This scrapper uses [oxylabs](https://oxylabs.io/) to bypass it.

In order to enable oxylabs, set `OXY_USERNAME` and `OXY_PASSWORD` as your environment variables.

```linux
export OXY_USERNAME = 'your_username'
export OXY_PASSWORD = 'your_password'
```

### Start Crawling

Usage:

```linux
python3 run.py <start_page_num> <end_page_num>
```
Parameters:
- <start_page_num>: The starting page number, must be a positive integer.
- <end_page_num>: The ending page number, must be a positive integer and not less than the starting page number.

Example:
- To process data from page 10 to page 20:
```linux
python3 run.py 10 20
```

### Results
For each job, company name, job title, salary, skills, education, benefits, experience and responsibilities are extracted.

Example:
```json
{
    "company name": "Quantifi",
    "job title": "Software Developer",
    "salary": "$105,000 - $120,000 a year",
    "skills": [
      "Java",
      "Financial services",
      "C++",
      "C#",
      "Product management"
    ],
    "education": [
      "Bachelor's degree",
      "Doctoral degree",
      "Master's degree"
    ],
    "benefits": [
      "401(k)",
      "AD&D insurance",
      "Commuter assistance",
      "Dental insurance",
      "Disability insurance",
      "Health insurance"
    ],
    "experience": [],
    "responsibilities": [
      "Design, development, implementation, and testing of new features in Quantifi's comprehensive software products",
      "Working with Sales and Product Management in the ongoing development of our products",
      "Working with our clients in understanding their needs and providing support when needed"
    ]
  },
```
