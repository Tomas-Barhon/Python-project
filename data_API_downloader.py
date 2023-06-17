#importing packages
import pandas as pd
import requests
import numpy as np
from zipfile import ZipFile

class Downloader:
    def __init__(self, year, month):
        self.file_name = f"{year}{month}"

    def get_request(self):
        try:
            r = requests.get("https://kriminalita.policie.cz/api/v2/downloads/" + self.file_name + ".zip")
            self.status_code = r.status_code
            print(self.status_code)
            self.request = r
            if self.status_code == 200:
                with open(self.file_name + ".zip",'wb') as output_file:
                    output_file.write(r.content)
        except:
            pass
    def unzip_files_return_dataframe(self):
        try:
            with ZipFile("./" + self.file_name + ".zip", 'r') as zObject:
                # Extracting all the members of the zip 
                # into a specific location.
                zObject.extractall(
                    path="./")
                return pd.read_csv(self.file_name + ".csv")
        except:
                return None
    def get_multiple_years(self,years):
        data = []
        for year in years:
            for month in ["01","02","03","04","05","06","07","08","09","10","11","12"]:
                self.file_name = f"{year}" + month
                file = self.get_request()
                unzipped_file = self.unzip_files_return_dataframe()
                if isinstance(unzipped_file,pd.DataFrame):
                    data.append(unzipped_file)
        return pd.concat(data,axis=0,ignore_index=True)