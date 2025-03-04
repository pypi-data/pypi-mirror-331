import os
# Increase GDAL Cache Size to 512MB
os.environ['GDAL_CACHEMAX'] = '512'
import numpy as np
from osgeo import gdal, gdal_array
from multiprocessing import Pool, cpu_count, Manager

def calculate_chunk_size(dataset, max_chunk_memory=500 * 1024**2):
    """
    Calculate the chunk size for reading the raster based on the desired maximum memory footprint.

    Parameters:
    dataset (gdal.Dataset): The GDAL dataset representing the raster.
    max_chunk_memory (int, optional): Maximum memory (in bytes) to be used for a chunk. Default is 500 MB.

    Returns:
    tuple: (chunk_width, chunk_height) representing the dimensions of the chunk.
    """
    band = dataset.GetRasterBand(1)
    
    dtype = gdal_array.GDALTypeCodeToNumericTypeCode(band.DataType)
    
    dtype_size = np.dtype(dtype).itemsize
    
    raster_x_size = dataset.RasterXSize
    raster_y_size = dataset.RasterYSize

    max_pixels = max_chunk_memory // dtype_size

    if raster_x_size * raster_y_size <= max_pixels:
        #if the entire raster fits within the memory limit, no need to chunk
        return raster_x_size, raster_y_size
    else:
        #calculate the chunk height that fits within the memory limit
        chunk_width = raster_x_size
        chunk_height = max(1, max_pixels // chunk_width)
    
        return chunk_width, chunk_height

def update_progress(result, progress_counter, total_rasters):
    """Callback function to update progress."""
    progress_counter.value += 1
    print(f"Processed {progress_counter.value}/{total_rasters} rasters")