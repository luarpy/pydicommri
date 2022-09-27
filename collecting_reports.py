#!/bin/env python

import os
import sys
import re # for regex expresions
import argparse
import signal
import traceback
import warnings

from pydicom.fileset import FileSet
from pydicom.data import get_testdata_file
import pydicom

report_regex_name = re.compile('vibe_q-dixon_tra_bh_higado_[0-9][0-9]_Report', re.IGNORECASE)
base_path = ''
modality = 'MR'
out_excel_path = ''
ff_index = ['User_ID','FF ROI','std ROI','FF Vol','std Vol','filename','Comments']
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
            pass # Otro tipo de anotaciones sin aparente interés
        else:
            aux_str = anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value
            if aux_str=='ROI' and k_section==1:
                anno_i = next(my_iter)
                output_dict['Area_ROI']=int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                anno_i = next(my_iter)
                output_dict['Mean_Fit_Error_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                anno_i = next(my_iter)
                output_dict['Vol_liver']=int(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value)
                anno_i = next(my_iter)
                output_dict['Mean_Fit_Error_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                k_section = k_section+1
            elif aux_str=='ROI' and k_section==2:
                k_section = k_section+1
            elif aux_str=='ROI' and k_section==3:
                anno_i = next(my_iter)
                output_dict['FF_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                output_dict['std_FF_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                anno_i = next(my_iter)
                output_dict['FF_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                anno_i = next(my_iter)
                output_dict['std_FF_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-1])
                k_section = k_section+1
            elif aux_str=='ROI' and k_section==4:
                k_section = k_section+1
            elif aux_str=='ROI' and k_section==5:
                anno_i = next(my_iter)
                output_dict['R2*_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                anno_i = next(my_iter)
                output_dict['std_R2*_ROI']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                anno_i = next(my_iter)
                anno_i = next(my_iter)
                output_dict['R2*_Vol_px']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                anno_i = next(my_iter)
                output_dict['std_R2*_Vol']=float(anno_i['TextObjectSequence'][0]['UnformattedTextValue'].value[0:-4])
                k_section = k_section+1
            #print(k_section,aux_str)
    return output_dict


def reading_dcm_files(input_folder):
    print("\n\tReading from " + input_folder)
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    num_files = len(files)
    k = 0
    report_found = False
    output_dict = {}
    output_dict['FF_ROI'] = \
        output_dict['std_FF_ROI'] = \
        output_dict['FF_Vol'] = \
        output_dict['std_FF_Vol'] = \
        output_dict['Filename'] = \
        output_dict['SeriesDescription'] = \
        output_dict['Comments'] = ''

    for f_i in files:
        k -= -1
        file_i = input_folder + f_i
        print(' ',end='\r', flush=True)
        print('\t%d of %d' % (k, num_files), end = '', flush = True)
        output_dict['Filename'] = file_i
        if not pydicom.misc.is_dicom(file_i):
            output_dict['Comments'] = 'Not a Dicom file'
            pass
        try: 
            dicom_data = pydicom.dcmread(file_i, force=True) #  If False (default), raises an InvalidDicomError if the file is missing the File Meta Information header. Set to True to force reading even if no File Meta Information header is found.
            
            if (report_regex_name.match(dicom_data.SeriesDescription)
                    and dicom_data.Modality == modality
                    and dicom_data.InstanceNumber == 1): 
                print('\tReport found: ' + dicom_data.SeriesDescription, end = '', flush=True)
                output_dict['SeriesDescription'] = dicom_data.SeriesDescription 
            try:
                output_dict = get_report(dicom_data, output_dict)
                output_dict['Comments'] = 'No comments' 
            except KeyError:
                output_dict['Comments'] = 'Keyword error. Could not read values'

        except RuntimeWarning:
            output_dict['Comments'] = 'End of file reached before delimiter'

        except IOError:
            output_dict['Comments'] =  'Could not read Dicom file'
        except Exception:
            # traceback.print_exc()
            output_dict['Comments'] = 'An error ocurred'
    return output_dict

def exit_handler(signum, frame):
    print('\nExiting...')
    exit(2)

def main():
    parser = argparse.ArgumentParser(description='Collect reports from DICOMM files')
    parser.add_argument('search_directory', help='Set dir to search recursively for users reports')
    parser.add_argument('-o', dest='output_directory', default=os.getcwd(), help='Set output dir for loaded data. If no dir is ser, it will use current working dir')
    parser.add_argument('-f', dest='input_file',help='Set input file to search for reports')
    args = parser.parse_args()

    if args.search_directory == '':
        parser.print_help()
    else: 
        base_path = args.search_directory

    if not args.output_directory == '':
        output_path = args.output_directory

    # CTRL+Z and CTRL+C
    signal.signal(signal.SIGTSTP, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    # writer = pd.ExcelWriter(out_excel_path+excel_file_name,engine = 'xlsxwriter')
    # df_ff = pd.DataFrame(index=ff_index) 
    
    if (os.path.isdir(base_path)):
        os.chdir(base_path)
    else:
        sys.stderr.write(base_path + " is not a directory")
        exit(1)
    cwd = os.getcwd()
    user_folder_scan = os.scandir(cwd)

    for user_i in user_folder_scan: 
        if not user_i.is_dir():
            continue
        
        print(' ',end='\r', flush=True)
        output_dict = reading_dcm_files(user_i.name + os.sep)
        # TODO: add other fields expanding the dictionary
        #         ff_i = [folder_i.name]
        #         # ff_index = ['User_ID','FF ROI','std ROI','FF Vol','std Vol','filename','Comments']
        #         ff_i.extend([output_dict['FF_ROI'],output_dict['std_FF_ROI'],
        #             output_dict['FF_Vol'],output_dict['std_FF_Vol'],
        #             output_dict['Filename'],output_dict['Comments']])

        #         print(ff_i)
        # ff_i = pd.DataFrame(ff_i,index=ff_index)
        # df_ff = pd.concat([df_ff,ff_i],axis=1)

    # df_ff = df_ff.transpose()
    # df_ff.to_excel(writer,index=False,sheet_name=sheet_name)
    # writer.save()

                

if __name__ == "__main__":
    main()