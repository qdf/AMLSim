#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 14:31:43 2019

@author: ryancompton
"""

import os
from shutil import copyfile

import pandas as pd

output_dir = os.path.join("outputs","cust_acct_tx_generation")

file_path = os.path.join("output_datasets")

acct_files = [os.path.join(file_path,x) for x in os.listdir(file_path) if "account" in x]

latest_account_csv = max(acct_files,key=os.path.getctime)

copyfile(latest_account_csv, os.path.join(output_dir,latest_account_csv.split(os.sep)[-1].split(" ")[0]+".csv"))

cust_files = [os.path.join(file_path,x) for x in os.listdir(file_path) if "customer" in x]

latest_cust_csv = max(cust_files,key=os.path.getctime)

copyfile(latest_cust_csv, os.path.join(output_dir,latest_cust_csv.split(os.sep)[-1].split(" ")[0]+".csv"))

copyfile("transaction_graph.pkl",os.path.join(output_dir,"transaction_graph.pkl"))

acct_data = pd.read_csv(latest_account_csv)

tx_data = pd.read_csv(output_dir,"cust_acct_tx_generation_log.csv")

acct_cust_dict = {record["account_id"]:record for record in acct_data.to_dict('records')}

tx_data["orig_cust_id"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["primary_cust_id"])

tx_data["ben_cust_id"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["ben_cust_id"])

tx_data.to_csv(output_dir,"cust_acct_tx_generation_log.csv")

