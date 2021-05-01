from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import BASE_URL, CHROMEDRIVER_PATH, KEYWORDS, SIBLING_PARENT_XPATH
from selenium.webdriver.common.action_chains import ActionChains
from helpers import time_difference_fmt

from pathlib import Path
Path('./logs').mkdir(exist_ok=True)

import logging
logging.basicConfig(level=logging.INFO, filename='./logs/jobscrap.log', filemode='w')

class JobScrapper(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        self.list_company_name = []
        self.list_job_posting_time = []
        self.list_career_level = []
        self.list_company_size = []
        self.list_company_industry = []
        self.list_company_description = []
        self.list_employment_type = []
        self.list_job_function = []

    def visit_job_search():
        for keyword in KEYWORDS:
            driver.get(BASE_URL)
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'searchKeywordsField'))).send_keys(keyword)

            search_element = driver.find_element(By.ID, 'searchKeywordsField')
            search_element.send_keys(Keys.ENTER) #input the keyword to search bar

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.ID, 'jobList')))

            pagination_elements = driver.find_elements(By.ID, 'pagination')

            if len(pagination_elements) > 0:  # pagination element exist
                pag_element = pagination_elements[0]
                option_elements = pag_element.find_elements(
                    By.XPATH, '//*[@id="pagination"]/option')
                max_page = int(option_elements[-1].text)
                logging.info(f"{keyword} keyword search results max page: {max_page}")

                base_job_url = driver.current_url

                for page in range(1, max_page+1):
                    logger.info(f"Current Page: {base_job_url}{page}")
                    driver.get(f"{base_job_url}{page}")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.ID, 'jobList')))
                    article_elements = driver.find_elements(By.XPATH, '//article')

                    for i, article_element in enumerate(article_elements):
                        time_element = article_element.find_element(By.TAG_NAME, 'time')
                        job_post_iso_time = time_element.get_attribute("datetime")
                        job_posted_time = time_difference_fmt(posted_time=job_post_iso_time)
                        
                        job_card_element = driver.find_element(By.XPATH, f"//article[@data-automation='job-card-{i}']//div//h1/a")
                        driver.execute_script("arguments[0].scrollIntoView(true)", job_card_element)
                        driver.execute_script("arguments[0].click()", job_card_element)
                        
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-automation='splitModeJobDetailsScrollWrapper']"))
                        )
                        
                        scrap_jobs_data()
                        print('=========')

    def scrap_jobs_data():
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//div[@data-automation='detailsTitle']//span"))
        )
        company_element = driver.find_element(By.XPATH, "//div[@data-automation='detailsTitle']//span")
        logger.info(company_element.text)
        print(company_element.text)
        
        desc_element = driver.find_element(By.XPATH, "//div[@data-automation='jobDescription']")
        logging.info(desc_element.text)
            
        job_highlights_elements = driver.find_elements(By.XPATH, "//div[@data-automation='job-details-job-highlights']")
        if len(job_highlights_elements) >= 1: #check element if exist or not
            job_highlight_element = driver.find_element(By.XPATH, "//div[@data-automation='job-details-job-highlights']") #will be append to detail description
            job_highlight_element_text = job_highlight_element.text
            logging.info(job_highlight_element_text)
            print(job_highlight_element_text)

        contains_benefit_elements = driver.find_elements(By.XPATH, "//span[text() = 'Benefits & Others']")
        print(f"Any benefits? {len(contains_benefit_elements)}")
        if len(contains_benefit_elements) >= 1:
            benefit_element = contains_benefit_elements[-1].find_element(By.XPATH, SIBLING_PARENT_XPATH)
            benefit_text = benefit_element.text
            logging.info(benefit_text)
            print(benefit_text)
        
        career_level_text = get_additional_information('Career Level')
        job_function_text = get_additional_information('Job Specializations')
        employment_type_text = get_additional_information('Job Type')
        company_size_text = get_additional_information('Company Size')
        industry_text = get_additional_information('Industry')

        print(career_level_text)
        print(job_function_text)
        print(employment_type_text)
        print(company_size_text)
        print(industry_text)

    def get_additional_information(text_prop):
        prop_elements = driver.find_elements(By.XPATH, f"//span[text() = '{text_prop}']")
        if len(prop_elements) >= 1:
            sibling_element = prop_elements[-1].find_element(By.XPATH, SIBLING_PARENT_XPATH)
            information_text = sibling_element.text
        else:
            information_text = f'No {text_prop}'
        
        return information_text
