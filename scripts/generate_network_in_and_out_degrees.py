#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:38:59 2019

@author: ryancompton
"""

import os

import pandas as pd
import numpy as np

print("GENERATING IN AND OUT DEGREES FOR GRAPH GENERATION")

data = pd.read_csv(os.path.join("outputs","accounts.csv"))

num_tx = 10 * data.shape[0]
remaining_tx = num_tx

max_tx = 200

in_degrees = {}

offset = 0
total_out = 0
total_in = 0

def gen_in_out_degree(row):
    global offset
    global total_out
    global total_in
    #TODO: Add in functionality for account_type
    #Need to include withdraw limits for savings accounts
    #row["acct_type"]

    out_degree = int(((np.random.power(15)-1)*-1)*200)

    noise = np.random.randint(-10,10) if out_degree > 10 else np.random.randint(-1*out_degree,out_degree+1)

    in_degree = out_degree + noise

    total_out += out_degree
    total_in += in_degree

    return in_degree, out_degree

in_out_series = data.apply(lambda row : gen_in_out_degree(row),axis=1)

data["In-degree"] = pd.Series([x for x,y in in_out_series.values])
data["Out-degree"] = pd.Series([y for x,y in in_out_series.values])


#print("Balancing degrees")
#i = 0
while total_in != total_out:
    offset = total_out - total_in
#    i += 1
#    if i % 100 == 0:
#        print(offset)
    indv  = np.random.randint(0,data.shape[0])
    if offset > 0:
        if data.iloc[indv]["Out-degree"] > 0:

            if offset < data.iloc[indv]["Out-degree"]:
                extra_out = np.random.randint(0,10) if offset > 10 else np.random.randint(0,offset)
            else:
                extra_out = np.random.randint(0,10) if data.iloc[indv]["Out-degree"] > 10 else np.random.randint(0,data.iloc[indv]["Out-degree"])

            data.loc[indv, "Out-degree"] = data.iloc[indv]["Out-degree"] - extra_out

            offset -= extra_out

    #        added_outs = np.random.multinomial(extra_out, np.ones(data.shape[0])/data.shape[0], size=1)[0]

    #        data["Out-degree"] = data["Out-degree"]-added_outs
            total_out -= extra_out

            if offset < data.iloc[indv]["In-degree"]:
                extra_out = np.random.randint(0,10) if offset > 10 else np.random.randint(0,offset)
            else:
                extra_in = np.random.randint(0,10) if data.iloc[indv]["In-degree"] > 10 else np.random.randint(0,data.iloc[indv]["In-degree"]+1)



            data.loc[indv, "In-degree"] = data.iloc[indv]["In-degree"] + extra_in


    #        offset -= extra_out
    #        added_ins = np.random.multinomial(offset, np.ones(data.shape[0])/data.shape[0], size=1)[0]

    #        data["In-degree"] = data["In-degree"]+added_ins
            total_in += extra_in
    else:
        if data.iloc[indv]["In-degree"] > 0:
            offset = total_in - total_out
            if offset < data.iloc[indv]["In-degree"]:
                extra_in = np.random.randint(0,10) if offset > 10 else np.random.randint(0,offset)
            else:
                extra_in = np.random.randint(0,10) if data.iloc[indv]["In-degree"] > 10 else np.random.randint(0,data.iloc[indv]["In-degree"])

            data.loc[indv, "In-degree"]  = data.iloc[indv]["In-degree"] - extra_in

            offset -= extra_in

    #        added_outs = np.random.multinomial(extra_out, np.ones(data.shape[0])/data.shape[0], size=1)[0]

    #        data["Out-degree"] = data["Out-degree"]-added_outs
            total_in -= extra_in


            if offset < data.iloc[indv]["Out-degree"]:
                extra_out = np.random.randint(0,10) if offset > 10 else np.random.randint(0,offset)
            else:
                extra_out = np.random.randint(0,10) if data.iloc[indv]["Out-degree"] > 10 else np.random.randint(0,data.iloc[indv]["Out-degree"]+1)

            data.loc[indv, "Out-degree"]  = data.iloc[indv]["Out-degree"] + extra_out

            total_out += extra_out
    #        offset -= extra_out
    #        added_ins = np.random.multinomial(offset, np.ones(data.shape[0])/data.shape[0], size=1)[0]

    #        data["In-degree"] = data["In-degree"]+added_ins

#        offset = total_in - total_out
#        extra_out = np.random.randint(0,offset)
#        added_outs = np.random.multinomial(extra_out, np.ones(data.shape[0])/data.shape[0], size=1)[0]
#
#        data["Out-degree"] = data["Out-degree"]+added_outs
#        total_out += extra_out
#
#        offset -= extra_out
#        added_ins = np.random.multinomial(offset, np.ones(data.shape[0])/data.shape[0], size=1)[0]
#
#        data["In-degree"] = data["In-degree"]-added_ins
#        total_in -= offset

print(data["In-degree"].describe())
print(sum(data["In-degree"]))

print(data["Out-degree"].describe())
print(sum(data["Out-degree"]))

if sum(data["In-degree"]) == sum(data["Out-degree"]):
    print("Degrees match!")
    print("DONE")
else:
    print("INVALID DATA GENERATION: In and Out Degrees failed to match, see summary stats above to begin tracing the error")

data.to_csv("degree.csv")


