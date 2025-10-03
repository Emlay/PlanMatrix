import requests
import pandas as pd
import os
from PlanMatrixVariables import *

uname = os.getlogin()
lesavelocation = f"C:\\Users\\{uname}\\Downloads\\"


def lejson(off, location):
    allthejson={"aptc_override": None, 
    "filter": {"division": "HealthCare", "metal_design_types": None}, 
    "household": 
    {"has_married_couple": False, 
    "income": income, 
    "people": 
    [{"age": age, "aptc_eligible": False, "gender": gender, "has_mec": False, "is_parent": is_parent, "is_pregnant": is_pregnant, "uses_tobacco": uses_tobacco}], 
    "unemployment_received": "None"}, 
    "limit": 10, "market": "Individual", "offset": off, "order": "asc", 
    "place": location, 
    "sort": "premium", "suppressed_plan_ids": [], "year": year}
    return allthejson



# def indivplanurl(elurl):
#     return f"https://marketplace-int.api.healthcare.gov:443/api/v1/plans/{elurl}?year=2025"


currentyear = year
baseurl = "https://marketplace-int.api.healthcare.gov:443/api/v1"
searchurl = f"{baseurl}/plans/search?year={year}"
zipurl = f"{baseurl}/counties/by/zip/{zipcode}?year={year}"
headers = {"Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "en-US,en;q=0.9", "Sec-Ch-Ua": "\"Chromium\";v=\"139\", \"Not;A=Brand\";v=\"99\"", "Content-Type": "text/plain;charset=UTF-8", "Sec-Ch-Ua-Mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36", "Accept": "*/*", "Origin": "https://www.healthcare.gov", "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://www.healthcare.gov/", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=1, i"}

zipfips = requests.get(zipurl, headers=headers)
generalfips = zipfips.json()['counties'][0]
lefips = {}
lefips["zipcode"] = generalfips['zipcode']
lefips["state"] = generalfips['state']
lefips["countyfips"] = generalfips['fips']

current_offset = 0
# ins_packs = []
alltheplans = []
while True:
    print(f"Requesting plans {current_offset} through {10+current_offset}")
    r = requests.post(searchurl, headers=headers, json=lejson(off = current_offset, location=lefips))
    plans = r.json()['plans']
    for plan in plans:
        alltheplans.append(plan)
    # for plan in plans:
    #     ins_packs.append(plan['benefits_url'])
    current_offset = current_offset + 10
    if current_offset > r.json()['total']:
        break


# Retrieve all the details of all of the plans
# df = pd.DataFrame(alltheplans)
# for eachid in df['id'].to_list():
#     r = requests.post(indivplanurl(eachid), headers=burp0_headers, json=indivurlparams)
#     print(r.json()['plan']['benefits'][32])



# Basic Mental Health Inpatient, Deductible, OOP Max and Premium discovery for all via easily available methods.
df = pd.DataFrame(alltheplans)
desireddf = pd.DataFrame(columns=['Issuer', 'Plan Name', 'Premium', 'Mental Health Inpatient Cost', 'Deductible', 'OOP Max'])
for i in range(len(df)):
    issuer = df.loc[i, 'issuer']['name']
    name = df.loc[i, 'name']
    premium = df.loc[i, 'premium']
    benefits = df.loc[i, 'benefits']
    maxoops = df.loc[i, 'moops']
    tiermaxoops = df.loc[i, 'tiered_moops']
    deducts = df.loc[i, 'deductibles']
    for x in benefits:
        if x['type'] == "MENTAL_BEHAVIORAL_HEALTH_INPATIENT_SERVICES":
            mhinco = x['cost_sharings'][0]['display_string']
            befdeductible = x['cost_sharings'][0]['benefit_before_deductible']
    for x in maxoops:
        if x['network_tier'] == "In-Network":
            maxoop = x['amount']
    for x in deducts:
        if x['network_tier'] == 'In-Network':
            netdeduct = x['amount']
    desireddf.loc[i, ['Issuer', 'Plan Name', 'Premium', 'Mental Health Inpatient Cost', 'Deductible', 'OOP Max']] = [issuer, name, premium, mhinco, netdeduct, maxoop]


desireddf.to_excel(f"{lesavelocation}{zipcode}_Plan_Spreadsheet.xlsx", index=False)

# rejected_urls = []
# for url in rejected_urls:
#     filename = url.split("/")[-1]
#     savelocation = "{}{}".format(lesavelocation, filename)
#     print(f"Retrieving {filename} now")
#     r = requests.get(url, headers=headers)
#     if r.status_code == 200:
#         with open(savelocation, 'wb') as f:
#             f.write(r.content)
#         print(f"Saved {savelocation}")
#     else:
#         rejected_urls.append(url)
#         print(f"{filename} returned with a code of {r.status_code}")

# lefiles = os.listdir(lesavelocation)
# for afile in lefiles:
#     reader = pypdf.PdfReader(f"{lesavelocation}{afile}")
#     print(len(reader.pages))