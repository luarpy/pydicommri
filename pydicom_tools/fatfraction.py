#!/bin/env python

import argparse
import os
import signal
import time
from pathlib import Path
from typing import (Optional, Union)

import pydicom
from pydicom.dataset import Dataset
import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk

def writeSlices(
    writer,
    series_tag_values: dict, 
    new_img, 
    out_dir: Union[str, Path], 
    i
) -> None:
    image_slice = new_img[:, :, i]

    # Tags shared by the series.
    list(map(lambda tag_value: image_slice.SetMetaData(
                tag_value[0], tag_value[1]
            ),series_tag_values
    ))

    # Slice specific tags.
    #   Instance Creation Date
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))
    #   Instance Creation Time
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))

    # Setting the type to CT so that the slice location is preserved and
    # the thickness is carried over.
    image_slice.SetMetaData("0008|0060", "CT")

    # (0020, 0032) image position patient determines the 3D spacing between
    # slices.
    #   Image Position (Patient)
    image_slice.SetMetaData(
        "0020|0032",
        "\\".join(map(str, new_img.TransformIndexToPhysicalPoint((0, 0, i)))),
    )
    #   Instance Number
    image_slice.SetMetaData("0020,0013", str(i))

    # Write to the output directory and add the extension dcm, to force
    # writing in DICOM format.
    writer.SetFileName(os.path.join(out_dir, str(i) + ".dcm"))
    writer.Execute(image_slice)

def fatfraction(
    water_file: str,
    fat_file: str,
    *,
    verbose: Optional[bool],
    **decode_options,
) -> Dataset:
    """
    Generates a fat fraction image from water and fat images

    Parameters
    ----------

    water_file: str
        The path to the water image file
    
    fat_file: str
        The path to the fat image file

    
    Returns
    -------
    #TODO: que devuelve???? que formato???
    """
    if verbose:
        print("Combining water and fat: \n\t{water_file} + {fat_file}")
    
    water_img = pydicom.dcmread(water_file, force=True).pixel_array
    fat_img = pydicom.dcmread(fat_file, force=True).pixel_array
    
    if water_img.shape != fat_img.shape:
        print("fatfraction: both files must have the same shape, got " + water_img.shape + " for water and " + fat_img.shape + " for fat")

    ff_img = np.zeros(water_img.shape, dtype=water_img.dtype)
    
    if len(water_img.shape) == 3:
        for i in range(water_img.shape[0]):
            tmp = water_img[i,:,:] + fat_img[i,:,:]      
            np.divide(fat_img[i,:,:], tmp, out=ff_img[i, :, :], where=tmp!=0, casting='unsafe')
    else:
        tmp = water_img + fat_img
        np.divide(fat_img, tmp, out=ff_img, where=tmp!=0, casting='unsafe')
    return ff_img    

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--fat", "-f", type=str, help="fat DICOM file")
    parser.add_argument("--water", "-w", type=str, help="water DICOM file")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, help="whether to print out the progress and debug messages")
    parser.add_argument("--output-file", "-o", default="./ff.dcm", type=str, help="file to save the output")
   
    args = parser.parse_args().__dict__

    water = args.pop("water")
    fat = args.pop("fat")
    output_file = args.pop("output_file")

    output_dir = Path(output_file).parent.absolute()
    os.makedirs(output_dir, exist_ok=True)

    result = fatfraction(water, fat, **args)

    ff_img = sitk.GetImageFromArray(result)   
    writer = sitk.ImageFileWriter()
    writer.SetFileName("ff.dcm")
    writer.Execute(ff_img)

if __name__ == "__main__":
    main()