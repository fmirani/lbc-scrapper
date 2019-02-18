from datetime import datetime
import pandas as pd
import os.path
import drive

# Pandas Pickle data file name
pFile = "data.pkl"

# CSV table file name
cFile = "data.csv"

# Create new data from search or update existing table
# Create -> cu = True   /    Update -> cu = False
cu = True

if __name__ == "__main__":
    if cu:  # Creating primary table out of search results
        # Define all the variables
        brand = "Citroen"
        model = "C3"
        start = datetime.now()
        cat = 2
        region = 12
        fuel = 1
        mileage = "min-10000"
        price = "8000-max"
        kw = ""
        # Creating primary URL to run
        url = "https://www.leboncoin.fr/recherche/?category={}&text={}&regions={}&model={}&" \
              "brand={}&fuel={}&mileage={}&price={}&page=".format(cat, kw, region, model, brand, fuel, mileage, price)
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
