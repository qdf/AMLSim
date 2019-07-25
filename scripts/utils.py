#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 13:58:18 2019

@author: ankurmanikandan
"""

from __future__ import division

from random import randrange
from datetime import timedelta
from time import gmtime, strftime

import numpy as np
from scipy.stats import truncnorm


def write_data_to_machine(df, file_name):
    """Function to write data to machine.

    Parameters
    ----------
    df : pandas dataframe
        dataframe you wish to write to the machine
    file_name : string
        the filename you would like for the dataset
    """

    output_directory = "output_datasets/"
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    comb_file_name = file_name + "_" + current_time
    df.to_csv(output_directory + comb_file_name + ".csv", index=False)
    print("Done writing " + output_directory + comb_file_name + ".csv")


def write_text_to_machine(STR, file_name):
    """Function to write generated STR to machine.

    Parameters
    ----------
    STR : string
       the STR generated from  the suspicious transactions
    file_name : string
       the filename you would like for the dataset
    """

    STR_directory = "STR/"
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    comb_file_name = file_name + "_" + current_time
    textfile = open(STR_directory + comb_file_name + '.txt', 'w')
    textfile.write(STR)
    textfile.close()


def _allocate_money(
        tot_fund=1010,
        num_txn=10,  # num of transactions
        prop_round_amount=.4,  # proportion of aound amount transactions
        max_limit=None,
        denomination=None,
        lambda_base=30):
    """Allocate the amount of money to a number of transactions.

    Parameters
    ----------
    tot_fund : integer
        total amount of money flows in/out an account
    num_txn : integer
        num of transactions
    prop_round_amount : float
        proportion of aound amount transactions
    denomination : list of integers OR None.
        The denominations that to be generated.
    lambda_base : float
        A tuning parameter for the variance of the amount of transactions
    max_limit : float OR None
        The limit of the maximum amount of the transactions

    Returns
    -------
    A list of transaction amounts.
    """
    # generate probabilities over the transactions
    prob_vec = np.random.dirichlet([lambda_base * np.sqrt(num_txn)] * num_txn,
                                   1)
    if denomination is None:
        if max_limit is None:
            # Allocate the total fund to the transactions according the probabilities
            # defined above
            each_txn_round = np.random.multinomial(tot_fund,
                                                   prob_vec.flatten(), 1)
        else:
            # Allocate the total fund to the transactions according the probabilities
            # defined above
            each_txn_round = np.random.multinomial(tot_fund,
                                                   prob_vec.flatten(), 15)
        # Determine which transactions have round amount
        ind_non_round = np.random.choice(
            num_txn,
            np.random.binomial(num_txn, 1 - prop_round_amount, 1),
            replace=False)
        # Generate a small non-integer number for the transactions
        # that are not round amount
        txn_noise = np.zeros(num_txn)
        txn_noise[ind_non_round] = np.random.normal(size=len(ind_non_round))
        # Add the small non-integer numbers to the non round amount transactions
        each_txn = each_txn_round + txn_noise
    # If denomination is not None, then certain denominations will be used.
    elif len(denomination) > 1:
        each_txn = []
        denomination.sort()
        # loop through all the denominations.
        for i in range(1, len(denomination)):
            num_denomination = np.ceil((tot_fund / len(denomination))\
                                       //denomination[i]).astype(int)
            each_txn = each_txn + [denomination[i]] * num_denomination
        each_txn = each_txn + \
                   [denomination[0]]*int((tot_fund - np.sum(each_txn))
                                      //denomination[0])
        each_txn = np.array([each_txn])
    else:
        if max_limit is None:
            # number of 20 dollar denominations
            num_of_20bills = np.random.multinomial(tot_fund // 20,
                                                   prob_vec.flatten(), 1)
        else:
            # number of 20 dollar denominations
            num_of_20bills = np.random.multinomial(tot_fund // 20,
                                                   prob_vec.flatten(), 15)
        # generate the 20 dollar denominations for each transactions.
        each_txn = num_of_20bills * 20
    # remove the rows with transactions larger or equal to the maximum limit
    if max_limit is not None:
        ind_no_exceed = np.argwhere((each_txn >= max_limit).sum(axis=1) == 0)
        if ind_no_exceed.shape[0] == 0:
            raise RuntimeError('Some of the transactions exeeds the limit' \
                               'of transaction amount.')
        # pick the transactions that don't exceed the maximum transaction limit.
        each_txn = each_txn[ind_no_exceed[0]]
        # ind_exceed_max = each_txn >= max_limit
        # txn_exceed_max = each_txn[ind_exceed_max]
        # each_txn[ind_exceed_max] = txn_exceed_max/2
        # each_txn = np.append(each_txn,txn_exceed_max - each_txn[ind_exceed_max])
        # if (each_txn >= max_limit).any():
        #     raise RuntimeError('Some of the transactions exeeds the limit' \
        #     'of transaction amount.')
    #     if denomination is not None:
    #         raise RuntimeError('max_limit has not been implemented for' \
    #         'transactions w/ denomination restrict.')
    # # in case sum transactions exceed the maximum amount allowed
    # if max_limit is not None:
    # find the allocation, for which no txn exceeds max_limit.
    return each_txn


def _random_date(start, end):
    """This function will return a random datetime between two datetime
    objects.

    Parameters
    ----------
    start: datetime
           start date-time
    end: datetime
         end date-time

    Returns
    -------
    rand_datetime: datetime object
                   a random date time
    """

    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    rand_datetime = start + timedelta(seconds=random_second)

    return rand_datetime


def __get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

def gen_income_vals(min_val, max_val, nbr_recs):

    # Determine the mean of the distribution
    mean_income = (min_val + max_val)/2.0

    # Determine the standard deviation of the income bracket distribution
    sd_income = (min_val + max_val)/10.0

    # Define the normal distribution with the parameters
    X = __get_truncated_normal(
        mean=mean_income, sd=sd_income,
        low=min_val, upp=max_val)

    # Generate income values
    income_vals = X.rvs(nbr_recs).astype(int)

    return income_vals
