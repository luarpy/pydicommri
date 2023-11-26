# from pydicom.fileset import FileSet
# from pydicom.data import get_testdata_file
from pydicom import dcmread
from pydicom.fileset import FileSet

import SimpleITK as sitk
import cv2 as cv
import numpy as np
import os
import tempfile
import glob

def reading_dcm_files(input_path):
    files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
    num_files = len(files)
    k=0
    seg_image = None
    dict_uid = dict()
    
    list_segs = []
    # Building index
    dicomdir_path = input_path + 'DICOMDIR'
    list_overlays_files = []
    if os.path.isfile(dicomdir_path):
        fs = FileSet(dicomdir_path) 
        list_SeriesNumber = fs.find_values('SeriesNumber')
        list_SeriesNumber.sort()
        k = 0
        num_series = len(list_SeriesNumber)
        for serieNumber in list_SeriesNumber:
            k = k+1
            # print(serieNumber)
            print(' ',end='\r', flush=True)
            print('     %d of %d' %(k,num_series),end='',flush=True)
            list_instance = fs.find(SeriesNumber=serieNumber)
            for instance in list_instance:
                ds_i = dcmread(instance.path)
                dict_uid[ds_i.SeriesInstanceUID] = instance.path
                print(list_instance[0].SeriesDescription)
                print(list_instance[0].Modality)
                if list_instance[0].SeriesDescription == 't1_vibe_e-dixon_tra_bh_pre_higado_seg_W_SEG' and list_instance[0].Modality=='PR':
                    list_overlays_files = []
                    for instance in list_instance:
                        list_overlays_files.append(instance.path)     
    else:
        for root, dirs, files in os.walk(input_path):
            for f_i in files:
                abs_file_i = os.path.join(root, f_i)
                k=k+1
                print(' ',end='\r', flush=True)
                print('     %d of %d' %(k,num_files),end='',flush=True)
                try: 
                    ds_i = dcmread(abs_file_i) 
                    # # PROVISIONAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    # if 'GraphicAnnotationSequence' in ds_i:
                    #     print('overlay found in: '+ds_i.SeriesDescription)
                    # # PROVISIONAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    dict_uid[ds_i.SeriesInstanceUID] = abs_file_i
                    print(ds_i.SeriesDescription)
                    print(ds_i.Modality)
                    if ds_i.SeriesDescription=='t1_vibe_e-dixon_tra_bh_pre_higado_seg_W_SEG' and ds_i.Modality=='PR':
                        list_overlays_files.append(abs_file_i)
                        print('         Overlay image found: '+f_i)
                except:
                    print('     ERROR initial reading files!!!!!!!!!!!')
    # Reading specific files
    if len(list_overlays_files)>0:
        for i,f_i in enumerate(list_overlays_files):
            try:
                ds_overlay = dcmread(f_i)
                # if i>43:
                #     print('Stop')
                #     aux_img = sitk.ReadImage(f_i)
                #     show_volume(viewer,aux_img)
                try:
                    base_uid = ds_overlay['ReferencedSeriesSequence'][0]['SeriesInstanceUID'].value
                except:
                    base_uid = ds_overlay['RelatedSeriesSequence'][0]['SeriesInstanceUID'].va
                try:
                    base_filename = dict_uid[base_uid]
                    base_img =sitk.ReadImage(base_filename)
                    aux_mat = sitk.GetArrayFromImage(base_img)
                    aux_shape = aux_mat.shape
                except:
                    aux_shape = (320,260,88)
                mask_mat_size = aux_shape
     
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
            except:
                print('     Error reading overlay files')
    else:
        print('     ERROR: overlays not found!!!!!!!!!!!')
    if seg_image==None:
        print('     ERROR: files not found!!!!!!!!!!!')
    return list_segs


def get_segments(input_path, output_path):
    dirs = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]
    num_users = len(dirs)
    for d_i in dirs:
        print(' ',end='\r', flush=True)
        print('Processing user: '+d_i)
        list_segs = reading_dcm_files(input_path+d_i+'/')
        if list_segs:
            k=1
            for seg_i in list_segs:
                if k>1:
                    sub_str='_'+str(k)
                else:
                    sub_str=''
                sitk.WriteImage(seg_i, output_path+d_i+'_liver_orig'+sub_str+'.seg.nrrd')
                k=k+1

def main():
    pass

if __name__ == "__main__":
    main()
