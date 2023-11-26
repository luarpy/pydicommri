import time
import os
from typing import Iterator, TextIO
import numpy as np

def format_time(_time = None, **kwargs):
    if myformat is None: return _time
    
    if myformat:
       _format = myformat 
    else:
        _format = '%H:%M:%S'
    my_time = time.strptime(_time, _format)
    return time.strftime(my_time, '%H%M%S.%f')

def combine_str(*strings, **kwargs):
    """
    Returns a string combining the input strings with a blak space. 
    The separator between strings can be set with 'separator=', default is ' '
    """
    if separator:
        _separator = separator
    else:
        _separator = ' '

    string = ''
    for s in strings:
        if s:
            string += s + _separator
    return string

def write_csv(transcript: Iterator[dict], file: TextIO):
    for segment in transcript:
        print(segment['text'].strip(), file=file, flush=True)

def write_json(file: TextIO):
    pass
    

def write_xlsx():
    pass

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def recurse(ds):
    for elem in ds:
        if elem.VR == 'SQ':
            [recurse(item) for item in elem.value]
        else:
            print(elem)

def parent_dir(a)-> str:
    """
    Return the parent directory of file or directory

    """
    return os.path.abspath(os.path.join(a, os.pardir))

def list2ndarray(lst, dtype=None):
    """fast conversion from list type to numpy.ndarray type"""
    if len(lst) > 1:
        return [np.array(a, dtype=dtype) if isinstance(a, list) else a for a in lst]
    else:
        return np.array(lst[0], dtype=dtype) if isinstance(lst[0], list) else lst[0]