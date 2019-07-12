#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 10:44:57 2019

@author: ankurmanikandan
"""

import json

# import modin.pandas as pd
import pandas as pd


class read_cust_config_data(object):
    def __init__(self):
        super(read_cust_config_data, self).__init__()

        # pathname of the customer config file
        self.cust_config_path = "config/"
        cust_config_filename = "customer_config.json"

        # Read in the JSON config file
        with open(self.cust_config_path+cust_config_filename) as json_file:
            self.cust_config_data = json.load(json_file)


class ip_data(object):
    def __init__(self):
        super(ip_data, self).__init__()

        # Path to the directory containing the input datasets
        ip_dir_nm = "input_datasets/"

        # Read in the country code dataset
        file_nm = "CntryCrncyCDE.csv"
        self.cntry_cd_data = pd.read_csv(ip_dir_nm+file_nm)

        # Read in the Country Santions List
        file_nm = "ctry_sanctions_list.csv"
        self.cntry_sanctions_data = pd.read_csv(ip_dir_nm+file_nm)

        # Read in the PEP List
        file_nm = "cust_everypolitician.csv"
        self.pep_data = pd.read_csv(ip_dir_nm+file_nm)

        # Read in the OFAC watchlist
        file_nm = "watch_list_entry.csv"
        self.ofac_wl_data = pd.read_csv(ip_dir_nm+file_nm)

        # Read in the Organization dataset
        file_nm = "cust_organization_list.csv"
        self.org_data = pd.read_csv(ip_dir_nm+file_nm)


if __name__ == '__main__':

    # Create a variable to access the customer config data
    config_data = read_cust_config_data()

    # Read in the input datasets required to generate customer data
    cust_ip_data = ip_data()
