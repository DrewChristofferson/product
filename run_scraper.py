import sys
import argparse

# sys.path.append('../')  # Add parent directory to Python path
from job_scraper_pipeline.scraper.job_scraper import scrape_jobs
from job_scraper_pipeline.scraper.testing.test_scrape import test_scrape
from job_scraper_pipeline.scraper.fmp.test_fmp import test_fmp
from job_scraper_pipeline.other_scripts.bulk_update_data import upload_imgs_to_airtable, onboard_company, update_company_fields, job_descriptions_to_s3, read_s3_job, get_job_posting_data, get_logos, clean_images, upload_imgs_to_s3, get_airtable_logos
from companies_to_run import companies_to_run


def main(args):
    print(f"Script to run: {args.script}")
    print(f"Companies to filter: {args.filter_companies}")
    print(f"N company: {args.company_name}")
    print(f"Fields to update: {args.fields}")

    if args.script == "jobs":
        scrape_jobs(args.company_name)
    elif args.script == "upload_imgs":
        upload_imgs_to_s3()
    elif args.script == "upload_imgs_airtable":
        upload_imgs_to_airtable(args.filter_companies)
    elif args.script == "round":
        clean_images()
    elif args.script == "fmp":
        test_fmp()
    elif args.script == "logos":
        get_logos()
    elif args.script == "analyze_job":
        get_job_posting_data(args.company_name)
    elif args.script == "get-airtable-logos":
        get_airtable_logos(args.filter_companies)
    elif args.script == "jd-to-s3":
        job_descriptions_to_s3(args.company_name)
    elif args.script == "update-company":
        if args.fields:
            if args.filter_companies:
                update_company_fields(args.filter_companies, *args.fields)
            else:
               update_company_fields(None, *args.fields) 
        else:
            print("No fields provided to update.")
    elif args.script == "onboard":
        if args.fields and len(args.fields) > 1:
            onboard_company(args.fields[0], args.fields[1])
        else:
            onboard_company(args.fields[0])
    else:
        print("Unknown script name. Running default job scraper.")
        scrape_jobs()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Python command-line script to run scripts in the careers pipeline.")
    parser.add_argument("script", type=str, help="Script file to run.")
    parser.add_argument("-C", "--filter_companies", nargs='*', default=companies_to_run, type=str, help="Companies to evaluate or take action on.")
    parser.add_argument("-N", "--company_name", nargs='?', type=str, help="Company to pull jobs for.")
    parser.add_argument("-F", "--fields", nargs='*', help="Your company fields to update.")
    arguments = parser.parse_args()
    print(arguments.script)
    main(arguments)