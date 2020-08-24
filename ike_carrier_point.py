# ===================
# Name: Austin Way
# Date: 8/6/2020
# ===================


# ===================
# IMPORTS
# ===================
import requests
import time
import os
import smtplib
import json
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup 
from selenium import webdriver
from datetime import datetime 

# ===================
# CLASSES and METHODS
# ===================
class Browser:
    def wait(self, seconds): 
        # An implicit wait makes WebDriver poll the DOM for a certain amount of time when trying to locate an element
        print("Waiting " + str(seconds) + " seconds to allow page load")
        driver.implicitly_wait(float(seconds))

    def browser_refresh(self):
        # Refresh the browser
        refresh_browser_text = "Refreshing... " + str(datetime.now())
        print(refresh_browser_text)
        driver.refresh()
        return refresh_browser_text

class Log:      
    def current_time(self):
        #returns custom formatted time
        get_time = datetime.now()
        now = get_time.strftime("%m/%d/%Y, %H:%M:%S")
        current_time = str(now)
        print(current_time)
        return current_time

class Login():
    def enter_credentials(self, username, password):
        # Enter in username and password
        print("Entering in login credentials")
        username_css_name = driver.find_element_by_name('loginId')
        password_css_name = driver.find_element_by_name('password')
        username_css_name.send_keys(username)
        password_css_name.send_keys(password)

    def press_logon_button(self):
        # login_button_xpath = driver.find_element_by_xpath("html/body/div[@id='root']/div[@class='app-component']/div[@id='app-routes-component']/div[@class='body-wrapper page-wrapper-component']/div[@class='body-content']/div[@class='site-section tenders-section']/div[@class='row']/div[@class='col-sm-6 col-sm-offset-3']/div[@class='box login-box']/form/div[@class='buttons']/button[@id='btnLogin']")
        login_button_xpath = driver.find_element_by_xpath("/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[4]/td/input")

        print("Pressing login button with the usage of some JavaScript\n")
        driver.execute_script("arguments[0].click();", login_button_xpath)

# ===================
# FUNCTIONS
# ===================
def send_email(email_subject, email_body):
    address_book = ['']
    msg = MIMEMultipart()    
    sender = ''
    subject = email_subject
    body = email_body

    msg['From'] = sender
    msg['To'] = ','.join(address_book)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text=msg.as_string()
    #print text
    # Send the message via SMTP server
    s = smtplib.SMTP('')
    s.sendmail(sender,address_book, text)
    s.quit() 


# =========
# LOGIC
# =========

# Defining url(s)
url = "https://market-atl.carrierpoint.com/market/jsp/CPRespondToOffers.jsp" #variable to be passed to requests and selenium packages, Carrier Point login page

# Adding options to ignore browser errors when the browser asks to accept certificates from a website
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--headless') # opens browser silently 

# Open ChromeDriver browser
path = os.getcwd()
log_file = path + "\\IKE\\Ike Carrier Point\\carrier_point_log.txt"
html_file = path + "\\IKE\\Ike Carrier Point\\ike_carrier_point.html"
chrome_driver_path = path + "\\IKE\\chromedriver_win32\\chromedriver.exe"
json_tender_file = path + "\\IKE\\Ike Carrier Point\\carrier_point_tenders_json.json"
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options) 
print("Opening ChromeDriver")

driver.get(url) #load url
print("Loading " + url)

# Defining class objects 
browser = Browser()
login = Login()
log = Log()

browser.wait(5) #wait for browser to load 

# Defining credentials to pass to enter_credentials method
username = ""
password = ""

login.enter_credentials(username, password) #enter login credentials
login.press_logon_button() #press login button

# use requests and beautiful soup together, doesnt work with javascript driven web pages
# r = requests.get(driver.current_url) #get request with current url
# soup = BeautifulSoup(r.text, 'html.parser') # saves html from get request into 'soup' variable

# use selenium and beautiful soup together, works with javascript driven web pages
html = driver.execute_script("return document.documentElement.outerHTML")
soup = BeautifulSoup(html, 'html.parser')

# write html file to file
f = open(html_file, "w")
f.write(str(soup))
f.close()

output = list() #defile output variable
table = driver.find_elements_by_xpath('//table')[-11] #search for table 12th from the bottom of the page

output.append([i.text for i in table.find_elements_by_tag_name('th')]) #data scrape all th within table and add to output list, gets header information
# output = [i for i in output if i!='']

rows = table.find_elements_by_tag_name('tr') #find all tr's within table

for row in rows:
    a = ['{}'.format(x.text) for x in row.find_elements_by_tag_name('td')]
    a = a[:7] + [k for k in a[7:] if k!='']
    if len(a) != 0:
        output.append(a)
    # print(row.text)
    print(a)

file = os.path.join('carrierpoint.csv') #get current working directory and create .csv 
outfile = open(file, "w") #opens a file for writing, creates the file if it does not exist

# write tr's into .csv file
for row in output:
    outfile.write('"' + '","'.join(row) + '"\n')
outfile.close()

#using pandas to format JSON from csv
df = pd.read_csv('carrierpoint.csv',header=1) #reading .csv into variable df(data frame)
df.dropna(how='all',inplace=True) #remove missing values
df.reset_index(drop=True,inplace=True) #reset the index, or a level of it
df.to_json('carrierpoint.json') #convert the object to a JSON string

print('Data downloaded and file saved with name carrierpoint.json')

# post JSON file 
files = {'file': open(json_tender_file, 'rb')}
headers = {'Authorization' : '(some auth code)', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
response = requests.post('http://httpbin.org/post', files=files)
print(response.status_code)
print(response.json())

#check if tender is still on webpage 
driver.refresh() #refresh browser

# send email with (email_subject, email_body) parameters
# send_email("Carrier Point - JSON", str(tender_dict))

# close all browser sessions and terminate driver graciously
driver.quit()