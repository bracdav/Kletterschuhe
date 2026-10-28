import numpy as np

def convert_single_size(size):
    if not isinstance(size, str):
        return 0.0
    if 'US' in size:
        return np.round(float(size.replace('US ', '').replace(',','.').replace('+','').strip()), 1) + 32
    elif 'UK' in size:
        return np.round(float(size.replace('UK ', '').replace(',','.').strip()), 1) + 33
    elif '-' in size:
       return np.round(float(size.split('-')[0]), 1)
    elif 'EUI' in size:
        return np.round(float(size.replace('EUI ', '').replace(',', '')), 1)
    else:
       return np.round(float(size.replace(',', '')), 1)

def convert_size_list(size_list):
    res = []
    for size in size_list:
        res.append(convert_single_size(size))
    return res


def eval_string_data(to_eval):
    if (isinstance(to_eval, int) or (isinstance(to_eval, float))):
        return to_eval
    if isinstance(to_eval, list):
        return to_eval
    if (isinstance(to_eval, str) & ('[' in to_eval)):
        return eval(to_eval)
    return to_eval