#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:38:59 2019

@author: ryancompton
"""

import os

import pandas as pd
import numpy as np

print("CONVERTING ACCOUNTS TO AMLSIM FORMATTED ACCOUNTS")

file_path = os.path.join("output_datasets")

files = [os.path.join(file_path,x) for x in os.listdir(file_path) if "account" in x]

latest_account_csv = max(files,key=os.path.getctime)

data = pd.read_csv(latest_account_csv)

def random_min(row):
    return np.random.randint(100,401)

def random_max(row):
    return row["min_balance"] + np.random.randint(100,401)

data["min_balance"] = data.apply(lambda row : random_min(row),axis=1)

data["max_balance"] = data.apply(lambda row : random_max(row),axis=1)

data.to_csv("accounts.csv")
print("DONE")
