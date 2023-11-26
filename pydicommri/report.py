#!/bin/env python

import os
import sys
import re
import argparse
import signal
from typing import (
    BinaryIO,
    Optional, Union, List
)

from pydicom.dataset import FileDataset
from pydicom.fileutil import path_from_pathlike

import pydicom

from .utils import format_time, write_csv, write_xlsx

class ReportDataset(Dataset):
    """
    A dataset of report tags
    """
    def __init__(self, *args: Dataset, **kwargs: Any) -> None:
        super()
        # Create empty dictionary if there are no arguments, else append to Dataset._dict new key and values
        if not args:
            self._dict = {}
        elif isinstance(args[0], Dataset):
            self._dict = args[0]._dict
            __parse(self.args[0]) # Parse Dataset for report values
        else:
            raise TypeError("ReportDataset: Expected a Dataset but got " + type(args[0]).__name__)

    def __parse(self, data: Dataset) -> None: 
        anno_seq = data['GraphicAnnotationSequence']
        section = 1
        for anno_i in my_iter:
            aux_str = ''
            # Check if there are values available
            if not anno_i['TextObjectSequence'][0]['UnformattedTextValue']:         
                continue
            try:
                aux_str = anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value
                if aux_str == 'ROI':
                    if  section == 1:
                        anno_i = next(my_iter)
                        self._dict['AreaROI'] = int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                        anno_i = next(my_iter)
                        self._dict['MeanFitErrorROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                        anno_i = next(my_iter)
                        anno_i = next(my_iter)
                        self._dict['VolLiver'] = int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                        anno_i = next(my_iter)
                        self._dict['MeanFitErrorVol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                        section = section + 1
                    if section == 2:
                        section = section + 1
                    if section == 3:
                        anno_i = next(my_iter)
                        self._dict['FFROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                        anno_i = next(my_iter)
                        self._dict['StdFFROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                        anno_i = next(my_iter)
                        anno_i = next(my_iter)
                        self._dict['FFVol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                        anno_i = next(my_iter)
                        self._dict['StdFFVol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                        section = section + 1
                    if section == 4:
                        section = section + 1
                    if section == 5:
                        anno_i = next(my_iter)
                        self._dict['R2ROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                        anno_i = next(my_iter)
                        self._dict['StdR2ROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                        anno_i = next(my_iter)
                        anno_i = next(my_iter)
                        self._dict['R2Volpx'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                        anno_i = next(my_iter)
                        self._dict['StdR2Vol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                        section = section + 1
            except KeyError:
                pass
    
    def data_element(self, name: str) -> Optional[str]:
        """
        Return the element corresponding to t
    def _is_report(self) -> bool:
        return _is_a_reporthe element keyword 'name'

        Paramenters
        -----------
        name: str
            A report keyword

        Returns
        -------
            str if present,  ``None`` otherwise.
        """
        return self[name] if name is not None else None

def reportread(data: Union[FileDataset, PathType, BinaryIO],
    *,
    verbose = False) -> ReportDataset:
    """
    Read a report dataset stored in a DICOM file. 

    Parameters
    ----------

    data: FileDataset, PathType or str
        Either a FileDataset object, a path to the file or a string 
        containing the file name. 

    Returns
    -------
    ReportDataset
        An instance of :class:ReportDataset` that represents a parsed 
        DICOM file

    Raises
    ------
    TypeError
        If `data` is ``None`` or of an unsupported type

    """

    data = path_from_pathlike(data)
    if isinstance(data, str):
        data = open(data, 'rb')
    elif isinstance(data, PathType) or isinstance(data, BinaryIO):
        #TODO: generar un metodo que gestione la repeticion si se falla en la primera vez y se repite con el force
        try:
            data = pydicom.dcmread(data)
        except:
            try:
                data = pydicom.dcmread(data, force=True)
            except:
                return
    elif data is None:
        raise TypeError("reportread: Expected a FileDataset, BinaryIO or str, but got " + type(data).__name__)

    return ReportDataset(data)

def collect(
    file: str,
    mylist: List,
    *,
    verbose: Optional[bool] = None,
    expression: str,
    time_format: str = '%H%M%S.%f',
    **decode_options,
) -> dict:
    """
    Collect data from report file 

    file: str
        The path to the file to open
    
    verbose: bool
        Whether to display the data being parsed to the console. If True, displays all the details.
        If False, displays minimal details. If None, does not display anything.
    
    expression: str
        Regular expression to use when searching for files by SeriesName. Regular expression are
        operations similar to those found in Perl.

    time_format: str
        Time format to use when formating series time format. Originally in the files appears as '%H%M%S.%f'
        so this conversions helps understanding easier the time of acquisition. if None, does not convert the 
        time format

    decode_options: dict
        Keyword arguments to construct 'DecodingOptions' instances

    Returns
    -------
    A dictionary containing the resulting data ("data") from parsing the file, series date, time,
    number, description, modality and instance number, filename
    """

    if verbose:
        print("Reading from file {file}\n")    
        
    if not pydicom.misc.is_dicom(file):
        return

    _dicom_data = ''
    _dict = {str(ele) : "" for ele in _dict_index}

    if not expression:
        print("There must be used an expression\n")
        return
    _regex_report_name = re.compile(expression, re.IGNORECASE)
    
    try: 
        _dicom_data = pydicom.dcmread(file) 
    except: # Control for end of file before EOF delimitir runtime warning
        _eof_hit = True
        try:
            _dicom_data = pydicom.dcmread(file, force=True)
            _file_forced = True
        except:
            print("Could not read file {file}\n")
            return
    finally:
        if _regex_report_name.match(_dicom_data.SeriesDescription):
            if _dicom_data.Modality != modality: 
                return
            if _dicom_data.InstanceNumber != instance_number: 
                return
            # Appends attributes 
            _report_data = reportread(_dicom_data, verbose)
            if verbose:
                print('\tReport found: ' + _dicom_data.SeriesDescription)

            for ele in mylist:
                # Report data from DICOM
                _dict[ele] = _report_data.data_element(ele) if ele in _report_data else None
                if verbose:
                    print("{ele}: {_dict[ele]}")
            
            if time_format is not None:
                _dict["SeriesTime"] = format_time(_dict["SeriesTime"])
 
            return _dict
        else:
            return



def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file", nargs="+", type=str, help="file(s) to parse")
    parser.add_argument("--time_format", "-t", type=str, default='%H:%M:%S', help="change time format output. By default '%H:%M:%S'")
    parser.add_argument("--expression", "-e", type=str, help="regular expression for search file's names")
    parser.add_argument("--output-dir", "-o", type=str, default=".", help="directory to save the outputs")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, default=True, help="whether to print out the progress and debug messages")
    parser.add_argument("--combine", "-c", action=argparse.BooleanOptionalAction, default=True, help="Do not combine every parsed file in one big file")

    args = parser.parse_args().__dict__

    example_list = ['PatientID',  
    'PatientName',
    'PatientSex',
    'area_roi', 
    'mean_fit_error_roi', 
    'vol_liver', 
    'mean_fit_error_vol', 
    'ff_roi', 
    'std_ff_roi', 
    'ff_vol', 
    'std_ff_vol', 
    'r2*_roi', 
    'std_r2*_roi', 
    'r2*_vol_px', 
    'std_r2*_vol', 
    'SeriesDate',
    'SeriesTime',
    'SeriesNumber', 
    'Filename', 
    'ProtocolName', 
    'InstanceNumber',
    'Modality', 
    'comments']

    output_dir = args.pop("output_dir")
    os.makedirs(output_dir, exist_ok=True)

    for file_path in args.pop("file"):
        result = collect(file_path, example_list, modality="PR", instance_number=1, **args)
        file_basename = os.path.basename(file_path)
        
        if verbose:
            print(result)

        # save JSON
        with open(os.path.join(output_dir, file_basename + ".json"), "w", encoding="utf-8") as json:
            write_json(result['data'], file=json)
        
    
    # TODO: collect every report in one big report
    if combine:
        pass
        
    

    # out_f = open(output_file, 'w+')
    # writer = csv.writer(out_f)
    # writer.writerow(index)

    # for user_i in user_folder_scan: 
    #     print("\nProccessing user: ", user_i.name)
    #     if not user_i.is_dir(): 
    #         continue
    #     user_reports = reading_dcm_files(user_i.name + os.sep)
    #     for report_data in iter(user_reports):
    #         writer.writerow(list(report_data.values()))        
        
    #     print(' ', end='', flush=True)
        
    # user_folder_scan.close()
    # out_f.close()
       

if __name__ == "__main__":
    main()