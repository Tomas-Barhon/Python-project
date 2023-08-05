from .visualizer import VisualizerOfCriminalData
from .data_API_downloader import Downloader, DataPipeline, MethodOrderError
import pytest
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def test_visualizer_constructor_error():
    pipeline = DataPipeline(crime_data = None,create_data = False)
    pipeline.match_crime_data_to_polygons()
    pipeline.compute_counts_per_polygon()
    pipeline.preprocess_paq_data()
    table = pipeline.merge_final_table()
    table.drop(["Lidé v exekuci (2021) [%]"],axis = 1, inplace = True)
    with pytest.raises(ValueError) as exc_info:
        VisualizerOfCriminalData(table)
    assert str(exc_info.value) == "The data_table is not in the correct format, try to follow the intruction for the preprocessing pipeline."

def test_downloader_constructor_error_year_1():
    year = "a"
    if type(year) != int:
        with pytest.raises(TypeError) as exc_info:
            downloader = Downloader(year = year, month = 6)
        assert str(exc_info.value) == "Expected an integer, but received {}.".format(type(year).__name__)
    if type(year) == int:
        with pytest.raises(ValueError) as exc_info:
            downloader = Downloader(year = year, month = 6)
        assert str(exc_info.value) == "The year has to be greater than 2012."

def test_downloader_constructor_error_year_2():
    year = 2000
    if type(year) != int:
        with pytest.raises(TypeError) as exc_info:
            downloader = Downloader(year = year, month = 6)
        assert str(exc_info.value) == "Expected an integer, but received {}.".format(type(year).__name__)
    if type(year) == int:
        with pytest.raises(ValueError) as exc_info:
            downloader = Downloader(year = year, month = 6)
        assert str(exc_info.value) == "The year has to be greater than 2012."

def test_downloader_constructor_error_month_1():
    month = "a"
    if type(month) != int:
        with pytest.raises(TypeError) as exc_info:
            downloader = Downloader(year = 2015, month = month)
        assert str(exc_info.value) == "Expected an integer, but received {}.".format(type(month).__name__)

    if type(month) == int:
        with pytest.raises(ValueError) as exc_info:
            downloader = Downloader(year = 2015, month = month)
        assert str(exc_info.value) == "The month has to be between 1-12."

def test_downloader_constructor_error_month_2():
    month = month = 13
    if type(month) != int:
        with pytest.raises(TypeError) as exc_info:
            downloader = Downloader(year = 2015, month = month)
        assert str(exc_info.value) == "Expected an integer, but received {}.".format(type(month).__name__)

    if type(month) == int:
        with pytest.raises(ValueError) as exc_info:
            downloader = Downloader(year = 2015, month = month)
        assert str(exc_info.value) == "The month has to be between 1-12."

def test_downloader_multiple_years_1():
    years = [2014,"a"]
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

def test_downloader_multiple_years_2():
    years = [2011,2010]
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

def test_no_years_available():
    years = [5000,8000]
    downloader = Downloader(2014,6)
    with pytest.raises(ValueError) as exc_info:
        downloader.get_multiple_years(years)
    assert str(exc_info.value) == "You might have chosen years that do not have the data available yet. Try to check this on the kriminalita.policie API."

def test_no_bool_pipeline():
    with pytest.raises(ValueError) as exc_info:
        DataPipeline(crime_data = None, create_data = "a")
    assert str(exc_info.value) == "create_data must be set to True or False."

def test_no_dataframe_pipeline():
    with pytest.raises(ValueError) as exc_info:
        DataPipeline(crime_data = [3,2,1], create_data = True)
    assert str(exc_info.value) == "If you want to create data you need to provide the crime data in a pd.DataFrame created by the downloader."

    with pytest.raises(ValueError) as exc_info:
        DataPipeline(crime_data = None, create_data = True)
    assert str(exc_info.value) == "If you want to create data you need to provide the crime data in a pd.DataFrame created by the downloader."

def test_wrong_order_exception():
    download = Downloader(2014,5)
    download.get_request()
    data = download.unzip_files_return_dataframe()
    pipeline = DataPipeline(crime_data = data, create_data = True)
    with pytest.raises(MethodOrderError) as exc_info:
        pipeline.compute_counts_per_polygon()
    assert str(exc_info.value) == "MethodOrderError: 'compute_counts_per_polygon' was called out of order.\nExpected order: ['match_crime_data_to_polygons', 'compute_counts_per_polygon', 'preprocess_paq_data', 'merge_final_table']"

    with pytest.raises(MethodOrderError) as exc_info:
        pipeline.merge_final_table()
    assert str(exc_info.value) == "MethodOrderError: 'merge_final_table' was called out of order.\nExpected order: ['match_crime_data_to_polygons', 'compute_counts_per_polygon', 'preprocess_paq_data', 'merge_final_table']"


def main():
    #running the test to test that if a column is missing the class will return ValueError for visualizer
    test_visualizer_constructor_error()
    #testing different wrong inputs to the constructor of Downloader
    test_downloader_constructor_error_year_1()
    test_downloader_constructor_error_year_2()
    test_downloader_constructor_error_month_1()
    test_downloader_constructor_error_month_2()
    #testing for wrong input to download_multiple_years method
    test_downloader_multiple_years_1()
    test_downloader_multiple_years_2()
    #years that do not have data available test
    test_no_years_available()
    #no tests for FileNotFound as that would require deleting the files and the Error is quite obvious
    
    #testing wrong inputs to pipeline
    test_no_bool_pipeline()
    test_no_dataframe_pipeline()
    #tests when some method is called before it should have been correctly called
    test_wrong_order_exception()

if __name__ == "__main__":
    main()