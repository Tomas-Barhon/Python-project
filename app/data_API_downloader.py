#importing packages
import pandas as pd
import requests
import numpy as np
from zipfile import ZipFile
import geopandas as gp
from shapely import geometry
from shapely.geometry import Point

class Downloader:
    """
    Downloader is a class for downloading data from kriminalita.policie API that are stored as geographical points with their attributes specifying them. It can work in two regimes. 
    The first usecase it to download the data for one specific month and unzip it into csv file. The other usecase is meant for more complex analysis as the method get_multiple_years() 
    downloads data for several available years and combines them together into one DataFrame. It is only designed to download data from this specific API for future analysis
    and thus can be used in different project on its own.

    ...

    Attributes
    ----------
    year : int
        The year from which to choose the month you specify later. It has to be of an integer type from 2012 which is the first year that is available on the API. 
        If non-integer is provided it will cause TypeError. If year < 2012 is provided Value Error will be raised.

    month : int
        The month from the specific year you want to obatin the data from. It has to be of an integer type and it has to be in the range from 1-12.
        If non-integer is provided it will cause TypeError. If month does not fall into range 1-12 ValueError will be raised.
        
    Methods
    -------
    get_request()
        Tries to download the data from the kriminalita.policie API for the specified year and month of the class constructor. If it fails it might mean that there is a problem on the side of the API. 
        Check the link, whether the data is available there.

    unzip_files_return_dataframe()
        Returns DataFrame if the previous get_request() was successful by unzipping the downloaded file. Make sure not to rename the downloaded files. Returns None if it was not able
        to unzip the downloaded zip file.  

    get_multiple_years(years)
        Returns a DataFrame with all the data available 

        ...

        Attributes
        ----------
        years : list of int
            List of years in integer form specifing the years from which you want to collect the data. The year has to be higer or equal to 2012 and in order to obtain the DataFrame
            at least some of the years have to have available data for them. Raises TypeError if non-integer list ist passed. Raises ValueError if any of the years if smaller than 2012.

    """
    def __init__(self, year, month) -> None:
        #check that year and month are integers and whether they are from the possible range
        if not isinstance(year, int):
            raise TypeError("Expected an integer, but received {}.".format(type(year).__name__))
        
        if not isinstance(month, int):
            raise TypeError("Expected an integer, but received {}.".format(type(month).__name__))
        
        if isinstance(year, int) and isinstance(month, int) and year < 2012:
            raise ValueError("The year has to be greater than 2012.")
        
        if month not in range(1,13):
            raise ValueError("The month has to be between 1-12.")
        
        #convert the numbers from 1-9 to 01-09
        self.months_mapping = ["0" + str(month) if month < 10 else str(month) for month in range(1,13)]
        self.month = str(month)
        self.year = str(year)
        if month in range(1,10):
            self.month = self.months_mapping[month - 1]
        self.file_name = self.year + self.month

        

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
            print("Something went wrong, try to check your previous steps.")
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
            print("Downloader was not able to unzip the file. It might have been renamed or deleted try to repeat your previous steps and follow the instructions carefully.")
            return None
        
    def get_multiple_years(self,years):
        data = []

        #check that all years are integers greater than 2011
        for year in years:
            if not isinstance(year, int):
                raise TypeError("Expected an integer, but received {}.".format(type(year).__name__))
            if isinstance(year, int) and isinstance(month, int) and year < 2012:
                raise ValueError("The year has to be greater than 2012.")
            
        for year in years:
            for month in self.months_mapping:
                self.file_name = f"{year}" + month
                file = self.get_request()
                unzipped_file = self.unzip_files_return_dataframe()
                if isinstance(unzipped_file,pd.DataFrame):
                    data.append(unzipped_file)
        try:
            return pd.concat(data,axis=0,ignore_index=True)
        except:
            raise ValueError("You might have chosen years that do not have the data available yet. Try to check this on the kriminalita.policie API.")
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
