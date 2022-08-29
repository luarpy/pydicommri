#!/bin/python3

# from pydicom.fileset import FileSet
# from pydicom.data import get_testdata_file
from pydicom import dcmread
from os.path import expanduser
import SimpleITK as sitk
import cv2 as cv
import numpy as np
import os
import sys
import glob
import tempfile

path_user = expanduser("~")
path_slicer = 'AppData/Local/NA-MIC/Slicer 4.11.20210226/Slicer.exe'
path_tmp_folder = tempfile.gettempdir() + "/variabilidad"

viewer = sitk.ImageViewer()
viewer.SetProcessDelay(15)
viewer.SetApplication(path_user+path_slicer)

root_path = ''
output_path = ''

def show_volume(viewer,volume):
    viewer.Execute(volume)
    for f in glob.glob(path_user+path_tmp_folder+'*.mha'):
        os.remove(f)

def reading_dcm_files(input_path):
    files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
    num_files = len(files)
    k=0
    seg_image = None
    dict_uid = dict()
    list_overlays_files = []
    list_segs = []
    # Building index
    for f_i in files:
        abs_file_i = input_path+f_i
        k=k+1
        print(' ',end='\r', flush=True)
        print('     %d of %d' %(k,num_files),end='',flush=True)
        try: 
            ds_i = dcmread(abs_file_i)
            dict_uid[ds_i.SeriesInstanceUID] = abs_file_i
            if ds_i.SeriesDescription=='t1_vibe_e-dixon_tra_bh_pre_higado_seg_W_SEG' and ds_i.Modality=='PR':
                list_overlays_files.append(abs_file_i)
                print('         Overlay image found: '+f_i)
        except:
            print('     ERROR reading files!!!!!!!!!!!')
    # Reading specific files
    if list_overlays_files:
        for f_i in list_overlays_files:
            ds_overlay = dcmread(f_i)
            base_uid = ds_overlay['ReferencedSeriesSequence'][0]['SeriesInstanceUID'].value
            base_filename = dict_uid[base_uid]
            base_img =sitk.ReadImage(base_filename)
            aux_mat = sitk.GetArrayFromImage(base_img)
            mask_mat_size = aux_mat.shape
            anno_seq = ds_overlay['GraphicAnnotationSequence']
            mask_mat = np.zeros(mask_mat_size,dtype=np.uint8)

            for anno_i in anno_seq:
        
                slice_idx = anno_i['ReferencedImageSequence'][0]['ReferencedFrameNumber'].value
                n_points =  anno_i['GraphicObjectSequence'][0]['NumberOfGraphicPoints'].value
                pts_coords = np.round(np.reshape(anno_i['GraphicObjectSequence'][0]['GraphicData'].value,(n_points,2))-0.5)
                pts_coords = np.int32(pts_coords)
                aux_mat=np.zeros((mask_mat_size[1:3]),dtype=np.uint8)

                cv.fillPoly(aux_mat,pts=[pts_coords],color=255)
                mask_mat[slice_idx-1,:,:] = cv.bitwise_xor(mask_mat[slice_idx-1,:,:],aux_mat)

                #cv.imshow('Slice by slice',mask_mat[:,:,slice_idx-1])
                #cv.waitKey()

            seg_image = sitk.GetImageFromArray(mask_mat)
            seg_image.CopyInformation(base_img)
            list_segs.append(seg_image)
    else:
        print('     ERROR: overlays not found!!!!!!!!!!!')
    if seg_image==None:
        print('     ERROR: files not found!!!!!!!!!!!')
    return list_segs

def main():
    # Parse input arguments
    for i, arg in enumerate(sys.argv):
        if (arg == '-i'):
            root_path = sys.argv[i+1]
        elif (arg == '-o'):
            ouput_path = sys.argv[i+1]

    if not root_path || not output_pah:
        print("Root and output paths must be provided")
        exit(1)
        
    dirs = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    num_users = len(dirs) # Número de usuarios
    for d_i in dirs:
        # d_i = 'E-116-1'
        print(' ',end='\r', flush=True)
        print('Processing user: '+d_i)
        list_segs = reading_dcm_files(root_path+d_i+'/')
        if list_segs:
            k=1
            for seg_i in list_segs:
                if k>1:
                    sub_str='_'+str(k)
                else:
                    sub_str=''
                sitk.WriteImage(seg_i,output_path+d_i+'_liver_orig'+sub_str+'.seg.nrrd')
                k=k+1
                # show_volume(viewer,seg_image)

if __name__ == "__main__":
    main()