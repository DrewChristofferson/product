from bs4 import BeautifulSoup
import csv
import os
import re
from pyairtable import Api
from dotenv import load_dotenv
from ..old_files.company_mapping import Airtable_codes as airtable_ids, linkedInCompanyCodes as linkedin_ids
from ..utils.company_mapping_2 import airtable_codes as new_airtable_codes 
from ..scraper.utils import set_airtable_config


def compare_with_crunchbase(): 
    with open(f"../my_project/companies/crunchbase-unicorns.html", 'r') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    grid_rows = soup.find_all('tr')

    print(len(grid_rows))
    company_data = []
    for row in grid_rows:
        row_data = []
        cells = row.find_all('td')
        # print(cells)
        for cell in cells:
            cell_data = cell.get_text(strip=True)
            # print(cell_data)
            row_data.append(cell_data)
        company_data.append(row_data)
    
    us_companies = []
    # print(row_data)
    for row in company_data:
        if len(row) > 4 and row[4] == 'United States':
            us_companies.append(row)

    missing_unicorns = []

    for company in us_companies:
        if company[0] in new_airtable_codes:
            # print(f"{company} found in the list ---------")
            airtable = set_airtable_config('tblGwlPqq03yEQjV1')
            valuation = company[1].strip()[1:-1]
            valuation = int(valuation)
            print(valuation, company[1])
            try:
                response = airtable.update(new_airtable_codes[company[0]], {
                    "Last Valuation Amount ($B)": valuation
                })
                print(response['fields']['Name'])
            except Exception as e:
                print(f"failed for {company[0]}")

        else:
            # missing_unicorns.append(company)
            print(f"'{company[0]}',")
    # print(len(missing_unicorns))



# missing crunchbase 

# Cruise, $30B
# Waymo, $30B
# Lineage Logistics, $18B
# CloudKitchens, $15B
# Nuro, $9B
# NYDIG, $7B
# CoreWeave, $7B
# iCapital Network, $6B
# OneStream Software, $6B
# Sierra Space, $5B
# Quantinuum, $5B
# Ava Labs, $5B
# Neuralink, $5B
# Binance.US, $5B
# AngelList, $4B
# Turing.com, $4B
# Skydance Media, $4B
# Inflection AI, $4B
# InsightSoftware, $4B
# Avride, $4B
# Goat Group, $4B
# Aptean, $4B
# Wonder, $4B
# Armis Security, $3B
# Uber Freight, $3B
# Figure, $3B
# Group14 Technologies, $3B
# iCIMS, $3B
# iFIT, $3B
# Transmit Security, $3B
# Ethos Life, $3B
# Figure, $3B
# Plume Design, $3B
# Syniverse, $3B
# VistaJet, $3B
# Mavenir, $3B
# Electrify America, $2B
# Uptake Technologies, $2B
# 1inch Limited, $2B
# Recharge, $2B
# Clear Street, $2B
# Mural, $2B
# Pivot Bio, $2B
# Black Sesame Technologies, $2B
# XtalPi, $2B
# Aleph Holding, $2B
# Saks.com, $2B
# ISN Software, $2B
# ShiftKey, $2B
# Xpansiv, $2B
# MX Technologies, $2B
# NinjaOne, $2B
# Kindbody, $2B
# BitGo, $2B
# NantOmics, $2B
# Ascend Elements, $2B
# NMI, $2B
# Perfect Day, $2B
# Apollo GraphQL, $2B
# Candy Digital, $2B
# fabric, $2B
# Runway, $2B
# Lambda, $2B
# Berachain, $2B
# Zip, $2B
# M1 Holdings, $1B
# Figment, $1B
# Dexterity, $1B
# Papa Inc., $1B
# Wealthfront, $1B
# LIQUiDITY Group, $1B
# EverlyWell, $1B
# Included Health, $1B
# Hotel Engine, $1B
# Zum, $1B
# Mapbox, $1B
# Keyfactor, $1B
# Doc.com, $1B
# Wilson Wolf Corporation, $1B
# Cart.com, $1B
# Incode Technologies, $1B
# Triller, $1B
# Sidewalk Infrastructure Partners, $1B
# Together AI, $1B
# Vectra Networks, $1B
# Human Longevity, $1B
# Iyuno-SDI, $1B
# Form Energy, $1B
# Our Next Energy, $1B
# Lightmatter, $1B
# Proteus Digital Health, $1B
# Innovusion, $1B
# HeadSpin, $1B
# Replit, $1B
# Alphaeon, $1B
# KoBold Metals, $1B
# Enable, $1B
# Lendbuzz, $1B
# Plenty, $1B
# Kong Studios, Inc., $1B
# TeraWatt Infrastructure, $1B
# Atmosphere, $1B
# Colossal Biosciences, $1B
# Adept AI, $1B
# Headway, $1B
# BFMeta, $1B
# Ohmium, $1B
# Avenue One, $1B
# Gradiant, $1B
# Restaurant365, $1B
# VectorBuilder, $1B
# Typeface, $1B
# Imbue, $1B
# Kin Insurance, $1B
# Electric Hydrogen, $1B
# Lyten, $1B
# Prove, $1B
# Metropolis, $1B
# Rokid, $1B
# MaintainX, $1B
# Andalusia Labs, $1B
# Vestwell, $1B
# EmployerDirect Healthcare, $1B
# Insitro, $1B
# ElevenLabs, $1B
# Bugcrowd, $1B
# Polyhedra Network, $1B
# Merkle Manufactory, $1B
# LetsGetChecked, $1B
# Stax, $1B
# UST, $1B
# Securonix, $1B
# Plus, $1B
# FLASH, $1B
# Forward, $1B
# Aqua Security, $1B
# Forte, $1B
# Jellysmack, $1B
# Commonwealth Fusion, $1B
# Resilience, $1B
# OfferUp, $1B
# Wisk Aero, $1B
# FLYR Labs, $1B
# Entrata, $1B
# GoGuardian, $1B
# Mark43, $1B
# FabFitFun, $1B
# Immunai, $1B
# HealthCare.com, $1B
# D2iq, $1B
# TechStyle Fashion Group, $1B
# Cadence Solutions, $1B
# EcoFlow Tech, $1B
# Sightline Payments, $1B
# KKW Beauty, $1B
# Verily, $1B
# Fractal Analytics, $1B
# InvestCloud, $1B
# Emplifi, $1B
# Kendra Scott Design, $1B
# assembly, $1B
# iSpot.tv, $1B
# Semperis, $1B
# Velocity Global, $1B
# Ultima Genomics, $1B
# MNTN, $1B
# Tebra, $1B
# Exterro, $1B
# Prodege, $1B
# TerraPower, $1B
# Palmetto Clean Technology, $1B
# 171



