from configparser import ConfigParser
import networkx as nx
import numpy as np
import itertools
import random
import csv
import os
import sys
import pickle

alert_types = {"fan_out":1, "fan_in":2, "cycle":3, "bipartite":4, "stack":5, "dense":6}  # Pattern name and model ID

# function to create and populate the alertPatterns.csv file
def generate_alertPatterns_file():
  
#Calculating each number of alert patterns to be generated
    count =0
    count = int (len(open('outputs/accounts.csv').readlines())/100)
    
    schedule_id=2
    number_min_accounts = 7
    number_max_accounts = 10
    min_aggregate_amount = 100
    max_aggregate_amount = 1000
    min_individual_amount = 10
    max_individual_amount = 100
    min_amount_difference = 20
    max_amount_difference = 100
    min_period = 10
    max_period = 20
    amount_rounded =0.5
    orig_country = bene_country = orig_business = bene_business = 'TRUE'
    is_fraud = 'TRUE'

    with open('paramFiles/alertPatterns.csv','w') as csvfile:

    	filewriter = csv.writer(csvfile)
    	filewriter.writerow(['count','type',
	  		'schedule_id','accounts',
	  		'individual_amount','aggregated_amount',
	  		'transaction_count','amount_difference',
	  		'period','amount_rounded',
	  		'orig_country','bene_country',
	  		'orig_business','bene_business','is_fraud'])

    	for i in alert_types.keys():
    		number_accounts = random.randint(number_min_accounts,number_max_accounts+1)
    		agg_amount = random.randint(min_aggregate_amount,max_aggregate_amount)
    		individual_amount = random.randint(min(min_aggregate_amount,min_individual_amount),min(max_individual_amount,agg_amount))
    		transaction_count = number_accounts * random.randint(2,5)
    		amount_difference = random.randint(min_amount_difference,max_amount_difference)
    		period = random.randint(min_period,max_period)

    		filewriter.writerow([count,i,schedule_id,number_accounts,
	  			individual_amount,agg_amount,
	  			transaction_count, amount_difference, 
	  			period, amount_rounded,
	  			orig_country,bene_country,
	  			bene_country,bene_business,is_fraud])





def main():
	generate_alertPatterns_file()

if __name__ == "__main__":
	main()



