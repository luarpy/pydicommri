#!/bin/env python

import argparse
import os
import sys
import signal
import time
from pathlib import Path
from typing import (Optional, Union, List)

import pydicom
from pydicom.dataset import Dataset
import numpy as np
import matplotlib.pyplot as plt

from utils.random import random_str
from filewriter import array2image
from provider import Siemens
from utils.utils import parent_dir

def __get_float_ndarray(data: Union[str, Dataset, np.ndarray]) -> None:
    if isinstance(data, str):
        if pydicom.misc.is_dicom(data):
            r = pydicom.dcmread(data, force=True).pixel_array
            return r.astype(float)
        else:
            raise TypeError("fatfraction.py: file is not a DICOM file")
            sys.exit(1)
    elif isinstance(data, np.ndarray): 
        return data.astype(float)
    elif isinstance(data, Dataset):
        r = data.pixel_array
        return r.astype(float)
    else:
        raise TypeError("fatfraction.py: Expected a Dataset, str or ndarray, but got " + type(data).__name__)
        sys.exit(1)
    
def __compute_ff(
    water_array: np.ndarray,
    fat_array: np.ndarray,
    *,
    real_ff: bool = False,
    **kwargs
) -> np.ndarray:
    # water_array = np.float(water_array)
    # fat_array = np.float(fat_array)
    # we want to have the best resolution, so we create a float array
    ff_array = np.zeros_like(water_array, float)
    tmp = water_array + fat_array
    ff_array = np.divide(fat_array, tmp, where=tmp != 0, casting='unsafe')
    if real_ff:
        ff_array = ff_array/(0.45*ff_array + 0.55)
    return ff_array

def __get_instancenumber(data):
    number = pydicom.dcmread(data, force=True).InstanceNumber
    return int(number)

def fatfraction(
    water_files: Union[str, Dataset, np.ndarray],
    fat_files: Union[str, Dataset, np.ndarray],
    *,
    provider: str = None,
    verbose: Optional[bool] = False,
    **kwargs,
) -> np.ndarray:
    """
    Calculates fat fraction from water and fat images.

    Parameters
    ----------
    water_files : Union[str, Dataset, np.ndarray]
        A string, xarray Dataset, or numpy array containing images of water.
    
    fat_files : Union[str, Dataset, np.ndarray]
        A string, xarray Dataset, or numpy array containing images of fat.

    provider : str, optional
        Name of the vendor or software used to generate the input files. Some vendors use numerical values or specific ranges to represent their results. Default is None.

    verbose : bool, optional
        Whether to print progress messages. Default is False.

    **kwargs : dict, optional
        Additional arguments to be passed to the underlying function.

    Returns
    -------
    np.ndarray
        An array containing the calculated fat fraction.

    Raises
    ------
    TypeError
        If water_files or fat_files is not a string, xarray Dataset, or numpy array.
    """

    result = []

    if len(water_files) != len(fat_files):
        sys.exit(__file__ +  ": lenght error: fat files and water files must be the same amount, but got: water files " + str(len(water_files)) + ", fat files " + str(len(fat_files)) + "\n")
   
    # sort list items by instance number
    water_files = sorted(water_files, key=__get_instancenumber)
    fat_files = sorted(fat_files, key=__get_instancenumber)

    for i in range(len(water_files)):
        water_file = water_files[i]
        fat_file = fat_files[i]

        # If the input is not a valid type, continue with the next iteration in the loop
        try:
            water_img = __get_float_ndarray(water_file)
            fat_img = __get_float_ndarray(fat_file)
        except TypeError: 
            if verbose:
                print(water_file + " or " + fat_file + " is not valid. Continuing with the next ones")
            continue

        if verbose:
            print("Combining: \n\t" + "water:\t" + water_file + "\n\tfat:\t" + fat_file)
        
        if water_img.shape != fat_img.shape:
            sys.exit("fatfraction: both files must have the same shape, got " + water_img.shape + " for water and " + fat_img.shape + " for fat")

        ff_img = np.zeros(water_img.shape, dtype=float)
        if len(water_img.shape) == 3:
            # TODO: buscar una manera de que detecte la dimension que recoge a las imagenes
            for i in range(water_img.shape[0]):
                ff_img[i, :, :] = __compute_ff(water_img[i,:,:], fat_img[i,:,:], **kwargs)
        elif len(water_img.shape) == 2:
            ff_img[:, :] = __compute_ff(water_img, fat_img, **kwargs)
        else:
            sys.exit("fatfraction: files must have from 2 or 3 dimensions, but got " + len(water_img.shape))
        

        if str(provider).lower() == "siemens":
            ff_img = Siemens.scatter_array(ff_img)
        elif provider is None:
            pass
        else:
            sys.stderr.write("fatfraction: could not know provider " + str(provider) + "\n")

        result.append(ff_img)

    return result

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--fat", "-f", nargs="+", type=str, help="fat DICOM file(s)")
    parser.add_argument("--water", "-w", nargs="+", type=str, help="water DICOM file(s)")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, help="whether to print out the progress and debug messages")
    parser.add_argument("--output-file", "-o", default='ff.mha', type=str, help="filename for output file(s)")
    parser.add_argument("--real-ff", default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument("--provider", default=None, help="vendor for which you are preparing the file. Some suppliers use numerical or specific range values to represent their results. Available: Siemens")
    args = parser.parse_args().__dict__

    water_files = args.pop("water")
    fat_files = args.pop("fat")
    output_file = args.pop("output_file")
    verbose = args.pop("verbose")
    provider = args.pop("provider")

    output_dir = parent_dir(output_file)

    os.makedirs(output_dir, exist_ok=True)
    
    result = []

    result = fatfraction(water_files, fat_files, verbose=verbose, provider=provider,**args)
    #TODO: no puede funcionar lo de copy information porque le hace falta copiar de archivos que sean DICOM. no todos lo son
    array2image(result, output_file, dtype=float, reference_data=water_files[-1], verbose=verbose, extension="mha")

if __name__ == "__main__":
    main()