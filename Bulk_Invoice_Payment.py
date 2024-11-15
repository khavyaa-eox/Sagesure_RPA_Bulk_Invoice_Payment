# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 10:58:51 2023

@author: shrihari
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as  pd
from datetime import datetime
import logging
import time
import config
import os
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Email triggers
from send_email import send_email_with_attachment
from send_email import send_email_with_attachment_error
from send_email import send_text_email
from send_email import send_text_email_error

# Set up logging with date and time format
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Main file processing function
def call_process(file_path,credential):
    try:
        usr = credential['user']
        pwd = credential['password']
        filename = os.path.basename(file_path)
        filename1 = filename
        filename1_flag = 0
        
        def click_using_text(textValue):
            # Replace 'Click me' with the text of the element you want to click
            element_text = textValue
            
            # Find and click the element based on its text
            found = False
            for element in driver.find_elements(by=By.XPATH,value="//*[text() = '%s']" % element_text):
                try:
                    element.click()
                    found = True
                    break  # Stop searching once we've found and clicked the element
                except Exception as e:
                    pass  # Ignore exceptions if the click fails for this element           
        
        def wait_for_ele_presence(ele,timelimit=30):
            WebDriverWait(driver,timelimit).until(EC.presence_of_element_located((By.XPATH,ele)))
        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        def search_claim_number_in_webpage(cNum):
            searchButton = '//*[@id="header"]/div/div[1]/div[1]/div'
            wait_for_ele_presence(searchButton,100)
            driver.find_element(by=By.XPATH,value=searchButton).click()
            
            inputField = '//*[@id="header"]/div/div[1]/div[1]/input'
            wait_for_ele_presence(inputField)
            driver.find_element(by=By.XPATH,value=inputField).send_keys(cNum,Keys.ENTER)
            time.sleep(2)
        
        def check_for_webpage_text(checkTextWebpage,waitTime=10):
            webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
            #print(webpageText)
            countwebpageText = 0
            while checkTextWebpage not in webpageText and countwebpageText <= waitTime:
                time.sleep(1)
                webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                countwebpageText += 1
        
        def Change_Claim_Status(current,toChange):
            claimDetails = '//*[@id="scaffold-wrapper"]/div/div[1]/div/div[4]'
            wait_for_ele_presence(claimDetails,60)
            claimDetailsCheckText = driver.find_element(by=By.XPATH,value=claimDetails).text
            countclaimDetailsCheckText = 0
            while claimDetailsCheckText != 'Claim Details' and countclaimDetailsCheckText <= 30 :
                claimDetailsCheckText = driver.find_element(by=By.XPATH,value=claimDetails).text
                time.sleep(0.5)
                countclaimDetailsCheckText += 1
                #print(countclaimDetailsCheckText,claimDetailsCheckText)
            driver.find_element(by=By.XPATH,value=claimDetails).click()
            
            closedCheckText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]/div[1]/div[3]/div/div/label/div/div/div[1]/div[1]/div').text
            countclosedCheckText = 0
            while closedCheckText.upper() != current.upper() and countclosedCheckText <=25:
                closedCheckText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]/div[1]/div[3]/div/div/label/div/div/div[1]/div[1]/div').text
                time.sleep(1)
                countclosedCheckText += 1
                #print(countclosedCheckText,closedCheckText)
            time.sleep(1)
            driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]/div[1]/div[3]/div/div/label/div/div').click()
            driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/div[1]/div[1]/div[3]/div/div/label/div/div/div[1]/div[2]/div/input').send_keys(toChange,Keys.ENTER)
            
        data = pd.read_excel(file_path)
        startTime = time.time()
        
        data['EOX Comments'] = ''
        
        options = Options()
        options.add_experimental_option("excludeSwitches" , ["enable-automation"])
        # options.add_argument('--headless')
        options.add_argument("--window-size=1920,1080")
        chrome_path = r"chromedriver.exe" #path from 'which chromedriver'#path from 'which chromedriver'
        # chrome_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        try:
            driver.get(config.test_url)
            logger.info(f'Browser instance started')
            
        except:
            time.sleep(60)
            logger.error("Issue While Opening the Browser")
            driver.get(config.test_url)

        driver.implicitly_wait(15)
        
        # =============================================================================
        # **************************   login ****************************************
        # =============================================================================
        driver.find_element(by=By.XPATH,value='//*[@id="app"]/div/form[2]/label/input').send_keys(usr,Keys.ENTER)
        time.sleep(5)
        driver.find_element(by=By.XPATH,value='//*[@id="app"]/div/form[2]/label[2]/input').send_keys(pwd)
        time.sleep(5)
        driver.find_element(by=By.XPATH,value='//*[@id="app"]/div/form[2]/label[2]/input').send_keys(Keys.ENTER)

        # Iterate over the records to start processing        
        for i in range(len(data)):
            checkPointPayment = 1
            try:
                # =============================================================================
                # ******************  search and enter the claim value ***********************
                # =============================================================================
                clnumberfromexcel = data['Client Claim Number'].iloc[i]
                clnumberfromexcel = str(clnumberfromexcel).replace(',','')
                clnumberfromexcel = clnumberfromexcel.strip()
                clnumberfromexcel = clnumberfromexcel.upper()
                invoiceNumber = data['Invoice Number'].iloc[i]
                #print(clnumberfromexcel)
                
                search_claim_number_in_webpage(clnumberfromexcel)
                
                #print('search time',time.time() - startTime)
                
                claimsListCount = driver.find_elements(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div/div[3]/ul/div/div[3]/div/div[2]/div')
                
                for clLen in range(len(claimsListCount)):
                    try:
                        claimNumWeb = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div/div[3]/ul/div/div[3]/div/div[2]/div['+str(clLen+1)+']/div[1]/div[2]/a/span').text
                    except:
                        time.sleep(3)
                        claimNumWeb = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div/div[3]/ul/div/div[3]/div/div[2]/div['+str(clLen+1)+']/div[1]/div[2]/a/span').text
                    
                    if claimNumWeb == clnumberfromexcel:
                        logger.info(claimNumWeb)
                        claimStatus = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div/div[3]/ul/div/div[3]/div/div[2]/div['+str(clLen+1)+']/div[2]/div[2]/div').text
                        time.sleep(1)
                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div/div[3]/ul/div/div[3]/div/div[2]/div['+str(clLen+1)+']/div[1]/div[2]/a/span').click()
                        break
                    
                # =============================================================================
                # --------------------- Claims Details Handling -------------------------------
                # =============================================================================
                if claimStatus.upper() != 'CANCELLED':
                    if claimStatus == 'Closed':
                        webpageTextWaitCounter = 0
                        webpageTextWait = driver.find_element(by=By.XPATH,value='/html/body').text
                        time.sleep(3)
                        if claimNumWeb not in webpageTextWait and webpageTextWaitCounter <=20:
                            time.sleep(1)
                            webpageTextWait = driver.find_element(by=By.XPATH,value='/html/body').text
                            webpageTextWaitCounter+=1
                            
                        Change_Claim_Status('Closed','Open')
                        
                        webpageTextWaitCounter1 = 0
                        webpageTextWait = driver.find_element(by=By.XPATH,value='/html/body').text
                        time.sleep(3)
                        if 'OPEN' not in webpageTextWait and webpageTextWaitCounter1 <=20:
                            time.sleep(1)
                            webpageTextWait = driver.find_element(by=By.XPATH,value='/html/body').text
                            webpageTextWaitCounter1+=1
                        
                        yesCheckText = driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').text
                        countyesCheckText = 0
                        while yesCheckText != 'Yes' and countyesCheckText <= 20:
                            yesCheckText = driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').text
                            time.sleep(1)
                            countyesCheckText += 1
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').click()
                        # print('Claim Reopend')
                        
                    
                    # =============================================================================
                    #  ------------------------ Claim Summary Process -----------------------------
                    # =============================================================================
                    # print('Starting CLaim Summary')
                    claimSummaryText = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[1]/div/div[2]').text
                    countclaimSummaryText = 0
                    while claimSummaryText != 'Claim Summary' and countclaimSummaryText < 10:
                        claimSummaryText = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[1]/div/div[2]').text
                        time.sleep(1)
                        countclaimSummaryText += 1
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    countwebpageText = 0
                    while ('CLAIM: '+clnumberfromexcel not in webpageText) and countwebpageText <= 20:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText += 1
                    
                    
                    
                    
                    driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[1]/div/div[2]').click()
                    ClaimsSummaryListTable = '//*[@id="claim-page-wrapper"]/div/div/div[3]/div[2]/table/tbody'
                    ClaimsSummaryListTableText = driver.find_element(by=By.XPATH,value=ClaimsSummaryListTable).text
                    # print('Clicked CLaim Summary')
                    
                    if 'Dwelling' in ClaimsSummaryListTableText:
                        firstexposureText = 'Dwelling'
                        cliamSummaryListRows = driver.find_elements(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div[3]/div[2]/table/tbody/tr')
                        for cRow in range(len(cliamSummaryListRows)):
                            dwellingCheckText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div[3]/div[2]/table/tbody/tr['+str(cRow+1)+']/td[2]/button').text
                            if dwellingCheckText == 'Dwelling':
                                time.sleep(1)
                                # Scroll the element into view
                                element = driver.find_element(By.XPATH, '//*[@id="claim-page-wrapper"]/div/div/div[3]/div[2]/table/tbody/tr['+str(cRow+1)+']/td[2]/button')
                                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div[3]/div[2]/table/tbody/tr['+str(cRow+1)+']/td[2]/button').click()
                                vendorButtonXpath = '//*[@id="claim-page-wrapper"]/div/div[1]/div/div[2]/a[3]/button'
                                break
                    else:
                        firstexposureText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div[3]/div[2]/table/tbody/tr[1]/td[2]/button').text
                        driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div[3]/div[2]/table/tbody/tr[1]/td[2]/button').click()
                        
                        if firstexposureText == 'Personal Property':
                            vendorButtonXpath = '//*[@id="claim-page-wrapper"]/div/div[1]/div/div[2]/a[3]/button'
                        elif firstexposureText == 'Other Structures':
                            vendorButtonXpath = '//*[@id="claim-page-wrapper"]/div/div[1]/div/div[2]/a[2]/button'
                        else:
                            countOfVEndorCheckNames = driver.find_elements(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[2]/a')
                            
                            # =============================================================================
                            #         #fill in for looping to get vendor button for other cases
                            # =============================================================================
                    
                        
            
                    # =============================================================================
                    #  ---------------------------> Adding Vendors  <------------------------------
                    # =============================================================================
                    vendorNameExcel = data['Payee/Vendor'].iloc[i]
                    driver.find_element(by=By.XPATH,value=vendorButtonXpath).click()
                    vendorTableHeader = '//*[@id="claim-page-wrapper"]/div/div[2]/div[2]/div[1]'
                    wait_for_ele_presence(vendorTableHeader)
                    
                                # *********** check if exposure is open/closed ******************
                    
                    exposureOpenCloseTextXpath = '//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]/div[1]/div[1]/div[3]/div/label/div/div'
                    wait_for_ele_presence(exposureOpenCloseTextXpath,35)
                    exposureOpenCloseText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]/div[1]/div[1]/div[3]/div/label/div/div').text
                    
                    if exposureOpenCloseText == 'CLOSED':
                        driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]/div[1]/div[1]/div[3]/div/label/div/div').click()
                        driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/div[1]/div[1]/div[1]/div[3]/div/label/div/div[1]/div[1]/div[2]/div/input').send_keys('Open',Keys.ENTER)
                        
                        check_for_webpage_text('Reopen Exposure')
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').click()
                        countexposureOpenCloseText = 0
                        while exposureOpenCloseText != 'OPEN' and countexposureOpenCloseText <= 120:
                            time.sleep(0.5)
                            exposureOpenCloseText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]/div[1]/div[1]/div[3]/div/label/div/div').text
                            countexposureOpenCloseText += 1
                    try:
                        try:#get the vendor table using relative xpath when it failes use the class name
                            table = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[2]/div[2]/div[1]')
                        except:
                            table = driver.find_element(by=By.XPATH,value='//div[@class="_5UQt0Iza1XW9Hs74zdxLd nCHYD7xlq6UE1q-7xb1G9 _2buL7UDmuAvUMZo4rGgNdA"]')
                        # Find all the rows in the table
                        # print("table:\t\t",table)
                        rows = table.find_elements(by=By.XPATH,value='//a[@class="_38ZQikJDvcmVI21d2WY6T"]')
                        # print("rows: \n\n",rows)
                        # Extract the second column of data from each row
                        column_data = []
                        for row in rows:
                            # Find the second column using XPath
                            column = row.find_element(by=By.XPATH,value='//div[@class="_2DfN-63Z9Qg88hTLEmZtST _10O5tZHcEzLO4SQWu3_5fK"]')
                            # Get the text from the column and append it to the list
                            column_data.append(column.text)
                        
                        # Get the column data of vendors
                        vendorTable =  [column_data[i:i+2] for i in range(0, len(column_data), 2)]
                        vendorTableDf = pd.DataFrame(vendorTable,columns=['Service','Vendor'])
                    except:
                        vendorTableDf = pd.DataFrame(columns=['Service', 'Vendor'])
                    
                    if vendorNameExcel not in vendorTableDf['Vendor'].values:
                        driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[2]/div[1]/button').click()
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div/div/div[1]').click()
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/div/div[1]/button[1]').click()
                        #wait for table to load
                        WebDriverWait(driver,90).until(EC.invisibility_of_element_located((By.CSS_SELECTOR,'body > div.ss-dialog-container > div.ss-modal.-iGS5v22bgSXyAcLo9mXB > div.ss-modal__content._1zuMdpB8CL0L8xzY0EnZlC > div > div > div._5UQt0Iza1XW9Hs74zdxLd._3b99HJHJ-LGaKXhJf7vHLN > div._3BCBfM2jwpuAWiCGLF9faf > div')))
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div/div[1]/div[1]/div/input').send_keys(vendorNameExcel,Keys.ENTER)
                        vendorCheckFlag = 0
                        wait_for_ele_presence('/html/body/div[3]/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[1]',30)
                        time.sleep(2.5)
                        vendorNameWeb = driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[1]').text
                        countvendorNameWeb = 0
                        
                        while vendorNameWeb != vendorNameExcel and countvendorNameWeb < 7:
                            time.sleep(1)
                            vendorNameWeb = driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[1]').text
                            #print(vendorNameWeb,vendorNameExcel,'inside the loop')
                            countvendorNameWeb += 1
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[1]').click()
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/div/div[1]/button[1]').click()
                        
                        #Fill the vendor details
                        
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div[3]/div/div[3]/div/div/label[1]').click()
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div[3]/div/div[2]/div/div/div[2]/div/div/label/div/div/div[1]/div[2]').click()
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div[3]/div/div[2]/div/div/div[2]/div/div/label/div/div/div[1]/div[2]/div/input').send_keys('Payable Vendor',Keys.ENTER,Keys.TAB,Keys.TAB)
                        time.sleep(1)
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[2]/div/div[5]/div/div[2]/label[1]/div[1]').click()
                        time.sleep(2)
                        #save button
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/div/div[1]/button[1]').click()
                    
                    vendorCheckFlag = 1
                    # =============================================================================
                    # --------------------------- > Financials < ---------------------------------
                    # =============================================================================
                    # check_for_webpage_text('FINANCIAL SUMMARY')
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    countwebpageText = 0
                    while 'FINANCIAL SUMMARY' not in webpageText and countwebpageText <= 15:
                        try:
                            driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[1]/div/div[2]').click()
                            driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[1]/div/div[8]').click()
                        except:
                            pass
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText += 1
                    # driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[1]/div/div[8]').click()
                    
                    reservesAddButtonXpath = '//*[@id="claim-page-wrapper"]/div/div/div[2]/div/table/thead/tr/td[2]/div/button'
                    wait_for_ele_presence(reservesAddButtonXpath)
                    driver.find_element(by=By.XPATH,value=reservesAddButtonXpath).click()
                    
                    # =============================================================================
                    #  ------------------------> Adding Reserves <---------------------------------
                    # =============================================================================
                    
                    check_for_webpage_text('Add Reserve')
                    addReserveCategory = data['Adjuster Cost Category'].iloc[i]
                    addReserverNewValue = data['Grand Total'].iloc[i]
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    countwebpageText = 0
                    while 'Add Reserve' not in webpageText and countwebpageText <= 15:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText += 1
                    wait_for_ele_presence('//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[1]/button',20)
                    driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[1]/button').click()
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    
    
    
                    countwebpageText1 = 0
                    while firstexposureText not in webpageText and countwebpageText1 <= 15:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText1 += 1
                    click_using_text(firstexposureText)
                    countwebpageText2 = 0
                    while 'Cost Type' not in webpageText and countwebpageText2 <= 15:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText2 += 1
                    
                    element_to_hover_over = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[1]/button')
                    actions = ActionChains(driver)
                    actions.move_to_element(element_to_hover_over)
                    actions.perform()
                    
                    
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div/label/div/div/div[1]/div[2]').click()
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div/label/div/div/div[1]/div[2]/div/input').send_keys(
                        'Adjusting',Keys.ENTER,Keys.TAB,
                        str(addReserveCategory),Keys.ENTER,Keys.TAB,
                        str(addReserverNewValue),Keys.ENTER,Keys.TAB,
                        Keys.TAB,Keys.TAB,Keys.TAB,Keys.TAB,Keys.TAB,Keys.ENTER)
                    #print('Added')
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    countwebpageText3 = 0
                    
                    while 'RESERVE DETAILS' not in webpageText and countwebpageText3 <= 25:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText3 += 1
                        #print('waiting for reserves details')
                        
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    countwebpageText4 = 0
                    while 'RESERVE DETAILS' in webpageText and countwebpageText4 <= 20:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText4 += 1
                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[1]/div/div[8]').click()                    
                        #print('waiting for Payments button')
                        
                    # =============================================================================
                    # ------------------------> Payments <----------------------------------------
                    # =============================================================================
    
                    
                    driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div[2]/div/table/thead/tr/td[4]/div/button').click()
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    countwebpageText = 0
                    while 'Primary Payee Type' not in webpageText and countwebpageText <= 15:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText += 1
                    
                    
                    #Primary Payee Type
                    driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[2]/div/div[1]/label/div/div/div[1]/div[2]').click()
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[2]/div/div[1]/label/div/div/div[1]/div[2]/div/input').send_keys('Vendor',Keys.ENTER,Keys.TAB,vendorNameExcel,Keys.ENTER,Keys.TAB,'Self Select',Keys.ENTER)
                    wait_for_ele_presence('//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[4]/div[3]/div/div/label[1]/div',20)
                    driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[4]/div[3]/div/div/label[1]/div').click()
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[4]/div[2]/label/div/div/input').send_keys(str(invoiceNumber),Keys.TAB,Keys.TAB,Keys.TAB,Keys.TAB,Keys.TAB,Keys.TAB)
                    driver.find_element(by=By.XPATH, value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[13]/div[3]/div[1]/div/div/label[2]/div').click()               
                    driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[13]/div[4]/div[1]/div/div/label[1]/div').click()
                    
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div/div[2]/div/div/div/div[4]/button[2]').click()
                    
                    
                    countwebpageText5 = 0
                    while 'Notification Only' in webpageText and countwebpageText5 <= 15:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText5 += 1
                    
                    # =============================================================================
                    #                 #Add Payments Second window
                    # =============================================================================
                    driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[1]/button').click()
                    click_using_text(firstexposureText)
                    
                    countwebpageText6 = 0
                    while 'Cost Type' not in webpageText and countwebpageText6 <= 15:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText6 += 1
                        
                    if claimStatus == 'Closed':
                        paymentType = 'Final'
                    elif claimStatus == 'Open':
                        paymentType = 'Partial'
                    costType = data['Adjuster Cost Category'][i]
                    paymentAmout = data['Grand Total'][i]
                    
                    element_to_hover_over = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div/div/div[3]/div/div/div[1]/button')
                    actions = ActionChains(driver)
                    actions.move_to_element(element_to_hover_over)
                    actions.perform()
                    
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div/label/div/div/div[1]/div[2]').click()
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[3]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div/label/div/div/div[1]/div[2]/div/input').send_keys(str(costType),Keys.ENTER,Keys.TAB,
                    str(paymentAmout),Keys.ENTER,Keys.TAB,
                    str(paymentType),Keys.ENTER)
                    
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div/div[2]/div/div/div/div[4]/button[3]').click()
                    driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div/div[2]/div/div/div/div[4]/button[3]').click()
                    checkPointPayment = 0
                    countwebpageText6 = 0
                    while 'PAYMENT DETAILS' not in webpageText and countwebpageText6 <= 15:
                        time.sleep(1)
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText6 += 1
                    
                    time.sleep(3)
                    
                    if claimStatus == 'Closed':
                        Change_Claim_Status('Open','Closed')
                        
                        webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                        countwebpageText = 0
                        while 'Close Claim ' in webpageText and countwebpageText <= 60:
                            time.sleep(0.5)
                            webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                            countwebpageText += 1
                            
                        #close the claim    
                        driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').click()
                        
                        exposureClosCheckText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]').text
                        countexposureClosCheckText = 0
                        while 'CLOSED' not in exposureClosCheckText and countexposureClosCheckText <= 150:
                            time.sleep(0.5)
                            exposureClosCheckText = driver.find_element(by=By.XPATH,value='//*[@id="claim-page-wrapper"]/div/div[1]/div/div[1]').text
                            countexposureClosCheckText += 1    
                    
                    # =============================================================================
                    #  -------------------------> Closing the tasks <-----------------------------
                    # =============================================================================
                    counterCheckTaskButton = 0
                    while driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[1]/button[5]').get_attribute('title') != 'Tasks' and counterCheckTaskButton <= 20:
                        time.sleep(0.5)
                        counterCheckTaskButton += 1
                    
                    driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[1]/button[5]').click()
                    driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[1]/div/div[2]/div/button[2]').click()
                    # time.sleep(5)
                    if claimStatus == 'Closed':
                        # time.sleep(2)
                        checkReviewText = driver.find_element(by=By.XPATH,value='/html/body').text
                        checkReviewTextCounter = 0
                        while "Review Claim for Closure" not in checkReviewText and checkReviewTextCounter < 30:
                            time.sleep(1)
                            checkReviewText = driver.find_element(by=By.XPATH,value='/html/body').text
                            checkReviewTextCounter += 1
                            if checkReviewTextCounter == 29:
                                logger.info(f"{checkReviewTextCounter}, Max wait exceeding while waiting for Review Claim Task")
                    taskListCountText = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[1]').text  
                    taskListCount = int(taskListCountText.replace('CURRENT(','').replace(')',''))
                    
                    t = 1
                    tCounter = 1
                    logger.info(f'task numbers: {taskListCount}')
                    while t <= taskListCount:
                        logger.info(f"Closing "+str(t)+" of "+str(taskListCount)+" tasks -->"+claimStatus)
                        if claimStatus == 'Closed':
                            # time.sleep(2)
                            checkReviewText = driver.find_element(by=By.XPATH,value='/html/body').text
                            checkReviewTextCounter = 0
                            while "Review Claim for Closure" not in checkReviewText and checkReviewTextCounter < 90:
                                time.sleep(1)
                                checkReviewText = driver.find_element(by=By.XPATH,value='/html/body').text
                                checkReviewTextCounter += 1
                                logger.info(checkReviewTextCounter)
                                if "Review Claim for Closure" in checkReviewText:
                                    logger.info(f'YESS')
                            taskName = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/div').text
                            # print(claimStatus,'---->',taskName)
                            
                            if taskName == 'Reopen associated exposure(s) for further handling' or taskName == 'Review Claim for Closure':
                                time.sleep(3)
                                driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/div[2]/button').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/label/div').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/div[6]/button[2]').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/button').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[1]/div/div[2]/div/button[2]').click()
                                logger.info(f'closed the task','---->',taskName)              
                                t -= 1
                                taskListCount-=1
                        elif claimStatus == 'Open':
                            taskName = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/div').text
                            # print(taskName)
                            if taskName == 'Issue Payment' or taskName == 'Send Settlement letter':
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/button').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/label/div').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/div[6]/button[2]').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/button').click()
                                driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[1]/div/div[2]/div/button[2]').click()
                    
                                t -= 1
                                taskListCount-=1
                        t += 1
                    
                    # print('done')
                    
                    
                    data.loc[i, 'EOX Comments'] = 'Processed'

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name, ext = os.path.splitext(filename)
                    completed_filename = f"{name}_{timestamp}_completed{ext}"
                    # filename1 = str(filename).replace('.xlsx','')
                    data.to_excel(config.local_completed_path+"/"+str(completed_filename),index=False)
                    filename1_flag = 1
                    endTime = time.time()
                    logger.info(f"Total Time: {endTime-startTime}")
                    
                elif claimStatus.upper() == 'CANCELLED':
                    data.loc[i, 'EOX Comments'] = 'Claim State is CANCELLED'
                    
                else:
                    data.loc[i, 'EOX Comments'] = 'Unknown Error in Claim State'
                    
                
            except Exception as e:
                try:
                    addComment = ''
                    # filename1 = str(filename).replace('.xlsx','')
                    data.to_excel(config.local_completed_path+"/"+str(completed_filename),index=False)
                    
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    filenamedate = datetime.now().strftime('%m_%d_%Y')
                    directory = config.local_error_path+'/'+filenamedate
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    time.sleep(3)
                    if "Your password has expired. Please reset your password." in webpageText:
                        send_text_email("Sagesure | RPA | Password Expired | "+str(usr))
                        logger.info(f"Password expired mail sent")
                    
                    try:
                        if vendorCheckFlag == 0:
                            addComment = 'Check if Vendor is Present'
                    except:
                        pass
                        
                        
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    if 'We didn\'t find any results for the search' in webpageText:
                        data.loc[i, 'EOX Comments'] = 'We did not find any results for this Claim Number'
                        
                        driver.save_screenshot(config.local_error_path+'/'+str(filenamedate)+'/'+str(i)+'_'+str(clnumberfromexcel)+'_'+str(invoiceNumber)+'.png')
                        
                    else:
                        addCommentPageNotFound = ''
                        if 'Page not found' in webpageText:
                            addCommentPageNotFound = 'Page Not Found - '
                        if checkPointPayment == 1:
                            data.loc[i, 'EOX Comments'] = addCommentPageNotFound + addComment + 'Resend this record.\n' + str((exc_tb.tb_lineno,exc_type,exc_obj))
                            driver.save_screenshot(config.local_error_path+'/'+str(filenamedate)+'/'+str(i)+'_'+str(clnumberfromexcel)+'_'+str(invoiceNumber)+'.png')
                            
                        elif checkPointPayment == 0:
                            data.loc[i, 'EOX Comments'] = addCommentPageNotFound + addComment +'Completed the payment with an issue while closing tasks. Please check manually.'+ str((exc_tb.tb_lineno,exc_type,exc_obj))
                            driver.save_screenshot(config.local_error_path+'/'+str(filenamedate)+'/'+str(i)+'_'+str(clnumberfromexcel)+'_'+str(invoiceNumber)+'.png')
                    
                    # filename1 = str(filename).replace('.xlsx','')
                    data.to_excel(config.local_completed_path+"/"+str(completed_filename),index=False)
                           
                    try:
                        
                        if claimStatus == 'Closed':
                            driver.refresh()
                            claimSearchButton = '//*[@id="header"]/div/div[1]/div[1]/div'
                            wait_for_ele_presence(claimSearchButton,100)
                            Change_Claim_Status('Open','Closed')
                            yesCheckText = driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').text
                            countyesCheckText = 0
                            while yesCheckText != 'Yes' and countyesCheckText <= 20:
                                yesCheckText = driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').text
                                time.sleep(1)
                                countyesCheckText += 1
                            driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[2]/div[3]/button[2]').click()
                            
                            counterCheckTaskButton = 0
                            while driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[1]/button[5]').get_attribute('title') != 'Tasks' and counterCheckTaskButton <= 20:
                                time.sleep(0.5)
                                counterCheckTaskButton += 1
                                
                            driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[1]/button[5]').click()
                            driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[1]/div/div[2]/div/button[2]').click()
                            # time.sleep(15)
                            if claimStatus == 'Closed':
                                # time.sleep(2)
                                checkReviewText = driver.find_element(by=By.XPATH,value='/html/body').text
                                checkReviewTextCounter = 0
                                while "Review Claim for Closure" not in checkReviewText and checkReviewTextCounter < 30:
                                    time.sleep(1)
                                    checkReviewText = driver.find_element(by=By.XPATH,value='/html/body').text
                                    checkReviewTextCounter += 1
                                    logger.info(checkReviewTextCounter)
                                    if "Review Claim for Closure" in checkReviewText:
                                        logger.info(f'YESS')
                            taskListCountText = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[1]').text  
                            taskListCount = int(taskListCountText.replace('CURRENT(','').replace(')',''))
                            # check_for_webpage_text('Review Claim for Closure',20)
                            t = 1
                            tCounter = 1
                            while t <= taskListCount:
                                #print("Closing "+str(t)+" of "+str(taskListCount)+" tasks -->"+claimStatus)
                                if claimStatus == 'Closed':
                                    
                                    taskName = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/div').text
                                    logger.info(f"{claimStatus}---->{taskName}")
                                    if taskName == 'Reopen associated exposure(s) for further handling' or taskName == 'Review Claim for Closure':
                                        # time.sleep(3)
                                        driver.find_element(by=By.XPATH,value='/html/body/div[2]/div/div[2]/div/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/div[2]/button').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/label/div').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/div[6]/button[2]').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/button').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[1]/div/div[2]/div/button[2]').click()
                                        logger.info(f"closed the task----->{taskName}")
                                        t -= 1
                                        taskListCount-=1
                                elif claimStatus == 'Open':
                                    taskName = driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/div').text
                                    # print(taskName)
                                    if taskName == 'Issue Payment' or taskName == 'Send Settlement letter':
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div[1]/div[2]/div['+str(t)+']/div/div[1]/button').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/label/div').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/div/div[6]/button[2]').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[2]/div/button').click()
                                        driver.find_element(by=By.XPATH,value='//*[@id="scaffold-wrapper"]/div/div[3]/div[5]/div/div[2]/div[1]/div/div[2]/div/button[2]').click()
                            
                                        t -= 1
                                        taskListCount-=1
                                t += 1                   
                        claimStatus = '' 
                    except:
                        pass
                except Exception as e:
                    try:
                        driver.quit()
                        pass
                    except:
                        pass
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    
                    data.loc[i, 'EOX Comments'] = "Closed unexpectedly. Please check manually for payment confirmation" + str((exc_tb.tb_lineno,exc_type,exc_obj))
                    
                    driver = webdriver.Chrome(options=options)
                    driver.maximize_window()
                    driver.get(config.test_url)
                    driver.implicitly_wait(15)
                    
                    wait_for_ele_presence('//*[@id="app"]/div/form[2]/label/input')
                    driver.find_element(by=By.XPATH,value='//*[@id="app"]/div/form[2]/label/input').send_keys(usr,Keys.ENTER)
                    wait_for_ele_presence('//*[@id="app"]/div/form[2]/label[2]/input')
                    driver.find_element(by=By.XPATH,value='//*[@id="app"]/div/form[2]/label[2]/input').send_keys(pwd,Keys.ENTER)
                    time.sleep(3)
                    webpageText = driver.find_element(by=By.XPATH,value='/html/body').text
                    if "Your password has expired. Please reset your password." in webpageText:
                        send_text_email("Sagesure | RPA | Password Expired | "+str(usr))
                        logger.info(f"Password expired mail sent")
                            
                    claimSearchButton = '//*[@id="header"]/div/div[1]/div[1]/div'
                    wait_for_ele_presence(claimSearchButton,100)
                    
                
                driver.refresh()
                claimSearchButton = '//*[@id="header"]/div/div[1]/div[1]/div'
                try:
                    wait_for_ele_presence(claimSearchButton,100)
                except:
                    pass
                vendorCheckFlag = ''

                # filename1 = str(filename).replace('.xlsx','')
                data.to_excel(config.local_completed_path+"/"+str(completed_filename),index=False)
                
            g = i
            #print(g+1)
            if i % 10 == 0:
                driver.refresh()
                time.sleep(3)
            if i % 50 == 0:
                
                driver.quit()
                driver = webdriver.Chrome(options=options)
                driver.maximize_window()
                driver.get(config.test_url)
                driver.implicitly_wait(15)
                
                wait_for_ele_presence('//*[@id="app"]/div/form[2]/label/input')
                driver.find_element(by=By.XPATH,value='//*[@id="app"]/div/form[2]/label/input').send_keys(usr,Keys.ENTER)
                wait_for_ele_presence('//*[@id="app"]/div/form[2]/label[2]/input')
                driver.find_element(by=By.XPATH,value='//*[@id="app"]/div/form[2]/label[2]/input').send_keys(pwd,Keys.ENTER)
                claimSearchButton = '//*[@id="header"]/div/div[1]/div[1]/div'
                wait_for_ele_presence(claimSearchButton,100)
        
        # filename1 = str(filename).replace('.xlsx','')
        data.to_excel(config.local_completed_path+"/"+str(completed_filename),index=False) 

        # =============================================================================
        # ************** Get the Failed records in separate Excel File ***************
        # =============================================================================
        # Reload the full file to get the error records if any
        try:
            error_data = pd.read_excel(config.local_completed_path + "/" + str(completed_filename))

            # Filter records where "EOX Comments" is not "Processed"
            failed_records = error_data[error_data['EOX Comments'] != 'Processed']

            if not failed_records.empty:
                # Save the entire rows (with all columns) of failed records to the error file
                failed_records.to_excel(config.local_error_path + "/" + str(completed_filename), index=False)
                logger.info(f"Failed records saved to {config.local_error_path + '/' + str(completed_filename)}")
                # send_email_with_attachment_error(config.local_completed_path + "/" + str(completed_filename))
            else:
                logger.info(f"No failed records found.")

        except Exception as e:
            logger.error(f"Error reading or processing the file: {str(e)}")

        driver.quit()
        # send_email_with_attachment(config.local_completed_path + "/" + str(completed_filename))
        
        endTime = time.time()
        logger.info(f"Total Time: {endTime-startTime}")

        logger.info(f"Completed filename: {completed_filename}")
        return completed_filename

# =============================================================================
    except:
        if filename1_flag:
            # send_email_with_attachment_error(config.local_completed_path + "/" + str(completed_filename))
            return completed_filename
        elif filename1_flag == 0:
            # send_text_email_error("Sagesure | RPA | Chrome Crash", filename)
            return filename
# =============================================================================
    

call_process('/home/eox_kavya/Sagesure_RPA_Bulk_Invoice_Payment/attachments/Input_Files/test.xlsx',{'user': 'svc_claims_rpa+vendorbulkpay3@icg360.com', 'password': '_3$FD^%UPwJs`53"$xsX'})