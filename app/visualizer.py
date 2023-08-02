#importing packages
import seaborn as sns
import folium
import matplotlib.pyplot as plt
class VisualizerOfCriminalData:
    """
    Visualizer that can return choropleth Folium maps for 6 different parameters with the polygons on the level ORP ("obce s rozšířenou působností"): 
    "Počet kriminálních aktivit per capita","Lidé v exekuci (2021) [%]","Propadání (průměr 2015–2021) [%]",
    "Podíl lidí bez středního vzdělání (2021) [%]","Domácnosti čerpající přídavek na živobytí (2020) [%]","Criminality risk index", 
    it can visualize scatter plots with regression line where the first parameters stands for a response variable against the 4 indicators 
    or it can visualize correlation heatmap of those parameters.

    ...

    Attributes
    ----------
    data_table : DataFrame
        DataFrame obatined from the pipeline class which does include all the parameters for each ORP, otherwise an error will be raised. 

    Methods
    -------
    get_folium_maps()
        Returns a list of 6 choropleth Folium maps that can be shown by the user in Jupyter simply as returned_list[i], while i is an int from 0-5.
    show_scatter_correlations()
        Plots 4 subplots each of them being one of the explanatory variables against the "Počet kriminálních aktivit per capita" acting as the response variable. 
        The method will work only if the data_table provided to the constructor was in the correct format.
    show_correlation_heatmap()
        Plots correlation heatmap of the explanatory variables with the response variable "Počet kriminálních aktivit per capita".
        The method will work only if the data_table provided to the constructor was in the correct format.

    """
    def __init__(self, data_table) -> None:
        self.CZ_COORDINATES = [49.8037633,15.4749126]
        self.data_table = data_table
        self.relative_crime_map = folium.Map(location = self.CZ_COORDINATES,zoom_start = 8.4)
        self.foreclosure_map = folium.Map(location = self.CZ_COORDINATES,zoom_start = 8.4)
        self.dropout_rate_map = folium.Map(location = self.CZ_COORDINATES,zoom_start = 8.4)
        self.without_highschool_map = folium.Map(location = self.CZ_COORDINATES,zoom_start = 8.4)
        self.benefits_map = folium.Map(location = self.CZ_COORDINATES,zoom_start = 8.4)
        self.criminality_risk_index_map = folium.Map(location = self.CZ_COORDINATES,zoom_start = 8.4)
        for name in ["Počet kriminálních aktivit per capita","Lidé v exekuci (2021) [%]","Propadání (průměr 2015–2021) [%]",
                            "Podíl lidí bez středního vzdělání (2021) [%]","Domácnosti čerpající přídavek na živobytí (2020) [%]","Criminality risk index"]:
            try:
                a = data_table[name]
            except Exception:
                print("The data_table is not in the correct format, try to follow the intruction for the preprocessing pipeline.")
                


    def get_folium_maps(self):
        """
        Returns a list of 6 choropleth Folium maps that can be shown by the user in Jupyter simply as returned_list[i], while i is an int from 0-5.
        """
        map_buffer = [self.relative_crime_map,self.foreclosure_map,self.dropout_rate_map,self.without_highschool_map,self.benefits_map,self.criminality_risk_index_map]
        column_name_buffer = ["Počet kriminálních aktivit per capita","Lidé v exekuci (2021) [%]","Propadání (průměr 2015–2021) [%]",
                            "Podíl lidí bez středního vzdělání (2021) [%]","Domácnosti čerpající přídavek na živobytí (2020) [%]","Criminality risk index"]
        self.english_legend_name_buffer = ["Criminality per capita","People in foreclosure (2021) [%]","Dropout (average 2015–2021) [%]",
                            "Share of people without completed high school (2021) [%]","Households on allowances (2020) [%]","Criminality risk index"]
        map_output_list = []
        for map, column_name, english_legend_name in zip(map_buffer, column_name_buffer, self.english_legend_name_buffer):
            folium.Choropleth(
            geo_data=self.data_table,
            data=self.data_table,
            columns=["ORP", column_name],
            key_on="feature.properties.ORP",
            fill_color="RdYlGn_r",
            fill_opacity=0.8,
            line_opacity=0.3,
            nan_fill_color="white",
            legend_name=english_legend_name,).add_to(map)
            folium.LayerControl().add_to(map)
            map_output_list.append(map)
        return map_output_list
    
    def show_scatter_correlations(self):
        """
        Plots 4 subplots each of them being one of the explanatory variables against the "Počet kriminálních aktivit per capita" acting as the response variable. 
        The method will work only if the data_table provided to the constructor was in the correct format.
        """
        fig, axes = plt.subplots(nrows=2, ncols=2,figsize=(10,10))
        sns.regplot(data=self.data_table, x="Lidé v exekuci (2021) [%]",y="Počet kriminálních aktivit per capita", color="blue", scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'}, ax=axes[0,0])
        sns.regplot(data=self.data_table, x="Podíl lidí bez středního vzdělání (2021) [%]",y="Počet kriminálních aktivit per capita", color="blue", scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'}, ax=axes[0,1])
        sns.regplot(data=self.data_table,x="Domácnosti čerpající přídavek na živobytí (2020) [%]",y="Počet kriminálních aktivit per capita", color="blue", scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'}, ax=axes[1,0])
        sns.regplot(data=self.data_table, x="Propadání (průměr 2015–2021) [%]",y="Počet kriminálních aktivit per capita", color="blue", scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'}, ax=axes[1,1])
        plt.show()
        
    def show_correlation_heatmap(self):
        """
        Plots correlation heatmap of the explanatory variables with the response variable "Počet kriminálních aktivit per capita".
        The method will work only if the data_table provided to the constructor was in the correct format.
        """
        sns.heatmap(self.data_table[["Počet kriminálních aktivit per capita","Lidé v exekuci (2021) [%]","Propadání (průměr 2015–2021) [%]",
                            "Podíl lidí bez středního vzdělání (2021) [%]","Domácnosti čerpající přídavek na živobytí (2020) [%]"]].corr()[["Počet kriminálních aktivit per capita"]].sort_values(by="Počet kriminálních aktivit per capita"), linewidths=1, annot=True)