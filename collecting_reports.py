#!/bin/env python

import os
import sys
import re
import argparse
import signal
import warnings
import csv

from pydicom.fileset import FileSet
from pydicom.data import get_testdata_file
import pydicom

warnings.filterwarnings("error")  
regex_report_name = re.compile('^vibe_q-dixon_tra_bh_higado_[0-9][0-9]_Report$', re.IGNORECASE)
modality = 'PR'
instance_number = 1
index = ['ID', 
    'Tanda', 
    'Repeticion', 
    'Area_ROI', 
    'Mean_Fit_Error_ROI', 
    'Vol_liver', 
    'Mean_Fit_Error_Vol', 
    'FF_ROI', 
    'std_FF_ROI', 
    'FF_Vol', 
    'std_FF_Vol', 
    'R2*_ROI', 
    'std_R2*_ROI', 
    'R2*_Vol_px', 
    'std_R2*_Vol', 
    'SeriesDate',
    'SeriesTime',
    'SeriesNumber',
    'Filename', 
    'SeriesDescription', 
    'InstanceNumber',
    'Modality', 
    'Comments']

warnings.filterwarnings("error")    

def combine_str(*strings):
    string = ''
    for s in strings:
        if s:
            string += s + ' '
    return string

def get_report(ds_overlay, output_dict):
    anno_seq = ds_overlay['GraphicAnnotationSequence']
    prev_str = ''
    section = 1
    output_dict = {}
    my_iter = iter(anno_seq)
    keyworderror_hit = False
    output_dict['Comments'] = combine_str(output_dict.get('Comments'), 'No comments.') 
    for anno_i in my_iter:
        try:
            aux_str = ''
            if not anno_i['TextObjectSequence'][0]['UnformattedTextValue']:
                continue
            aux_str = anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value
            if aux_str == 'ROI':
                if  section == 1:
                    anno_i = next(my_iter)
                    output_dict['Area_ROI']=int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                    anno_i = next(my_iter)
                    output_dict['Mean_Fit_Error_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                    anno_i = next(my_iter)
                    anno_i = next(my_iter)
                    output_dict['Vol_liver']=int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                    anno_i = next(my_iter)
                    output_dict['Mean_Fit_Error_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                    section = section+1
                if section == 2:
                    section = section+1
                if section == 3:
                    anno_i = next(my_iter)
                    output_dict['FF_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                    anno_i = next(my_iter)
                    output_dict['std_FF_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                    anno_i = next(my_iter)
                    anno_i = next(my_iter)
                    output_dict['FF_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                    anno_i = next(my_iter)
                    output_dict['std_FF_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                    section = section+1
                if section == 4:
                    section = section+1
                if section == 5:
                    anno_i = next(my_iter)
                    output_dict['R2*_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                    anno_i = next(my_iter)
                    output_dict['std_R2*_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                    anno_i = next(my_iter)
                    anno_i = next(my_iter)
                    output_dict['R2*_Vol_px']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                    anno_i = next(my_iter)
                    output_dict['std_R2*_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                    section = section+1
        except KeyError:
            keyworderror_hit = True
            pass
        # finally:
    # print(output_dict)
    if keyworderror_hit:
        output_dict['Comments'] = combine_str(output_dict.get('Comments'), 'Keyword error. Could not read values.')
    return output_dict


def reading_dcm_files(input_folder):
    print("\n\tReading from " + input_folder)
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    num_files = len(files)
    file_count = 0
    data = [] # A list of dictionaries
    output_dict = {key:'' for key in iter(index)} # Generate dictionary with keys from index but with empty values

    for f_i in files:
        file_count -= -1     
        EOF_hit = False
        output_dict = {key: "" for key in output_dict.keys()} # clear values but not the key names
        file_i = input_folder + f_i
        print(' ',end='\r', flush=True)
        print('\t%d of %d' % (file_count, num_files), end = '', flush = True)
        if not pydicom.misc.is_dicom(file_i):
            continue
        dicom_data = ''
        try: 
            dicom_data = pydicom.dcmread(file_i) 
        except : # Control for end of file before EOF delimitir runtime warning
            EOF_hit = True
            try:
                dicom_data = pydicom.dcmread(file_i, force=True)
            except:
                print("Could not read Dicom file {file_i}")
                continue
        finally:
            if (regex_report_name.match(dicom_data.SeriesDescription) and dicom_data.Modality == modality and dicom_data.InstanceNumber == instance_number): 
                print('\tReport found: ' + dicom_data.SeriesDescription, end = '', flush=True)
                output_dict['ID'] = input_folder
                output_dict['Filename'] = file_i
                output_dict['SeriesDescription'] = dicom_data.SeriesDescription 
                output_dict['Modality'] = dicom_data.Modality
                output_dict['InstanceNumber'] = dicom_data.InstanceNumber
                output_dict['SeriesDate'] = dicom_data.SeriesDate
                output_dict['SeriesTime'] = dicom_data.SeriesTime
                output_dict['SeriesNumber'] = dicom_data.SeriesNumber
                if EOF_hit:
                    output_dict['Comments'] = 'End of file reached before delimiter.'
                try:
                    output_dict.update(get_report(dicom_data, output_dict))
                except Exceptio as e:
                    output_dict['Comments'] = combine_str(output_dict['Comments'], 'An error occurred: ', str(e))
                finally:
                    dicom_data = None
                    print(output_dict)
                    data.append(output_dict) # Only append data if it finds reports of interets
    return data

def exit_handler(signum, frame):
    print('\nUser stopped job...')
    user_folder_scan.close()
    out_f.close()
    sys.exit(2)

def main():
    parser = argparse.ArgumentParser(description='Collect reports from DICOMM files')
    # parser.add_argument('search_directory', help='Set dir to search recursively for users reports')
    parser.add_argument('-o', dest='output_file', default=os.getcwd()+ os.sep + 'reports.csv', help="Set output dir for loaded data. If no file is set, it will create a 'reports.csv' file in the current directory")
    parser.add_argument('-f', dest='input_file',help='Set input file to search for reports')
    args = parser.parse_args()

    # if args.search_directory == '':
    #     parser.print_help()
    # else: 
    #     base_path = args.search_directory
    base_path = '../../Variabilidad'

    if not args.output_file == '':
        output_file = args.output_file

    # CTRL+Z and CTRL+C
    signal.signal(signal.SIGTSTP, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)
    
    study_dirs = ''
    if (os.path.isdir(base_path)):
        os.chdir(base_path)
        study_dirs = os.getcwd()
    else:
        sys.stderr.write(base_path + " is not a directory")
        exit(1)
    global user_folder_scan
    user_folder_scan = os.scandir(study_dirs)
    
    global out_f
    out_f = open(output_file, 'w+')
    writer = csv.writer(out_f)
    writer.writerow(index)

    for user_i in user_folder_scan: 
        print("Proccessing user: {user_i}")
        if not user_i.is_dir(): 
            continue
        print(' ', end='', flush=True)
        user_reports = reading_dcm_files(user_i.name + os.sep)
        for report_data in iter(user_reports):
            writer.writerow(list(report_data.values()))
        out_f.close()
        break
        
    user_folder_scan.close()
    out_f.close()
    
    print('\n', end='', flush=True)
   

if __name__ == "__main__":
    main()