import sys

# sys.path.append('../')  # Add parent directory to Python path
from .scraper.openai.test_openai import test_openai
from .scraper.job_scraper import scrape_jobs
from .scraper.testing.test_scrape import test_scrape
from .scraper.fmp.test_fmp import test_fmp
from .other_scripts.bulk_update_data import bulk_update, onboard_company
from .scraper.s3.test import s3_test

def main():
    # Initialize components or resources
    # (e.g., database connections, logging setup)
    arguments = sys.argv[1:]

    if arguments[0] == "--jobs":
        scrape_jobs()
    elif arguments[0] == "--openai":
        test_openai()
    elif arguments[0] == "--scraping":
        test_scrape()
    elif arguments[0] == "--fmp":
        test_fmp()
    elif arguments[0] == "--bulk":
        bulk_update()
    elif arguments[0] == "--s3":
        s3_test()
    elif arguments[0] == "--onboard":
        if len(arguments) > 2:
            onboard_company(arguments[1], arguments[2])
        else:
            onboard_company(arguments[1]) 
    else:
        scrape_jobs()

# to ensure that main() is only executed when the script is run as the main program, rather than being imported as a module. 
if __name__ == "__main__":
    main()
