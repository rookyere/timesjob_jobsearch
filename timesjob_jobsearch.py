from bs4 import BeautifulSoup
import requests, re,sys,time,os  
import pandas as pd


job_role_to_search = input('\nWhat job role do you want to search?: ')
search_cboWorkExp1 = input('\nEnter work experience to search: ') or '5'
remoteJob = input('\nRemote job (y\\n): ').lower() or '\\n'
loc_quest = input('\nDo you want to specify job location? (y\\n): ').lower() or '\\n'
if loc_quest in ['y','Y','yes','YES']:
    job_location = input('\nJob location: ')
else: job_location = ''
result_count = int(input('\nExpected number of search results (1 - 200): '))
if result_count > 200 or result_count < 1:
    sys.exit('\nValue must be greater than 0 and less than 201\n')
jobs_count = 0
search_params = {
    'searchType': 'personalizedSearch',
    'from': 'submit',
    'txtKeywords':job_role_to_search,
    'txtLocation': job_location,
    'cboWorkExp1': search_cboWorkExp1,
    'remoteJob': remoteJob,
    'luceneResultSize' : result_count
}

url = f'https://www.timesjobs.com/candidate/job-search.html'

html_txt = requests.get(url, params=search_params).text
soup = BeautifulSoup(html_txt, 'lxml')
jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

jobs_info_list = []
details_url_list = []

for job in jobs:
    job_info = dict()
    if remoteJob == 'y':
        wfh = job.find('span', class_='jobs-status covid-icon clearfix').text.strip()
        published_date = job.find(text=re.compile('Posted'))
    else: 
        published_date = job.find('span', class_='sim-posted').text.strip()
        wfh = "Employer's location"
    if 'day' in published_date:
        jobs_count+=1
        job_role = job.find('h2').text.strip()
        company_name = job.find('h3', class_='joblist-comp-name').text.strip()
        experience = re.search(r'([0-9]{1,}\s-\s[0-9]{1,})',job.find('ul', class_='top-jd-dtl clearfix').li.text.strip()).group()
        key_skills = job.find('span', class_='srp-skills').text.strip()
        location = job.find('ul',class_='top-jd-dtl clearfix').span.text

        
        print(location)
        if location is None:
            location = ''
        else: location = job.find('ul',class_='top-jd-dtl clearfix').span.text
        further_info = job.header.h2.a['href']

        details_url_list.append(further_info)

        job_info['Role'] = job_role
        job_info['Company name'] = company_name
        job_info['Years of experience'] = experience
        job_info['Key Skills'] = key_skills
        job_info['Published date'] = published_date
        job_info['Further_info'] = further_info
        job_info['Job type'] = wfh
        job_info['Location'] = location

        jobs_info_list.append(job_info)
              
        print(f'''
            Role                : {job_role}
            Company name        : {company_name}
            Years of experience : {experience}
            Key Skills          : {key_skills}
            Published date      : {published_date}
            Further_info        : {further_info}
            Job type            : {wfh}
            Location            : {location}
            ''')

        print('=====================================')
print(requests.get(url, params=search_params).url)


dt = time.localtime()
dt_fmt = time.strftime('%d-%m-%Y-%H:%M', dt)
date_time = dt_fmt.replace(':', '-')

excel_dir = 'Times-jobs'
excel_fn = f'{excel_dir}/{job_role_to_search}' + '-'+ date_time + '.xlsx'

if remoteJob == 'y':
    excel_fn = f'{excel_dir}/{job_role_to_search}' + '-'+ date_time + '-' + 'remote.xlsx'
if not job_location == '':
    excel_fn = f'{excel_dir}/{job_role_to_search}' + '-'+ date_time + '-' + f'remote-{job_location}.xlsx'

if os.path.exists(excel_dir):
    pass
else:
    p=os.makedirs(excel_dir)

df = pd.DataFrame.from_dict(jobs_info_list)
df.to_excel(excel_fn)

print(f'\nTotal jobs found: {jobs_count}')
if len(jobs) == 0:
    print('\nSorry!!! No match found for search criteria')

