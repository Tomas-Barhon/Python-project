# Python-project
This is a python project for our subject Data Processing in Python (JEM207) belonging to Tomáš Barhoň and Radim Plško.
<br/>
We will be studying the impact of socio-economical indicators that might be the driving forces for an increased economical criminality in different regions in the Czech Republic.
<br/>
The main data source will be the https://kriminalita.policie.cz/ API that contains information about all sorts of crimes and their geographical location.
<br/>
For the socio-economical data we used the data from PAQ research. The four indicators chosen were "Lidé v exekuci (2021) [%]" (ammount of people with foreclosure), "Podíl lidí bez středního vzdělání (2021) [%]" (ammount of people without completed highschool), "Domácnosti čerpající přídavek na živobytí (2020) [%]" (ammount of people receiving social benefits), "Propadání (průměr 2015–2021) [%]" (ammount of kids that obtain the worst grade 5 from any subject at the end of summer semester). These data are obtained from various open-data sources that are mentioned in the references.
<br/>
The data on criminality is subseted in order to fulfill following conditions. The crime is illegal and is confirmed that it really happened. The record has relevance "Místo následku" (the place where the consequences appear) "Místo spáchání" (the exact place where it was commited). And finally we subset only the crimes that are of an economical nature. (thefts, burglary, ...). We are analysing the data from 2021-2023 (currently till June) which yields about 500 000 criminal records.
<br/>
The main purpouse of the project is to analyse the data on the level of "ORP" which is relatively small administrative unit in the Czech Republic. We would like to take two different approaches. One being visualizations of the states of each factor in the regions and visually comparring the maps. The second one being correlational analysis between criminality and each of the indicators.
<br/>
We analysed how the individual indicators influence the level of economic criminality. As following, we created the index of criminality that indicates how each ORPs stand on the scale of criminal activities compared to other regions. All this based on the information we received from the previous analysis.
<br/>
References:
<br/>
https://www.datapaq.cz/
<br/>
PAQ data endpoints:
<br/>
Domácnosti čerpající přídavek na živobytí (2020) po ORP -> Agentura pro sociální začleňování, MPSV
<br/>
Podíl lidí bez středního vzdělání -> ČSÚ, SLDB 2021
<br/>
Propadání (2015-2021)-> ČŠI
<br/>
Lidé v exekuci (2021)-> Exekutorská komora ČR, ČSÚ, Czech Household Panel Study
<br/>
https://kriminalita.policie.cz/
<br/>
https://www.czso.cz/csu/xs/obyvatelstvo-xs
Czech Statistical office - the data on the population in each ORP
as the data was in quite a messy Excel file, we had to transform it manually and the new table is now to your disposal in our repository (app/počet_obyvatel_ORP.xlsx) and can be used in other projects with similar nature. It makes it easier to share the project with others.
<br/>

## How to install the project
<br/>

## How to use the modules seperately for your own project
<br/>

### Downloader (check "how_to_downloader.ipynb")
Downloader is a module to download data from the https://kriminalita.policie.cz/ API. It is designed to either download data for one specific month or for multiple years and return them to user as pandas.DataFrame.
<br/>
In order to use Downloader module you first need to import it using the following command:

<pre>
from data_API_downloader import Downloader
</pre>

Now to obtain the criminal records for one specific month you need to run the following lines of code.

<pre>
download = Downloader(year= 2012,month = 5)
#send the get request to obtain the zip file
download.get_request()
#unzip the downloaded file and get .csv file for the month
download.unzip_files_return_dataframe()
</pre>

You can freely adjust the year and month. It is important that the year and month are numbers in integer form. The data is available from year 2012, that means you have to enter year higher or equal to 2012 and month has to clearly be from range 1-12 otherwise an error will be returned.
<br/>

In order to use Downloader to download data for multiple years you need to run the following line of code.
<pre>
#How to use Downloader to download data for multiple years
crime_data = download.get_multiple_years(years = [2012,2013,2014])
</pre>
You can adjust the years you want to download the data for. Mind that again years must be a list of integers from 2012 and higher. It is important that you specify at least one year with some available data otherwise an error will be raised. For example specifing years = [5000,5001] will result in a specific ValueError.

### DataPipeline (check "how_to_data_pipeline.ipynb")
DataPipeline is a module created to process data created by Downloader and create a final table where each ORP does have all of the 6 parameters and can be used for further analysis of users choice. Thus it can be freely used in any other project requiring such data on the level of ORP.
<br/>
First, we need to import the two modules with the following command:

<pre>
from data_API_downloader import Downloader, DataPipeline
</pre>
Now we proceed with initializing the Downloader object with the year and month being irrelevant if we want to use the get_multiple_years method. And we run already mentioned get_multiple_years method as following:
<pre>
download = Downloader(year= 2012,month = 5)
crime_data = download.get_multiple_years(years = [2012,2013,2014])
</pre>
Then the user needs to initialize the DataPipeline object passing the crime_data created by the Downloader and specifying create_data = True meaning that we want to use the provided new data. If we would set it to False it would use our data from 2021-2023 which are part of the repository. This will be mentioned in the other parts.
<pre>
pipeline = DataPipeline(crime_data = crime_data, create_data = True)
</pre>
To obtain the desired table we need to run the following 4 methods in the correct order and look at the table in the end.
<pre>
pipeline.match_crime_data_to_polygons()
pipeline.compute_counts_per_polygon()
pipeline.preprocess_paq_data()
table = pipeline.merge_final_table()
table.head(10)
</pre>
Make sure to use more years in order to obtain enough observations so that there is at least one observation for each ORP.

### Visualizer (check "how_to_visualizer.ipynb")


## Userguide for the project

<br/>

## How to open the notebook with the Folium maps displayed
<br/>
In order to open the notebook in your web-browser and be able to see all the visualizations you need to open the notebook in nbviewer. 
<br/>
You can find it on the following link:
<br/>
https://nbviewer.org/github/Tomas-Barhon/Python-project/blob/main/app/main.ipynb





