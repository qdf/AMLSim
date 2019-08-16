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

#from tabulate import tabulate

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

        # Determine the number of cores on the machine
        self.nbr_cores = multiprocessing.cpu_count()

        # Read in the configuration files corresponding to the fi types
        self.read_fi_type_config_files()

        # Read in account data to find list of accounts to associate with institutions
        self.read_acct_data()

        # Create column objects
        self.create_col_obj()

        # Number of FIs to be generated
        self.n_fis = self.fi_config_data['n_fi']['value']

        # Read in the configuration files corresponding to the fi types
        self.read_fi_type_config_files()

        # Create column objects
        self.create_col_obj()

    def read_acct_data(self):
        df = pd.read_csv(os.path.join(os.getcwd(),self.fi_config_data["account_data_filepath"]["value"]))
        self.acct_df = df[["account_id","primary_cust_id"]]

    def read_fi_type_config_files(self):

        # Create a variable to store the different fi types
        self.fi_types = list(self.fi_config_data[
                'fi_types']['value'].keys())

        # Get the config file names corresponding to the fi type
        fi_type_config_filename = {}
        for i in self.fi_types:
            fi_type_config_filename[i] = self.fi_config_data[
                    'fi_types']['value'][i]['filename']

        #TODO: Currently we don't have any variation in FI types as there is only BANK
        #      Need to add additional types, then add addition configuration files for each type
        #      Look to how customer type is handled for a model
        # Read in the configuration files associated to the different
        # fi types
        # Define a variable to store the fi type specific configurations
#        self.fi_type_config_data = {}
#        for i in self.fi_types:
#            # Read in the JSON config file
#            with open(self.fi_config_path +
#                      fi_type_config_filename[i]) as json_file:
#                self.fi_type_config_data[i] = json.load(json_file)

    def create_col_obj(self):

        # Create variables to store the column names of the FB_fi table
        fb_fi_cols = self.fi_config_data[
                'column_names']['value']['fb_bank_customers']['value']
        self.fi_id_col = fb_fi_cols[0]
        self.fi_nm_col = fb_fi_cols[1]
        self.fi_type_col = fb_fi_cols[2]
        self.cust_id_col = fb_fi_cols[3]
        self.acct_id_col = fb_fi_cols[4]
        
        
        
        # Create a variable to store the sequence of column names
        self.seq_col_nm = [fb_fi_cols[0],
                           fb_fi_cols[1],
                           fb_fi_cols[2],
                           fb_fi_cols[3],
                           fb_fi_cols[4]
                          ]


    def gen_fi_id(self):

        # # Placed the import statement within the method is because of Ray.
        # # It was throwing errors otherwise.
        # import uuid

        # # Determine the number of records to be assigned to each core
        # cores_use, recs_per_core = nbr_rec_per_core(
        #         self.n_fis, self.nbr_cores)

        # @ray.remote
        # def gen_uuid():
        #     return [str(uuid.uuid4()) for _ in range(recs_per_core)]

        # # Generate the fi ids
        # dummy_fi_ids = ray.get(
        #         [gen_uuid.remote() for _ in range(cores_use)])
        # # Flatten the list of lists
        # fi_ids = [
        #         item for sublist in dummy_fi_ids for item in sublist]

        # Generate fi ids for normal fis
        fi_ids = ["FI-"+str(uuid.uuid4()).replace('-', '')
                    for _ in range(self.n_fis)]

        # Add fi ids to the fb_fi dataset
        self.fb_fi = pd.DataFrame(
                np.array(fi_ids), columns=[self.fi_id_col])

        print("DONE GENERATING THE FI IDS.")

    def _det_fi_type_counts(self):

        # Determine the count of the various fi types
        self.fi_type_counts = {}
        fi_type_val_counts = self.fb_fi[
                self.fi_type_col].value_counts(dropna=False)
        for i in self.fi_types:
            self.fi_type_counts[i] = fi_type_val_counts[i]

    def _det_fi_type_indices(self):

        # Determine the indices of the various fi types
        self.fi_type_indices = {}
        for i in self.fi_types:
            self.fi_type_indices[i] = np.where(
                    self.fb_fi[self.fi_type_col] == i)[0]

    def gen_fi_types(self):

        # Create a variable to store the percentage of each fi type
        fi_types_probs = []
        for i in self.fi_types:
            fi_types_probs.append(
                    self.fi_config_data[
                            'fi_types']['value'][i]['value']/100.)

        # Generate the fi types based on the specified percentages
        self.fb_fi[self.fi_type_col] = np.random.choice(
                self.fi_types, size=self.n_fis, p=fi_types_probs)

        print("DONE GENERATING THE fi TYPES.")

        # Determine the count of the various fi types
        self._det_fi_type_counts()

        # Determine the indices of the various fi types
        self._det_fi_type_indices()


    def _gen_org_fi_nm(self, c_type):

        # Having an issue when generating the company names via Ray.
        # Somehow the number of names getting generated is never equal to
        # the current number of fi type ORG in the dataset.
#        # Determine the number of records to be assigned to each core
#        cores_use, recs_per_core = nbr_rec_per_core(nbr_org, self.nbr_cores)
#
#        @ray.remote
#        def gen_org():
#            return [fake.company() for _ in range(recs_per_core)]
#
#        # Generate the ORG names
#        self.dummy_org_nm = ray.get(
#                [gen_org.remote() for _ in range(cores_use)])
#        # Flatten the list of lists
#        self.org_nm = [
#                item for sublist in self.dummy_org_nm for item in sublist]
#        print(len(self.org_nm))

        # Generate the ORG names
        c_type_count = self.fi_type_counts[c_type]
        org_nm = [barnum.create_company_name() for _ in range(c_type_count)]

        # There seems to be a problem when trying to add the organization
        # names to the existing modin series. To resolve the issue its best
        # to duplicate the data in the modin series to a numpy array, then
        # add the organization names to the numpy array and copy the data
        # back to the modin dataframe
#        disp_nm_arr = self.fb_fi[self.fi_nm_col].values
#        disp_nm_arr[self.fi_type_indices[c_type]] = org_nm

        # Add the fi names to the fb_fi dataframe
#        self.fb_fi[self.display_nm_col].where(
#                    org_ind, np.array(self.org_nm), inplace=True)
        self.fb_fi[self.fi_nm_col] = pd.Series(org_nm)

        print("DONE GENERATING THE FI NAMES FOR FI TYPE - \
        ORGANIZATIONS.")

    def gen_fi_nm(self):

        # The below line of code is used if we are able to get one function
        # to generate both ind and org names. But there seems to be an issue
        # with the number of records that are getting generated. Maybe a
        # Ray issue.
        # Create the fi name column with empty values
        # self.fb_fi[self.display_nm_col] = ['']*self.n_fis

        # Generate fi names based on fi type
        for i in self.fi_types:
            if i.lower() in "bank":
                self._gen_org_fi_nm(i)

        print("DONE GENERATING THE FI NAMES.")

    def assign_acct_to_fi(self):
        
        self.acct_df
        
        self.fb_fi
        
        self.fb_combined = self.acct_df.copy()
        
        self.fb_combined["fi_id"] = pd.Series(np.random.choice(self.fb_fi["fi_id"].unique(),self.fb_combined.shape[0],p=self.fi_config_data["n_fi"]["distribution"]))
        
        fi_types = dict(zip(self.fb_fi.fi_id,self.fb_fi.fi_type))
        self.fb_combined["fi_type"] = self.fb_combined.apply(lambda row : fi_types[row["fi_id"]],axis=1)
        
        fi_names = dict(zip(self.fb_fi.fi_id,self.fb_fi.fi_name))
        self.fb_combined["fi_name"] = self.fb_combined.apply(lambda row : fi_names[row["fi_id"]],axis=1)

        
        

    def data(self):

        start_time = time.time()

        # Generate fi ids
        self.gen_fi_id()

        # Generate fiomer types
        self.gen_fi_types()

        # Generate fiomer names
        self.gen_fi_nm()

        # Assign accounts to FIs
        self.assign_acct_to_fi()

        # Determine the time taken to generate the fi dataset
        print("Time taken to generate fi data: ", \
            time.time() - start_time, " secs")



if __name__ == '__main__':

    from utils import write_data_to_machine

    # Create an object
    fb_fi_data = generate_fi_data()
    # Generate account data
    fb_fi_data.data()
#    print(tabulate(fb_fi_data.fb_fi,headers = "keys",tablefmt="psql"))
    # Write combined fi data to csv file
    write_data_to_machine(fb_fi_data.fb_combined,
                          "fi_combined")