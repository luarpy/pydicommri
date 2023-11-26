import argparse
import SimpleITK as sitk
import numpy as np
import os

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file '{arg}' does not exist.")
    return arg

def compute_ff(water_path, fat_path, output_mha_path, *args):
    water = sitk.ReadImage(water_path, outputPixelType=sitk.sitkFloat64)
    fat = sitk.ReadImage(fat_path, outputPixelType=sitk.sitkFloat64)

    water_arr = sitk.GetArrayFromImage(water)
    fat_arr = sitk.GetArrayFromImage(fat)
    
    tmp = water_arr + fat_arr
    ff_arr = np.divide(fat_arr, tmp, where=tmp != 0)
    
    ff_image = sitk.GetImageFromArray(ff_arr)
    ff_image.CopyInformation(water)

    sitk.WriteImage(ff_image, output_mha_path)
    
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("water_path", type=lambda x: is_valid_file(parser, x), help="Ruta del archivo de fase de entrada.")
    parser.add_argument("fat_path", type=lambda x: is_valid_file(parser, x), help="Ruta del archivo de fase de salida.")
    parser.add_argument("output_mha_path", help="Ruta del archivo MHA de salida.")
    args = parser.parse_args()
    water_path = args.water_path
    fat_path = args.fat_path
    output_mha_path = args.output_mha_path

    compute_ff(water_path, fat_path, output_mha_path)


if __name__ == "__main__":
  main()