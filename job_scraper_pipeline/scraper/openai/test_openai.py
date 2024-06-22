from .utils.set_openai_config import set_open_config
from ...utils.utils_general import is_valid_json
from datetime import datetime
import json
import time

GPT_ROLE = """
    You are a market researcher that needs to find information about a company. Respond in a valid JSON structure (e.g., no unnecessary whitespace or non-ASCII characters). Don't include don't include '\n' in the JSON. If you can't find an answer, put a value of null, do not guess. Sites like Pitchbook, TechCrunch, Crunchbase, or other PR articles typcially are good places to look for company funding and valuation data. Here are the field(s) that you are looking for (don't include any other fields in the JSON):
    """

FIELD_DEFINITIONS = {
    'name': "Name of the company", 
    'formerly_known_as': "List of names that the company was formerly known as", 
    'website': "Home page URL for the company", 
    'careers_page': "The URL of the company's current job openings", 
    'hq_city': "The city of the company headquarters", 
    'hq_state': "If the company headquarters is in the United States, return the state of the company headquarters in its two-letter abbreviation (e.g., CA, NY, TX)", 
    'hq_country': "The country of the company headquarters (return 'United States' if the country is the US)", 
    'description': "A paragraph summarizing what the company is", 
    'long_description': "A longer multi-paragraph description that goes more in depth on the products and services the company offers", 
    'company_mission': "The company mission (return None if you can't find it)",
    'business_model': "Description of how the company makes money",
    'market_memo': "A brief memo by a market researcher about how the company is set up for success and why the company will win in its industry",
    'competitors': "A list of up to 5 competitors for this company",
    'office_locations': "List of the US cities where this company has all of it's locations (format response as city name, state abbrev.)", 
    'year_founded': "The year of the company's founding", 
    'founders': "The list of founders for the company", 
    'founder_resume': "A list of background/resumes for each founder highlighting their education and experience before starting the company (One list item per founder, each item should be one paragraph, and don't use colon notation)",
    'ceo_name': "The name of the current CEO of the company",
    'is_ceo_founder': "Whether the CEO is one of the company founders (return 'YES' or 'NO')", 
    'ceo_resume': "A background/resume of the CEO highlighting their education and experience before becoming the CEO of the company (don't use colon notation and if the ceo is also a founder, you can use the same paragraph as the one for the founder background)",
    'num_employees': "Integer for the number of employees that work for the company", 
    'ipo_status': "Whether the company has gone through an IPO (select from Public, Private, or Delisted)", 
    'ipo_year': "What year the company went public - public companies only", 
    'ticker_symbol': "The ticker symbol - public companies only", 
    'estimated_revenue': "Integer for the estimated annual 2023 or 2022 revenue (In $M with no decimal points)", 
    'acquisitions': "List of company names of up to 5 of biggest companies that this company has acquired", 
    'acquired_by': "Name of the company that acquired this company if applicable", 
    'acquired_year': "Year the company was acquired if applicable", 
    'benefits': "List of the top benefits or noteworthy perks that the company offers (maximum 10 benefits/perks)", 
    'equity_series': "[For pre-IPO companies only] The most recent equity series raised in startup fundraising (select from Seed, or Series A-Z)", 
    'total_funding': "Integer for the total funding a company has received - pre_IPO companies only (In $M with no decimal points)", 
    'company_valuation': "[For pre-IPO companies only] Float for the company valuation after the most recent fundraising round (In $B with one decimal point)"
}

GPT_ROLE_JOBS = """
    You are a product manager looking for you next role. You are browsing a job post for an open position at a tech company with the goal to extract the relevant information and synthesize into fields in a JSON object. Respond in a valid JSON structure (e.g., no unnecessary whitespace or non-ASCII characters). Don't include don't include '\n' in the JSON response. Don't put ```json in your response. Here are the field(s) that you are looking for (don't include any other fields in the JSON):
    """

JOB_FIELD_DEFINITIONS = {
    'is_remote': "Whether the job is or can be a remote position (return 'YES' or 'NO', if remote work is not mentioned put 'NO')",
    'is_people_manager': "Whether the role includes responsibilities managing other people or not (return 'YES' or 'NO', if management responsibilities are not mentioned put 'NO')",
    'product_name': "The name of the product or a very short description of the product that this role is for",
    'product_summary': "A paragraph summarizing first what the product is and then how the person in this role will impact the product.", 
    'key_stakeholders': "A list of all the stakeholder teams mentioned that the person in this role will work with (Choose from 'Engineering', 'Design', 'Marketing', 'Sales', 'Data Science', 'Customer Support', 'Finance', 'Business', 'Legal', 'Operations'",
    'minimum_qualifications': "A list of all the qualifications that a candidate should have",
    'preferred_qualifications': "A list of all the qualifications that are preferred or nice-to-haves (there should be no overlap with the minimum_qualifications)",
    'product_type': "Whether it's an internal or customer-facing product (return 'Internal' or 'Customer-facing')",
    'min_base_salary': "Integer of the minimum of the range mentioned (return null if not listed)", 
    'max_base_salary': "Integer of the maximum of the range mentioned (return null if not listed)", 
    'is_equity_offered': "Whether or not equity compensation or stock options are offered for this role (return 'YES' or 'NO', and anything other than a definitive yes should be no)",
    'years_experience_req': "Integer (not a range) of the number of years of relevant work expereince required, but format the value in a String (return "" if there's no years experience mentioned)",
    'job_responsibilities': "A list of all the things expected to do in this role",
    'minimum_education_degree_level': "The education degree level required (Choose from null, 'Bachelor', 'Master', 'PhD')",
    'preferred_education_degree_level': "The education degree level preferred (Choose from null, 'Bachelor', 'Master', 'PhD')",
    'preferred_undergrad_field_of_study': "List of preferred undergrad degrees for this role",
    'product_management_skills': "List of up to product management specific skills mentioned in this job description",
    'benefits': 'List of benefits that this company offers for this role'
}


def sythesize_job_posting_wrapper(job_posting, company_name, job_title, *fields, max_retries=2):
    retries = 0
    while retries <= max_retries:
        retries += 1
        response_content = synthesize_job_posting(job_posting, company_name, job_title, *fields)
        if is_valid_json(response_content):
            json_response = json.loads(response_content)
            return json_response
        else:
            if max_retries == retries:
                print("reached max retries")
                return(None)


def synthesize_job_posting(job_posting, company_name, job_title, *fields):
    fields_str = ""
    if fields:
        for field in fields:
            fields_str += f"{field}: {JOB_FIELD_DEFINITIONS[field]},"
    else:
        fields_str = JOB_FIELD_DEFINITIONS
    client = set_open_config()
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"{GPT_ROLE_JOBS} {fields_str}"},
        {"role": "user", "content": f"Analyze the job description for {job_title} and {company_name}. This is the raw text of the job description: {job_posting} "}
    ])
    res_msg = completion.choices[0].message.content
    return res_msg


def get_investors(company_name, investors):
    client = set_open_config()

    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": 
        f"You are a research analyst and need to give accurate information. Your response should be a JSON list with elements that have the follwing fields - company_name: name of the company, investors: list of names of investor firms. You can also put a single element 'None' if the company didn't leverage venture capital firms. Don't include ```json in your response. Your response should be a valid JSON object. While looking for companies, prioritize these: Accel, Andreessen Horowitz, Benchmark, Bessemer Venture Partners, Founders Fund, General Catalyst, Google Ventures, Greylock Partners, Index Ventures, Insight Partners, Institutional Venture Partners (IVP), Khosla Ventures, Kleiner Perkins, Lightspeed Venture Partners, New Enterprise Associates (NEA), Sequoia Capital, Thrive Capital, Y Combinator. Also, if any from this list are in your response, please spell it the same way in your response."
        },
        {"role": "user", "content": f"Can you give me up to 10 of the most prominent venture capital firms that invested in the following companies?\n{company_name}?"}
    ]
    )
    content = completion.choices[0].message.content
    print(content)
    json_response = json.loads(completion.choices[0].message.content)

    return(json_response)

def gpt_get_company_metrics(company_name, company_website, *fields):
    fields_str = ""
    for field in fields:
        fields_str += f"{field}: {FIELD_DEFINITIONS[field]},"
    
    client = set_open_config()
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": f"{GPT_ROLE} {fields_str}"},
        {"role": "user", "content": f"Please find me the details for {company_name}. If you find multiple companies with the same name, use the company with this website: {company_website}. Don't include ```json in your response."}
    ])
    res_msg = completion.choices[0].message.content
    print(res_msg)
    print(company_name)
    json_response = json.loads(res_msg)
    return json_response


def gpt_get_company_info(company_name, company_website, max_retries=2):
    retries = 0
    while retries <= max_retries:
        retries += 1
        response_content = make_company_info_request(company_name, company_website)
        if is_valid_json(response_content):
            json_response = json.loads(response_content)
            return json_response
        else:
            if max_retries == retries:
                print("reached max retries")
                return(None)


def make_company_info_request(company_name, company_website):
    client = set_open_config()

    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": 
        """
        Your job is to take the name and website of a company and respond with detailed company information. 
        
        You will need to respond in a JSON format (please don't include '\n' in the json) with the following fields - 
        name: Name of the company, 
        formerly_known_as: List of names that the company was formerly known as, 
        website: Home page URL for the company, 
        careers_page: The URL of the company's current job openings, 
        hq_city: The city of the company headquarters, 
        hq_state: If the company headquarters is in the United States, return the state of the company headquarters in its two-letter abbreviation (e.g., CA, NY, TX), 
        hq_country: The country of the company headquarters (return 'United States' if the country is the US), 
        description: A paragraph summarizing what the company is, 
        long_description: A longer multi-paragraph description that goes more in depth on the products and services the company offers, 
        company_mission: The company mission (return None if you can't find it),
        business_model: Description of how the company makes money,
        market_memo: A brief memo by a market researcher about how the company is set up for success and why the company will win in its industry,
        competitors: A list of up to 5 competitors for this company,
        office_locations: List of cities where this company has offices (just return city name, don't include state!), 
        year_founded: The year of the company's founding, 
        founders: The list of founders for the company, 
        founder_resume: A list of background/resumes for each founder highlighting their education and experience before starting the company (One list item per founder, each item should be one paragraph, and don't use colon notation),
        ceo_name: The name of the current CEO of the company,
        is_ceo_founder: whether the CEO is one of the company founders (return 'YES' or 'NO'), 
        ceo_resume: A background/resume of the CEO highlighting their education and experience before becoming the CEO of the company (don't use colon notation and if the ceo is also a founder, you can use the same paragraph as the one for the founder background),
        num_employees: String for the number of employees that work for the company (select from 1-10, 11-50, 51-100, 101-250, 251-500, 501-1000, 1001-5000, 5001-10000, or 10000+), 
        ipo_status: Whether the company has gone through an IPO (select from Public, Private, or Delisted), 
        ipo_year: What year the company went public - public companies only, 
        ticker_symbol: The ticker symbol - public companies only, 
        estimated_revenue: String for the estimated annual 2023 revenue (select from 'less than $1M', '$1M to $5M', '$5M to $10M', '$10M to $50M', '$50M to $100M', '$100M to $500M', '$500M to $1B', '$1B to $10B', '$10B to $20B', '$20B to $50B', '$50B to $100B', or '$100B+'), 
        acquisitions: List of company names of up to 5 of biggest companies that this company has acquired, 
        acquired_by: Name of the company that acquired this company if applicable, 
        acquired_year: Year the company was acquired if applicable, 
        benefits: List of the top benefits or noteworthy perks that the company offers (maximum 10 benefits/perks), 
        equity_series: The last equity series raised - pre-IPO companies only (select from Seed, or Series A-Z), 
        total_funding: String for the total funding a company has received - pre_IPO companies only (select from 'less than $100M', '$101M to $250M', '251M to $500M', '$501M to $1B', '$1B to $2B', or '$2B+'), 
        company_valuation: String for the company valuation - pre_IPO companies only (select from 'less than $1B', '$1.1B to $2B', '$2.1B to $3B', '$3.1B to $5B', '$5.1B to $10B', or '$10B+'). 
        
        Also, please make sure your response is valid JSON (e.g., no unnecessary whitespace or non-ASCII characters). Don't include ```json in your response. If you can't find information for a field, assign a value of null instead.
        """
        },
        {"role": "user", "content": f"Please find me the details for {company_name}. The website for the company is {company_website}. If you're not sure about a field put a value of null for it. Don't include ```json in your response."}
    ]
    )

    res_msg = completion.choices[0].message.content
    print(res_msg)
    return(res_msg)



    """
    use something like prompt templates to be able to make the prompt cleaner
    use an example to make it more clear what the format should be
    Use embeddings with langchain and pinecone to give gpt context on available jobs, companies as well as candidate data like resume pdf

    https://www.reddit.com/r/OpenAI/comments/1280a25/how_are_people_feeding_gpt_large_amounts_of_data/
    https://medium.com/@anderson.riciamorim/a-quick-guide-to-use-your-own-data-in-gpt-with-retrieval-augmented-generation-73f3e9d54bcd
    
    
    old fields for companies

    employee_equity_plan: whether stock options are offered (select 'YES' or 'NO'), 
    401k_match: whether 401(k) with match is offered (select 'YES' or 'NO'), 
    medical_insurance: whether medical insurance is provided (select 'YES' or 'NO'), 
    dental_insurance: whether dental insurance is provided (select 'YES' or 'NO'),
    vision_insurance: whether vision insurance is provided (select 'YES' or 'NO'), 
    life_insurance: whether life insurance is provided (select 'YES' or 'NO'), 
    disability_insurance: whether disability insurance is provided (select 'YES' or 'NO'), 
    unlimited_pto: whether unlimited PTO is offered (select 'YES' or 'NO'), 
    pto_days: The total number of pto days if not unlimited, 
    maternity_leave_weeks: number of weeks given for maternity leave and those that give birth (if the company has unlimited pto assign a value of null), 
    paternity_leave_weeks: number of weeks give for paternity leave and those that don't give birth, 
    tuition_reimbursement: whether tuition reimbursement is offered (select 'YES' or 'NO'), 
    fitness_stipend: whether a wellness/fitness stipend is offered (select 'YES' or 'NO'), 
    home_office_stipend: whether home office stipend is offered (select 'YES' or 'NO'), 
    
    """





    # Old functions

def test_openai(job_posting):
    client = set_open_config()

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": 
        f"Your job is to take a job posting and synthesize it into a JSON format (please don't include '\n' in the json) with the following fields - job_title: String name of job role, posted_date: Date for when the job was posted (for reference, today's date is {datetime.now()}) in python datetime type, locations: A list of all locations for the job, specifying the city and state (an example format is 'San Francisco, CA', don't include country!), job_summary: A paragraph summarizing what product is and what the role is, min_salary: The minimum of the range mentioned, max_salary: The maximum of the range mentioned, years_experience_req: Integer of the number of years required in product management. Also, please make sure your response is valid JSON (e.g., no unnecessary whitespace or non-ASCII characters). If you can't find information for a field, assign a value of null instead. If the date is 30+ days ago, then just use one month from today as the posted_date"
        },
        {"role": "user", "content": job_posting}
    ]
    )
    content_read = completion.choices[0].message.content
    print(content_read)
    json_response = json.loads(completion.choices[0].message.content)

    return(json_response)


# def test_openai_jobs(job_listing):
#     client = set_open_config()

#     completion = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": 
#         f"Your job is to take a list of raw data of some job postings and synthesize it into a JSON list with elements that have the following fields (please don't include \n in the json) - job_title: String name of job role, location: The location for the job, specifying the city and state (an example format is 'San Francisco, CA', don't include country!), job_url: the link to the job posting page. Also, please make sure your response is valid JSON (e.g., no unnecessary whitespace or non-ASCII characters). If you can't find information for a field, don't add the job to the list."
#         },
#         {"role": "user", "content": job_listing}
#     ]
#     )
#     content = completion.choices[0].message.content
#     # print(content)
#     json_response = json.loads(completion.choices[0].message.content)

#     return(json_response)