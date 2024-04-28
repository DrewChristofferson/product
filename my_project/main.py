import sys

# sys.path.append('../')  # Add parent directory to Python path

from .scraper.job_scraper import scrape_jobs
from .scraper.job_details_scraper import scrape_details
from .scraper.bulk_update_data import bulk_update
from .old_files.json_to_csv import update_csv
from .old_files.csv_to_sheets import update_google_sheet
from .utils.csv_to_airtable import update_airtable
from .utils.dedup import handle_duplicates
from .companies.get_company_details import update_companies
from .old_files.failory_scrape import get_unicorns, add_extra_companies_to_list
from .companies.compare_crunchbase import compare_with_crunchbase

def main():
    # Initialize components or resources
    # (e.g., database connections, logging setup)
    arguments = sys.argv[1:]

    if arguments[0] == "--jobs":
        scrape_jobs()
    elif arguments[0] == "--details":
        scrape_details()
    elif arguments[0] == "--bulk":
        bulk_update()
    elif arguments[0] == "--google":
        update_google_sheet()
    elif arguments[0] == "--full":
        end_to_end_run()
    elif arguments[0] == "--airtable":
        update_airtable()
    elif arguments[0] == "--json_to_csv":
        update_csv()
    elif arguments[0] == "--dedup":
        handle_duplicates()
    elif arguments[0] == "--companies":
        update_companies()
    elif arguments[0] == "--failory":
        get_unicorns()
    elif arguments[0] == "--add_companies":
        add_extra_companies_to_list()
    elif arguments[0] == "--compare-crunchbase":
        compare_with_crunchbase()
    else:
        print("Please use a parameter")


# Additional logic and control flow here
def end_to_end_run():
    scrape_jobs()

# to ensure that main() is only executed when the script is run as the main program, rather than being imported as a module. 
if __name__ == "__main__":
    main()
