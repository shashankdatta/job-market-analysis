import indeed, json, asyncio
from pathlib import Path

output = Path(__file__).parent / "results"
output.mkdir(exist_ok=True)

POSITION = "software+engineer"
LOCATION = "New+York%2C+New+York"
PAGES = 1

async def run():
    # enable scrapfly cache for basic use
    indeed.BASE_CONFIG["cache"] = True

    print("running Indeed scrape and saving results to ./results directory")

    url = f"https://www.indeed.com/jobs?q={POSITION}&l={LOCATION}"
    job_keys = await indeed.get_job_keys(url, max_pages=PAGES)
    print(f"scraping {len(job_keys)} job keys")
    print(job_keys)
    jobs = await indeed.scrape_jobs(job_keys)
    output.joinpath("job_dataset.json").write_text(json.dumps(jobs, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(run())