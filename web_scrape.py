import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

from tqdm import tqdm

import random

seed = 42
random.seed(seed)
np.random.seed(seed)

p = pd.read_csv('AID_Focus_Final_Dataset.csv', usecols = ['IMO NO', 'Cargo Type'])
print(p.shape)
p = p[p['Cargo Type'].isna() == True]
print(p.shape)
ids = pd.unique(p['IMO NO'])
# ids = [229992]
imo_id = []
cargo_type = []
ages = []

with open('scrape_det.txt', 'w') as f:
    f.close()

for x, i in enumerate(tqdm(ids)):
    
    # print(i)
    url = 'https://www.marinevesseltraffic.com/vessels'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    
    form = soup.find('form', {'id':'vessel-form'})
    
    input_field = form.find('input', {'id': 'search-vessel'})
    # print('***',input_field)
    input_field['value'] = i
    
    action_url = f"?page=1&vessel={input_field['value']}"
    
    post_data = {input_field['name']: input_field['value']}  

    response = requests.get(url+action_url, data=post_data)


    soup = BeautifulSoup(response.text, 'html.parser')

    
    
    imo_mmsi = soup.find('td', {'class' : "vessel_td td_vessel_name"})
    
    if imo_mmsi == None:
        imo_id.append(i)
        ages.append(np.nan)
        cargo_type.append(np.nan)
        with open('scrape_det.txt', 'a') as f:
            f.writelines(f'IMO: {i}\tAge: {np.nan}\tCargo Type: {np.nan}\n')
    
    else:
        ism_info = imo_mmsi.find('b')

        ism_info = ism_info.get_text() # ism_info


        imo_mmsi = imo_mmsi.find('span')
        imo_mmsi = imo_mmsi.findAll('b')
        # print(i, imo_mmsi)
        det = []
        for tag in imo_mmsi:
            det.append(tag.next_sibling.replace(':','').strip())
    
        if len(det) == 1:
            url_2 = f"https://www.marinevesseltraffic.com/ship-owner-manager-ism-data/{ism_info}/{det[0]}/1"
        else:
            url_2 = f"https://www.marinevesseltraffic.com/ship-owner-manager-ism-data/{ism_info}/{det[0]}/{det[1]}"
            # print(url_2)
            response = requests.get(url_2)
            # print(response)
            soup = BeautifulSoup(response.text, 'html.parser')

            soup = soup.find('div', {"class":"ship-owner-manager-ism-info__section"})
            age = soup.find_all('td')
            if age[23].text.strip()!='-':
                age = age[23].text.strip()
                ages.append(age)                
            else:
                age = 2024 - int(age[21].text.strip())
                ages.append(age)
                
            ####
            imo_id.append(det[0])
            cargo_type.append(soup.find_all('td')[5].text.strip())

            with open('scrape_det.txt', 'a') as f:
                f.writelines(f'IMO: {i}\tAge: {age}\tCargo Type: {soup.find_all("td")[5].text.strip()}\n')


df = pd.DataFrame({'imo':imo_id, 'cargo_type':cargo_type, 'age': ages})

df.to_csv('cargo_details.csv', index = False)
