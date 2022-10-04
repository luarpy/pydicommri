from ast import AsyncFunctionDef
from email.mime import base
from pydicom.fileset import FileSet
from pydicom.data import get_testdata_file
import os
import pandas as pd
# import SimpleITK as sitk
import pydicom

import re


base_path = '../../Variabilidad/'
# Path to excel output file
out_excel_path = './'
excel_file_name = 'FF_Siemens_Liver_Extreme_variability.xlsx'
sheet_name = 'FF Siemens Liver Extreme_pre'
ff_index = ['User_ID','FF ROI','std ROI','FF Vol','std Vol','filename','Comments']

report_regex_name = re.compile('^vibe_q-dixon_tra_bh_higado_[0-9][0-9]_Report$', re.IGNORECASE)

#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################

def reading_report(ds_overlay,output_dict):
          
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
            #print(aux_str)
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
    print(output_dict)
    return output_dict


def reading_dcm_files(input_folder):
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    num_files = len(files)
    report_foundQ = False
    k=0
    output_dict = {}
    output_dict['FF_ROI']=output_dict['std_FF_ROI']= \
            output_dict['FF_Vol']=output_dict['std_FF_Vol']= \
            output_dict['Filename']=output_dict['Comments']=''
    for f_i in files:
        k=k+1
        file_i = input_folder+f_i
        print(' ',end='\r', flush=True)
        print('     %d of %d' %(k,num_files),end='',flush=True)
        try: 
            ds = pydicom.dcmread(file_i) 
             
            # if ds.SeriesDescription=='t1_vibe_e-dixon_tra_bh_pre_higado_seg_Report' and \
            #if ds.SeriesDescription=='vibe_q-dixon_tra_bh_higado_Report' and \
            if report_regex_name.match(ds.SeriesDescription) and \
                ds.Modality=='PR' and \
                ds.InstanceNumber==1: 
                print('         Report found: '+ f_i)
                # if report_foundQ:
                #     output_dict['Comments'] = output_dict['Comments']+' Multiple reports found '
                report_foundQ = True
                output_dict = reading_report(ds,output_dict)
                output_dict['Filename'] = f_i
                output_dict['Comments'] = 'No comments'
        except:
            print('     ERROR reading files!!!!!!!!!!!')
            output_dict['Comments'] = output_dict['Comments']+' Error reading files '
    if not report_foundQ:
        print('     ERROR: report not found!!!!!!!!!!!')
        output_dict['Comments'] = output_dict['Comments']+' Report not found '
    return output_dict


writer = pd.ExcelWriter(out_excel_path+excel_file_name,engine = 'xlsxwriter')
df_ff = pd.DataFrame(index=ff_index) 


base_folder_scan = os.scandir(base_path)

next(base_folder_scan)
# test_folders = [next(base_folder_scan),next(base_folder_scan),next(base_folder_scan)]
# test_folders = [next(base_folder_scan))]
# for i in range(60):
#     next(base_folder_scan)
# test_folders = [next(base_folder_scan)]

for folder_i in base_folder_scan: #test_folders:
    print(' ',end='\r', flush=True)
    print('Processing user: '+folder_i.name)
    if not folder_i.name.startswith('.') and folder_i.is_dir():
        path_i = base_path+folder_i.name
        ff_i = [folder_i.name]
        output_dict = reading_dcm_files(path_i+'/')
        # ff_index = ['User_ID','FF ROI','std ROI','FF Vol','std Vol','filename','Comments']
        ff_i.extend([output_dict['FF_ROI'],output_dict['std_FF_ROI'],
            output_dict['FF_Vol'],output_dict['std_FF_Vol'],
            output_dict['Filename'],output_dict['Comments']])

    ff_i = pd.DataFrame(ff_i,index=ff_index)
    df_ff = pd.concat([df_ff,ff_i],axis=1)

df_ff = df_ff.transpose()
df_ff.to_excel(writer,index=False,sheet_name=sheet_name)
# writer.save()