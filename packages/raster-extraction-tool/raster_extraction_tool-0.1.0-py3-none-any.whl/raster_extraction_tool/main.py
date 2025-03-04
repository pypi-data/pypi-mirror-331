import raster_extraction_tool.raster_extraction_functions as ref

if __name__ == "__main__":
    ref.extract_values(
        input_csv=r"E:\raster_extraction_io\doetinchem\Expanse_adressen_Doetinchem_V2_geocoded.csv",
        raster_folder=r"E:\EXPANSE\Netherlands\_subsets\test",
        output_csv=r"E:\raster_extraction_io\doetinchem\Expanse_adressen_Doetinchem_V2_geocoded_temperatures.csv",
        in_crs='EPSG:28992',
        raster_crs='EPSG:3035',
        decimal='.',
        sep = ';' ,
        writemethod='concat',
    )
