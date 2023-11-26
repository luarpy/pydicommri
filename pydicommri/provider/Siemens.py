
import numpy as np

NAME = 'SIEMENS'

def scatter_array(data) -> int:
    if isinstance(data, np.ndarray):
        return (data*1000).astype(int)
    elif isinstance(data, int):
        return int(data*1000)
    elif isinstance(data, list):
        aux = []
        for d in list(data): 
            d = scatter(d)
            aux.append(d)
        return aux
            