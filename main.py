import time
from scrapper import JobScrapper

if __name__ == '__main__':
    start = time.time()
    print("Scrapping is started...")
    
    js = JobScrapper()
    js.begin_scrap()
    
    print("Scrapping done!")
    run_in_minutes = (time.time() - start)/60
    print(f"The program runs for {run_in_minutes} minutes")