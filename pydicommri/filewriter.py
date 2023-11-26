#! /bin/env python
import time
from typing import Dict, Union

import SimpleITK as sitk
from SimpleITK import ImageFileWriter
import numpy as np
from numpy import ndarray

import random
from utils import utils
import convert

def array2image(
    array_list: list, 
    filename: str,
    *,
    dtype: Union[int, float, complex, np.number] = None,
    extension: str = "mha",
    reference_data: str = None,
    verbose: bool = False,
) -> None:
    array = utils.list2ndarray(array_list, dtype=dtype)
    image_file = sitk.GetImageFromArray(array)
    if extension.lower() == "mha" or extension.lower().endswith(".mha"):
        convert.convert2mha(image_file, out=filename, reference_data=reference_data, verbose=verbose)
    else:
        sys.exit("array2image: could not use extension " + str(extension))
        
    if verbose:
        print("Output file:  " + filename)