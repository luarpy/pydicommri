import os.path
import sys

import utils

class ReadDicom:
    def __init__(self, **args):
        if file:
            self.file = file
    
    def is_eof_hit(self):
        return self.EOF_hit
    
    def read_dcm_file(self, **args):
        """Returns a dicon file"""
        if not os.path.isfile(file):
            pass
        if not pydicom.misc.is_dicom(file):
            sys.stderr.write("{file} is not a DICOM file")
            sys.exit(2)
        
        try:
            dicom_data = pydicom.dcmread(file)
            return dicom_data
        except:
            EOF_hit = True
            try:
                dicom_data = pydicom.dcmread(file, force=True)
                forced_mode = True
                return dicom_data
            except:
                sys.stderr.write("Could not read {fiel}")
                sys.exit(2)
        

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
            except: # Control for end of file before EOF delimitir runtime warning
                EOF_hit = True
                try:
                    dicom_data = pydicom.dcmread(file_i, force=True)
                except:
                    print("Could not read Dicom file {file_i}")
                    continue
            finally:
                if (regex_report_name.match(dicom_data.SeriesDescription) and dicom_data.Modality == modality and dicom_data.InstanceNumber == instance_number): 
                    print('\tReport found: ' + dicom_data.SeriesDescription, end = '', flush=True)
                    output_dict['ID'] = input_folder.replace(os.sep, '')
                    output_dict['Filename'] = file_i
                    output_dict['SeriesDescription'] = dicom_data.SeriesDescription 
                    output_dict['Modality'] = dicom_data.Modality
                    output_dict['InstanceNumber'] = dicom_data.InstanceNumber
                    output_dict['SeriesDate'] = dicom_data.SeriesDate
                    output_dict['SeriesTime'] = parse_time(dicom_data.SeriesTime)
                    output_dict['SeriesNumber'] = dicom_data.SeriesNumber
                    if EOF_hit:
                        output_dict['Comments'] = 'End of file reached before delimiter.'
                    try:
                        output_dict.update(get_report(dicom_data, output_dict))
                    except Exception as e:
                        output_dict['Comments'] = combine_str(output_dict['Comments'], 'An error occurred: ', str(e))
                    finally:
                        dicom_data = None
                        data.append(output_dict) # Only append data if it finds reports of interets
                
        return data

# def read(data)-> FileDataset:
#     """

#     Raises
#     ------
#     ForceError

#     """
#     try:
#         return pydicom.dcmread(data)
#     except:
#         try:
#             return pydicom.dcmread(data, force=True)
#         except:
#             raise InvalidDicomError
