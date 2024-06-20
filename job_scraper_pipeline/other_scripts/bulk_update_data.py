from ..scraper.db_requests.get_companies import pull_companies, get_one_company
from ..scraper.db_requests.get_investors import pull_investors
from ..scraper.db_requests.update_company import add_investors, update_company
from ..scraper.db_requests.get_jobs import pull_existing_jobs_for_company
from ..scraper.db_requests.update_job import update_job
from ..scraper.openai.test_openai import get_investors, gpt_get_company_info, gpt_get_company_metrics, test_openai, sythesize_job_posting_wrapper
from ..utils.utils_parsing import get_url_content, get_element_text
from ..utils.utils_selenium import set_up_selenium_browser
from ..scraper.s3.test import upload_txt_to_s3, download_file_from_s3, upload_png_files_to_s3
from ..utils.utils_general import get_domain, round_corners_image, make_image_square, save_image_to_file, convert_to_png
from ..scraper.sub_pipelines.job_details_scraper_company import temp_fetch_job_details
import json
from datetime import datetime
import re
import requests
import tweepy
from dotenv import load_dotenv
import os

"""
check walmart jobs
rerun details
"""

TO_ADD = [
    "Alloy",
    "Solo.io",
    "1Password",
    "Target Corporation",
   "The Home Depot",
    "Tinder",
    "Uniswap",
    "X",
    "JP Morgan Chase"
]


COMPS = [
    "Symphony Communication Services",
    "1inch Limited",
    "1Password",
    "ActiveCampaign",
    "Activision Blizzard",
    "Adobe Inc.",
    "Affirm",
    "Airbnb",
    "Airtable",
    "Alchemy",
    "Algolia",
    "Alteryx",
    "American Express",
    "Apollo GraphQL",
    "Apple Inc.",
    "Armis Security",
    "Autodesk",
    "Automation Anywhere",
    "Bill.com",
    "Bumble Inc.",
    "Cadence Translate",
    "Capital One",
    "Cart.com",
    "Chewy, Inc.",
    "Cisco Systems, Inc.",
    "Coupa Software",
    "DailyPay, Inc.",
    "G2",
    "GitHub",
    "H2O.ai",
    "HashiCorp",
    "Hilton Worldwide",
    "HoneyBook",
    "Innovaccer",
    "iTrustCapital Inc.",
    "JP Morgan Chase",
    "LinkedIn",
    "Macy's Inc.",
    "Marriott International",
    "Microsoft",
    "Mindbody Business",
    "Notion Labs Inc.",
    "NVIDIA",
    "OneStream Software",
    "Oracle Corporation",
    "OutSystems",
    "Pinterest",
    "Prodege",
    "Progressive Corporation",
    "project44",
    "Quantum Metric",
    "Redesign Health",
    "Redfin",
    "Redis",
    "Reify Health",
    "ReliaQuest",
    "Reltio",
    "Remote",
    "Replit",
    "Rightway",
    "Ripple",
    "Rippling",
    "Roku, Inc.",
    "Roofstock",
    "Route",
    "Runway",
    "SailPoint",
    "Salesforce",
    "Salsify",
    "Salt Security",
    "Scale AI",
    "SeatGeek",
    "Securonix",
    "Semperis",
    "Sendbird",
    "ServiceNow",
    "ServiceTitan",
    "ShipBob",
    "Shopify",
    "Sidecar Health",
    "Sift",
    "Sightline Payments",
    "Signifyd",
    "Sirius XM",
    "Sisense",
    "Slack",
    "SmartRecruiters",
    "SMS Assist",
    "Snap Inc.",
    "Snapdocs",
    "SnapLogic",
    "Socure",
    "Solo.io",
    "Splashtop",
    "SpotOn",
    "Spotter",
    "Spring Health",
    "Square",
    "Squarespace",
    "Standard Cognition",
    "Starburst",
    "Stash",
    "State Farm",
    "Stax",
    "StockX",
    "Stord",
    "Strava",
    "Stripe",
    "StubHub",
    "Stytch",
    "Sunbit",
    "Swiftly",
    "Sword Health",
    "Syniverse",
    "Sysdig",
    "T-Mobile",
    "Tackle",
    "Talkdesk",
    "Talos",
    "Tanium",
    "Target Corporation",
    "TaxBit",
    "Tealium",
    "Tebra",
    "Tekion",
    "Teleport",
    "Temporal Technologies",
    "Tempus",
    "Tenable",
    "Tesla",
    "thatgamecompany",
    "The Brandtech Group",
    "The Home Depot",
    "The New York Times",
    "The Trade Desk",
    "The Walt Disney Company",
    "The Zebra",
    "ThoughtSpot",
    "Thumbtack",
    "TikTok",
    "Timescale",
    "Tinder",
    "Tipalti",
    "Toast",
    "Together AI",
    "Tonal",
    "Topgolf Entertainment Group",
    "Tradeshift",
    "TradingView",
    "Transcarent",
    "Transmit Security",
    "TransUnion",
    "Tresata",
    "Triller",
    "Truepill",
    "Trumid",
    "Turing",
    "Turo",
    "Twilio",
    "Typeface",
    "U.S. Bancorp",
    "Uber",
    "Udemy",
    "UiPath",
    "Uniphore",
    "Uniswap",
    "Unit",
    "Unite Us",
    "United Airlines",
    "Unqork",
    "Unstoppable Domains",
    "Upgrade",
    "Upside",
    "Uptake",
    "Upwork",
    "Vagaro",
    "Vanta",
    "Varo Money",
    "VAST Data",
    "Vectra AI",
    "Veho",
    "Velocity Global",
    "Venafi",
    "Vendr",
    "Verbit",
    "Vercel",
    "Verily",
    "Verizon",
    "Verkada",
    "Vestwell",
    "Via",
    "VideoAmp",
    "Visa Inc.",
    "Vise",
    "VMware",
    "VTS",
    "Walmart",
    "Warner Bros. Discovery",
    "Wasabi Technologies",
    "Wayfair",
    "Waymo",
    "Wealthfront",
    "Webflow",
    "Weee!",
    "Weights & Biases",
    "Wells Fargo",
    "Whatnot",
    "WHOOP",
    "Wise",
    "Wix",
    "Wiz",
    "Wonder",
    "Workato",
    "Workday",
    "Workiva",
    "Workrise",
    "Wrapbook",
    "X",
    "Yahoo",
    "Yelp",
    "Yotpo",
    "Yuga Labs",
    "Yugabyte",
    "Zapier",
    "Zebec",
    "ZenBusiness",
    "Zendesk",
    "Zenoti",
    "Zeta",
    "Zillow",
    "Zip",
    "Zocdoc",
    "Zoom Video Communications, Inc.",
    "ZoomInfo",
    "Zscaler",
    "Zynga"
]


def upload_imgs_to_airtable(filter_companies):
    companies = pull_companies()
    print(TO_ADD)
    for company in companies:
        if company['name'] in TO_ADD:
            img_url = f"https://careers-in-product-company-logos.s3.amazonaws.com/images/{company['name'].replace(' ', '+')}.png"
            print(company['name'])
            data = {
                "logo": [
                    {
                        "url": img_url
                    }
                ]
            }
            response = update_company(company['airtable_id'], data)

"""
clearbit logos
1inch Limited
1Password
ActiveCampaign
Activision Blizzard
Adobe Inc.
Affirm
Airbnb
Airtable
Alchemy
Algolia
Alteryx
American Express
Apollo GraphQL
Apple Inc.
Armis Security
Autodesk
Automation Anywhere
Bill.com
Bumble Inc.
Cadence Translate
Capital One
Cart.com
Chewy, Inc.
Cisco Systems, Inc.
Coupa Software
DailyPay, Inc.
G2
GitHub
H2O.ai
HashiCorp
Hilton Worldwide
HoneyBook
Innovaccer
iTrustCapital Inc.
JP Morgan Chase
LinkedIn
Macy's Inc.
Marriott International
Microsoft
Mindbody Business
Notion Labs Inc.
NVIDIA
OneStream Software
Oracle Corporation
OutSystems
Pinterest
Prodege
Progressive Corporation
project44
Quantum Metric
Redesign Health
Redfin
Redis
Reify Health
ReliaQuest
Reltio
Remote
Replit
Rightway
Ripple
Rippling
Roku, Inc.
Roofstock
Route
Runway
SailPoint
Salesforce
Salsify
Salt Security
Scale AI
SeatGeek
Securonix
Semperis
Sendbird
ServiceNow
ServiceTitan
ShipBob
Shopify
Sidecar Health
Sift
Sightline Payments
Signifyd
Sirius XM
Sisense
Slack
SmartRecruiters
SMS Assist
Snap Inc.
Snapdocs
SnapLogic
Socure
Solo.io
Splashtop
SpotOn
Spotter
Spring Health
Square
Squarespace
Standard Cognition
Starburst
Stash
State Farm
Stax
StockX
Stord
Strava
Stripe
StubHub
Stytch
Sunbit
Swiftly
Sword Health
Symphony Communication Services
Syniverse
Sysdig
T-Mobile
Tackle
Talkdesk
Talos
Tanium
Target Corporation
TaxBit
Tealium
Tebra
Tekion
Teleport
Temporal Technologies
Tempus
Tenable
Tesla
thatgamecompany
The Brandtech Group
The Home Depot
The New York Times
The Trade Desk
The Walt Disney Company
The Zebra
ThoughtSpot
Thumbtack
TikTok
Timescale
Tinder
Tipalti
Toast
Together AI
Tonal
Topgolf Entertainment Group
Tradeshift
TradingView
Transcarent
Transmit Security
TransUnion
Tresata
Triller
Truepill
Trumid
Turing
Turo
Twilio
Typeface
U.S. Bancorp
Uber
Udemy
UiPath
Uniphore
Uniswap
Unit
Unite Us
United Airlines
Unqork
Unstoppable Domains
Upgrade
Upside
Uptake
Upwork
Vagaro
Vanta
Varo Money
VAST Data
Vectra AI
Veho
Velocity Global
Venafi
Vendr
Verbit
Vercel
Verily
Verizon
Verkada
Vestwell
Via
VideoAmp
Visa Inc.
Vise
VMware
VTS
Walmart
Warner Bros. Discovery
Wasabi Technologies
Wayfair
Waymo
Wealthfront
Webflow
Weee!
Weights & Biases
Wells Fargo
Whatnot
WHOOP
Wise
Wix
Wiz
Wonder
Workato
Workday
Workiva
Workrise
Wrapbook
X
Yahoo
Yelp
Yotpo
Yuga Labs
Yugabyte
Zapier
Zebec
ZenBusiness
Zendesk
Zenoti
Zeta
Zillow
Zip
Zocdoc
Zoom Video Communications, Inc.
ZoomInfo
Zscaler
Zynga

"""

def get_text_fields(company_name):
    companies = pull_companies(company_name)
    for company in companies:
        print(company['name'])
        jobs = pull_existing_jobs_for_company(company['name']) 
        for job in jobs:
            fields_to_update = {}
            job_responsibilities_text = ""
            min_qualifications_text = ""
            preferred_qualifications_text = ""
            for responsibility in job['job_responsibilities']:
                job_responsibilities_text += f"{responsibility}. "
            for min_qual in job['minimum_qualifications']:
                min_qualifications_text += f"{min_qual}. "
            for preferred_qual in job['preferred_qualifications']:
                preferred_qualifications_text += f"{preferred_qual}. "

            fields_to_update['preferred_qualifications_text'] = preferred_qualifications_text
            fields_to_update['min_qualifications_text'] = min_qualifications_text
            fields_to_update['job_responsibilities_text'] = job_responsibilities_text
        update_job(job["id"], fields_to_update)


def upload_imgs_to_s3():
    directory = 'logos_manual'
    bucket_name = 'careers-in-product-company-logos'
    urls = upload_png_files_to_s3(directory, bucket_name)
    print(urls)

def clean_images():
    # Specify the directory path
    directory = 'logos_manual'

    # Iterate over files in the directory
    for filename in os.listdir(directory):
        if ".png" in filename or ".jpeg" in filename:
            company_name = filename.split('.')[0]
            input_filepath = f"{directory}/{filename}"
            output_filepath = input_filepath
            
            radius = 15
            if ".jpeg" in filename:
                input_filepath = convert_to_png(input_filepath)
                output_filepath = input_filepath
                print(input_filepath)
            square_logo = make_image_square(None, input_filepath)
            rounded_edges_logo = round_corners_image(square_logo, radius)
            save_image_to_file(rounded_edges_logo, output_filepath)
            print(f"Downloaded logo for {company_name} to {output_filepath}")

"""
chewy
automation anywhere
"""

def get_logos():
    companies = pull_companies()
    # company_domains = ["apple.com", "google.com", "microsoft.com", "https://www.reifyhealth.com", "https://www.redventures.com"]
    for i in range(len(companies)):
        companies[i]['website'] = get_domain(companies[i]['website'])
    for company in companies:
        get_logo(company['website'], company['name'])

def get_logo(company_domain, company_name):
    url = f"https://logo.clearbit.com/{company_domain}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            file_path = f"logos/{company_name}.png"
            radius = 15
            square_logo = make_image_square(response.content)
            rounded_edges_logo = round_corners_image(square_logo, radius)
            save_image_to_file(rounded_edges_logo, file_path)
            print(f"Downloaded logo for {company_domain} to {file_path}")
        except Exception as e:
            print(f"Error processing image: {e}")
    else:
        print(f"Failed to download logo for {company_domain}. Status code: {response.status_code}")



def get_job_posting_data(company_name, *fields):
    companies = pull_companies(company_name)
    for company in companies:
        print(company['name'])
        jobs = pull_existing_jobs_for_company(company['name']) 
        for job in jobs:
            print(job['job_title'])
            if job['raw_jd_uploaded']:
                if not job['job_details_added']:
                    content = download_file_from_s3(company['name'], job['id']) 
                    response = sythesize_job_posting_wrapper(content, company['name'], job['job_title'], *fields)
                    response['job_details_added'] = True
                    update_job(job['id'], response)
                else:
                    print('job details already added')
            else:
                print('no jd in s3 for this job or no linkedin url')

    # print(response)

def read_s3_job(company_name):
    jobs = pull_existing_jobs_for_company(company_name) 
    for job in jobs:
        content = download_file_from_s3(company_name, job['id']) 


def job_descriptions_to_s3(company_name):
    selenium_browser = set_up_selenium_browser()
    companies = pull_companies(company_name)
    for company in companies:
        print(company['name'])
        jobs = pull_existing_jobs_for_company(company['name']) 
        for job in jobs:
            job_post_url = None
            html_classname = None
            xpath = None
            job_eligible = False
            if job['job_post_linkedin_url'] and job['raw_jd_uploaded'] is None:
                html_classname = "description__text"
                job_post_url = job['job_post_linkedin_url']
                job_eligible = True
            elif job['job_post_company_url'] and job['job_details_xpath'] and job['raw_jd_uploaded'] is None:
                xpath = job['job_details_xpath']
                job_post_url = job['job_post_company_url']
                job_eligible = True
            else:
                print("insufficient url data or jd already uploaded")
            
            if job_eligible:
                try:
                    job_to_s3(job, job_post_url, html_classname, xpath[0], selenium_browser)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                else:
                    # Code to execute if no exceptions are raised
                    print("Successfully added jd to s3!")
                    update_job(job['id'], {'raw_jd_uploaded': True})


def job_to_s3(job, url, class_name=None, xpath=None, browser=None):
    if 'linkedin' in url:
        content = get_url_content(url)
        jd_content = content.find("div", class_=class_name)
        jd_text = jd_content.get_text().strip()
    else:
        jd_text = temp_fetch_job_details(url, xpath, browser)
    print(job['company_name'][0], job['id'])
    upload_txt_to_s3(job['company_name'][0], job['id'], jd_text)


def onboard_company(company_name, company_website=None):
    company_airtable = get_one_company(company_name)
    # print(company_airtable)
    id = company_airtable['id']
    website = ''
    if 'website' in company_airtable['fields']:
        website = company_airtable['fields']['website']
    else:
        website = company_website
    gpt_response = gpt_get_company_info(company_name, website)
    updated_company = update_company(id, gpt_response)

def get_airtable_logos(companies_filter):
    companies = pull_companies()
    print(companies[0])
    for company in companies:
        # URL of the image
        logo_data = company['logo'][0]
        image_url = logo_data['url']

        # Download the image
        response = requests.get(image_url)

        save_path  = f"airtable_logos/{company['Industry Name'][0]}/{company['Count of Jobs']}_{logo_data['filename']}"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the image to a file
        with open(save_path, 'wb') as file:
            file.write(response.content)

        print(f"Image downloaded and saved as {logo_data['filename']}")

def update_existing_company_data():
    companies = pull_companies()
    for company in companies:
        if not company["hq_country"]:
            gpt_response = gpt_get_company_info(company['name'], company['website'])
            updated_company = update_company(company['airtable_id'], gpt_response)

def update_company_fields(companies_filter, *fields):
    companies_response = pull_companies(companies_filter)
    for company in companies_response:
        fields_to_update = {}
        gpt_response = gpt_get_company_metrics(company['name'], company['website'], *fields)
        for field in fields:
            if gpt_response[field] and company[field] != gpt_response[field]:
                fields_to_update[field] = gpt_response[field]
            else:
                print("not updating")
        updated_company = update_company(company['airtable_id'], fields_to_update)


def update_company_investors():
    investors_map = {}
    investors_list_str = ""
    companies = pull_companies()
    # print(companies)
    investors = pull_investors()
    for investor in investors:
        investors_map[investor['fields']['name']] = investor['id']
        investors_list_str += f"{investor['fields']['name']}, "
    # print(investors_map)

    for company in companies:
        print(company['name'], investors_list_str)
        investors_gpt = get_investors(company['name'], investors_list_str)
        formatted_list_investors = []
        for response in investors_gpt:
            for investor in response['investors']:
                if investor in investors_map:
                    formatted_list_investors.append(investors_map[investor])
        print(formatted_list_investors)
        if formatted_list_investors:
            add_investors(company['airtable_id'], formatted_list_investors)
        # company_investors = company['Top 5 Investors']
        # if company_investors:
        #     formatted_list_investors = []
        #     for company_investor in company_investors:
        #         if company_investor in investors_map:
        #             formatted_list_investors.append(investors_map[company_investor])
        #     if formatted_list_investors:
        #         add_investors(company['airtable_id'], formatted_list_investors)
        #         print(company['name'], formatted_list_investors)


