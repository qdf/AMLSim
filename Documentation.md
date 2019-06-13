# Outline

* [AMLSim Overview](#AMLSim-Overview)
* [AMLSim Sample Use](#AMLSim-Sample-Use)
* [Simulation Properties](#Simulation-Properties)
* [Graph Generation Properties](#Graph-Generation-Properties)
* [Transaction Graph Generator](#Transaction-Graph-Generator)
* [Transaction Types](#Transaction-Types)
* [Build Transaction Types](#How-to-build-fraud-transaction-types)
* [Issues/Concerns](#Issues-Concerns)
---
# AMLSim Overview
---
## Java Object Simple Overview
![alt text](https://github.com/qdf/AMLSim/blob/master/AMLSim%20Overview.png "AMLSim Java object simple overview")

The AMLSim object extends an existing inherentence structure within PaySim, by first extending ParameterizedPaySim. PaySim uses the [Mason](https://cs.gmu.edu/~eclab/projects/mason/) Java library to help build Agent-Based Simulations through extending the SimState object. Within SimState is where the tasks are handled through the Schedule object. The schedule object takes in any object that implements the Steppable interface (which the Client superobject does), where a function called step will be called from the scheduler. 

AMLSim also builds up its specialized objects from the client superobject within PaySim. These are the objects acting as the Agents. FraudAccount extends Account, which extends Client. Accounts handle the transactions through an AbstractTransactionModel.

Events within the scheduler are handled as they are inputted, as the scheduler is using a heap to gather the next event. Clients, once called to step by the scheduler, will then enact their next action where an AbstractTransactionModel will assist with handling the transaction.

For fraud type of transactions they are handled with the classes within the amlsim.model.fraud module. Each one handles transactions based on the type of Graphical configuration set for the fraud account. For normal accounts, transactions are handled through the objects within the amlsim.model.normal depending on the model type.

---

# AMLSim Sample Use
## Transaction Simulator (Java)

```bash
sh scripts/build_AMLSim.sh
sh scripts/run_AMLSim.sh [SimulationName] [Steps]
```
- SimulationName: Simulation name
- Steps: Number of steps per simulation

Example:
```bash
sh scripts/run_AMLSim.sh sample 150
```


### Example: generate transaction CSV files from small sample parameter files
Before running the Python script, please check and edit configuration file `prop.ini`.
```ini
[InputFile]
directory = paramFiles/1K
alertPattern = alertPatterns.csv
```

Then, please run transaction graph generator and simulator scripts.
```bash
cd /path/to/AMLSim
python scripts/transaction_graph_generator.py prop.ini paramFiles/1K/accounts.csv paramFiles/1K/degree.csv paramFiles/1K/transactionType.csv
sh scripts/run_AMLSim.sh sample 150
```


## Visualize a transaction subgraph of the specified alert
```bash
python scripts/visualize/plot_transaction_graph.py [TransactionLog] [AlertID]
```
- TransactionLog: Log CSV file path from AMLSim (e.g. `outputs/sample/sample_log.csv`)
- AlertID: An alert ID to be visualized


## Convert the raw transaction log file
```bash
python scripts/convert_logs.py [ConfFile] [TransactionLog]
```
- ConfFile: Configuration ini file for the data conversion (`convert.ini`)
- TransactionLog: Transaction log CSV file under `outputs/(name)/` (e.g. `outputs/sample/sample_log.csv`)

Example: 
```bash
python scripts/convert_logs.py convert.ini outputs/sample/sample_log.csv
```


## Remove all log and image files from `outputs` directory
```bash
sh scripts/clean_logs.sh
```

---
# Simulation Properties

All properties within the amlsim.properties file

---

## PaySim parameters
Notes from AMLSim mention these are to be removed

```
nrOfMerchants=34749
debugFlag=0
saveToDbFlag=0
saveNetwork=0
clientBeta=0
fraudProbability=0.0
numFraudsters=1000
transferLimit=20000000000
logPath=outputs/
paramFileHistory=//outputs//ParamFileHistory
parameterFilePath=//paramFiles//AggregateTransaction.csv
transferMaxPath=//paramFiles//transferMax.csv
balanceHandler=//paramFiles//initialBalanceClients.csv
transferFreqMod=//paramFiles//transferFreq4Mod.csv
transferFreqModInit=//paramFiles//transferFreq4ModInit.csv
```

---

# Graph Generation Properties
All properties within the prop.ini file

---

## General
Random seed value
```
seed = 0
```
Individual transaction amounts, currently uses the preset values from the original AMLSim library. **Need to formulate good limits to these based more realistic amounts.** Currently, transaction amounts are set within scripts/transaction_graph_generator.py where a value is choosen between the min and max set here uniformly. **Additionally need to see if a uniform distribution is the right option here based on real data.**
Minimum individual transaction amount, default is 1
```
default_min_amount = 1
```
Maximum individual transaction amount, default is 10000
```
default_max_amount = 10000
```
Total number of simulation steps, preset is 200. **Is 200 enough?**
```
total_step = 200
```
## Base
Accounts with larger degree than this threshold will be selected as alert accounts. 
Questions:
* **Is this a good rule to have?** 
* **Is having a large degree producing large amounts of false alerts?**
* **Need to check the accuracy of this rule**
```
degree_threshold = 10
```
## HighRisk
High-risk business types and countries (comma-separated). Currently set to none, however easy to incorporate autogenerated data of organizations from customer segmentation work.
```
business = ""
countries = ""
```
## InputFile
Input file and directory path. Currenlty set to one of the samples within the AMLSim repo. Can use this for now, but would be good to incorporate our generated data into this. 
**Need to build a script that formats our data in the expected format of these examples**
```
directory = paramFiles/1m
alertPattern = alertPatterns.csv

is_aggregated = True
```
## OutputFile
Output and intermediate file and directory path. For now, no reason to change these unless we want to change the directory structure. This will overwrite some existing files, so back up prior work before running additional simulations.
```
directory = outputs
transactions = transactions.csv
accounts = accounts.csv
alert_members = alert_members.csv
counter_log = tx_count.csv
diameter_log = diameter.csv
```
## PlotFile
Output file for visualizations. Also no reason to change these at the moment, unless needed to change the directory structure. Also these are outputs meant for the visualization scripts for the most part.
```
degree = deg.png
wcc = wcc.png
alert = alert.png
count = count.png
clustering = cc.png
diameter = diameter.png
```

---

# Transaction Graph Generator
Documentation of the python script transaction_graph_generator.py within the scripts directory.

---

# Transaction Types
Default transaction types are already provided, all transaction types are a subclass of the AbstractTransactionModel.

## Normal Transactions
Normal transactions are those enacted by agents who are Not considered to be fraud accounts.

### SingleTransactionModel
*Object Location: amlsim.model.normal.SingleTransactionModel*

Conducts a single transaction at a random time point (computed through uniformly random distribution) to a random destination of that account. Amount is determined by the balance of the account.

### FanOutTransactionModel
*Object Location: amlsim.model.normal.FanOutTransactionModel*

Conducts multiple transaction from one account to all destinations listed within that account. The amount is determined through the balance divided by the number of destinations. This is only enacted if the step within the simulation is determined to be a valid step for that account (determined through randomization of generateDiff function within the AbstractTransactionModel object).

### FanInTransactionModel
*Object Location: amlsim.model.normal.FanInTransactionModel*

Conducts multiple transactions from multiple accounts to one destination listed within that account (inverse of FanOutTransactionModel). Amount is determined through dividing the total amount of the accounts from the sending accounts and dividing that by the number of destinations (primarily will be 1, haven't seen a case otherwise yet). 

### MutualTransactionModel
*Object Location: amlsim.model.normal.MutualTransactionModel*

Conducts a reciprocal transaction (transaction previously made to this account). Amount is determined to be the account balance. Transactions only occur if the step in the simulation is determined to be a valid step. Valid steps are computed through taking the current step of the simulation minus the start step of the account (typically a range of -10 to 0 as this is randomly determined), then the modulus of that value by the INTERVAL (INTERVAL is hard coded to 10). If that value is Not equal to 0, then the step is considered valid (steps are only invalid 1 in every 10 steps, as set by the INTERVAL).  

### ForwardTransactionModel
*Object Location: amlsim.model.normal.ForwardTransactionModel*

Conducts a simple transaction to all accounts listed as a destination within the account. The documentation lists this type as conducting a transaction after recieving a transaction from another account, however the implementation doesn't seem to follow through this (**Need to verify this**). Transactions only occur if the step in the simulation is determined to be a valid step. Valid steps are computed through taking the current step of the simulation minus the start step of the account (typically a range of -10 to 0 as this is randomly determined), then the modulus of that value by the INTERVAL (INTERVAL is hard coded to 10). If that value is equal to 0, then the step is considered valid (steps are only valid 1 in every 10 steps, as set by the INTERVAL).

Only difference between this transaction model and the SingleTransactionModel is that this model will repeat through the simulation, while a SingleTransactionModel will only occur once.

### PeriodicalTransactionModel
*Object Location: amlsim.model.normal.PeriodicalTransactionModel*

Conducts scheduled transactions from one account to others as set by a PERIOD hard coded value. PERIOD is used to check if the simulation is in a valid step to conduct the transaction. While the documentation lists this type as conducting sending money to neighbors periodically, the code doesn't seem to be conducting anything that different from a Mutual or Forward TransactionModel, except for the number of destinations (**Need to verify this**). Valid steps are computed through a similar function as previous TransactionModels, however instead this function uses PERIOD instead of INTERVAL (both are set to 10 though).

### EmptyModel
*Object Location: amlsim.model.normal.EmptyModel*

Doesn't do anything

## Fraud Transactions
Fraud transactions are those enacted by agents who are considered to be fraud accounts.

### FraudTransactionModel
*Object Location: amlsim.model.fraud.FraudTransactionModel*



### BipartiteTransactionModel
*Object Location: amlsim.model.fraud.BipartiteTransactionModel*



### FanOutTransactionModel
*Object Location: amlsim.model.fraud.FanOutTransactionModel*



### FanInTransactionModel
*Object Location: amlsim.model.fraud.FanInTransactionModel*


### CycleTransactionModel
*Object Location: amlsim.model.fraud.CycleTransactionModel*



### RandomTransactionModel
*Object Location: amlsim.model.fraud.PeriodicalTransactionModel*



### StackTransactionModel
*Object Location: amlsim.model.fraud.StackTransactionModel*


---

# How to build fraud transaction types

---





# Issues Concerns

---

## Random Assumptions
Many of the processes or decisions being made throughout the simulation is random, i.e. use a uniform distribution to choose various features or properties of the agents. Those in **bold** need to have better justifications.

Found random uses:
* **Agent start step (within Account)**
* Amount of cash transactions (within CashInModel and CashOutModel)
* Target step of a single normal transaction (within SingleTransactionModel)

## Simulation Decisions
Hard coded decision are also littered throughout the sim, these need to have valid justifications as to why they are set.

Found hard coded values:
* Model transactions are the balance spread out to the number of destinations (this can be seen within any object that extends the AbstractTransactionModel, best seen in FanIn and FanOutTransaction)
* Default transaction interval is set to 10 (seen in AbstractTransactionModel)
* Flunctuation of transactions is set to 2 (seen in AbstractTransactionModel)
* Amount of transaction for SingleTransactionModel is set to the amount of the balance of the account
