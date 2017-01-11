import struct
import numpy as np


def blob_to_byte_array(bytes_obj):
    return np.array([z[0] + 128 for z in struct.iter_unpack('>b', bytes_obj)])

def blob_to_float_array(bytes_obj):
    return np.array([z[0] for z in struct.iter_unpack('>f', bytes_obj)])
