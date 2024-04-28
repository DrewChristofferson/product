# Product Management Job Scraper

## Overview

This Python-based web scraping tool extracts job listings for Product Management positions at top-tier technology companies. It automates the process of gathering job postings from various job boards and company career pages, providing users with a centralized source of job opportunities in the Product Management field.

## Features

- Scrapes job listings from multiple job boards and company career pages simultaneously.
- Filters job listings based on user-defined criteria, such as location, company, or job title.
- Extracts key information from job postings, including job title, company name, location, and job description.
- Provides a user-friendly interface for managing and viewing scraped job listings.

## Installation

1. Clone this repository to your local machine:

```
git clone https://github.com/your_username/product-management-job-scraper.git
```

2. Navigate to the project directory:

```
cd product-management-job-scraper
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

1. Run the scraper script to start scraping job listings:

```
python scraper.py
```


2. Follow the on-screen prompts to specify your search criteria (e.g., location, company, job title).

3. Sit back and relax while the scraper collects job postings from various sources.

4. Once the scraping process is complete, review the extracted job listings in the output file (`jobs.csv` by default).

## Configuration

- You can customize the scraper's behavior by modifying the configuration parameters in `config.py`. For example, you can adjust the list of target websites to scrape or fine-tune the scraping settings.

## FAQs

Data is collected from public and oopen data sources on the internet, and proprietary data licensed from other companies. 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project was inspired by the need for a convenient tool to aggregate Product Management job listings from various sources.
- Special thanks to the developers of the libraries and frameworks used in this project, including BeautifulSoup, Requests, and Selenium.
