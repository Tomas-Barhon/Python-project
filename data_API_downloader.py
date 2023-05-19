#importing packages
import pandas as pd
import requests
from zipfile import ZipFile

class Downloader:
    def __init__(self, year, month):
        self.file_name = f"{year}{month}"

    def get_request(self):
        r = requests.get("https://kriminalita.policie.cz/api/v2/downloads/" + self.file_name + ".zip")
        print(r.status_code)
        self.request = r
        with open(self.file_name + ".zip",'wb') as output_file:
            output_file.write(r.content)
    def unzip_files_return_dataframe(self):
        with ZipFile("C:\\Users\\tomas\\Python-Project\\" + self.file_name + ".zip", 'r') as zObject:
            # Extracting all the members of the zip 
            # into a specific location.
            zObject.extractall(
                path="C:\\Users\\tomas\\Python-Project")
        return pd.read_csv(self.file_name + ".csv")
        
