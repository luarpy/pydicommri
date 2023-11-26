import argparse
import SimpleITK as sitk
import numpy as np
import os

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file '{arg}' does not exist.")
    return arg

def compute_water(in_phase_path, opp_phase_path, output_mha_path):

  # Set up the reader and get the file information
  in_phase = sitk.ReadImage(in_phase_path, outputPixelType=sitk.sitkFloat64)  # Give it the mha file as a string
  opp_phase = sitk.ReadImage(opp_phase_path, outputPixelType=sitk.sitkFloat64)

  # Calculate fat matrix
  in_phase_arr = sitk.GetArrayFromImage(in_phase) 
  opp_phase_arr = sitk.GetArrayFromImage(opp_phase)
  
  water_arr = 0.5 * (in_phase_arr + opp_phase_arr)

  # Create a new SimpleITK image from the fat array
  water_image = sitk.GetImageFromArray(water_arr)
  water_image.CopyInformation(in_phase)

  # Write the fat image to the output MHA file
  sitk.WriteImage(water_image, output_mha_path)

def main():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("in_phase_path", type=lambda x: is_valid_file(parser, x), help="Ruta del archivo de fase de entrada.")
  parser.add_argument("opp_phase_path", type=lambda x: is_valid_file(parser, x), help="Ruta del archivo de fase de salida.")
  parser.add_argument("output_mha_path", help="Ruta del archivo MHA de salida.")
  args = parser.parse_args()

  in_phase_path = args.in_phase_path 
  opp_phase_path = args.opp_phase_path
  output_mha_path = args.output_mha_path


if __name__ == "__main__":
  main()