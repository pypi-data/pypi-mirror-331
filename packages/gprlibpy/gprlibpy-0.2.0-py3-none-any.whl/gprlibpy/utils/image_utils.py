import base64
import logging
import typing
from enum import Enum, auto
import io
import xarray as xr
import dask.array as da

import cv2
import graphviz
import numpy as np
from PIL import Image
from dask import optimize
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)

class ImageOutputFormat(Enum):
    """
    This class provides a set of image output formats
    """

    PIL = auto()
    BASE64 = auto()
    NUMPY = auto()

class StretchingFunction(Enum):
    """
    This enum provides a set of stretching functions
    """
    STDEV_CLIPPED = auto()



def timeit(func):
    """
    Decorator to measure the execution time of a function.
    """

    def wrapper(*args, **kwargs):
        import time

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Execution time: {end_time - start_time:.2f} seconds")
        return result

    return wrapper

def calculate_optimal_chunks(data_shape, dtype=np.float64, desired_chunk_mem=100e6):
    """
    Calculate optimal chunk sizes for a Dask array.

    Parameters:
    - data_shape (tuple): Shape of the array (e.g., (10000, 10000)).
    - dtype (data-type): NumPy data type (e.g., np.float64). Default is np.float64.
    - desired_chunk_mem (float): Desired chunk size in bytes. Default is 100MB.

    Returns:
    - tuple: Optimal chunk sizes for each dimension.
    """
    # Calculate the size of one element in bytes
    element_size = np.dtype(dtype).itemsize
    # Total number of elements in the array
    total_elements = np.prod(data_shape)
    # Total size of the array in bytes
    total_size = total_elements * element_size
    # Number of chunks desired
    num_chunks = total_size / desired_chunk_mem
    # Calculate the chunk size for each dimension
    chunk_size = int(np.ceil(np.power(total_elements / num_chunks, 1 / len(data_shape))))
    # Create the chunk shape
    chunk_shape = tuple(min(dim, chunk_size) for dim in data_shape)
    return chunk_shape

def stdev_clipped_normalization(array: da.Array, num_stdev: float):
    """
    Stretch an array based on the number of standard deviations using dask.array
    """
    # scale values first to 0-1 to reduce memory usage
    array = array.astype(da.float32)
    array = da.nan_to_num(array)
    data_stdev = da.std(array)
    data_mean = da.mean(array)
    data_max_new = data_mean + num_stdev * data_stdev
    data_min_new = data_mean - num_stdev * data_stdev
    array = da.clip(array, data_min_new, data_max_new)
    data_max = da.max(array)
    data_min = da.min(array)
    data_range = data_max - data_min

    array = (array - data_min) / data_range
    return array

@timeit
def to_image(xarr: xr.DataArray,
              cmap: str = 'gray',
              stretch_func: StretchingFunction = None,
              stretch_func_args: dict = None,
              output_format: ImageOutputFormat = ImageOutputFormat.BASE64,
              quality: float=85,
              scale_factor: float=1.0,
              desired_chunk_mem: float = 100e6) -> typing.Union[str, Image.Image, np.ndarray]:
    """
    Converts a large 3D GPR array (samples, traces, channels) into a Base64-encoded image using Dask.

    Parameters:
    - xarr (xr.DataArray): 3D GPR array (samples, traces, channels
    - cmap (str): Matplotlib colormap name. Default is 'gray'.
    - stretch_func (StretchingFunction): Stretching function. Default is None.
    - stretch_func_args (dict): Stretching function arguments. Default is None.
    - output_format (ImageOutputFormat): Output format. Default is ImageOutputFormat.BASE64.
    - quality (int): Image quality (0-100). Default is 85.
    - desired_chunk_mem (float): Desired chunk size in bytes. Default is 100MB.
    Returns:
        str: Base64-encoded PNG image.
    """
    xarr = xarr.data  # Extract Dask array from xarray
    if not isinstance(xarr, da.Array):
        xarr = da.from_array(xarr, chunks="auto")

    stretch_funcs = {
        StretchingFunction.STDEV_CLIPPED: stdev_clipped_normalization
    }
    # normalize values between 0 and 1
    data_shape = xarr.shape
    dtype = xarr.dtype
    optimal_chunks = calculate_optimal_chunks(data_shape, dtype, desired_chunk_mem)
    xarr = xarr.rechunk(optimal_chunks)
    stretch_func = stretch_funcs.get(stretch_func, None)
    if stretch_func is not None:
        xarr = stretch_func(xarr, **stretch_func_args)

    # Step 3: Apply colormap in parallel
    def apply_colormap(chunk_arr):
        """
        Apply colormap to a chunk array
        :param chunk_arr:
        :return:
        """
        cmap_func = plt.get_cmap(cmap)
        chunk_arr = cmap_func(chunk_arr)
        chunk_arr = np.uint8(chunk_arr * 255)
        return chunk_arr

    dask_colored = xarr.map_blocks(apply_colormap, dtype=np.uint8, new_axis=2)
    # Compute the final image
    dask_colored = optimize(dask_colored)[0]
    final_image = dask_colored.compute()
    # Convert to PIL Image
    pil_img = Image.fromarray(final_image)
    # down sdcale image size to 50%
    pil_img = pil_img.resize((int(pil_img.width * scale_factor), int(pil_img.height * scale_factor)))
    # Encode as Base64
    if output_format == ImageOutputFormat.NUMPY:
        return np.asarray(pil_img)
    elif output_format == ImageOutputFormat.BASE64:
        with io.BytesIO() as buffered:
            pil_img.save(buffered, format="PNG", quality=quality)
            base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return base64_str
    return pil_img


def array2rgb(data_arr: np.ndarray):
    """
    Convert a numpy array to a RGB image
    :param data_arr:
    :return:
    """
    data_arr = data_arr.astype("float")
    data_arr = cv2.normalize(data_arr, None, 0.0, 255.0, cv2.NORM_MINMAX)
    data_arr = data_arr.astype(np.uint8)
    data_arr = cv2.cvtColor(data_arr, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(data_arr, "RGB")

def scale(x, out_range=(-1, 1), axis=None):
    """
    Scale the data to a given range
    :param x: input data
    :param out_range: scale to this range
    :param axis: scale along this axis
    :return: scaled data
    """
    in_range = np.min(x, axis), np.max(x, axis)
    y = (x - (in_range[1] + in_range[0]) / 2) / (in_range[1] - in_range[0])
    return y * (out_range[1] - out_range[0]) + (out_range[1] + out_range[0]) / 2

def normalize(data_arr):
    """ "
    Normalize the data array
    :param data_arr: input data array
    :return: normalized data array
    """
    if data_arr.dtype == np.uint8:
        data_arr = data_arr.astype(np.float32) / 255.0
    else:
        data_arr = data_arr.astype(np.float32)
        data_arr = cv2.normalize(data_arr, None, 0.0, 1.0, cv2.NORM_MINMAX)
    return data_arr


def dgraph2image(d: graphviz.Digraph):
    """
    Convert a graphviz digraph to an image
    :param d:
    :return:
    """
    graph_stream = bytearray(d.pipe())
    graph_numpy = np.asarray(graph_stream, dtype=np.uint8)
    graph_image = cv2.imdecode(graph_numpy, cv2.IMREAD_COLOR)
    return graph_image


def stdev_clipped_normalization(array, num_stdev):
    """
    Stretch an array based on the number of standard deviations
    """
    array = array.astype(np.float32)
    data_stdev = np.std(array)
    data_mean = np.mean(array)
    data_max_new = data_mean + num_stdev * data_stdev
    data_min_new = data_mean - num_stdev * data_stdev
    array[array > data_max_new] = data_max_new
    array[array < data_min_new] = data_min_new
    data_max = np.max(array)
    data_min = np.min(array)
    data_range = data_max - data_min
    array = (array - data_min) / data_range
    return array

def fft2(data_arr):
    """
    This function is used to calculate the 2D FFT of an image
    :param data_arr: 2D array
    """
    data_fk_arr = np.fft.fft2(data_arr)
    data_fk_arr = np.fft.fftshift(data_fk_arr)
    data_fk_arr = abs(data_fk_arr)
    return data_fk_arr.astype(np.float32)


def ifft2(data_arr):
    """
    This function is used to calculate the 2D IFFT of an image
    :param data_arr: 2D array
    """
    data_fk_arr = np.fft.ifftshift(data_arr)
    data_fk_arr = np.fft.ifft2(data_fk_arr)
    data_fk_arr = abs(data_fk_arr)
    return data_fk_arr.astype(np.float32)
