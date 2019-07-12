#!/usr/bin/env bash

python scripts/generate_customer_data.py
python scripts/generate_account_data.py

python scripts/convert_generated_accounts_to_aml_accounts.py
python scripts/generate_network_in_and_out_degrees.py

echo "GENERATING GRAPH"
python scripts/transaction_graph_generator.py aml_prop.ini accounts.csv degree.csv paramFiles/transactionType.csv paramFiles/alertPatterns.csv
echo "DONE"

echo "RUNNING AMLSIM"
java -XX:+UseConcMarkSweepGC -XX:ParallelGCThreads=2 -Xms2g -Xmx30g -cp "jars/*:bin" amlsim.AMLSim -file amlsim.properties -for 150 -r 1 -name cust_acct_tx_generation

python scripts/move_files_to_output_dir.py

echo "DATA GENERATION COMPLETE"
echo "DATA LOCATED WITHIN outputs/cust_acct_tx_generation"
