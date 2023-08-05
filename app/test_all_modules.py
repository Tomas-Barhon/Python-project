from visualizer import VisualizerOfCriminalData
from data_API_downloader import Downloader, DataPipeline
import pytest
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def visualizer_constructor_error():
    pipeline = DataPipeline(crime_data = None,create_data = False)
    pipeline.match_crime_data_to_polygons()
    pipeline.compute_counts_per_polygon()
    pipeline.preprocess_paq_data()
    table = pipeline.merge_final_table()
    table.drop(["Lidé v exekuci (2021) [%]"],axis = 1, inplace = True)
    with pytest.raises(ValueError) as exc_info:
        VisualizerOfCriminalData(table)
    assert str(exc_info.value) == "The data_table is not in the correct format, try to follow the intruction for the preprocessing pipeline."

def downloader_constructor_error_year(year):
    if type(year) != int:
        with pytest.raises(TypeError) as exc_info:
            downloader = Downloader(year = year, month = 6)
        assert str(exc_info.value) == "Expected an integer, but received {}.".format(type(year).__name__)
    if type(year) == int:
        with pytest.raises(ValueError) as exc_info:
            downloader = Downloader(year = year, month = 6)
        assert str(exc_info.value) == "The year has to be greater than 2012."

def downloader_constructor_error_month(month):
    if type(month) != int:
        with pytest.raises(TypeError) as exc_info:
            downloader = Downloader(year = 2015, month = month)
        assert str(exc_info.value) == "Expected an integer, but received {}.".format(type(month).__name__)

    if type(month) == int:
        with pytest.raises(ValueError) as exc_info:
            downloader = Downloader(year = 2015, month = month)
        assert str(exc_info.value) == "The month has to be between 1-12."

def downloader_multiple_years(years):
    downloader = Downloader(2014,6)
    for year in years:
        if type(year) != int:
            with pytest.raises(TypeError) as exc_info:
                downloader.get_multiple_years(years)
            assert str(exc_info.value) == "Expected an integer, but received {}.".format(type(year).__name__)
        else:
            if year < 2012:
                with pytest.raises(ValueError) as exc_info:
                    downloader.get_multiple_years(years)
                assert str(exc_info.value) == "The year has to be greater than 2012."

def no_years_available(years):
    downloader = Downloader(2014,6)
    with pytest.raises(ValueError) as exc_info:
        downloader.get_multiple_years(years)
    assert str(exc_info.value) == "You might have chosen years that do not have the data available yet. Try to check this on the kriminalita.policie API."

def main():
    #running the test to test that if a column is missing the class will return ValueError for visualizer
    visualizer_constructor_error()
    #testing different wrong inputs to the constructor of Downloader
    downloader_constructor_error_year(year = "a")
    downloader_constructor_error_year(year = 2000)
    downloader_constructor_error_month(month = "a")
    downloader_constructor_error_month(month = 13)
    #testing for wrong input to download_multiple_years method
    downloader_multiple_years([2014,"a"])
    downloader_multiple_years([2011,2012])
    #years that do not have data available test
    no_years_available([5000,8000])


if __name__ == "__main__":
    main()