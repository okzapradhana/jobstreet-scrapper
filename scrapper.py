import pandas as pd
import os
import pandas_gbq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from config import BASE_URL, CHROMEDRIVER_PATH, KEYWORDS, SIBLING_PARENT_XPATH, LOG_DIR, LOG_INFO_PATH, LOG_INFO_FILEMODE, BIGQUERY_TABLE_NAME
from helpers import time_difference_fmt

from dotenv import load_dotenv
load_dotenv()

from selenium.webdriver.chrome.options import Options
options = Options()
# options.add_argument("--headless")
options.add_argument("window-size=1920,1080")

from pathlib import Path
Path(LOG_DIR).mkdir(exist_ok=True)

import logging
logging.basicConfig(level=logging.INFO, filename=LOG_INFO_PATH, filemode=LOG_INFO_FILEMODE)

class JobScrapper(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = webdriver.Chrome(chrome_options=options, executable_path=CHROMEDRIVER_PATH)
        self.list_company_name = []
        self.list_job_posting_time = []
        self.list_career_level = []
        self.list_company_size = []
        self.list_company_industry = []
        self.list_company_description = []
        self.list_employment_type = []
        self.list_job_function = []

    def begin_scrap(self):
        print(self.driver.get_window_size())

        for keyword in KEYWORDS:
            self.driver.get(BASE_URL)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'searchKeywordsField'))).send_keys(keyword)

            search_element = self.driver.find_element(By.ID, 'searchKeywordsField')
            search_element.send_keys(Keys.ENTER) #input the keyword to search bar

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.ID, 'jobList')))

            pagination_elements = self.driver.find_elements(By.ID, 'pagination')

            if len(pagination_elements) > 0:  # pagination element exist
                pag_element = pagination_elements[0]
                option_elements = pag_element.find_elements(
                    By.XPATH, '//*[@id="pagination"]/option')
                max_page = int(option_elements[-1].text)
                self.logger.info(f"{keyword} keyword search results max page: {max_page}")

                base_job_url = self.driver.current_url

                for page in range(1, max_page+1):
                    self.logger.info(f"Current Page: {base_job_url}{page}")
                    self.driver.get(f"{base_job_url}{page}")
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.ID, 'jobList')))
                    article_elements = self.driver.find_elements(By.XPATH, '//article')

                    for i, article_element in enumerate(article_elements):
                        time_element = article_element.find_element(By.TAG_NAME, 'time')
                        job_post_iso_time = time_element.get_attribute("datetime")
                        job_posted_time = time_difference_fmt(posted_time=job_post_iso_time)
                        self.list_job_posting_time.append(job_posted_time)

                        job_card_element = self.driver.find_element(By.XPATH, f"//article[@data-automation='job-card-{i}']//div//h1/a")
                        self.driver.execute_script("arguments[0].scrollIntoView(true)", job_card_element)
                        self.driver.execute_script("arguments[0].click()", job_card_element)
                        
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-automation='splitModeJobDetailsScrollWrapper']"))
                        )
                        
                        self.scrap_jobs_data()
        self.logger.info('Scrapping process Done!')

        #Put together to Pandas Dataframe then Store to BigQuery
        df = pd.DataFrame(
            {
                'company_name': self.list_company_name,
                'job_posting_time': self.list_job_posting_time,
                'career_level': self.list_career_level,
                'size_of_company': self.list_company_size,
                'company_industry': self.list_company_industry,
                'detail_description': self.list_company_description,
                'employment_type': self.list_employment_type,
                'job_function': self.list_job_function
            }
        )
        
        df.to_csv('jobstreet_scrap_result.csv', index=False)
        self.store_to_bigquery(df)

    def scrap_jobs_data(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//div[@data-automation='detailsTitle']//span"))
        )

        company_name_element = self.driver.find_element(By.XPATH, "//div[@data-automation='detailsTitle']//span")
        company_name_text = company_name_element.text
        self.list_company_name.append(company_name_text)
        self.logger.info(f"Now scrap company name: {company_name_text}")

        company_description_element = self.driver.find_element(By.XPATH, "//div[@data-automation='jobDescription']")
        company_description_text = company_description_element.text
        
        job_highlight_text = self.get_additional_information(
            selector_to_check="//div[@data-automation='job-details-job-highlights']", 
            text_selector="//div[@data-automation='job-details-job-highlights']",
            text='Job Highlight'
        )
        
        benefit_text = self.get_additional_information(
            selector_to_check="//span[text() = 'Benefits & Others']",
            text_selector=SIBLING_PARENT_XPATH,
            is_sibling=True,
            text='Benefits'
        )
        final_description = f"{company_description_text}\n\n{job_highlight_text}\n\nBenefits & Others:\n{benefit_text}"
        self.list_company_description.append(final_description)
            
        career_level_text = self.get_additional_information(
            selector_to_check="//span[text() = 'Career Level']",
            text_selector=SIBLING_PARENT_XPATH,
            is_sibling=True,
            text='Career Level'
        )
        self.list_career_level.append(career_level_text)
        
        job_function_text = self.get_additional_information(
            selector_to_check="//span[text() = 'Job Specializations']",
            text_selector=SIBLING_PARENT_XPATH,
            is_sibling=True,
            text='Job Function'
        )
        self.list_job_function.append(job_function_text)

        employment_type_text = self.get_additional_information(
            selector_to_check="//span[text() = 'Job Type']",
            text_selector=SIBLING_PARENT_XPATH,
            is_sibling=True,
            text='Employment Type'
        )
        self.list_employment_type.append(employment_type_text)

        company_size_text = self.get_additional_information(
            selector_to_check="//span[text() = 'Company Size']",
            text_selector=SIBLING_PARENT_XPATH,
            is_sibling=True,
            text='Company Size'
        )
        self.list_company_size.append(company_size_text)
        
        industry_text = self.get_additional_information(
            selector_to_check="//span[text() = 'Industry']",
            text_selector=SIBLING_PARENT_XPATH,
            is_sibling=True,
            text='Company Industry'
        )
        self.list_company_industry.append(industry_text)
        
    def get_additional_information(self, selector_to_check, text_selector, text, is_sibling=False):
        prop_elements = self.driver.find_elements(By.XPATH, selector_to_check)
        if len(prop_elements) >= 1:
            if is_sibling is True:
                sibling_element = prop_elements[-1].find_element(By.XPATH, text_selector)
                information_text = sibling_element.text
            else:
                element = self.driver.find_element(By.XPATH, text_selector)
                information_text = element.text
        else:
            information_text = f'No {text}'
        
        return information_text

    def store_to_bigquery(self, df):
        self.logger.info('Writing to BigQuery...')
        dataset_id = os.getenv('DATASET_ID')
        project_id = os.getenv('PROJECT_ID')
        pandas_gbq.to_gbq(
            df, f"{dataset_id}.{BIGQUERY_TABLE_NAME}", 
            project_id=project_id, if_exists="replace"
        )
        self.logger.info('SUCCESS writing to BigQuery')
