#importing packages
import pandas as pd
import requests
import numpy as np
from zipfile import ZipFile
import geopandas as gp
from shapely.geometry import Point

class MethodOrderError(Exception):
    """Custom exception class for calling methods in the wrong order."""

    def __init__(self, method_name, expected_order):
        """
        Initialize the MethodOrderError.

        Parameters:
        - method_name (str): The name of the method that was called.
        - expected_order (list): The list of methods that should have been called in order.
        
        """
        self.method_name = method_name
        self.expected_order = expected_order

    def __str__(self):
        """
        Return a string representation of the error.

        Returns:
        - str: A formatted error message.
        """
        return f"MethodOrderError: '{self.method_name}' was called out of order.\nExpected order: {self.expected_order}"


class Downloader:
    """
    Downloader is a class for downloading data from kriminalita.policie API that are stored as geographical points with their attributes specifying them. It can work in two regimes. 
    The first usecase is to download the data for one specific month and unzip it into csv file. The other usecase is meant for more complex analysis as the method get_multiple_years() 
    downloads data for several available years and combines them together into one DataFrame. It is only designed to download data from this specific API for future analysis
    and thus can be reused in different project on its own.

    ...

    Attributes
    ----------
    year : int
        The year from which to choose the month you specify later. It has to be of an integer type from 2012 which is the first year that is available on the API. 

    month : int
        The month from the specific year you want to obatin the data from. It has to be of an integer type and it has to be in the range from 1-12.

    Methods
    -------
    get_request()
        Tries to download the data from the kriminalita.policie API for the specified year and month of the class constructor. If it fails it might mean that there is a problem on the side of the API. 
        Check the link, whether the data is available there.

    unzip_files_return_dataframe()
        Returns DataFrame if the previous get_request() was successful by unzipping the downloaded file. Make sure not to rename the downloaded files. Returns None if it was not able
        to unzip the downloaded zip file.  

    get_multiple_years(years)
        Returns a DataFrame with all the data available for the specified years. It is enough that some months of the year do have available data. 
        For instance when some months from year 2023 are not yet available just the months where it manages to get the data will be part of the DataFrame

        ...

        Attributes
        ----------
        years : list of int
            List of years in integer form specifing the years from which you want to collect the data. The year has to be higer or equal to 2012 and in order to obtain the DataFrame
            at least some of the years have to have available data for them. Raises TypeError if non-integer list ist passed. Raises ValueError if any of the years if smaller than 2012.

    Raises
    ------
    TypeError 
        If non-integer year or month is provided.
    ValueError 
        If year < 2012 is provided.
    ValueError 
        If month does not fall into range 1-12.
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
        """
        Unzips the downloaded ZIP file and returns the data as a Pandas DataFrame.

        Returns:
        - pandas.DataFrame or None: 
            The unzipped data as a DataFrame, or None if the unzip operation fails.
        """
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
        """
        Downloads data for multiple years and combines them into a single DataFrame.

        Parameters:
        years : list of int
            A list of years for which to download the data.

        Returns:
        pandas.DataFrame : 
            The combined data for the specified years as a DataFrame.

        Raises :
        ValueError
            If the data for the specified years is not available on the API.
        """
        data = []
        #check that all years are integers greater than 2011
        for year in years:
            if not isinstance(year, int):
                raise TypeError("Expected an integer, but received {}.".format(type(year).__name__))
            if year < 2012:
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
        
class DataPipeline:
    """
    A class for processing and analyzing data related to crime and demographics.

    This class provides methods for matching crime data to geographical polygons,
    computing counts of crimes per polygon, preprocessing additional data,
    and creating a final table for analysis.

    Parameters
    ----------
    crime_data : pandas DataFrame, None
        The crime data to be processed. If create_data = False crime_data must be set to None (default is None). 

    create_data : bool, optional
        Flag to indicate whether to create data from the provided crime_data or to load them from data_in_polygons (default is False).

    Attributes
    ----------
    create_data : bool
        Flag indicating whether to create data.

    people_in_polygons : pandas DataFrame
        DataFrame containing population data for polygons.

    polygons : GeoDataFrame
        GeoDataFrame containing geographical polygon data.

    crime_data : pandas DataFrame
        DataFrame containing crime data. The data from kriminalita.policie API.

    data_in_polygons : pandas DataFrame
        DataFrame containing matched crime data within corresponding polygons.

    counts : pandas DataFrame
        DataFrame containing counts of crimes per polygon.

    paq_data : pandas DataFrame
        DataFrame containing additional data from PAQ research for further analysis.

    final_table : pandas DataFrame
        Final merged table prepared for analysis and visualizations.

    Methods
    -------
    match_crime_data_to_polygons()
        Match crime data to polygons.

    compute_counts_per_polygon()
        Compute counts of crimes per polygon.

    preprocess_paq_data()
        Preprocess additional data for analysis.

    merge_final_table()
        Merge final tables for analysis.

    Returns
    -------
    final_table : pandas DataFrame
        Final merged table for analysis.
    
    Raises
    ------
    ValueError
        If you want to create the data but did not provide the pd.DataFrame
    ValueError
        If you set create_data to anything different from bool type.
    FileNotFoundError
        If you set create_data = False but do not have data_in_polygons.csv in your directory.
    FileNotFoundError
        When you call preprocess_paq_data but do not have Data-pro-Python-DataPAQ.csv in your directory.
    MethodOrderError
        When you do not follow the correct order how to call the methods.
    """

    def __init__(self, crime_data = None, create_data = False) -> None:
        if not isinstance(create_data, bool):
            raise ValueError("create_data must be set to True or False.")
        if create_data and not isinstance(crime_data,pd.DataFrame):
            raise ValueError("If you want to create data you need to provide the crime data in a pd.DataFrame created by the downloader.")
        
        #load bool whether to load data
        self.create_data = create_data
        #load ammount of people per ORP 
        self.people_in_polygons = pd.read_excel("počet_obyvatel_ORP.xlsx").dropna()
        self.people_in_polygons.reset_index(drop=True,inplace=True)
        self.people_in_polygons.rename(columns = {"Kraje / SO ORP":"ORP_NAZEV",
                                                "Počet\nobyvatel\ncelkem":"AMMOUNT"},inplace = True)
        #read the shapefile with the correct encoding
        geojson = gp.read_file("ORP_P.shp",encoding = "Windows-1250")
        #change the epsg encoding
        self.polygons = geojson.to_crs(epsg=4326)
        
        #TODO:check that crime data was provided and isinstance(DataFrame) 
        #if create_data = True load the provided criminal records
        if self.create_data:
            self.crime_data = crime_data

        #TODO: write to README that data_in_polygons will be part of the repository in order to run the project exactly as we did
        #if the data already exists load it from data_in_polygons.csv
        if not self.create_data:
            try:
                self.data_in_polygons = pd.read_csv("data_in_polygons.csv")
                #delete one column that gets unintentionally created
                self.data_in_polygons = self.data_in_polygons.drop(["Unnamed: 0"],axis = 1)
            except:
                raise FileNotFoundError("File data_in_polygons.csv is probably not in your directory.")
            
    def match_crime_data_to_polygons(self):
        """
        Match crime data to geographical polygons.

        This method matches crime data points to corresponding polygons based on geographical coordinates.

        """

        if self.create_data:
            #filter the data for economic nature only
            self.crime_data = self.crime_data[(self.crime_data["relevance"] == 3) | 
                                            (self.crime_data["relevance"] == 4)]
            self.crime_data = self.crime_data[(self.crime_data["state"] == 1) |
                                            (self.crime_data["state"] == 2) |
                                            (self.crime_data["state"] == 3) | 
                                            (self.crime_data["state"] == 4)]
            self.crime_data= self.crime_data[(self.crime_data["types"] >= 18) & (self.crime_data["types"] <= 62)]
            #create the new column for the name of the ORP
            self.crime_data["ORP"] = np.nan
            #transform the longtitue and lattitude to Point class
            self.crime_data["points"] = self.crime_data.apply(lambda row: Point(row["x"],row["y"]),axis=1)
            #iterate through all the points and find the polygon where they belong, write the name to the ORP column 
            #and break finding of the region (point can only by part of one polygon)
            for indx,point in enumerate(self.crime_data["points"]):
                for region_name,polygon in zip(self.polygons["NAZEV"],self.polygons["geometry"]):
                    if point.within(polygon):
                        self.crime_data.iloc[indx,8] = region_name
                        break

            #load the final matched version to data_in_polygons
            self.data_in_polygons = self.crime_data
        
    def compute_counts_per_polygon(self):
        """
        Compute counts of crimes per polygon.

        This method calculates the counts of crimes within each polygon.

        Raises
        ------
        MethodOrderError
            When you do not follow the correct order how to call the methods.
        """
        try:
            counts = self.data_in_polygons["ORP"].value_counts().to_frame()
            counts.reset_index(inplace=True)
            self.counts = counts.rename(columns = {'index':'ORP',"ORP":"counts"})
        except:
            raise MethodOrderError("compute_counts_per_polygon",["match_crime_data_to_polygons", "compute_counts_per_polygon", "preprocess_paq_data","merge_final_table"])
        
    def preprocess_paq_data(self):
        """
        Preprocess additional data for analysis.

        This method preprocesses additional data for integration into the analysis.

        Raises
        ------
        FileNotFoundError
            When you call preprocess_paq_data but do not have Data-pro-Python-DataPAQ.csv in your directory.
        """
        try:
            self.paq_data = pd.read_csv("Data-pro-Python-DataPAQ.csv")
        except:
            raise FileNotFoundError("You probably do not have Data-pro-Python-DataPAQ.csv in your directory.")
        
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
        """
        Merge final tables for analysis.

        This method merges all previously created data tables to create a final table for analysis and visualizations.

        Returns
        -------
        pandas DataFrame
            The final merged table for analysis.

        Raises
        ------
        MethodOrderError
            When you do not follow the correct order how to call the methods.
        """
        try:
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
        except:
            raise MethodOrderError("compute_counts_per_polygon",["match_crime_data_to_polygons", "compute_counts_per_polygon", "preprocess_paq_data","merge_final_table"])