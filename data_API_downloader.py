#importing packages
import pandas as pd
import requests
import numpy as np
from zipfile import ZipFile
import geopandas as gp
from shapely import geometry
from shapely.geometry import Point

class Downloader:
    def __init__(self, year, month) -> None:
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
    
class Data_pipeline:
    def __init__(self, crime_data, create_data = True) -> None:
        self.create_data = create_data
        self.people_in_polygons = pd.read_excel("počet_obyvatel_ORP.xlsx").dropna()
        self.people_in_polygons.reset_index(drop=True,inplace=True)
        self.people_in_polygons.rename(columns = {"Kraje / SO ORP":"ORP_NAZEV","Počet\nobyvatel\ncelkem":"AMMOUNT"},inplace = True)
        geojson = gp.read_file("ORP_P.shp",encoding = "Windows-1250")
        self.polygons = geojson.to_crs(epsg=4326)
        if self.create_data:
            self.crime_data = crime_data
        if not self.create_data:
            self.data_in_polygons = pd.read_csv("data_in_polygons.csv")
            self.data_in_polygons = self.data_in_polygons.drop(["Unnamed: 0"],axis = 1)
        

    def match_crime_data_to_polygons(self):
        if self.create_data:
            self.crime_data = self.crime_data[(self.crime_data["relevance"] == 3) | (self.crime_data["relevance"] == 4)]
            self.crime_data = self.crime_data[(self.crime_data["state"] == 1) | (self.crime_data["state"] == 2) | (self.crime_data["state"] == 3) | (self.crime_data["state"] == 4)]
            self.crime_data= self.crime_data[(self.crime_data["types"] >= 18) & (self.crime_data["types"] <= 62)]
            self.crime_data["ORP"] = np.nan
            self.crime_data["points"] = self.crime_data.apply(lambda row: Point(row["x"],row["y"]),axis=1)
            for indx,point in enumerate(self.crime_data["points"]):
                for region_name,polygon in zip(self.polygons["NAZEV"],self.polygons["geometry"]):
                    if point.within(polygon):
                        self.crime_data.iloc[indx,8] = region_name
                        break
            self.data_in_polygons = self.crime_data
        if not self.create_data:
            self.data_in_polygons = pd.read_csv("data_in_polygons.csv")
            self.data_in_polygons = self.data_in_polygons.drop(["Unnamed: 0"],axis = 1)
        
    def compute_counts_per_polygon(self):
        counts = self.data_in_polygons["ORP"].value_counts().to_frame()
        counts.reset_index(inplace=True)
        self.counts = counts.rename(columns = {'index':'ORP',"ORP":"counts"})
        
    def preprocess_paq_data(self):
        self.paq_data = pd.read_csv("Data-pro-Python-DataPAQ.csv")
        self.paq_data.drop(['Propadání (průměr 2015–2021) / Průměr ČR [%]',
       'Propadání (průměr 2015–2021) / Průměr kraje [%]',
       'Propadání (průměr 2015–2021) / Průměr okresu [%]',
       'Propadání (průměr 2015–2021) / Průměr sociálně podobných ORP [%]',
       'Názvy sociálně podobných ORP', 'Kódy sociálně podobných ORP','Domácnosti čerpající přídavek na živobytí (2020) / Průměr ČR [%]',
       'Domácnosti čerpající přídavek na živobytí (2020) / Průměr kraje [%]',
       'Domácnosti čerpající přídavek na živobytí (2020) / Průměr okresu [%]',
       'Domácnosti čerpající přídavek na živobytí (2020) / Průměr sociálně podobných ORP [%]','Podíl lidí bez středního vzdělání (2021) / Průměr ČR [%]',
       'Podíl lidí bez středního vzdělání (2021) / Průměr kraje [%]',
       'Podíl lidí bez středního vzdělání (2021) / Průměr okresu [%]',
       'Podíl lidí bez středního vzdělání (2021) / Průměr sociálně podobných ORP [%]','Lidé v exekuci (2021) / Průměr ČR [%]',
       'Lidé v exekuci (2021) / Průměr kraje [%]',
       'Lidé v exekuci (2021) / Průměr okresu [%]',
       'Lidé v exekuci (2021) / Průměr sociálně podobných ORP [%]','Kód ORP','Kód okresu', 'Název okresu', 'Kód kraje',
       'Název kraje'],axis = 1,inplace=True)
        self.paq_data.replace(to_replace="Praha",value="Hlavní město Praha",inplace=True)

    def merge_final_table(self):
        self.final_table = self.polygons.merge(self.counts,how="left",left_on=["NAZEV"],right_on=["ORP"])
        self.final_table = self.final_table.merge(self.paq_data,how="left",left_on=["NAZEV"],right_on=["Název ORP"])
        self.final_table = self.final_table.merge(self.people_in_polygons,how="left",left_on=["NAZEV"],right_on=["ORP_NAZEV"])
        self.final_table = self.final_table.fillna(0)
        self.final_table["Počet kriminálních aktivit per capita"] = self.final_table["counts"]/self.final_table["AMMOUNT"]
        self.final_table = self.final_table.replace(to_replace=np.inf,value=0)
        self.final_table.drop(["NAZEV","counts","Název ORP","ORP_NAZEV","AMMOUNT"],axis = 1,inplace=True)
        weights = self.final_table.corr()[["Počet kriminálních aktivit per capita"]]
        weights.drop(["Počet kriminálních aktivit per capita"],axis = 0,inplace=True)
        weights = weights.values
        self.final_table["Criminality risk index"] = self.final_table.apply(lambda row: (row["Lidé v exekuci (2021) [%]"]*weights[0] + row["Podíl lidí bez středního vzdělání (2021) [%]"]*weights[1] +
                                                        row["Domácnosti čerpající přídavek na živobytí (2020) [%]"]*weights[2] + row["Propadání (průměr 2015–2021) [%]"]*weights[3])[0],axis=1)
        return self.final_table
