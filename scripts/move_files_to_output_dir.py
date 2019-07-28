#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 14:31:43 2019

@author: ryancompton
"""

import os
from shutil import copyfile

import barnum

from datetime import datetime
from random import randrange
from datetime import timedelta

import pandas as pd
import numpy as np

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

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

tx_data = pd.read_csv(os.path.join(output_dir,"cust_acct_tx_generation_log.csv"))

acct_cust_dict = {record["account_id"]:record for record in acct_data.to_dict('records')}
#cust_acct_dict = {record["customer_id"]+:record for record in acct_data.to_dict('records')}

d1 = datetime.strptime("1/1/2017", "%m/%d/%Y")
d2 = datetime.strptime("1/1/2019", "%m/%d/%Y")

start_date = random_date(d1,d2)

num_days = tx_data["step"].max()

date_map = {i:start_date+timedelta(days=i) for i in range(num_days+1)}


print("TRANFERRING CUSTOMER ID TO TX LOG")
tx_data["orig_cust_id"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["primary_cust_id"],axis=1)
print("DONE")
print("TRANFERRING BENIFACTOR ID TO TX LOG")
tx_data["ben_cust_id"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["ben_cust_id"],axis=1)
print("DONE")

new_wire_tx = pd.DataFrame(columns=[
            "orig_nm",
            "orig_cust_id",
            "orig_acct_id",
            "orig_bank_nm",
            "orig_cntry_cd",
            "ben_nm",
            "ben_bank_nm",
            "ben_cntry",
            "ben_instr_txt",
            "credit_or_debit",
            "txn_amt",
            "transfer_type",
            "transfer_dt",
            "txn_ref",
            "ben_cust_id",
            "ben_acct_id"
        ])

bank_names = [barnum.create_company_name() for i in range(30)]
    
new_wire_tx["orig_nm"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["display_nm"],axis=1)
new_wire_tx["orig_cust_id"] = tx_data["orig_cust_id"]
new_wire_tx["orig_acct_id"] = tx_data["nameOrig"]
new_wire_tx["orig_bank_nm"] = np.random.choice(bank_names)
new_wire_tx["orig_cntry_cd"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["cntry_cd"],axis=1)

new_wire_tx["ben_nm"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["display_nm"],axis=1)
new_wire_tx["ben_bank_nm"] = np.random.choice(bank_names)
new_wire_tx["ben_cntry"] = tx_data.apply(lambda row : acct_cust_dict[row["nameOrig"]]["cntry_cd"],axis=1)
new_wire_tx["ben_instr_txt"] = "TRANSFER"

new_wire_tx["credit_or_debit"] = "DEBIT"
new_wire_tx["txn_amt"] = tx_data["amount"]
new_wire_tx["transfer_type"] = tx_data["type"]
new_wire_tx["transfer_dt"] = tx_data.apply(lambda row : date_map[row["step"]],axis=1)
new_wire_tx["txn_ref"] = pd.series(range(1,tx_data.shape[0]+1))
new_wire_tx["ben_cust_id"] = tx_data["ben_cust_id"]
new_wire_tx["ben_acct_id"] = tx_data["nameOrig"]




print("WRITING NEW LOGS")
tx_data.to_csv(os.path.join(output_dir,"cust_acct_tx_generation_log.csv"))
new_wire_tx.to_csv(os.path.join(output_dir,"wire_txn_data.csv"))
print("DONE")
