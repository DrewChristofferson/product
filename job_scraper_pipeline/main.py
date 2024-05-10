import sys

# sys.path.append('../')  # Add parent directory to Python path

from .scraper.job_scraper import scrape_jobs

def main():
    # Initialize components or resources
    # (e.g., database connections, logging setup)
    arguments = sys.argv[1:]

    if arguments[0] == "--jobs":
        scrape_jobs()
    else:
        scrape_jobs()

# to ensure that main() is only executed when the script is run as the main program, rather than being imported as a module. 
if __name__ == "__main__":
    main()
