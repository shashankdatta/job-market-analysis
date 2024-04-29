# Data Scraping Team

This is a job posting scrapper for indeed.com

### Environment Configuration
```linux
conda create -n scrapper python==3.10
conda activate
pip3 install -r requirement
```

### Start Crawling
```linux
python3 run.py
```
By default, the program will scrape the 10 most recent job postings for software engineering positions in New York City from Indeed.com.

For each job, you'll see job title, company name, salary range, requirements and job types.
