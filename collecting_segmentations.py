#!/bin/python3

# from pydicom.fileset import FileSet
# from pydicom.data import get_testdata_file
from pydicom import dcmread
import SimpleITK as sitk
import cv2 as cv
import numpy as np
import os
import sys
import glob
import re
import signal
import argparse

def show_volume(viewer,volume):
    viewer.Execute(volume)
    for f in glob.glob(path_user+path_tmp_folder+'*.mha'):
        os.remove(f)

def get_segmentation(file, **args):
    """Get segmentation data from a file DICOM SEG file
    """

    data = dcmread(file)
    base_uid = data['ReferencedSeriesSequence'][0]['SeriesInstanceUID'].value
    base_filename = dict_uid[base_uid]
    base_img = sitk.ReadImage(base_filename)
    aux_mat = sitk.GetArrayFromImage(base_img)
    mask_mat_size = aux_mat.shape
    anno_seq = data['GraphicAnnotationSequence']
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
    pass

def reading_dcm_files(input_path, **args):
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

def exit_handler(signum, frame):
    print('\nUser stopped job...')
    sys.exit(2)

def main():
    """
    TODO: añadir argumentos para pasar las opciones
    - show image
    - input directory
    - input file -> must detect the file
    - series regrex name
    """
    parser = argparse.ArgumentParser(description='Collect segmentations from DICOM files')

    # CTRL+Z and CTRL+C
    signal.signal(signal.SIGTSTP, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    viewer = sitk.ImageViewer()
    viewer.SetProcessDelay(15)
    viewer.SetApplication(path_user+path_slicer)
    
    show_vol = False
    root_path = '../../Variabilidad'
    output_path = './'
    modality = 'PR'
    regex_series_name = re.compile('^t1_vibe_e-dixon_tra_bh_pre_higado_seg_[0-9][0-9]_W_SEG$', re.IGNORECASE)

    dirs = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    for d_i in dirs:
        print(' ',end='\r', flush=True)
        print('Processing user: ' + d_i)
        files = [f for f in os.listdir(root_path + os.sep + d_i + os.sep) if os.path.isfile(os.path.join(input_path, f))]
        for f_i in files:
            (data, title) = get_segmentation(root_path + d_i + f_i)
            sitk.WriteImage(data, output_path + os.sep + d_i + title +'.mha')
            if show_vol == True:
                show_volume(viewer, seg_image)

if __name__ == "__main__":
    main()