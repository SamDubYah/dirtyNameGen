#!/usr/bin/python3

import csv      #used for CSV exports
import datetime #used for datetime.today
import os       #used for os.system() and os.name()
import requests #Primary module to get web data
import time     #used for time.sleep()
#from pymongo import MongoClient #mongoDB used to store information
from bs4 import BeautifulSoup #used to parse website and collect data




#### [Constants] ####
# site to generate fake names
WEBSITE = "https://www.fakenamegenerator.com/"
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'} # modify

#### [PROXY] ####
PROXY = False #DEFAULT 'False'
PROXIES = {"http": "http://127.0.0.1:8080", "https":"http://127.0.0.1:8080"}


#### [DEFAULTS] ####
fakenameCount = 5# default 5 fake names generateed
processLimit = 5 # defualt 5 requests at once
waitRequest = 10 # default 10ms wait time between requests 
outPutCSV = False# default False out put to csv file
outPutDB = True  # default True out put to MongoDB
runOffline = False#Sets script to run offline, getting information from seclists


#process spawner
def processSpawn():
    print("TO BE REPLACED")



#Get webpage and return raw html
def getWebpage():
    
    #If PROXY is false, run normally
    if not PROXY:
        r = requests.get(WEBSITE, headers=HEADERS)#UPDATE AFTER 
        return r
    else:
        r = requests.get(WEBSITE, headers=HEADERS, proxies=PROXIES, verify=False)
        return r



#clearn data and return desired info
def BeautifulSoup_Sort(req):
    
    #defining a dictonary to add data to
    dict = {}

    soup = BeautifulSoup(req.text, 'html.parser')

    #get full fake name info within 'content' class
    fakenamegen_content = soup.find(class_='content')

    #get full name from 'content' class
    fullName = fakenamegen_content.find('h3').string #fakenamegen_fullname.contents prints out "['First M. Last']"
    dict.update({'Name':fullName})

    #get address from 'adr' class
    ###gets gets the entire contents from 'adr' class, gets text of class using space as separator, strip leading whitespace
    address = fakenamegen_content.find(class_='adr').get_text(separator=" ").strip()
    dict.update({'Address':address})
    
    #get phone number from 'extra' class
    fakenamegen_extra = fakenamegen_content.find_all('dl')
    for dlItem in fakenamegen_extra:
        dtItem = dlItem.find('dt')
        ddItem = dlItem.find('dd')
        
        #Change Visa/MasterCard to CC#
        if 'Visa' in dtItem:
            print("[!] Attempting to change Visa")
            dtItem.string.replace('Visa', 'CCN')
            print(dtItem)
            print(type(dtItem))
            print(ddItem)
        elif 'MasterCard' in dtItem:
            print("[!] Attempting to change MasterCard")
            dtItem.string.replace('MasterCard', 'CCN')
            print(dtItem)
            print(type(dtItem))
            print(ddItem)
        
        dict.update({dtItem.string:ddItem.string})
    

    #pop 'QR Code' and SSN as they dont populate correctly
    dict.pop('QR Code')
    dict.pop('SSN')
   
    #return the dictionary items
    return dict

def sendToDB(nameDict):
    mongo_client = MongoClient('mongodb://localhost:27017')
    mydb = mongo_client.fakename_DB
    mycol = mongo_client.fakename_COL
    returnMsg = mydb.fakename_COL.insert_many(nameList)
    print(returnMsg)


#Sends fake name data to a csv file
def sendToCSV(nameDict):
    csv_Columns = nameDict[0].keys()
    csv_file = ("fakeNames_%s.csv"%datetime.date.today())

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile,csv_Columns)
            writer.writeheader()
            writer.writerows(nameDict)

    except IOError:
        print("[!] I/O Error")



#Get user input of type integer
def getUserInput():
    while True:
        try:
            userInput = int(input("Enter Value: "))
            return userInput
        except:
            print ("[!] Read Error")


if __name__ == "__main__":
    
    #Selection menu
    while True: 
        #Clear screen to rebuild menu
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("[*] 1: Number of fake names generated \tCurrent:%d \t(Defualt=5)"%fakenameCount)
        print("[*] 2: Toggle Output to CSV file \tCurrent:%s \t(Default=False)"%outPutCSV)
        print("[*] 3: Toggle Output to MongoDB \tCurrent:%s \t(Default=True)"%outPutDB) 
        print("[*] 4: Wait time between requests \tCurrent:%dms \t(Default=10ms)"%waitRequest)
        print("[*] 5: Number of processes spawned \tCurrent:%d \t(Default=5)"%processLimit)
        print("[*] 9: Run scrip in offline mode \tCurrent:%s \t(WORK IN PROGRESS)"%runOffline)
        print("[*] 0: Start the script")        
        
        choice = getUserInput()

        if choice == 0:
            break
        elif choice == 1:
            print("[^] Changing generated count")
            fakenameCount = getUserInput()
        elif choice == 2:
            outPutCSV = not outPutCSV
        elif choice == 3:
            outPutDB = not outPutDB
        elif choice == 4:
            print("[^] Changing Wait time")
            waitRequest = getUserInput()
        elif choice == 5:
            print("[^] Changing processes spawned")
            processLimit = getUserInput()
        elif choice == 9:
            runOffline = not runOffline
        else:
            print("[!] Unknown Choice")
            time.sleep(100)

        
    
    #define outsite of forloop to pass to DB
    nameList = []

    for x in range(fakenameCount):

        #get and store raw page request
        req = getWebpage()
    
        #scrape request, format and store into nameDict
        nameList.append( BeautifulSoup_Sort(req))


    #store information in database
    if outPutDB:
        sendToDB(nameList)

    #export information to a csv
    if outPutCSV:
        sendToCSV(nameList)

