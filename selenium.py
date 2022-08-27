import sys
sys.path.append('/opt/selenium_scraping_facebook_ads/projects')

import json
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from MySqlConnemctor import MySqlConnector
from datetime import datetime
import time
import logging
import logging.handlers
import requests
import glob
import os

def send_slackalert(webhook_url, configJob, date,phase):
    slack_data = {'text': 'Selenium code for facebook_ads ads Failed in the %s phase \nAccount: %s  \nDate = %s ' % (
    phase,configJob.ACCOUNT_ID, date)}
    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'})
    logging.info(
        "Failed for the account  %s, in the %s phase response code is %s ,the response is:\n%s "
        % (configJob.ACCOUNT_ID,phase ,response.status_code, response.text)
    )
    if response.status_code != 200:
        logging.info("inside the status code not equals 200 block")
        logging.info(
            "Request to slack returned an error %s, the response is:\n%s for ACCOUNT ID = : %s "
            % (response.status_code, response.text, configJob.ACCOUNT_ID)
        )
    else:
        logging.info("Slack Response is 200.")


# method to get the downloaded file name
def getDownLoadedFileName():

    list_of_files = glob.glob('D:\\tmp\\*.csv')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    #print("latest file name is   " , latest_file)
    return latest_file


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    prefs={"download.default_directory":"D:\\tmp"}
    options.add_experimental_option("prefs",prefs)
    #driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options);
    # driver=webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
    logging.basicConfig(filename='scripts.log', level=logging.INFO, format='%(asctime)s:%(message)s')
    webhook_url = "https://hooks.slack.com/services/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"

    query = "select * from accounts where IS_ENABLED = 1 and EXCHANGE_ID=135;"
    jobs = MySqlConnector().execute(query)
    for job in jobs:
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
            date = (datetime.today()).strftime('%Y-%m-%d')
            stringinit = job.__getitem__(24)
            final_dictionary = json.loads(stringinit)

            error_val = "The exception occured in downloading file is  "
            phase = "Extraction"

            # fetching path from CUBE_DETALS Column of Accounts Table
            driver.get("https://bbmptax.karnataka.gov.in/")

            # Maximize the window and let code stall
            # for 5s to properly maximise the window.
            driver.maximize_window()
            time.sleep(5) # gives an implicit wait for 20 seconds

            logging.info("Performing operations to download file")
            # Obtain button by link text and click.
            button = driver.find_element_by_class_name("jwy3ehce").click()
            time.sleep(5)

            l1 = driver.find_element_by_css_selector("input[type='radio'][value='csv']").click()
            time.sleep(5)

            driver.find_element_by_xpath("//*[text()='Export']").click()
            # Increase the sleep time if required
            # As the file size increases , it takes more time to download the file so wait until file is downloaded
            time.sleep(40)

            logging.info("File Downloaded")

            file_name = getDownLoadedFileName()
            # file_name = "D:\\tmp\\Do_not_delete_FBAds_Conversions_last7days_data-Apr-29-2022-to-May-5-2022.csv"
            print(file_name)
            logging.info("Got the complete path of downloaded file ")
            driver.close()
            driver.quit()

            if (final_dictionary["TRANSFORMATION"] == "TRUE"):
                error_val = "The exception occured in transforming file is  "
                phase = "Transformation"
                logging.info("Transformation Started")
                logging.info("Transformation Ended")

            logging.info("Loader Started")
            error_val = "The exception occured in loading file is  "
            phase = "Loading"
            logging.info("Loader Ended")

        except Exception as e:
            logging.error(error_val+ str(e))
            print(e.__class__)
            driver.close()
            driver.quit()

