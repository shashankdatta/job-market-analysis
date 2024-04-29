import indeed, json, asyncio
from pathlib import Path

output = Path(__file__).parent / "results"
output.mkdir(exist_ok=True)

position = "software+engineer"
location = "New+York%2C+New+York"

async def run():
    # enable scrapfly cache for basic use
    indeed.BASE_CONFIG["cache"] = True

    print("running Indeed scrape and saving results to ./results directory")

    url = f"https://www.indeed.com/jobs?q={position}&l={location}"
    result_search = await indeed.scrape_search(url, max_results=10)
    output.joinpath("search.json").write_text(json.dumps(result_search, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(run())