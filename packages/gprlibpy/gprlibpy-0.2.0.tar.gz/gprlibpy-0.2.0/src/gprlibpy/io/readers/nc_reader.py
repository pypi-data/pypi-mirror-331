import logging
import typing
from pathlib import Path
import xarray as xr
from lgopy.core import DataReaderFactory, DataReader

logger = logging.getLogger("rich")


@DataReaderFactory.register(".nc")
class NcReader(DataReader):
    """
    Cdf data reader
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, file_path: typing.Union[str, Path]) -> xr.DataArray:
        return xr.open_dataarray(file_path)
