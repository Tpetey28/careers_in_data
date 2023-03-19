import pandas as pd
import numpy as np
import warnings
warnings.simplefilter("ignore")
from datetime import date


def transform(df):
    
    
    
    ''' Cleaning Up Data to Include Only Data Analyst, Scientist, and Engineer Roles. '''

    # adding 3 new columns to indicate what the roles are 
    df['scientist'] = np.where((df['position'].str.contains('Data')) & (df['position'].str.contains('Scientist')), 1, 0)
    df['analyst'] = np.where((df['position'].str.contains('Data')) & (df['position'].str.contains('Analyst')), 1, 0)
    df['engineer'] = np.where((df['position'].str.contains('Data')) & (df['position'].str.contains('Engineer')), 1, 0)

    # filtering out rows that are not analyst, scientist, or engineer roles

    df = df[(df['scientist'] == 1) | (df['analyst'] == 1) | (df['engineer'] == 1)]

    
    
    
    ''' Cleaning Up Pay/Salary Information '''

    # filtering out rows that do not include pay details

    df = df[(df['pay'].str.contains('year')) | (df['pay'].str.contains('hour'))]

    # splitting hourly vs salary positions into seperate columns and then dropping the 'pay' column

    df.loc[df['pay'].str.contains('year'), 'salary'] = df['pay']
    df.loc[df['pay'].str.contains('hour'), 'hourly'] = df['pay']
    df.drop('pay', inplace = True, axis = 1)

    # cleaning up the salary column and converting to int datatype

    df['salary'] = df['salary'].str.replace(' a year', '')
    df['salary'] = df['salary'].str.replace('$', '')
    df['salary'] = df['salary'].str.replace('From', '').str.strip()
    df['salary'] = df['salary'].str.replace(',','').str.strip()

    # creating 'salary_range' and 'salary_nrange' as seperate df to perform avg calculation of salaries w/ ranges

    salary_range = df.loc[df['salary'].str.contains('-', na = True)]
    salary_nrange = df.loc[~df['salary'].str.contains('-', na = True)]

    # splitting high and low end of salary ranges into sep columns and then assigning the 'salary' with the avg of the low and high

    #salary_range.fillna(0, inplace = True)
    salary_range['high'] = salary_range['salary'].str.split('-').str[1].astype(float)
    salary_range['low'] = salary_range['salary'].str.split('-').str[0].astype(float)
    salary_range['salary'] = (salary_range['low'] + salary_range['high']) / 2

    # joining salary_range & salary_nrange back together into df

    df = pd.concat([salary_range, salary_nrange])
    df['salary'] = df['salary'].astype(float)

    # cleaning up 'hourly' column

    df['hourly'] = df['hourly'].str.replace('Up to ', '')
    df['hourly'] = df['hourly'].str.replace(' an hour', '')
    df['hourly'] = df['hourly'].str.replace('$', '')
    df['hourly'] = df['hourly'].str.replace('From', '').str.strip()

    # creating 'hourly_range' and 'hourly_nrange' as seperate df to perform avg calculation of salaries w/ ranges

    hourly_range = df.loc[df['hourly'].str.contains('-', na = True)]
    hourly_nrange = df.loc[~df['hourly'].str.contains('-', na = True)]

    # splitting high and low end of salary ranges into sep columns and then assigning the 'salary' with the avg of the low and high

    #hourly_range.fillna(0, inplace = True)
    hourly_range['high'] = hourly_range['hourly'].str.split('-').str[1].astype(float)
    hourly_range['low'] = hourly_range['hourly'].str.split('-').str[0].astype(float)
    hourly_range['hourly'] = (hourly_range['low'] + hourly_range['high']) / 2

    # joining salary_range & salary_nrange back together into df

    df = pd.concat([hourly_range, hourly_nrange])
    df['hourly'] = df['hourly'].astype(float)

    # splitting hourly & salary positions into seperate dataframes

    salary = df[df['salary'].notnull()]
    hourly = df[df['hourly'].notnull()]

    # turning hourly wage into salary by multiplying by 2080 and then combining back together into df and dropping unneeded columns

    hourly['salary'] = hourly['hourly'] * 2080
    df = pd.concat([hourly, salary])
    df.drop(['hourly','high','low'], inplace = True, axis = 1)
    
    
    
    
    ''' Cleaning Up Location/Company Information '''

    states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
    }

    # taking organization out of the first line from the other column

    df['organization'] = df['other'].str.split('\n').str[0]

    # splitting other by new line symbols and combining into one line

    df['other'] = df['other'].str.split('\n').str.join(' ')

    # splitting df into 2 new dfs for those that have commas and those that dont

    df_c = df.loc[df['other'].str.contains(',')]
    df_nc = df.loc[~df['other'].str.contains(',')]

    # creating 'last' column in df_c as text after last comma in 'other' column

    df_c['last'] = df_c['other'].str.split(',').str[-1]

    # if state or state abbreviation exists in the columns, creating new column state with location or remote if remote
    for i in range(df_c.shape[0]):
        last = df_c.iloc[i]['last']
        for a, b in states.items():
            df_c.loc[df_c['last'].str.contains('remote'), 'state'] = 'remote'
            df_c.loc[df_c['last'].str.contains('Remote'), 'state'] = 'remote'
            df_c.loc[df_c['last'].str.contains(a), 'state'] = a
            df_c.loc[df_c['last'].str.contains(b), 'state'] = a

    for i in range(df_nc.shape[0]):
        last = df_nc.iloc[i]['other']
        for a, b in states.items():
            df_nc.loc[df_nc['other'].str.contains('remote'), 'state'] = 'remote'
            df_nc.loc[df_nc['other'].str.contains('Remote'), 'state'] = 'remote'
            df_nc.loc[df_nc['other'].str.contains(a), 'state'] = a
            df_nc.loc[df_nc['other'].str.contains(b), 'state'] = a

    # merging df_nc and df_c back to df and dropping columns no longer needed
    df = pd.concat([df_c, df_nc])
    df.drop(['other','last'], inplace = True, axis = 1)
    
    
    
    ''' Cleaning Up Skills ''' 

    skills = ['sql','python','matlab','jupyter','scripting','automation','tableau','visualization','api',
              'powerbi','power bi','domo','nosql','tsql','t-sql','statistics','machine learning','predictive modeling']

    df['details'] = df['details'].str.lower()

    for i in range(df.shape[0]):

        for skill in skills:

            df[skill] = np.where(df['details'].str.contains(skill), 1, 0)
            
    # combining same skillsets w/ different naming conventions

    df['powerbi'] = df['powerbi'] + df['power bi']
    df.loc[df['powerbi'] > 1, 'powerbi'] = 1

    df['tsql'] = df['tsql'] + df['t-sql']
    df.loc[df['tsql'] > 1, 'tsql'] = 1

    df.drop(['power bi', 't-sql', 'details'], inplace = True, axis = 1)
    
    # adds current date as column

    df['today'] = date.today()
    df['today'] = pd.to_datetime(df['today'])
    
    df.drop_duplicates(inplace = True, keep = 'first')

    return df