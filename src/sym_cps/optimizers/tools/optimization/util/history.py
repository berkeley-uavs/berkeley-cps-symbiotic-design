import numpy as np

class History():
    def __init__(self):
        self._hist_p = None # params
        self._hist_f = None # func values
        self._hist_v = None # valid

    def reset_history(self, p_dim, num_obj, num_con):
        """Clear all history"""
        self._hist_d = []
        self._hist_p = np.array([]).reshape((0, p_dim))
        self._hist_f = np.array([]).reshape((0, num_obj))
        self._hist_v = np.array([]).reshape((0, num_con))

    def add_hist(self, params, obj_vals, valid):
        """Push a data point to the history"""
        obj_vals = np.array(obj_vals)
        valid = np.array(valid)
        self._hist_p = np.concatenate((self._hist_p, params.reshape(1, -1)))
        self._hist_f = np.concatenate((self._hist_f, obj_vals.reshape(1, -1)))
        self._hist_v = np.concatenate((self._hist_v, valid.reshape(1, -1)))

    @property 
    def length(self):
        return len(self._hist_d)

    @property
    def hist_params(self):
        return self._hist_p

    @property
    def hist_func(self):
        return self._hist_f

    @property
    def hist_valid(self):
        return self._hist_v

    @property
    def hist(self):
        return self.hist_params, self.hist_func, self.hist_valid