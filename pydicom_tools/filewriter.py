#! /bin/env python
import time
from typing import Dict

import SimpleITK as sitk
from SimpleITK import FileImageWriter

def writeSlice(
    series_tag_values: Dict, 
    new_img: str, 
    out_dir: str, 
    i: int,
    *,
    writer: FileImageWriter,
    **kwargs,
) -> None:

    if kwargs.get("writer") is None:
        writer = sitk.ImageFileWriter()
    else:
        writer = kwargs.pop("writer")
    
    image_slice = new_img[i, :, :]
    # Tags shared by the series.
    list(
        map(
            lambda tag_value: image_slice.SetMetaData(tag_value[0], tag_value[1]),
            series_tag_values,
        )
    )

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