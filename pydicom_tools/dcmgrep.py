#!/bin/env python

import os
import re
import argparse
import sys
from typing import (List, AnyStr, BinaryIO, Union, Optional)
from re import Pattern

import pydicom
from pydicom import (Dataset, DataElement)
from pydicom.fileutil import PathType
from pydicom.filebase import DicomFileLike

from utils.color import Colored, RED, VIOLET

def print_result(
    text: DataElement,
    pattern: str,
    *,
    color: Optional[bool],
    **kwargs
) -> None:
    if color:
        string = str(text)
        string_split = string.split(pattern)
        color_string = ''
        #TODO: hacer de manera más elegante el parseo de esto. Si pattern aparece al final del string, esta no sera añadida con color
        for i in range(len(string_split)-1):
            color_string += string_split[i] + Colored(pattern, RED)
        color_string += string_split[len(string_split)-1]
        
        print(color_string)
    else:
        print(text)


def recursive_match(
    pattern: Pattern,
    ds: Dataset,
    **kwargs
) -> List[DataElement]:
    number_match = kwargs.get("number_match")
    files_with_matches = kwargs.get("files_with_matches")
    element = kwargs.get("element")
    count_match = 0
    found = False
    result = []

    #TODO: make sure it tries to search throw all the data types
    for elem in ds:
        if elem.VR == 'SQ':
            [recursive_match(pattern, item, **kwargs) for item in elem.value]
        else:
            if pattern.match(str(elem.value)):
                found = True
                count_match -= -1
                result.append(elem)
                if count_match == number_match:
                    break
    return result

def grep(
    file: str,
    pattern: str,
    ignore_case: Optional[bool],
    *,
    file_number: Optional[int],
    **kwargs,
) -> None:

    if not pydicom.misc.is_dicom(file): 
        sys.stderr.write('dcmgrep: %s: Is not a DICOM file' % file)
        return
    __dicom_data = pydicom.dcmread(file, force=True)
    result = []

    # Check if pattern is a DataElement inside the Dataset
    #TODO: elem in ds devuelve un warning. Hacer la comprobación de manera más elegante para que no aparezca el warning
    if pattern in __dicom_data:
        result.append(__dicom_data[pattern])
    else:
        if ignore_case == True:
            __regex = re.compile(str(pattern), re.IGNORECASE)
        else:
            __regex = re.compile(str(pattern))
    
        result = recursive_match(__regex, __dicom_data, **kwargs)

    for r in result:
        if kwargs.get("files_with_matches"):
            if kwargs.get("color"):
                print(Colored(file, VIOLET))
            else:
                print(file)
        else:
            if kwargs.get("filename"):
                if file_number > 1:
                    if kwargs.get("color"):
                        print(Colored(file, VIOLET), end=": ")
                    else:
                        print(file, end=": ")
            print_result(r, pattern, **kwargs)
    

def dcmgrep(
    files_path: Union[PathType, BinaryIO, DicomFileLike],
    pattern: str,
    *,
    verbose: Optional[bool],
    recursive: Optional[bool],
    **kwargs
    ) -> None:
    """
    Search files for DICOM patterns
    """
    for file_path in files_path:
        if os.path.isfile(file_path):
            grep(file_path, pattern, file_number=len(files_path),**kwargs)
        
        else:
            if recursive:
                more_paths = [file_path + '/' + child for child in os.listdir(file_path)]
                dcmgrep(more_paths, pattern, **kwargs)
            else:
                if verbose:
                    sys.stdout.write('dcmgrep: %s: Is a directory\n' %file_path)

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("pattern", type=str, help="regular pattern for search or DataElement to print.")
    parser.add_argument("files", nargs="+", type=str, help="file(s) to grep")
    parser.add_argument("--ignore-case", "-i", action=argparse.BooleanOptionalAction, help="ignore case distinctions in patterns and input data, so that characters that differ only in case match each other")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, help="wheter to print out progress and debug messages")
    parser.add_argument("--files-with-matches", "-l", action=argparse.BooleanOptionalAction, help="supress normal output; instead print the name of each input file")
    parser.add_argument("--recursive", "-r", action=argparse.BooleanOptionalAction, help="follow directories")
    parser.add_argument("--color", "--colour", default=True, action=argparse.BooleanOptionalAction, help="output match strings colorized")
    parser.add_argument("--filename", default=True, action=argparse.BooleanOptionalAction, help="supress the prefixing of file names on output")
    args = parser.parse_args().__dict__

    files = args.pop("files")
    pattern = args.pop("pattern")
    
    dcmgrep(files, pattern, **args)
            
if __name__ == "__main__":
    main()