BASE_URL = 'https://jobstreet.co.id/en/'
CHROMEDRIVER_PATH = './chromedriver_linux64/chromedriver'
TIMEZONE = 'Asia/Jakarta'
KEYWORDS = [
    'Senior Data Engineer',
    # 'Data Engineer',
    'Senior Data Scientist',
    # 'Data Scientist',
    'Senior Data Analyst',
    # 'Data Analyst',
    'Senior Business Intelligence',
    'Business Intelligence Analyst'
]
SIBLING_PARENT_XPATH = "../following-sibling::div/span"
LOG_DIR = "./logs"
LOG_INFO_PATH = f"{LOG_DIR}/jobscrap.log"
LOG_INFO_FILEMODE = 'w'
BIGQUERY_TABLE_NAME = 'jobstreet_jobs'
