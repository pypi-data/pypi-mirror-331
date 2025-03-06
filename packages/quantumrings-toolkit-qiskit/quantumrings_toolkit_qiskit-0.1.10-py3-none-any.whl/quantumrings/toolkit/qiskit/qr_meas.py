# This code is part of Quantum Rings SDK.
#
# (C) Copyright Quantum Rings Inc, 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=wrong-import-position,wrong-import-order

from typing import List, Union, Iterable, Tuple


#
# a helper class for the sampler to hold the measurement data
#

class meas:
    """
    A helper class for the QrSamplerV2 to store the measurement data.
    """
    def __init__(self, results):
        """
        Class initializer
        Args:
        results: The Results dictionary from the execution of a Quantum Circuit
        """
        self._result_dict = results;
    
    def get_int_counts(self):
        """
        Returns the integer counts of the Results
        """
        int_counts_dict = {}
        for key, value in self._result_dict.items():
            int_counts_dict[int(key,2)] = value
        return int_counts_dict
        
    def get_counts(self):
        """
        Returns the binary counts of the Results.
        """
        return self._result_dict