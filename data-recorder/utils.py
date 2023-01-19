import numpy as np


class Utils:
    @staticmethod
    def string_to_float_list(d):
        if d == '':
            return np.array([0.0, 0.0, 0.0])
        
        return np.array(d.replace("[", "").replace("]", "").split(r", ")).astype(float)
