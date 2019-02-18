from datetime import datetime
import time
import locale
import dateparser
import unidecode
from selenium import webdriver
import pandas as pd
locale.setlocale(locale.LC_TIME, '')

# Full path to the chromedriver.exe file
# Currently, the file resides in the same subdirectory as the code files
driverPath = "chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# This function takes a string input and parses for a finish type
# If not found, it returns "NULL" in string format
def ParseTitleForFinish(title):
    tit = title.upper()
    with open ("finish.txt", "r") as file:
        Finish = [line.strip("\n") for line in file.readlines()]
        for fin in Finish:
            if tit.find(fin) > 0:
                return fin
        return "NULL"


# This function takes a string input and parses for the engine type
# If not found, it returns "NULL" in string format
def ParseTitleForEngine(title):
    tit = title.upper()
    with open("engine.txt", "r") as file:
        Engine = [line.strip("\n") for line in file.readlines()]
        for eng in Engine:
            if tit.find(eng) > 0:
                return eng
        return "NULL"


# This function goes through the input file and check if each ad in the list is still up
# Up -> Ad still alive
# Down -> Ad down: car probably sold
def UpdateDataList(file):
    #   Load the driver for Chrome
    driver = webdriver.Chrome(driverPath, chrome_options=options)

    pdf = pd.read_pickle(file)
    for i, row in pdf.iterrows():
        driver.get(row["Link"])
        time.sleep(0.5)
        stat = driver.find_elements_by_class_name("_38YaG")
        if len(stat) > 0:
            pdf.at[i, "Status"] = "Down"
        else:
            pdf.at[i, "Status"] = "Up"
        print(row)
    # Close browser window
    driver.close()
    # Return pandas dataframe
    return pdf


# This function completes the CreateDataList function by going through each ad page in the list
# and supplements the table with the some more data which isn't available on search results page i.e.
# Mileage, Transmission, Finish, Engine and Status
def SupplementDataList(dataframe, driver):

    for i, row in dataframe.iterrows():
        driver.get(row["Link"])
        time.sleep(0.5)
        stat = driver.find_elements_by_class_name("_38YaG")
        print(len(stat))
        if len(stat) > 0:
            dataframe.at[i, "Status"] = "Down"
        else:
            yr = driver.find_elements_by_class_name("_3Jxf3")[2].text
            km = driver.find_elements_by_class_name("_3Jxf3")[3].text
            bv = driver.find_elements_by_class_name("_3Jxf3")[5].text
            dataframe.at[i, "Year"] = yr
            dataframe.at[i, "Mileage"] = km
            dataframe.at[i, "Transmission"] = bv
            dataframe.at[i, "Finish"] = ParseTitleForFinish(row["Title"])
            dataframe.at[i, "Engine"] = ParseTitleForEngine(row["Title"])
            dataframe.at[i, "Status"] = "Up"
        print(row)


# This function takes a search URL as input and
# - goes through all th search results (on all pages)
# - extracts all the info available on the search pages
# - builds a table (list of lists) with the extracted info
# - and finally converts the list into a pandas dataframe after adding labels
def CreateDataList(url):
    #   Load the driver for Chrome
    driver = webdriver.Chrome(driverPath, chrome_options=options)

    tab = []
    row = []

    page = 1
    driver.get(url + str(page))
    time.sleep(1.5)
    driver.save_screenshot("cs.png")
    NbOfAds = driver.find_elements_by_class_name("_2ilNG")[0].text
    if len(NbOfAds) < 1:
        print("There may have been a problem. No ads found on page. Exiting..")
        exit(-1)
    #TotPages = int(int(NbOfAds)/35) + 1
    TotPages = 1
    print("Total {} search results found. Collecting data spread over {} pages...".format(NbOfAds, TotPages))

    while True:
        print("Parsing page no: {}".format(page))
        TitleList = driver.find_elements_by_class_name("_2tubl")
        PriceList = driver.find_elements_by_class_name("_1NfL7")
        CityCodeList = driver.find_elements_by_class_name("_2qeuk")
        DateTimeList = driver.find_elements_by_class_name("mAnae")
        LinkList = driver.find_elements_by_class_name("clearfix")
        driver.stop_client()

        RefList = []
        DateList = []
        TimeList = []
        CityList = []
        CodeList = []
        CarPrice = []

        # Create RefList from LinkList
        for link in LinkList:
            RefList.append(link.get_attribute("href")[34:-5])

        # Condition car price figure
        for Price in PriceList:
            CarPrice.append(Price.text.strip(" €"))

        # Create CityList and CodeList from CityCodeList
        for CityCode in CityCodeList:
            city = CityCode.text[:-6]
            CityList.append(unidecode.unidecode(city))

            CodeList.append(CityCode.text[len(city)+1:])

        # Create DateList and TimeList from DateTimeList
        for DateTime in DateTimeList:
            Date = DateTime.text.split(', ')[0]
            if Date == "Aujourd'hui":
                Date = datetime.strftime(dateparser.parse("aujourd'hui"), '%d-%B')
            if Date == "Hier":
                Date = datetime.strftime(dateparser.parse('hier'), '%d-%B')
            DateList.append(datetime.strftime(dateparser.parse(Date), '%d-%B'))
            TimeList.append(DateTime.text.split(', ')[1])

        # Create main table
        for i in range(len(TitleList)):
            row.append(RefList[i])
            Title = unidecode.unidecode(TitleList[i].text)
            row.append(Title)
            row.append(CarPrice[i])
            row.append(CityList[i])
            row.append(CodeList[i])
            row.append(DateList[i])
            row.append(TimeList[i])
            row.append("Empty Year")
            row.append("Empty Finish")
            row.append("Empty Engine")
            row.append("Empty Transmission")
            row.append("Empty Mileage")
            row.append("https://www.leboncoin.fr/voitures/" + str(RefList[i]) + ".htm/")
            row.append("Empty Status")
            tab.append(row)
            row = []

        # Iterate through pages to collect all data
        page += 1
        if page > TotPages:
            # driver.close()
            break
        driver.get(url + str(page))
        time.sleep(1)

    # Giving labels to data columns
    labels = ["Reference",
              "Title",
              "Price",
              "City",
              "Code",
              "Date",
              "Time",
              "Year",
              "Finish",
              "Engine",
              "Transmission",
              "Mileage",
              "Link",
              "Status"]

    # Converting primary table into a pandas dataframe
    pdf = pd.DataFrame.from_records(tab, columns=labels)

    # Supplementing data from each ad page
    #SupplementDataList(pdf, driver)

    # Close browser window
    driver.close()

    # Return data table in Pandas dataframe format
    return pdf
