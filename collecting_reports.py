#!/bin/env python

import os
import sys
import re # for regex expresions
import argparse
import signal
import warnings

from pydicom.fileset import FileSet
from pydicom.data import get_testdata_file
import pydicom

report_regex_name = re.compile('^vibe_q-dixon_tra_bh_higado_[0-9][0-9]_Report$', re.IGNORECASE)
base_path = ''
modality = 'MR'
instance_number = 1
warnings.filterwarnings("error")    

def get_report(ds_overlay, output_dict):
    anno_seq = ds_overlay['GraphicAnnotationSequence']
    prev_str = ''
    k_section = 1
    output_dict = {}
    my_iter = iter(anno_seq)
    for anno_i in my_iter:
        try:
            anno_i['TextObjectSequence'][0]['UnformattedTextValue']
        except:
            output_dict['Comments'] = str(output_dict.get('Comments')) + 'Not interesting values. '
            return output_dict
        else:
            aux_str = anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value
            if aux_str == 'ROI' and k_section == 1:
                anno_i = next(my_iter)
                output_dict['Area_ROI'] = int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                anno_i = next(my_iter)
                output_dict['Mean_Fit_Error_ROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                anno_i = next(my_iter)
                output_dict['Vol_liver'] = int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                anno_i = next(my_iter)
                output_dict['Mean_Fit_Error_Vol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                k_section -= -1
            elif aux_str == 'ROI' and k_section == 2:
                k_section -= -1
            elif aux_str == 'ROI' and k_section == 3:
                anno_i = next(my_iter)
                output_dict['FF_ROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                output_dict['std_FF_ROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                anno_i = next(my_iter)
                output_dict['FF_Vol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                output_dict['std_FF_Vol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                k_section -= -1
            elif aux_str == 'ROI' and k_section == 4:
                k_section -= -1
            elif aux_str == 'ROI' and k_section == 5:
                anno_i = next(my_iter)
                output_dict['R2*_ROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                anno_i = next(my_iter)
                output_dict['std_R2*_ROI'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                anno_i = next(my_iter)
                anno_i = next(my_iter)
                output_dict['R2*_Vol_px'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                anno_i = next(my_iter)
                output_dict['std_R2*_Vol'] = float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                k_section -= -1

    output_dict['Comments'] = output_dict.get('Comments') + 'No comments. ' 
    return output_dict


def reading_dcm_files(input_folder):
    print("\n\tReading from " + input_folder)
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    num_files = len(files)
    file_count = 0
    data = [] # A list of dictionaries
    output_dict = {} # A dictionary of data names and corresponding values
    output_dict['ID'] = \
        output_dict['Tanda'] = \
        output_dict['Repeticion'] = \
        output_dict['Area_ROI'] = \
        output_dict['Mean_Fit_Error_ROI'] = \
        output_dict['Vol_liver'] = \
        output_dict['Mean_Fit_Error_Vol'] = \
        output_dict['FF_ROI'] = \
        output_dict['std_FF_ROI'] = \
        output_dict['FF_Vol'] = \
        output_dict['std_FF_Vol'] = \
        output_dict['R2*_ROI'] = \
        output_dict['std_R2*_ROI'] = \
        output_dict['R2*_Vol_px'] = \
        output_dict['std_R2*_Vol'] = \
        output_dict['Filename'] = \
        output_dict['SeriesDescription'] = \
        output_dict['Modality'] = \
        output_dict['Comments'] = ''

    for f_i in files:
        file_count -= -1     
        EOF_hit = False
        output_dict = {key: "" for key in output_dict.keys()} # clear values but not the key names
        file_i = input_folder + f_i
        print(' ',end='\r', flush=True)
        print('\t%d of %d' % (file_count, num_files), end = '', flush = True)
        if not pydicom.misc.is_dicom(file_i):
            continue
        try: 
            dicom_data = pydicom.dcmread(file_i) 
        except RuntimeWarning: # Control for end of file before EOF delimitir runtime warning
            EOF_hit = True
            dicom_data = pydicom.dcmread(file_i, force=True)
        finally:
            if (report_regex_name.match(dicom_data.SeriesDescription) and dicom_data.InstanceNumber == instance_number): 
                print('\tReport found: ' + dicom_data.SeriesDescription, end = '', flush=True)
                output_dict['ID'] = input_folder
                output_dict['Filename'] = file_i
                output_dict['SeriesDescription'] = dicom_data.SeriesDescription 
                output_dict['Modality'] = dicom_data.Modality
                if EOF_hit:
                    output_dict['Comments'] = 'End of file reached before delimiter. '
                try:
                    output_dict.update(get_report(dicom_data, output_dict))
                except KeyError:
                    output_dict['Comments'] = str(output_dict.get('Comments')) + 'Keyword error. Could not read values. '

                data.append(output_dict) # Only append data if it finds reports of interets
    return data

def exit_handler(signum, frame):
    print('\nUser stopped job...')
    user_folder_scan.close()
    exit(2)

def main():
    parser = argparse.ArgumentParser(description='Collect reports from DICOMM files')
    parser.add_argument('search_directory', help='Set dir to search recursively for users reports')
    parser.add_argument('-o', dest='output_file', default=os.getcwd(), help="Set output dir for loaded data. If no file is set, it will create a 'reports.csv' file in the current directory")
    parser.add_argument('-f', dest='input_file',help='Set input file to search for reports')
    args = parser.parse_args()

    if args.search_directory == '':
        parser.print_help()
    else: 
        base_path = args.search_directory

    if not args.output_file == '':
        output_file = args.output_file
    else:
        output_file = os.getcwd() + os.sep + 'reports.csv'

    # CTRL+Z and CTRL+C
    signal.signal(signal.SIGTSTP, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    # writer = pd.ExcelWriter(out_excel_path+excel_file_name,engine = 'xlsxwriter')
    # df_ff = pd.DataFrame(index=ff_index) 
    
    study_dirs = ''
    if (os.path.isdir(base_path)):
        os.chdir(base_path)
        study_dirs = os.getcwd()
    else:
        sys.stderr.write(base_path + " is not a directory")
        exit(1)
    global user_folder_scan
    user_folder_scan = os.scandir(study_dirs)

    all_repotrs = [] # A list of lists
    for user_i in user_folder_scan: 
        if not user_i.is_dir(): 
            continue
        all_repotrs.append(reading_dcm_files(user_i.name + os.sep))
        break
    # print(all_repotrs)
    print('',end='',flush=True )
    print('Saving data to {output_file}')
    import numpy as np
    np.savetxt(output_file, all_repotrs, delimiter=', ', fmt='% s')
    user_folder_scan.close()

if __name__ == "__main__":
    main()