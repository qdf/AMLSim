#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import json
import uuid
from datetime import datetime
import os

import numpy as np
import pandas as pd
from scipy.stats import skewnorm
from faker import Faker

from create_account_objects import read_act_config_data
from utils import _random_date

# Initialize the Faker class
fake = Faker()


class generate_act_data(read_act_config_data):
    def __init__(self):
        super(generate_act_data, self).__init__()

        # Read in the customer dataset
        self.cust_data = pd.read_csv(
            self.get_latest_output(self.act_config_data['customer_data_filepath']['value'])
            )

        # Assign customer data column names to variables
        self.get_cust_col_nm()

        # Read in the configuration files corresponding to the customer types
        self.read_cust_type_config_files()

        # Create column objects
        self.create_col_obj()
    #Find latest output from data generation
    #TODO: Path is currently hardcoded, beware of this for future use
    def get_latest_output(self,file_name):
        file_search_term = file_name.split("%")[0].split("/")[-1]
        path = "output_datasets"
        files = [os.path.join(path,x) for x in os.listdir(path) if file_search_term in x]
        return max(files,key=os.path.getctime)

    def read_cust_type_config_files(self):

        # Create a variable to store the different customer types
        self.cust_types = self.cust_data[self.cust_col_nm[
            'cust_cust_type_col']].unique()

        # Get the config file names corresponding to the customer type
        cust_type_act_config_filename = {}
        for i in self.act_config_data['act_config_files_cust_type']['value']:
            for j in self.cust_types:
                if "_" + j.lower() in i:
                    cust_type_act_config_filename[j] = i

        # Read in the configuration files associated to the different
        # customer types
        # Define a variable to store the customer type specific configurations
        self.cust_type_act_config_data = {}
        for i in self.cust_types:
            # Read in the JSON config file
            with open(self.act_config_path +
                      cust_type_act_config_filename[i]) as json_file:
                self.cust_type_act_config_data[i] = json.load(json_file)

    def get_cust_col_nm(self):

        # Create a dictionary to store the key-value pair of customer
        # column names
        self.cust_col_nm = self.act_config_data['customer_data_col_nm'][
            'value']

    def create_col_obj(self):

        # Create variables to store the column names of the FB_ACCOUNT table
        fb_account_cols = self.act_config_data[
            'column_names']['value']['fb_account']['value']
        self.act_id_col = fb_account_cols[0]
        self.bus_domain_col = fb_account_cols[1]
        self.jurisdiction_col = fb_account_cols[2]
        self.display_nm_col = fb_account_cols[3]
        self.acct_type_col = fb_account_cols[4]
        self.ownership_type_col = fb_account_cols[5]
        self.acct_purpose_col = fb_account_cols[6]
        self.acct_open_dt_col = fb_account_cols[7]
        self.primary_cust_id_col = fb_account_cols[8]

        # Create variable to store the column names of the FB_ACCT_TO_CUST table
        fb_act_to_cust_cols = self.act_config_data[
            'column_names']['value']['fb_acct_to_cust']['value']
        self.customer_id_col = fb_act_to_cust_cols[0]

        # Create variables to store the column names of the
        # FB_ACCT_PHONE_NUM table.
        fb_acct_phone_num_cols = self.act_config_data[
            'column_names']['value']['fb_acct_phone_num']['value']
        self.phone_id_col = fb_acct_phone_num_cols[0]
        self.phone_num_col = fb_acct_phone_num_cols[1]

        # Create variables to store the column names of the
        # FB_ACCT_ADDRESS table.
        fb_acct_address_cols = self.act_config_data[
            'column_names']['value']['fb_acct_address']['value']
        self.adrs_id_col = fb_acct_address_cols[0]
        self.city_nm_col = fb_acct_address_cols[1]
        self.cntry_cd_col = fb_acct_address_cols[2]
        self.postal_cd_col = fb_acct_address_cols[3]
        self.state_cd_col = fb_acct_address_cols[4]
        self.street_line1_txt_col = fb_acct_address_cols[5]

        # Create a variable to store the sequence of column names
        self.seq_col_nm = [fb_account_cols[0],
                           fb_account_cols[1],
                           fb_account_cols[2],
                           fb_account_cols[3],
                           fb_account_cols[4],
                           fb_account_cols[5],
                           fb_account_cols[6],
                           fb_account_cols[7],
                           fb_account_cols[8],
                           fb_act_to_cust_cols[0],
                           fb_acct_address_cols[0],
                           fb_acct_address_cols[1],
                           fb_acct_address_cols[2],
                           fb_acct_address_cols[3],
                           fb_acct_address_cols[4],
                           fb_acct_address_cols[5],
                           fb_acct_phone_num_cols[0],
                           fb_acct_phone_num_cols[1]]

    def determine_nbr_acts(self):

        # Determine the number of customer records created
        len_customer_id = len(self.cust_data)

        # Assign 'x' number of accounts per customer
        # the in built function "skewnorm.rvs" helps build a skewed distribution.
        # we can skew  distribution by changing the value of the "skewness_factor".
        self.nbr_act_nbr_customer = skewnorm.rvs(
            self.act_config_data['params_nbr_accounts_per_user'][
                'value']['skewness_factor']['value'],
                size=len_customer_id,
            scale=self.act_config_data['params_nbr_accounts_per_user'][
                'value']['scale_factor']['value']).astype(int)
        # adding the value 1 to the variable to ensure that there are no 0's.
        self.nbr_act_nbr_customer = self.nbr_act_nbr_customer + 1
        # determine the total number of accounts that the bank is
        # currently operating.
        self.sum_act_nbr_customer = np.sum(self.nbr_act_nbr_customer)

        print "DONE ASSIGNING ACCOUNT PER CUSTOMER."

    def gen_act_id(self):

        # Generate account ids
        act_ids = ["AC-"+str(uuid.uuid4()).replace('-', '')
                    for _ in xrange(self.sum_act_nbr_customer)]

        # Add customer ids to the fb_customer dataset
        self.fb_account = pd.DataFrame(
            np.array(act_ids), columns=[self.act_id_col])

        print "DONE GENERATING THE ACCOUNT IDS."

    def assign_primary_cust_id(self):

        # Determine the customer ids corresponding to each account id
        customer_id = [[self.cust_data[self.cust_col_nm[
            'cust_cust_id_col']][i]]*j for i, j in
                       enumerate(self.nbr_act_nbr_customer)]
        # Flatten out the list of lists
        customer_id = [item for sublist in customer_id for item in sublist]

        # Assign primary customer id to the account dataframe
        self.fb_account[self.primary_cust_id_col] = customer_id

        print "DONE ASSIGNING PRIMARY CUSTOMER ID."

        # Merge the customer dataframe with the account dataframe
        self.merge_cust_act = self.cust_data.merge(self.fb_account,
                                                   left_on=self.cust_col_nm[
                                                       'cust_cust_id_col'],
                                                   right_on=self.primary_cust_id_col)

    def assign_bus_domain(self):

        # Assign business domain values to the account dataframe
        self.fb_account[self.bus_domain_col] = self.merge_cust_act[
            self.cust_col_nm['cust_bus_domain_col']].values

        print "DONE ASSGINING BUSINESS DOMAIN TO ACCOUNT DATAFRAME."

    def assign_jurisdiction(self):

        # Assign jurisdiction to the account dataframe
        self.fb_account[self.jurisdiction_col] = self.merge_cust_act[
            self.cust_col_nm['cust_jurisdiction_col']].values

        print "DONE ASSIGNING JURISDICTION TO THE ACCOUNT DATAFRAME."

    def assign_display_nm(self):

        # Assign display name to the account dataframe
        self.fb_account[self.display_nm_col] = self.merge_cust_act[
            self.cust_col_nm['cust_display_nm_col']].values

        print "DONE ASSIGNING DISPLAY NAMES TO THE ACCOUNT DATAFRAME."

    def gen_act_type(self):

        # Assign a variable to store the account types
        act_type = np.array(['A']*self.sum_act_nbr_customer)

        # Randomly generate account types from the distribution provided in
        # the config file
        act_type = np.random.choice(self.act_config_data['act_types'][
            'value'].keys(),
            size=self.sum_act_nbr_customer,
            replace=True,
            p=self.act_config_data['act_types']['value'].values())

        # Add the account types to the account dataframe
        self.fb_account[self.acct_type_col] = act_type

        print "DONE WITH GENERATING ACCOUNT TYPES."

    def gen_act_owner_type(self):

        # Assign variable to store the account ownership tyoe values
        act_owner_type = self.merge_cust_act[self.cust_col_nm[
            'cust_cust_type_col']].values.copy()

        # Store the mapping between the customer type and account ownership
        # type in a variable
        cust_to_act = self.act_config_data[
            'map_cust_type_to_act_owner_type']['value']

        # Loop through each customer type and and assign the relevant
        # account ownership type to the account record
        for i in self.cust_types:
            act_owner_type_val = cust_to_act[i]
            act_owner_type_indices = np.where(
                act_owner_type == i)[0]
            act_owner_type[act_owner_type_indices] = act_owner_type_val

        # Add the account ownership data to the account dataframe
        self.fb_account[self.ownership_type_col] = act_owner_type

        print "DONE GENERATING ACCOUNT OWNERSHIP TYPE."

    def gen_act_purpose(self):

        # Assign variable to store the account purpose values
        act_purpose = np.array(['A']*self.sum_act_nbr_customer).astype(object)

        # Assign the account purpose based on the account type and customer
        # type
        # Loop through each customer type
        for i in self.cust_types:
            act_purpose_dict = self.cust_type_act_config_data[i][
                'account_purpose']['value']
            act_type_vals = act_purpose_dict.keys()
            for j in act_type_vals:
                # Determine the indices where customer type and account type
                # match 'i' and 'j' respectively
                cond = (
                    (self.merge_cust_act[self.cust_col_nm[
                        'cust_cust_type_col']] == i) & (
                            self.fb_account[self.acct_type_col] == j
                    ))
                # Number of indices where condition is 'True'
                nbr_indices = np.sum(np.array(cond).astype(int))
                # Extract the account purpose and its corresponding
                # probability
                act_purpose_vals = act_purpose_dict[j].keys()
                act_purpose_probs = []
                for k in act_purpose_vals:
                    act_purpose_probs.append(act_purpose_dict[j][k]['value'])
                # Check if the sum of the probabilities is 1.0
                if np.sum(act_purpose_probs) != 1.0:
                    print "Sum of probabilities for account purpose do not sum to 1.0.", i, j
                # Sample the account purpose
                act_purpose[cond] = np.random.choice(
                    act_purpose_vals,
                    size=nbr_indices,
                    replace=True,
                    p=act_purpose_probs
                )

        # Add the account purpose to the account dataframe
        self.fb_account[self.acct_purpose_col] = act_purpose

        print "DONE GENERATING ACCOUNT PURPOSE."

    def gen_act_open_dt(self):

        # Generate random dates from the range provided in the config file
        d1 = datetime.strptime(self.act_config_data[
            'open_account_date_range']['value'][0], '%m/%d/%Y %I:%M %p')
        d2 = datetime.strptime(self.act_config_data[
            'open_account_date_range']['value'][1], '%m/%d/%Y %I:%M %p')
        self.act_open_dt = np.array([_random_date(d1, d2)
                                     for _ in xrange(
                                         self.sum_act_nbr_customer)])

        # Add account open date to the account dataframe
        self.fb_account[self.acct_open_dt_col] = self.act_open_dt

        print "DONE GENERATING ACOCUNT OPEN DATE."

    def gen_act_to_cust(self):

        # Assign customer ids
        cust_ids = self.merge_cust_act[self.cust_col_nm[
            'cust_cust_id_col']].values

        # Add customer ids to the fb_acct_to_cust dataset
        self.fb_acct_to_cust = pd.DataFrame(
            cust_ids, columns=[self.customer_id_col])

        print "DONE ASSIGNING CUSTOMER IDS."

    def gen_phone_id(self):

        # Generate address ids for each account record
        phone_id = ["PH-"+str(uuid.uuid4()).replace('-', '')
                    for _ in xrange(self.sum_act_nbr_customer)]

        # Add phone ids ids to the fb_phone dataset
        self.fb_phone = pd.DataFrame(
            np.array(phone_id), columns=[self.phone_id_col])

        print "DONE GENERATING PHONE IDS."

    def gen_phone_number(self):

        # Assign phone numbers
        phone_num = self.merge_cust_act[
            self.cust_col_nm['cust_phone_num_col']].values

        # Change a few of the phone records. The percentage of phone records
        # to change is provided in the config file
        # Number of records to change
        nbr_change = int(self.act_config_data[
            'percent_act_ph_dfrnt']['value']/100.0)
        indices_change = np.random.choice(xrange(self.sum_act_nbr_customer),
            size=nbr_change, replace=False)
        phone_num[indices_change] = [
            fake.phone_number() for _ in xrange(nbr_change)
        ]

        # Add phone numbers to account phone dataframe
        self.fb_phone[self.phone_num_col] = phone_num

        print "DONE GENERATING PHONE NUMBERS."

    def gen_adrs_id(self):

        # Generate address ids for each account record
        adrs_id = ["ADR-"+str(uuid.uuid4()).replace('-', '')
                   for _ in xrange(self.sum_act_nbr_customer)]

        # Add address ids to the fb_address dataset
        self.fb_address = pd.DataFrame(
            np.array(adrs_id), columns=[self.adrs_id_col])

        print "DONE GENERATING THE ADDRESS IDS."

        # Determine which address records are going to be changed
        # Number of records to change
        self.adrs_nbr_change = int(self.act_config_data[
            'percent_act_adrs_dfrnt']['value']/100.0)
        self.adrs_indices_change = np.random.choice(
            xrange(self.sum_act_nbr_customer), size=self.adrs_nbr_change,
            replace=False)

    def gen_city_nm(self):

        # Create a variable to store the city names
        city_nm = self.merge_cust_act[
            self.cust_col_nm['cust_city_nm_col']].values

        # Generate city name for each account record
        city_nm[self.adrs_indices_change] = [
            fake.city() for _ in xrange(self.adrs_nbr_change)]

        # Address city name to fb_address dataset
        self.fb_address[self.city_nm_col] = city_nm

        print "DONE GENERATING THE CITY NAMES."

    def gen_cntry(self):

        # Add Country to fb_address dataset
        self.fb_address[self.cntry_cd_col] = self.fb_account[
            self.jurisdiction_col]

        print "DONE GENERATING THE COUNTRY NAMES."

    def gen_postal_cd(self):

        # Create a variable to store the postal codes
        postal_cd = self.merge_cust_act[
            self.cust_col_nm['cust_postal_cd_col']].values

        # Generate postal codes for each account record
        postal_cd[self.adrs_indices_change] = [
            fake.postalcode() for _ in xrange(self.adrs_nbr_change)]

        # Address city name to fb_address dataset
        self.fb_address[self.postal_cd_col] = postal_cd

        print "DONE GENERATING THE POSTAL CODES."

    def gen_state_cd(self):

        # Create a variable to store the state codes
        state_cd = self.merge_cust_act[
            self.cust_col_nm['cust_state_cd_col']].values

        # Generate state codes for each account record
        state_cd[self.adrs_indices_change] = [
            fake.state() for _ in xrange(self.adrs_nbr_change)]

        # Address city name to fb_address dataset
        self.fb_address[self.state_cd_col] = state_cd

        print "DONE GENERATING THE STATE CODES."

    def gen_street_adrs(self):

        # Create a variable to store the street address
        street_adrs = self.merge_cust_act[
            self.cust_col_nm['cust_street_line1_txt_col']].values

        # Generate state codes for each account record
        street_adrs[self.adrs_indices_change] = [
            fake.street_address() for _ in xrange(self.adrs_nbr_change)]

        # Address city name to fb_address dataset
        self.fb_address[self.street_line1_txt_col] = street_adrs

        print "DONE GENERATING THE STREET ADDRESS."

    def data(self):

        start_time = time.time()

        # determine the number of accounts to assign per customer
        self.determine_nbr_acts()

        # Generate account ids
        self.gen_act_id()

        # Assign primary customer ids
        self.assign_primary_cust_id()

        # Assign business domain
        self.assign_bus_domain()

        # Assign jurisdiction
        self.assign_jurisdiction()

        # Assign display name
        self.assign_display_nm()

        # Generate account types
        self.gen_act_type()

        # Generate account ownership type
        self.gen_act_owner_type()

        # Generate account purpose
        self.gen_act_purpose()

        # Generate account open date
        self.gen_act_open_dt()

        # Assign customer ids
        self.gen_act_to_cust()

        # Generate phone ids
        self.gen_phone_id()

        # Generate phone numbers
        self.gen_phone_number()

        # Generate address ids
        self.gen_adrs_id()

        # Generate city name
        self.gen_city_nm()

        # Generate country
        self.gen_cntry()

        # Generate postal codes
        self.gen_postal_cd()

        # Generate state codes
        self.gen_state_cd()

        # Generate street address
        self.gen_street_adrs()

        # Combine the account, account to customer, address and phone
        # dataframe in to a single dataframe
        self.comb_act_df = pd.concat([self.fb_account, self.fb_acct_to_cust,
                                       self.fb_address, self.fb_phone],
                                      axis=1)

        # Rearrange the sequence of column names in the combined
        # account data
        self.comb_act_df = self.comb_act_df[self.seq_col_nm]

        # Determine the time taken to generate the account dataset
        print "Time taken to generate account data: ", \
            time.time() - start_time, " secs"


if __name__ == '__main__':

    from utils import write_data_to_machine

    # Create an object
    fb_act_data = generate_act_data()
    # Generate account data
    fb_act_data.data()

    # Write combined customer data to csv file
    write_data_to_machine(fb_act_data.comb_act_df,
                          "account_combined")
