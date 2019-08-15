#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 13:58:18 2019

@author: ankurmanikandan
"""

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

from create_customer_objects import read_cust_config_data, ip_data
from utils import gen_income_vals


# Initiate Ray
# ray.init(ignore_reinit_error=True)

# Initialize the Faker class
fake = Faker()


def nbr_rec_per_core(total_recs, nbr_cores):

    val = gcd(total_recs, nbr_cores)
    recs_per_core = int(total_recs/val)

    return val, recs_per_core


# Having many issues with class inheritance. Complex class inhertiance is
# causing a few problems for Ray to function properly.
class generate_cust_data(ip_data, read_cust_config_data):
    def __init__(self):
        super(generate_cust_data, self).__init__()

        # Determine the number of cores on the machine
        self.nbr_cores = multiprocessing.cpu_count()

        # Read in the configuration files corresponding to the customer types
        self.read_cust_type_config_files()

        # Create column objects
        self.create_col_obj()

        # Determine a list of countries that do not exist in the sanctions
        # list
        self.gen_cntry_vars()

        # Number of customers to sample from the PEP list
        # Number of customers to be generated
        self.n_customers = self.cust_config_data['n_customers']['value']
        self.n_customers_pep = int(
            self.n_customers*(self.cust_config_data['percent_cust_pep'][
                'value']/100.0))

        # Number of customers to sample from the sanctions list
        self.n_customers_sanc = int(
            self.n_customers*(self.cust_config_data['percent_cust_sanctions'][
                'value']/100.0)
        )

        # Total number of customers to generate data for
        self.tot_customers = self.n_customers + self.n_customers_pep \
            + self.n_customers_sanc

    def read_cust_type_config_files(self):

        # Create a variable to store the different customer types
        self.cust_types = list(self.cust_config_data[
                'customer_types']['value'].keys())

        # Get the config file names corresponding to the customer type
        cust_type_config_filename = {}
        for i in self.cust_types:
            cust_type_config_filename[i] = self.cust_config_data[
                    'customer_types']['value'][i]['filename']

        # Read in the configuration files associated to the different
        # customer types
        # Define a variable to store the customer type specific configurations
        self.cust_type_config_data = {}
        for i in self.cust_types:
            # Read in the JSON config file
            with open(self.cust_config_path +
                      cust_type_config_filename[i]) as json_file:
                self.cust_type_config_data[i] = json.load(json_file)

    def create_col_obj(self):

        # Create variables to store the column names of the FB_CUSTOMER table
        fb_customer_cols = self.cust_config_data[
                'column_names']['value']['fb_customer']['value']
        self.cust_id_col = fb_customer_cols[0]
#        self.first_nm_col = fb_customer_cols[1]
#        self.last_nm_col = fb_customer_cols[2]
        self.display_nm_col = fb_customer_cols[3]
        self.cob_ctry_col = fb_customer_cols[4]
        self.cor_ctry_col = fb_customer_cols[5]
        self.cust_status_col = fb_customer_cols[6]
        self.cust_type_col = fb_customer_cols[7]
        self.income_range_col = fb_customer_cols[8]
        self.annual_income_col = fb_customer_cols[9]
        self.bus_domain_nm_col = fb_customer_cols[10]
        self.jurisdiction_col = fb_customer_cols[11]

        # Create variables to store the column names of the
        # FB_CUST_PHONE_NUM table.
        fb_cust_phone_num_cols = self.cust_config_data[
                'column_names']['value']['fb_cust_phone_num']['value']
        self.phone_id_col = fb_cust_phone_num_cols[0]
        self.phone_num_col = fb_cust_phone_num_cols[1]

        # Create variables to store the column names of the
        # FB_CUST_ADDRESS table.
        fb_cust_address_cols = self.cust_config_data[
                'column_names']['value']['fb_cust_address']['value']
        self.adrs_id_col = fb_cust_address_cols[0]
        self.city_nm_col = fb_cust_address_cols[1]
        self.cntry_cd_col = fb_cust_address_cols[2]
        self.postal_cd_col = fb_cust_address_cols[3]
        self.state_cd_col = fb_cust_address_cols[4]
        self.street_line1_txt_col = fb_cust_address_cols[5]

        # Create a variable to store the sequence of column names
        self.seq_col_nm = [fb_customer_cols[0],
                           fb_customer_cols[3],
                           fb_customer_cols[4],
                           fb_customer_cols[5],
                           fb_customer_cols[6],
                           fb_customer_cols[7],
                           fb_customer_cols[8],
                           fb_customer_cols[9],
                           fb_customer_cols[10],
                           fb_customer_cols[11],
                           fb_cust_address_cols[0],
                           fb_cust_address_cols[1],
                           fb_cust_address_cols[2],
                           fb_cust_address_cols[3],
                           fb_cust_address_cols[4],
                           fb_cust_address_cols[5],
                           fb_cust_phone_num_cols[0],
                           fb_cust_phone_num_cols[1]]

    def gen_cntry_vars(self):

        # Determine the countries that do not exist in the sanctions list
        self.cntry_cd_nonUS_nonSanctions = self.cntry_cd_data[
            ~(np.in1d(self.cntry_cd_data['ISO3166-1-Alpha-3'],
                      self.cntry_sanctions_data[
                              'Sanctions, Countries']))]['ISO3166-1-Alpha-3']\
            .values

    def gen_cust_id(self):

        # # Placed the import statement within the method is because of Ray.
        # # It was throwing errors otherwise.
        # import uuid

        # # Determine the number of records to be assigned to each core
        # cores_use, recs_per_core = nbr_rec_per_core(
        #         self.n_customers, self.nbr_cores)

        # @ray.remote
        # def gen_uuid():
        #     return [str(uuid.uuid4()) for _ in range(recs_per_core)]

        # # Generate the customer ids
        # dummy_cust_ids = ray.get(
        #         [gen_uuid.remote() for _ in range(cores_use)])
        # # Flatten the list of lists
        # cust_ids = [
        #         item for sublist in dummy_cust_ids for item in sublist]

        # Generate customer ids for normal customers
        cust_ids = ["C-"+str(uuid.uuid4()).replace('-', '')
                    for _ in range(self.n_customers)]

        # Add customer ids to the fb_customer dataset
        self.fb_customer = pd.DataFrame(
                np.array(cust_ids), columns=[self.cust_id_col])

        print("DONE GENERATING THE CUSTOMER IDS.")

    def _det_cust_type_counts(self):

        # Determine the count of the various customer types
        self.cust_type_counts = {}
        cust_type_val_counts = self.fb_customer[
                self.cust_type_col].value_counts(dropna=False)
        for i in self.cust_types:
            self.cust_type_counts[i] = cust_type_val_counts[i]

    def _det_cust_type_indices(self):

        # Determine the indices of the various customer types
        self.cust_type_indices = {}
        for i in self.cust_types:
            self.cust_type_indices[i] = np.where(
                    self.fb_customer[self.cust_type_col] == i)[0]

    def gen_cust_types(self):

        # Create a variable to store the percentage of each customer type
        cust_types_probs = []
        for i in self.cust_types:
            cust_types_probs.append(
                    self.cust_config_data[
                            'customer_types']['value'][i]['value']/100.)

        # Generate the customer types based on the specified percentages
        self.fb_customer[self.cust_type_col] = np.random.choice(
                self.cust_types, size=self.n_customers, p=cust_types_probs)

        print("DONE GENERATING THE CUSTOMER TYPES.")

        # Determine the count of the various customer types
        self._det_cust_type_counts()

        # Determine the indices of the various customer types
        self._det_cust_type_indices()

    def _gen_ind_cust_nm(self):

        # # Determine the number of records to be assigned to each core
        # cores_use, recs_per_core = nbr_rec_per_core(
        #         self.n_customers, self.nbr_cores)

        # @ray.remote
        # def gen_nm():
        #     return [fake.name() for _ in range(recs_per_core)]

        # # Generate the customer names
        # dummy_cust_nm = ray.get(
        #         [gen_nm.remote() for _ in range(cores_use)])
        # # Flatten the list of lists
        # cust_nm = [item for sublist in dummy_cust_nm for item in sublist]

        # Generate customer names
        cust_nm = [fake.name() for _ in range(self.n_customers)]

        # Add the customer names to the fb_customer dataframe
        self.fb_customer[self.display_nm_col] = np.array(cust_nm)

        print("DONE GENERATING THE CUSTOMER NAMES FOR CUSTOMER TYPE - \
        INDIVIDUALS.")

    def _gen_org_cust_nm(self, c_type):

        # Having an issue when generating the company names via Ray.
        # Somehow the number of names getting generated is never equal to
        # the current number of customer type ORG in the dataset.
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
        c_type_count = self.cust_type_counts[c_type]
        org_nm = [barnum.create_company_name() for _ in range(c_type_count)]

        # There seems to be a problem when trying to add the organization
        # names to the existing modin series. To resolve the issue its best
        # to duplicate the data in the modin series to a numpy array, then
        # add the organization names to the numpy array and copy the data
        # back to the modin dataframe
        disp_nm_arr = self.fb_customer[self.display_nm_col].values
        disp_nm_arr[self.cust_type_indices[c_type]] = org_nm

        # Add the customer names to the fb_customer dataframe
#        self.fb_customer[self.display_nm_col].where(
#                    org_ind, np.array(self.org_nm), inplace=True)
        self.fb_customer[self.display_nm_col] = disp_nm_arr

        print("DONE GENERATING THE CUSTOMER NAMES FOR CUSTOMER TYPE - \
        ORGANIZATIONS.")

    def gen_cust_nm(self):

        # The below line of code is used if we are able to get one function
        # to generate both ind and org names. But there seems to be an issue
        # with the number of records that are getting generated. Maybe a
        # Ray issue.
        # Create the customer name column with empty values
        # self.fb_customer[self.display_nm_col] = ['']*self.n_customers

        # Generate customer names based on customer type
        for i in self.cust_types:
            if i.lower() in "individual":
                self._gen_ind_cust_nm()
            elif i.lower() in "organization":
                self._gen_org_cust_nm(i)

        print("DONE GENERATING THE CUSTOMER NAMES.")

    def gen_pep_cust_data(self):

        # Generate customer ids for PEP customers
        pep_cust_ids = ["PEP-C-"+str(uuid.uuid4()).replace('-', '')
                        for _ in range(self.n_customers_pep)]

        # Sample customer names and customer types from the PEP data
        pep_sample_data = self.pep_data[['name', 'type']].sample(
            n=self.n_customers_pep, replace=False
        )

        # Add PEP customer ids to the PEP dataframe
        pep_sample_data[self.cust_id_col] = pep_cust_ids

        # Change the customer type to the values defined in the configuration
        # file
        for i in self.cust_types:
            if i.lower() in "individual":
                ind_cust_type_val = i
        pep_sample_data['type'] = np.array(
            [ind_cust_type_val]*self.n_customers_pep)

        # Rename the PEP dataframe columns to the column names defined in
        # the configuration file
        pep_sample_data = \
            pep_sample_data.rename(
                index=str, columns={"name": self.display_nm_col,
                                    "type": self.cust_type_col})

        # Append the PEP dataframe to the parent customer dataframe
        self.fb_customer = pd.concat([self.fb_customer,
                                     pep_sample_data], ignore_index=True,
                                     sort=False)

        print("DONE ADDING PEP NAMES.")

        # Determine the count of the various customer types
        self._det_cust_type_counts()

        # Determine the indices of the various customer types
        self._det_cust_type_indices()

    def gen_watchlist_cust_data(self):

        # Generate customer ids for watchlist customers
        wl_cust_ids = ["WL-C-"+str(uuid.uuid4()).replace('-', '')
                       for _ in range(self.n_customers_sanc)]

        # Sample customer names and customer types from the watchlist data
        wl_sample_data = self.ofac_wl_data[['entity_nm',
                                            'entity_type']].sample(
            n=self.n_customers_sanc, replace=False
        )

        # Add watchlist customer ids to the watchlist dataframe
        wl_sample_data[self.cust_id_col] = wl_cust_ids

        # Change the customer type to the values defined in the configuration
        # file
        for i in self.cust_types:
            if i.lower() in "individual":
                # Determine the indices where customer type is 'individual'
                ind_indices = (wl_sample_data['entity_type'] == "Individual")
                wl_sample_data.loc[ind_indices, 'entity_type'] = i
            elif i.lower() in "organization":
                # Determine the indices where customer type is 'organization'
                org_indices = (
                        wl_sample_data['entity_type'] == "Organization")
                wl_sample_data.loc[org_indices, 'entity_type'] = i

        # Rename the PEP dataframe columns to the column names defined in
        # the configuration file
        wl_sample_data = \
            wl_sample_data.rename(
                index=str, columns={"entity_nm": self.display_nm_col,
                                    "entity_type": self.cust_type_col})

        # Append the PEP dataframe to the parent customer dataframe
        self.fb_customer = pd.concat([self.fb_customer,
                                      wl_sample_data], ignore_index=True,
                                     sort=False)

        print("DONE ADDING WATCHLIST NAMES.")

        # Determine the count of the various customer types
        self._det_cust_type_counts()

        # Determine the indices of the various customer types
        self._det_cust_type_indices()

    # This method can be easily optimized and the computations can be
    # parallelized by using Ray.
    def gen_cust_cob(self):

        # Create a numpy array to store the values for the COB values
        # Assign 'USA' as default values
        cob_arr = np.array(['USA']*self.tot_customers)

        # Loop through each customer type and assign values to COB based
        # on the values provided in the configuration files
        for i in self.cust_types:
            # Check if the percentages add to 100%
            US_pct = self.cust_type_config_data[i]['percent_cust_cob_US'][
                'value']
            nonUS_nonSanctions_pct = self.cust_type_config_data[i][
                'percent_cust_cob_nonUS_nonSanctionCtry']['value']
            if US_pct+nonUS_nonSanctions_pct != 100.0:
                # If it is not equal to 100% then determine the percentage
                # of sanctions countries to be assigned (based on
                # configuration files)
                sanctions_pct = 100.0 - US_pct - nonUS_nonSanctions_pct
            # Determine the number of countires to be sampled for non-USA &
            # non-Sanction countries
            nonUS_nonSanctions_nbr = int(
                self.cust_type_counts[i]*(nonUS_nonSanctions_pct/100.0))
            # Determine the number of countroes to be sampled for sanction
            # countries
            sanctions_nbr = int(self.cust_type_counts[i]*(sanctions_pct/100.0))
            # Let us assign non-USA & non-Sanction countries to the COB array
            # First determine the indices to which we want to assign the
            # values to
            nonUS_nonSanctions_indices = np.random.choice(
                self.cust_type_indices[i],
                nonUS_nonSanctions_nbr,
                replace=False
            )
            # Determine the remaining indices
            remaining_indices = self.cust_type_indices[i][
                ~(np.in1d(self.cust_type_indices[i],
                  nonUS_nonSanctions_indices))]
            # Next, determine the indices we want to assign sanctions countries
            # to
            sanctions_indices = np.random.choice(
                remaining_indices,
                sanctions_nbr,
                replace=False
            )
            # Sample the country values now that we have the indices
            # Sample the non-USA & non-Sanction countries
            cob_arr[nonUS_nonSanctions_indices] = np.random.choice(
                self.cntry_cd_nonUS_nonSanctions,
                nonUS_nonSanctions_nbr,
                replace=True
            )
            # Sample the sanctions countries
            cob_arr[sanctions_indices] = np.random.choice(
                self.cntry_sanctions_data['Sanctions, Countries'].values,
                sanctions_nbr,
                replace=True
            )

        # Add the COB data to the dataframe
        self.fb_customer[self.cob_ctry_col] = cob_arr

        print("DONE GENERATING COUNTRY OF BIRTH.")

    def gen_cust_cor(self):

        # Create a variable to store the values to be assigned to country
        # of residence. Assign the default value - 'USA'
        cor_arr = np.array(['USA']*self.tot_customers)

        # Loop through each customer type to assign the country of residence
        # value defined in the configuration files
        for i in self.cust_types:
            cor_arr[self.cust_type_indices[i]
                    ] = self.cust_type_config_data[i]['residence_ctry_cd'][
                        'value']

        # Add country of residence column to the dataframe
        self.fb_customer[self.cor_ctry_col] = cor_arr

        print("DONE GENERATING COUNTRY OF RESIDENCE.")

    def gen_cust_status(self):

        # Create a variable to store the customer status values. Assign 'A' -
        # Active as the default value
        cust_status = np.array(['A']*self.tot_customers)

        # Generate customer status values
        # Loop through each customer type
        for i in self.cust_types:
            cust_status[self.cust_type_indices[i]] = np.random.choice(
                self.cust_type_config_data[i]['cust_status_cd']['value'],
                self.cust_type_counts[i],
                replace=True,
                p=self.cust_type_config_data[i]['cust_status_prob']['value']
            )

        # Add customer status to the customer dataframe
        self.fb_customer[self.cust_status_col] = cust_status

        print("DONE GENERATING CUSTOMER STATUS.")

    def __gen_annual_income_var(self):

        # Create a variable to store the annual income of the customers
        annual_income = np.zeros(self.tot_customers)

        # Assign indicator values to the 'annual_income' variable. This helps
        # in ensuring that there are no missing values in the annual income
        # variable
        # Assign a variable to indicate 'individual'
        self.annual_income_indv_ind = 0.0
        # Assign a variable to indicate 'organization'
        self.annual_income_org_ind = 1.0
        # Loop through each customer type
        for i in self.cust_types:
            if i.lower() in 'individual':
                annual_income[self.cust_type_indices[i]
                              ] = self.annual_income_indv_ind
            elif i.lower() in 'organization':
                annual_income[self.cust_type_indices[i]
                              ] = self.annual_income_org_ind

        return annual_income

    def gen_annual_income(self):

        # Create annual income variable
        annual_income = self.__gen_annual_income_var()

        # Assign annual income values to each customer record
        # Loop through each customer type
        for i in self.cust_types:
            if i.lower() in 'individual':
                # Determine the number of income brackets defined for customer
                # type 'individuals'
                income_brackets = self.cust_type_config_data[i][
                        'income_brackets']['value']
                nbr_income_brackets = len(income_brackets.keys())
                # Define a variable to track the number of income brackets
                # we are looping through
                count_inc_bracket = 0
                # Number of individuals values need to be assigned to
                nbr_ind = self.cust_type_counts[i]
                # List of indices where customer type is 'individuals'
                indices_indv = self.cust_type_indices[i]
                # Loop through each income bracket, generate values and assign
                # them to the annual income variable
                for j in income_brackets.keys():
                    # Count the number of income brackets we have cycled
                    # through. We do this to ensure that there are no missing
                    # values in the annual income variable
                    count_inc_bracket = count_inc_bracket + 1
                    # Store the income bracket percentage values in variables
                    pcnt_income_bracket_val = income_brackets[j]/100.0
                    # Generate annual income values
                    # Determine the min and max values of the income bracket
                    income_bracket_list = j.split('_')
                    min_val = int(income_bracket_list[0])
                    max_val = int(income_bracket_list[1])
                    if count_inc_bracket != nbr_income_brackets:
                        # Determine the number of records we need to
                        # assign values to
                        nbr_recs = int(pcnt_income_bracket_val * nbr_ind)
                        # Generate income values
                        income_vals = gen_income_vals(min_val,
                                                      max_val, nbr_recs)
                        # Sample the indices corresponding to customer
                        # type 'individual'
                        sample_indices = np.random.choice(indices_indv,
                                                          size=nbr_recs,
                                                          replace=False)
                        # Assign the generated income values to the
                        # sampled indices
                        if len(sample_indices) == len(income_vals):
                            annual_income[sample_indices] = income_vals
                        # Determine the list of unsued indices
                        # First, determine the indices that have
                        # no values assigned
                        indices_indv = np.where(
                            annual_income == self.annual_income_indv_ind)[0]
                        # Determine the number of 'individual' indices left
                        nbr_ind = len(indices_indv)
                    elif count_inc_bracket == nbr_income_brackets:
                        # Determine the new number of 'individual' records
                        # that need to be assigned an annual income value.
                        # For the last income bracket the number of records
                        # to assign values is equal to the number of indices
                        # to which annual income values have not been assigned.
                        # This is done to ensure that there are no missing
                        # values in the 'annual_income' variable
                        nbr_recs = len(indices_indv)
                        # Generate income values
                        income_vals = gen_income_vals(min_val,
                                                      max_val, nbr_recs)
                        # Sample the indices corresponding to customer
                        # type 'individual'
                        sample_indices = np.random.choice(indices_indv,
                                                          size=nbr_recs,
                                                          replace=False)
                        # Assign the generated income values to the
                        # sampled indices
                        if len(sample_indices) == len(income_vals):
                            annual_income[sample_indices] = income_vals
            elif i.lower() in 'organization':
                # Determine the min and max values to be assigned for
                # organization annual income
                min_val = self.cust_type_config_data[i][
                        'income_brackets']['value']['min']
                max_val = self.cust_type_config_data[i][
                        'income_brackets']['value']['max']
                # Generate income values
                nbr_recs = self.cust_type_counts[i]
                income_vals = gen_income_vals(min_val, max_val, nbr_recs)
                # Assign the income values to the indices where customer
                # type is 'organization'
                if len(self.cust_type_indices[i]) == len(income_vals):
                    annual_income[self.cust_type_indices[i]] = income_vals

        # Add customer annual income to the customer dataframe
        self.fb_customer[self.annual_income_col] = annual_income

        print("DONE GENERATING ANNUAL INCOME.")

    def gen_income_range(self):

        # Create variable to store the income range values
        income_range = np.array(['A']*self.tot_customers)

        # Create a variable to store the annual income values
        annual_income_vals = self.fb_customer[self.annual_income_col].values

        # Loop through each customer type
        for i in self.cust_types:
            if i.lower() in 'individual':
                income_range_buckets = self.cust_type_config_data[i][
                        'income_range']['value']
            elif i.lower() in 'organization':
                income_range_buckets = self.cust_type_config_data[i][
                        'income_range']['value']
                for j in income_range_buckets.keys():
                    # Determine the min and max values of the income bracket
                    income_bracket_list = j.split('_')
                    min_val = int(income_bracket_list[0])
                    max_val = int(income_bracket_list[1])
                    # Determine the indices where the annual income values
                    # falls in the range
                    annual_inc_indices = np.where(
                        (min_val <= annual_income_vals) & (
                            annual_income_vals < max_val
                        ))[0]
                    income_range[annual_inc_indices] = income_range_buckets[j]

        # Add customer income range to the customer dataframe
        self.fb_customer[self.income_range_col] = income_range

        print("DONE GENERATING INCOME RANGE.")

    def gen_bus_domain(self):

        # Create a variable to store the values assigned to business domain
        bus_domain = np.array(['A']*self.tot_customers)

        # Loop through each customer type
        for i in self.cust_types:
            if i.lower() in 'individual':
                bus_domain[self.cust_type_indices[i]] = \
                    np.random.choice(self.cust_type_config_data[i][
                            'bus_domain_cd']['value'],
                    size=self.cust_type_counts[i],
                    replace=True)
            elif i.lower() in 'organization':
                bus_domain[self.cust_type_indices[i]] = \
                    np.random.choice(self.cust_type_config_data[i][
                        'bus_domain_cd']['value'],
                    size=self.cust_type_counts[i],
                    replace=True)

        # Add customer business domain to the customer dataframe
        self.fb_customer[self.bus_domain_nm_col] = bus_domain

        print("DONE GENERATING BUSINESS DOMAIN.")

    def gen_jurisdiction(self):

        # Create a variable to store the values assigned to jurisdiction
        jurisdiction = np.array(['USA']*self.tot_customers)

        # Loop through each customer type
        for i in self.cust_types:
            if i.lower() in 'individual':
                jurisdiction[self.cust_type_indices[i]] = \
                    self.cust_type_config_data[i][
                        'jurisdiction_ctry_cd']['value']
            elif i.lower() in 'organization':
                jurisdiction[self.cust_type_indices[i]] = \
                    self.cust_type_config_data[i][
                        'jurisdiction_ctry_cd']['value']

        # Add customer business domain to the customer dataframe
        self.fb_customer[self.jurisdiction_col] = jurisdiction

        print("DONE GENERATING JURISDICTION.")

    def gen_address_id(self):

        # Generate address ids for each customer record
        adrs_id = ["ADR-"+str(uuid.uuid4()).replace('-', '')
                   for _ in range(self.tot_customers)]

        # Add address ids to the fb_address dataset
        self.fb_address = pd.DataFrame(
            np.array(adrs_id), columns=[self.adrs_id_col])

        print("DONE GENERATING THE ADDRESS IDS.")

    def gen_city_nm(self):

        # Generate city name for each customer record
        self.fb_address[self.city_nm_col] = [
            fake.city() for _ in range(self.tot_customers)]

        print("DONE GENERATING THE CITY NAMES.")

    def gen_adrs_cntry_cd(self):

        # Assign country code value to each address record
        self.fb_address[self.cntry_cd_col] = self.fb_customer[
            self.cor_ctry_col].values

        print("DONE GENERATING COUNTRY NAMES FOR EACH ADDRESS.")

    def gen_postal_cd(self):

        # Assign postal code values to each address record
        self.fb_address[self.postal_cd_col] = [
            str(fake.postalcode()) for _ in range(self.tot_customers)]

        print("DONE GENERATING POSTAL CODES.")

    def gen_state_cd(self):

        # Assign state code values to each address record
        self.fb_address[self.state_cd_col] = [
            fake.state() for _ in range(self.tot_customers)]

        print("DONE GENERATING STATE CODES.")

    def gen_street_adrs(self):

        # Assign street code values to each address record
        self.fb_address[self.street_line1_txt_col] = [
            fake.street_address() for _ in range(self.tot_customers)]

        print("DONE GENERATING STREET ADDRESS.")

    def gen_phone_id(self):

        # Generate address ids for each customer record
        phone_id = ["PH-"+str(uuid.uuid4()).replace('-', '')
                    for _ in range(self.tot_customers)]

        # Add phone ids to the fb_phone dataset
        self.fb_phone = pd.DataFrame(
            np.array(phone_id), columns=[self.phone_id_col])

        print("DONE GENERATING PHONE IDS.")

    def gen_phone_number(self):

        # Assign phone numbers
        self.fb_phone[self.phone_num_col] = [
            fake.phone_number() for _ in range(self.tot_customers)
        ]

        print("DONE GENERATING PHONE NUMBERS.")

    def data(self):

        start_time = time.time()

        # Generate customer ids
        self.gen_cust_id()

        # Generate customer types
        self.gen_cust_types()

        # Generate customer names
        self.gen_cust_nm()

        # Add PEP customer data
        self.gen_pep_cust_data()

        # Add watchlist customer data
        self.gen_watchlist_cust_data()

        # Generate customer country of birth
        self.gen_cust_cob()

        # Generate customer country of residence
        self.gen_cust_cor()

        # Generate customer status
        self.gen_cust_status()

        # Generate annual income
        self.gen_annual_income()

        # Generate income range
        self.gen_income_range()

        # Generate business domain
        self.gen_bus_domain()

        # Generate jurisdiction
        self.gen_jurisdiction()

        # Generate address id
        self.gen_address_id()

        # Generate city names
        self.gen_city_nm()

        # Generate address country code
        self.gen_adrs_cntry_cd()

        # Generate postal codes
        self.gen_postal_cd()

        # Generate state codes
        self.gen_state_cd()

        # Generate street address
        self.gen_street_adrs()

        # Generate phone ids
        self.gen_phone_id()

        # Generate phone numbers
        self.gen_phone_number()

        # Combine the customer, address and phone dataframe in to a single
        # dataframe
        self.comb_cust_df = pd.concat([self.fb_customer,
                                       self.fb_address, self.fb_phone],
                                      axis=1)

        # Rearrange the sequence of column names in the combined
        # customer data
        self.comb_cust_df = self.comb_cust_df[self.seq_col_nm]

        # Determine the time taken to generate the customer dataset
        print("Time taken to generate customer data: ", \
            time.time() - start_time, " secs")


if __name__ == '__main__':

    from utils import write_data_to_machine

    # Create an object
    fb_customer_data = generate_cust_data()
    # Generate customer data
    fb_customer_data.data()

    # Write combined customer data to csv file
    write_data_to_machine(fb_customer_data.comb_cust_df,
                          "customer_combined")
