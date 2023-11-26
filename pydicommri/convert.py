from typing import Union, BinaryIO
from pathlib import Path

from pydicom import Dataset
import SimpleITK as sitk

def convert2mha(
    image_file, 
    *,
    out: Union[str,BinaryIO, Path] = None,
    reference_data = None,
    verbose: bool = False,
    **kwargs
)-> sitk.ImageFileWriter:  
    """
    Converts a SimpleItk image to a file and writes it in the filesystem

    Parameters
    ----------
    image_file: 
        SimpleITK's image
    
    filename: str
        Output file name and path
    
    reference_data: 
        Reference file to take tags in conversion from Image to file. If None it does not take reference data
    
    verbose: bool
        Debug and log option      

    Return
    ------
        None
    """
    if out is not None and not str(out).lower().endswith(".mha"):
        out = out + ".mha"

    #TODO: no funciona el tomar valores de la referencia
    if reference_data is not None:
        try:
            image_file.CopyInformation(reference_data)
        except TypeError:
            pass

    writer = sitk.ImageFileWriter()
    writer.SetFileName(out)

    if out is not None:
        writer.Execute(image_file)
    else:
        return writer

def convert(
    input_file: Union[str, Dataset, BinaryIO, Path],
    __type: str = "mha",
    output_file: str = None,
    *,
    verbose: bool = False,
    **kwargs
):
    #TODO: get data from input_file
    if __type.lower() == "mha":
        __image_file = sitk.GetImageFromArray(__array)
        convert2mha(reference_data=input_file,**kwargs)

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file", type=str, help="file to convert")
    parser.add_argument("--type", type=str, default=None, help="convert to file type")
    parser.add_argument("--output", "-o", type=str, default=None, help="output file")

    args = parser.parse_args().__dict__
    file = args.pop("file")
    __type = args.pop("type")
    output = args.pop("output")

    convert(file, __type, output, **args)

if __name__ == "__main__":
    main()