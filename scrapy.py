from datetime import datetime
import pandas as pd
import os.path
import drive

# Pandas Pickle data file name
pFile = "data.pkl"

# CSV table file name
cFile = "data.csv"

# Create new data from search OR update existing table
# Create -> cu = True   /    Update -> cu = False
cu = True

if cu:  # Creating primary table out of search results
    # Define all the variables
    make = "Citroen"
    model = "C3"
    start = datetime.now()
    cat = 2
    region = "r_12"
    fuel = 1
    mileage = "min-10000"
    price = "8000-max"
    yr = "2018-max"
    # Creating primary URL to run
    url = "https://www.leboncoin.fr/recherche/?category=2&locations={}&model={}&brand={}&fuel={}&price={}&mileage={}" \
          "&regdate={}".format(region, model, make, fuel, price, mileage, yr)
    # Create data table in Pandas dataframe format
    pdf = drive.CreateDataList(url)
    if os.path.exists(pFile):
        FullTable = pd.read_pickle(pFile)
        pd.concat([FullTable, pdf])
        # Drop duplicates
        FullTable.drop_duplicates(subset="Reference", keep="last")
    else:
        print("No existing file found. Starting fresh..")
        FullTable = pdf
else:  # Update existing table
    print("Updating existing table")
    if os.path.exists(pFile):
        FullTable = drive.UpdateDataList(pFile)
    else:
        print("Update not possible. No existing file found. Exiting..")
        exit(-1)

# Save FullTable
FullTable.to_pickle(pFile)

# Setting up everything in a csv Output file
FullTable.to_csv(cFile)
