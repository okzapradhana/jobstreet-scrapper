# Job Scrapper
Command Line Based Tool for scrap job/vacancy data from JobStreet website.

Please refer to [Note](#note) if you're facing some issues or want to do other things within this repo

## Tech Stack
1. Python (3.8.5) with packages installed as listed in `Pipfile` and `Pipfile.lock`
2. Chromedriver 
   - Download here: [link](https://sites.google.com/a/chromium.org/chromedriver/downloads) and choose one depends on your **Operating System**
   - Remember to set your `CHROMEDRIVER_PATH` later at [Setup](#setup)
3. [BigQuery](https://cloud.google.com/bigquery) as **Data Warehouse** (DWH) to store the scrap result

## Setup
1. Install `pipenv` first by executing `pip install pipenv` . Ensure that you already have `pip` on your machine
2. Run `pipenv shell` to create a virtual environment if doesn't exist yet
3. Install the dependecies by executing `pipenv install` command on the same directory where `Pipfile.lock` located
4. Create `.env` file at the root directory of this project/repo
5. Fill `PROJECT_ID` on your `.env` file based on your Google Cloud Platform (GCP) account
6. Then fill `DATASET_ID` on your `.env` file regarding to what dataset name you want. e.g `blankspace-jobstreet`
7. Change the `CHROMEDRIVER_PATH` on `config.py` to your chromedriver path after download the file
8. Setup done! Please go straight to [here](#how-to-use-this-tool-after-doing-setup)
## How to Use this Tool After Doing Setup?
Simply run `python main.py` to scrap the data

## Scrapping Flow
All scrapping processes were did by `scrapper.py`. And to give you more clearance about how this program gets the data by scrapping. Here is the flow:
1. First, it will go to [jobstreet page](https://www.jobstreet.co.id/)
2. Then it will type the keyword on the search bar and clicked the Enter
3. It redirects you to search result page, e.g this URL https://www.jobstreet.co.id/en/job-search/senior-data-engineer-jobs/
4. Before get the job data, it checks the pagination first whether it has only 1 page or more. It will get the maximum page from the pagination to traverse all the pages later
5. For each job card:
   1. It will get the datetime attribute of job posting time then do the calculation using `timeago` library to get the real Job Posting Time (xyz day/hour/minute ago)
   2. It will perform click action then it will scrap the job data that we needed (after the job details content showing at the right side )
6. Then, the program will visit the next page and do step 5 until the max page of pagination.
7. If all pages have been visited on a keyword, the rest of process just repeating the step 1-6 for the next search keyword.
8. The scrap result then will be formed as Pandas DataFrame
9. After that, we store the DataFrame to CSV and BigQuery to do further analysis

## Scrapping Output
This program will automatically produce two files after you run it:
1. The **logs** will be stored at `/logs` . Thus you don't need to create the folder manually
2. The **CSV** file will be stored at the same dir named `jobstreet_scrap_result.csv`. If you insist on check the CSV file you may open these file

## Data Visualization (Dashboard)
I used Data Studio to visualize the Data which stored on BigQuery earlier. <br>
If this embedded viz [link](https://datastudio.google.com/embed/reporting/29fdd73e-8edb-4540-ab0c-162f1b93eb2c/page/DHfGC) doesn't works on you,
kindly check my visualization on: https://datastudio.google.com/reporting/29fdd73e-8edb-4540-ab0c-162f1b93eb2c

### **Note**
- If you got a `TimeoutException` or another `Exception` Error in the middle of scrapping process. Please just re-run `python main.py`. <br>
I'am sorry for not handling that *rare* case in this version yet. <br> But the thing is, those issues weren't cause of incompatibility either Python version or Chromedriver version.
Thus don't be afraid. I've tested on local and it works perfectly!
- Or if you wish to only scrap some keywords for the sake of faster scrapping time. Just edit the `config.py` and comment some keywords that you want to exclude.
- At the end of scrapping process, Google OAuth2 will ask for authorization by sending this message: `Please visit this URL to authorize this application:` followed by the URL. <br>Just visit or click the URL to authorize the scrap application and gives BigQuery access to write the file

### **Disclaimer**
From my test on this program at local machine. It tooks **around 1 hour in total** to complete the scrap process (from getting the data until store to BigQuery) using all keywords that listed at `config.py` .<br>
Thus, if you want to get the result faster you might just delete/comment some keywords.