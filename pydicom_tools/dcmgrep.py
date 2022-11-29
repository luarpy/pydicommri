#!/bin/env python

import os
import re
import argparse
import sys
from typing import (List, AnyStr, BinaryIO, Union)
from re import Pattern

import pydicom
from pydicom import Dataset
from pydicom.fileutil import PathType
from pydicom.filebase import DicomFileLike

from utils import recurse

def print_result():
    pass

def recursive_match(
    pattern: Pattern,
    ds: Dataset,
    **kwargs
) -> str:
    number_match = kwargs.get("number_match")
    count_match = 0
    for elem in ds:
        if elem.VR == 'SQ':
            [recursive_match(pattern, item, **kwargs) for item in elem.value]
        else:
            if pattern.match(str(elem.value)):
                print(elem.value)
                count_match -= -1
                if count_match == number_match:
                    break

def grep(
    file: str,
    pattern: str,
    **kwargs,
) -> None:

    if not pydicom.misc.is_dicom(file): 
        sys.stderr.write('dcmgrep: %s: Is not a DICOM file' % file)
        return
    __dicom_data = pydicom.dcmread(file, force=True)
    
    if kwargs.get("ignore_case") == True:
        __regex = re.compile(str(pattern), re.IGNORECASE)
    else:
        __regex = re.compile(str(pattern))
    
    recursive_match(__regex, __dicom_data, **kwargs)

def dcmgrep(
    files_path: Union[PathType, BinaryIO, DicomFileLike],
    pattern: str,
    **kwargs
    ) -> None:
    """
    Search files for DICOM patterns
    """
    for file_path in files_path:
        if os.path.isfile(file_path):
            grep(file_path, pattern, **kwargs)
        else:
            if recursive:
                more_paths = [paths + '/' + child for child in os.listdir(file_path)]
                dcmgrep(more_paths, pattern, **kwargs)
            else:
                sys.stdout.write('dcmgrep: %s: Is a directory\n' %path)

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("pattern", type=str, help="regular pattern for search")
    parser.add_argument("files", nargs="+", type=str, help="file(s) to grep")
    parser.add_argument("--ignore-case", "-i", action=argparse.BooleanOptionalAction, help="ignore case distinctions in patterns and input data, so that characters that differ only in case match each other")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, help="wheter to print out progress and debug messages")
    parser.add_argument("--files-with-matches", "-l", action=argparse.BooleanOptionalAction, help="supress normal output; instead print the name of each input file")
    parser.add_argument("--recursive", "-r", action=argparse.BooleanOptionalAction, help="follow directories")
    args = parser.parse_args().__dict__

    pattern = args.pop("pattern")
    files = args.pop("files")

    dcmgrep(files, pattern, **args)
            
if __name__ == "__main__":
    main()