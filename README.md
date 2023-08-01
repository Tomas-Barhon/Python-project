# Python-project
This is a python project for our subject Data Processing in Python (JEM207) belonging to Tomáš Barhoň and Radim Plško.

We will be studying the impact of socio-economical indicators that might be the driving forces for an increased economical criminality in different regions in the Czech Republic.
The main data source will be the https://kriminalita.policie.cz/ API that contains information about all sorts of crimes and their geographical location.
For the socio-economical data we used the data from PAQ research. The four indicators chosen were "Lidé v exekuci (2021) [%]" (ammount of people with foreclosure), "Podíl lidí bez středního vzdělání (2021) [%]" (ammount of people without completed highschool), "Domácnosti čerpající přídavek na živobytí (2020) [%]" (ammount of people receiving social benefits), "Propadání (průměr 2015–2021) [%]" (ammount of kids that obtain the worst grade 5 from any subject at the end of summer semester). These data are obtained from various open-data sources that are mentioned in the references.

The data on criminality is subseted in order to fulfill following conditions. The crime is illegal and is confirmed that it really happened. The record has relevance "Místo následku" (the place where the consequences appear) "Místo spáchání" (the exact place where it was commited). And finally we subset only the crimes that are of an economical nature. (thefts, burglary, ...). We are analysing the data from 2021-2023 (currently till June) which yields about 500 000 criminal records.

The main purpouse of the project is to analyse the data on the level of "ORP" which is relatively small administrative unit in the Czech Republic. We would like to take two different approaches. One being visualizations of the states of each factor in the regions and visually comparring the maps. The second one being correlational analysis between criminality and each of the indicators.

We analysed how the individual indicators influence the level of economic criminality. As following, we created the index of criminality that indicates how each ORPs stand on the scale of criminal activities compared to other regions. All this based on the information we received from the previous analysis.

References:
https://www.datapaq.cz/
PAQ data endpoints:
Domácnosti čerpající přídavek na živobytí (2020) po ORP -> Agentura pro sociální začleňování, MPSV
Podíl lidí bez středního vzdělání -> ČSÚ, SLDB 2021
Propadání (2015-2021)-> ČŠI
Lidé v exekuci (2021)-> Exekutorská komora ČR, ČSÚ, Czech Household Panel Study

https://kriminalita.policie.cz/

https://www.czso.cz/csu/xs/obyvatelstvo-xs
Czech Statistical office - the data on the population in each ORP
as the data was in quite a messy Excel file, we had to transform it manually and the new table is now to your disposal in our repository (app/počet_obyvatel_ORP.xlsx) and can be used in other projects with similar nature. It makes it easier to share the project with others.

## How to install the project with pip

## Userguide for the project




