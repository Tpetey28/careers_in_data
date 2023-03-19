# importing libraries needed

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from transform import *

# setting options for chromedriver
options = Options()
options.add_argument('start-maximized')

# initializing chromdriver for selenium
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

#------ SCRAPING DATA ANALYST POSTINGS---------------------------------------------------------------------------------------------------------

start = time.time()

df_final = pd.DataFrame()

urls = ['https://www.indeed.com/jobs?q=data+analyst&fromage=1&vjk=33797408d01286b4', 
        'https://www.indeed.com/jobs?q=data+scientist&fromage=1&vjk=7540aeac4a38acb9', 
        'https://www.indeed.com/jobs?q=data+engineer&fromage=1&vjk=a4ecbaa8e54a43f5']

jobs = ['analyst','scientist','engineer']
    
for url, job in zip(urls, jobs):
    # getting first URL 
    driver.get(url)

    # initializing empty lists to store links to job postings for data analysts
    listing_links = []

    #pages is used for testing to ensure all pages are hit. It is commented out when not being used for testing
    #pages = []

    # finding if the 'next page' button exists in the url requested
    next_btn_status = len(driver.find_elements(By.XPATH, "//a[@data-testid='pagination-page-next']"))

    ''' The below while loop will loop through 'Data Analyst' job postings posted in the last 24 hours. The purpose of this loop is to simply
        grab the urls to the specific job postings. A second loop will be needed to iterate through the job posting URLs later on in the script'''

    # while a 'next button' exists, run the loop
    while next_btn_status > 0:

        try:

            # grabs the current url to be used if an exception arises and we need to pick up where we left off
            url = driver.current_url
            url = str(url)

            # page listings stores collection of 'a' tags that include links to job postings
            page_listings = driver.find_elements(By.XPATH, '//div/h2/a')

            # curr_page stores the current page number. This is used for testing to ensure that all pages were parsed
            #curr_page = driver.find_element(By.XPATH, "//button[@data-testid='pagination-page-current']")
            #pages.append(curr_page.text)

            # nested for loop iterates through each job listing and adds the dedicated link to posting to listing_links list
            for listing in page_listings:
                link = listing.get_attribute('href')
                listing_links.append(link)

            # next_btn_status will be 1 if there is a 'next page' button, and 0 if not. This determines if the while loop continues or finishes
            next_btn_status = len(driver.find_elements(By.XPATH, "//a[@data-testid='pagination-page-next']"))

            # next_btn stores the actual button to the next page which will be clicked to go to the next page of listings and continue looping
            next_btn = driver.find_element(By.XPATH, "//a[@data-testid='pagination-page-next']")

            # clicks the 'next page' button
            next_btn.click()


        except:

            # if an exception is raised, we print the url that had the issue during testing. It is commented out when not used for testing
            #print('exception raised: {}'.format(url))
            time.sleep(5)

            # web-browser is closed here. Indeed attempts to limit bot traffic, so a new session must be establishe to continue
            driver.close()

            # waiting 5 seconds to allow browser to terminate successfully before moving on
            time.sleep(5)

            # establishes new driver session to circumvent Indeeds efforts to limit bot traffic
            driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

            # opens the browser back to the url that threw the exception
            driver.get(url)

            # waiting 5 seconds to allow the page to load
            time.sleep(5)

            # after a new session is established and page re-loads, we continue with the loop
            continue


    # initializing empty lists to store data scraped to be transformed into dataframe later
    detail_list = []
    salary_list = []
    title_list = []
    other_list = []

    for link in listing_links:

        try:
            driver.get(link)
            time.sleep(1)

            fail_test = driver.find_element(By.XPATH, '//div[1]/h1/span').text

            # grabs the current url to be used if an exception arises and we need to pick up where we left off
            url = driver.current_url
            url = str(url)

            details_exist = driver.find_elements(By.XPATH, "/html/body")
            if len(details_exist) > 0:
                details = driver.find_element(By.XPATH, "/html/body").text
                detail_list.append(details)
            else:
                detail_list.append('')


            salary_exists = driver.find_elements(By.XPATH, '//*[@id="salaryInfoAndJobType"]/span[1]')
            if len(salary_exists) > 0:
                salary = driver.find_element(By.XPATH, '//*[@id="salaryInfoAndJobType"]/span[1]').text
                salary_list.append(salary)
            else:
                salary_list.append('')

            title_exists = title = driver.find_elements(By.XPATH, '//div[1]/h1/span')
            if len(title_exists) > 0:
                title = driver.find_element(By.XPATH, '//div[1]/h1/span').text
                title_list.append(title)
            else:
                title_list.append('')



            other_exist = driver.find_elements(By.CLASS_NAME, "jobsearch-CompanyInfoContainer")
            if len(other_exist) > 0:
                other = driver.find_element(By.CLASS_NAME, "jobsearch-CompanyInfoContainer").text
                other_list.append(other)
            else:
                other_list.append('')


        except:

            # if an exception is raised, we print the url that had the issue during testing. It is commented out when not               used for testing
            #print('exception raised: {}'.format(url))
            time.sleep(5)

            # web-browser is closed here. Indeed attempts to limit bot traffic, so a new session must be establishe to                   continue
            driver.close()

            # waiting 5 seconds to allow browser to terminate successfully before moving on
            time.sleep(5)

            # establishes new driver session to circumvent Indeeds efforts to limit bot traffic
            driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

            # opens the browser back to the url that threw the exception
            driver.get(url)

            # waiting 5 seconds to allow the page to load
            time.sleep(5)

            # after a new session is established and page re-loads, we continue with the loop
            continue

    print('len salary: {}'.format(len(salary_list)))
    print('len title: {}'.format(len(title_list)))
    print('len detail: {}'.format(len(detail_list)))
    print('len other: {}'.format(len(other_list)))

    df = pd.DataFrame({
        'position':title_list,
        'pay': salary_list,
        'details': detail_list,
        'other': other_list,
    })
    
    df = transform(df)

    df.to_excel('{}.xlsx'.format(job), index = False)
    
    df_final = df_final.append(df, ignore_index = True)
    

df_final.to_excel('transformed data.xlsx', index = False)

end = time.time()

print('Total Minutes: {}'.format((end - start)/60))
