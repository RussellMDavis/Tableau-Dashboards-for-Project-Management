#!/bin/env python3
#SBATCH --job-name=web_scrap
#SBATCH --output=web_scrap.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cores=1
#SBATCH --mem=100G
#SBATCH --time=8:00:00


import urllib
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import re
from string import ascii_uppercase

def URL_concat(job = '', city = 'Boston'):
    URL_first = "https://www.indeed.com/jobs?q="
    
    URL_mid = "&l="
    
    return URL_first + job + URL_mid + city

#########
list_of_professions = []

for letter in ascii_uppercase:
    html_professions = requests.get('https://www.indeed.com/find-jobs.jsp?title='+str(letter))
    soup_professions = BeautifulSoup(html_professions.content, 'html.parser', from_encoding="utf-8")
    
    for each in soup_professions.find_all('table', {'id': 'letters'}):
        for profession in each.find_all(class_='job'):
            list_of_professions.append(profession.text)

list_of_professions = [w.replace(' ', '+') for w in list_of_professions]
            
list_of_professions.append('Data+Scientist')
list_of_professions.append('')
###############

cities = set(['New+York', 'Chicago', 'San+Francisco', 'Austin', 'Seattle', 
    'Los+Angeles', 'Philadelphia', 'Atlanta', 'Dallas', 'Pittsburgh', 
    'Portland', 'Phoenix', 'Denver', 'Houston', 'Miami', 
    'Charlottesville', 'Richmond', 'Baltimore', 'Harrisonburg', 'San+Antonio', 'San+Diego', 'San+Jose'
    'Austin', 'Jacksonville', 'Indianapolis', 'Columbus', 'Fort+Worth', 'Charlotte', 'Detroit', 'El+Paso', 
    'Memphis', 'Boston', 'Nashville', 'Louisville', 'Milwaukee', 'Las+Vegas', 'Albuquerque', 'Tucson', 
    'Fresno', 'Sacramento', 'Long+Beach', 'Mesa', 'Virginia+Beach', 'Norfolk', 'Atlanta', 'Colorado+Springs',
    'Raleigh', 'Omaha', 'Oakland', 'Tulsa', 'Minneapolis', 'Cleveland', 'Wichita', 'Arlington', 'New+Orleans', 
    'Bakersfield', 'Tampa', 'Honolulu', 'Anaheim', 'Aurora', 'Santa+Ana', 'Riverside', 'Corpus+Christi', 'Pittsburgh', 
    'Lexington', 'Anchorage', 'Cincinnati', 'Baton+Rouge', 'Chesapeake', 'Alexandria', 'Fairfax', 'Herndon',
    'Reston', 'Roanoke'])

#################


def create_df(job=[''], cit = ['Boston', 'Houston']):
    
    out_df = pd.DataFrame(columns=["City", "Job", 
                                   "Full-time", 'Part-time', 'Contract', 'Commission', 'Temporary', 'Internship',
                                  'Entry Level', 'Mid Level', 'Senior Level', 'Top Employer_1', 'Top Employer_2',
                                   'Top Employer_3','Top Employer_4','Top Employer_5', 'avg_salary'])


    
    ci = 0
    for city in cit:
        print(city)
        for j in job:
            ci += 1
            if j == '':
                job_temp = 'None'
            else:
                job_temp = j
            positions = {'Full-time':None, 'Part-time':None, 'Contract':None, 'Commission':None, 'Temporary':None, 'Internship':None}
            experience_levels = {'Entry Level': None, 'Mid Level': None, 'Senior Level': None}
            top_employers = {'Top Employer_1': None, 'Top Employer_2': None, 'Top Employer_3': None, 'Top Employer_4': None, 'Top Employer_5': None}

            #print(city)
            html = requests.get(URL_concat(j, city))
            soup = BeautifulSoup(html.content, 'html.parser', from_encoding="utf-8")

            for each in soup.find_all('div', {'id': 'rb_Job Type'}):
                try: 
                    title = each.find(class_='rbList').text
                except:
                    title = 'None'

            for each in soup.find_all('div', {'id': 'rb_Experience Level'}):
                try: 
                    exp = each.find(class_='rbList').text
                except:
                    exp = 'None'
                    

            #for each in soup.find_all('div', id_= "rb_Job Type" ):
            for each in soup.find_all('div', {'id': 'rb_Company'}):
                try: 
                    emps = each.find(class_='rbList').text#.replace('\n', '')
                except:
                    emps = 'None'
                    
            for each in soup.find_all('div', {'id': 'SALARY_rbo'}):
                try: 
                    sals = each.find(class_='rbList').text#.replace('\n', '')
                except:
                    sals = 'None'
                
            split_sals = sals.split('\n')     
            split_emps = emps.split('\n')
            split_title = title.split('\n')
            split_exp = exp.split('\n')

            for k in positions.keys():
                for t in split_title:
                    if k in t:
                        positions[k] = int(t.split(' ')[1].replace('(', '').replace(')', ''))
            for e in experience_levels.keys():
                for s in split_exp:
                    if e in s:
                        experience_levels[e] = int(s.split(' ')[2].replace('(', '').replace(')', ''))
            for indx, emp in enumerate(top_employers.keys()):
                if (indx+1)*2 < len(split_emps):
                    top_employers[emp] = split_emps[(indx+1)*2].split(' (')[0]
                    
            list_of_sals = []
            list_of_nums = []

            for s in split_sals:
                if '$' in s:
                    sal_and_num = s.split(' ')
                    sal = int(sal_and_num[0].strip('$').replace(',', ''))
                    num = int(sal_and_num[1].replace('(', '').replace(')', ''))
                    list_of_sals.append(sal)
                    list_of_nums.append(num)

            list_of_nums_cut = []

            for indx in range(len(list_of_nums) -1):
                list_of_nums_cut.append(list_of_nums[indx] - list_of_nums[indx+1])

            list_of_nums_cut.append(list_of_nums[-1])


            list_sal_times_num = [a*b for a,b in zip(list_of_sals, list_of_nums_cut)]

            avg_sal = sum(list_sal_times_num)/sum(list_of_nums_cut)

            out_df = out_df.append(pd.Series([city, job_temp] + list(positions.values()) + list(experience_levels.values()) + list(top_employers.values()) + [avg_sal], index=list(out_df.columns)), ignore_index=True)
        if ci % 100 == 0:
            print(i)
    return out_df

out_df = create_df(list_of_professions, cit=cities)

out_df.to_csv('out_df.csv')