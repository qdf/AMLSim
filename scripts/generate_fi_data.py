#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 11:57:31 2019

@author: ryancompton
"""

import os
import time
import multiprocessing
from fractions import gcd
import json
import uuid

import numpy as np
# import modin.pandas as pd
import pandas as pd
from faker import Faker
# import ray
import barnum

from create_fi_objects import read_fi_config_data
from utils import gen_income_vals

class generate_fi_data(read_fi_config_data):
    def __init__(self):
        super(generate_fi_data, self).__init__()

        # Read in the finacial institute dataset
        self.fi_data = pd.read_csv(
            self.get_latest_output(self.fi_config_data['fi_data_filepath']['value'])
            )

        # Assign customer data column names to variables
        self.get_fi_col_nm()

        # Read in the configuration files corresponding to the customer types
        self.read_fi_type_config_files()

        # Create column objects
        self.create_col_obj()

    #Find latest output from data generation
    #TODO: Path is currently hardcoded, beware of this for future use
    def get_latest_output(self,file_name):
        file_search_term = file_name.split("%")[0].split("/")[-1]
        path = "output_datasets"
        if path not in os.listdir(os.getcwd()):
            os.mkdir(os.path.join(os.getcwd(),path))
        files = [os.path.join(path,x) for x in os.listdir(path) if file_search_term in x]
        return max(files,key=os.path.getctime)


if __name__ == '__main__':

    from utils import write_data_to_machine

    # Create an object
    fb_act_data = generate_fi_data()
    # Generate account data
    fb_act_data.data()

    # Write combined customer data to csv file
    write_data_to_machine(fb_act_data.comb_act_df,
                          "account_combined")