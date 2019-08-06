# Outline

* [AMLSim Overview](#AMLSim-Overview)
* [AMLSim Sample Use](#AMLSim-Sample-Use)
* [Simulation Properties](#Simulation-Properties)
* [Graph Generation Properties](#Graph-Generation-Properties)
* [Transaction Graph Generator](#Transaction-Graph-Generator)
* [Transaction Types](#Transaction-Types)
* [Build Transaction Types](#How-to-build-fraud-transaction-types)
* [TODO](#TODO)
* [Issues/Concerns](#Issues-Concerns)

* CRICTICAL 
    * **FIX NEEDED: IGNORE TRANSACTION AMOUNTS UNTIL TRANSACTION AMOUNT FUNCTION IS FIXED** Look at [Issues/Concerns](#Issues-Concerns) for more details

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

![alt text](https://github.com/qdf/AMLSim/blob/master/AMLSim%20Transaction%20Object%20Hierarchy.jpg "AMLSim Transaction object overview")


## Normal Transactions
Normal transactions are those enacted by agents who are Not considered to be fraud accounts.

### SingleTransactionModel
*Object Location: amlsim.model.normal.SingleTransactionModel*

![alt text](https://user-images.githubusercontent.com/7017528/51157051-86277b80-18c1-11e9-930a-e2f763f446f9.png "Single Transaction Normal")

Conducts a single transaction at a random time point (computed through uniformly random distribution) to a random destination of that account. Amount is determined by the balance of the account.

AMLSim TODO List for updating single transactions:
Need to answer the following questions and update this model

* In the case of individual persons, people buy living goods every day with a debit card or credit card, send a living cost to their family with WIRE transaction on a monthly basis. There should be recurring behaviors.
* In the case of business accounts, the amount should be larger than individual accounts. In the case of car dealers, they buy used cars and re-sell them. In that case, their transaction amount is larger and might be fluctuated based on their business situations.
* In summary, each transaction amount and transaction frequency vary depending on whether it is individual or business.


### FanOutTransactionModel
*Object Location: amlsim.model.normal.FanOutTransactionModel*

![alt text](https://user-images.githubusercontent.com/7017528/51157052-86277b80-18c1-11e9-8734-cc06ec9f6883.png "FanOut Transaction Normal")

Conducts multiple transaction from one account to all destinations listed within that account. The amount is determined through the balance divided by the number of destinations. This is only enacted if the step within the simulation is determined to be a valid step for that account (determined through randomization of generateDiff function within the AbstractTransactionModel object).

### FanInTransactionModel
*Object Location: amlsim.model.normal.FanInTransactionModel*

![alt text](https://user-images.githubusercontent.com/7017528/51157053-86277b80-18c1-11e9-9b60-e2fb7c1e0860.png "FanIn Transaction Normal")

Conducts multiple transactions from multiple accounts to one destination listed within that account (inverse of FanOutTransactionModel). Amount is determined through dividing the total amount of the accounts from the sending accounts and dividing that by the number of destinations (primarily will be 1, haven't seen a case otherwise yet). 

### MutualTransactionModel
*Object Location: amlsim.model.normal.MutualTransactionModel*

![alt text](https://user-images.githubusercontent.com/7017528/51157054-86c01200-18c1-11e9-920e-c3df99ea2e13.png "Mutual Transaction Normal")

Conducts a reciprocal transaction (transaction previously made to this account). Amount is determined to be the account balance. Transactions only occur if the step in the simulation is determined to be a valid step. Valid steps are computed through taking the current step of the simulation minus the start step of the account (typically a range of -10 to 0 as this is randomly determined), then the modulus of that value by the INTERVAL (INTERVAL is hard coded to 10). If that value is Not equal to 0, then the step is considered valid (steps are only invalid 1 in every 10 steps, as set by the INTERVAL).  

### ForwardTransactionModel
*Object Location: amlsim.model.normal.ForwardTransactionModel*

![alt text](https://user-images.githubusercontent.com/7017528/51157055-86c01200-18c1-11e9-943f-f7885c5f4085.png "Forward Transaction Normal")

Conducts a simple transaction to all accounts listed as a destination within the account. The documentation lists this type as conducting a transaction after recieving a transaction from another account, however the implementation doesn't seem to follow through this (**Need to verify this**). Transactions only occur if the step in the simulation is determined to be a valid step. Valid steps are computed through taking the current step of the simulation minus the start step of the account (typically a range of -10 to 0 as this is randomly determined), then the modulus of that value by the INTERVAL (INTERVAL is hard coded to 10). If that value is equal to 0, then the step is considered valid (steps are only valid 1 in every 10 steps, as set by the INTERVAL).

Only difference between this transaction model and the SingleTransactionModel is that this model will repeat through the simulation, while a SingleTransactionModel will only occur once.

### PeriodicalTransactionModel
*Object Location: amlsim.model.normal.PeriodicalTransactionModel*

![alt text](https://user-images.githubusercontent.com/7017528/51157056-86c01200-18c1-11e9-8d78-1f06df968f06.png "Periodic Transaction Normal")

Conducts scheduled transactions from one account to others as set by a PERIOD hard coded value. PERIOD is used to check if the simulation is in a valid step to conduct the transaction. While the documentation lists this type as conducting sending money to neighbors periodically, the code doesn't seem to be conducting anything that different from a Mutual or Forward TransactionModel, except for the number of destinations (**Need to verify this**). Valid steps are computed through a similar function as previous TransactionModels, however instead this function uses PERIOD instead of INTERVAL (both are set to 10 though).

### EmptyModel
*Object Location: amlsim.model.normal.EmptyModel*

Doesn't do anything

## Fraud Transactions
Fraud transactions are those enacted by agents who are considered to be fraud accounts.

### FraudTransactionModel
*Object Location: amlsim.model.fraud.FraudTransactionModel*

Main class to handle Fraud transaction types.


### BipartiteTransactionModel
*Object Location: amlsim.model.fraud.BipartiteTransactionModel*

![alt text](https://camo.githubusercontent.com/a8c0947f94abe81776a32ce880e5107aa96315c2/68747470733a2f2f64326d787565667165616137736a2e636c6f756466726f6e742e6e65742f735f333743433344443744303435344436433433373939353332354136433538424142413135414337454335383445333136303030333633314445374444333735455f313534363835363138373135365f696d6167652e706e67 "Bipartite Transaction Fraud")

Conducts a fraud transaction between the list of accounts within an Alert group. The first half of the list of members within the Alert group are considered the senders and the second half is the receivers. Amounts are determined at random from the simulation object (which has set minimums and maximums for transctions). 

### FanOutTransactionModel
*Object Location: amlsim.model.fraud.FanOutTransactionModel*

![alt text](https://camo.githubusercontent.com/ba715a70e51e837309b91cd57e5c81a5c8ac57b7/68747470733a2f2f64326d787565667165616137736a2e636c6f756466726f6e742e6e65742f735f333743433344443744303435344436433433373939353332354136433538424142413135414337454335383445333136303030333633314445374444333735455f313534363835363036303831395f696d6167652e706e67 "FanOut Transaction Fraud")

Conducts a fraud transaction from one account to many accounts. Accounts sent to are determined by those within the Alert group. The amount is determined randomly through the simulation object and then split to all destination accounts. This transaction model uses a private scheduler to determine the simulation steps in which these transactions occur. There are three types of scheudling: *SIMULATNEOUS* (Conduct all transactions within the same step), *FIXED_INTERVAL* (Conduct transactions sequentially through a computed interval or batch, order is determined through order within Alert list of members), *RANDOM_RANGE* (Conducts transactions randomly as determined through a random function). Amounts are determined at random from the simulation object (which has set minimums and maximums for transctions). 

### FanInTransactionModel
*Object Location: amlsim.model.fraud.FanInTransactionModel*

![alt text](https://camo.githubusercontent.com/1f9ef1295218020d9e3d4a27a34cc6ef365e2636/68747470733a2f2f64326d787565667165616137736a2e636c6f756466726f6e742e6e65742f735f333743433344443744303435344436433433373939353332354136433538424142413135414337454335383445333136303030333633314445374444333735455f313534363835363039373632305f696d6167652e706e67 "FanIn Transaction Fraud")

Conducts a fraud transaction from multiple accounts to one account. Accounts involved are those within the same Alert group. This also contains a private scheduler for when such transaction occur. There are three types of scheudling: *SIMULATNEOUS* (Conduct all transactions within the same step), *FIXED_INTERVAL* (Conduct transactions sequentially through a computed interval or batch, order is determined through order within Alert list of members), *RANDOM_RANGE* (Conducts transactions randomly as determined through a random function). Amounts are determined at random from the simulation object (which has set minimums and maximums for transctions). 

### CycleTransactionModel
*Object Location: amlsim.model.fraud.CycleTransactionModel*

![alt text](https://camo.githubusercontent.com/cc5bbe727a7f5104f3acb2d1f6dfc8d80340ca04/68747470733a2f2f64326d787565667165616137736a2e636c6f756466726f6e742e6e65742f735f333743433344443744303435344436433433373939353332354136433538424142413135414337454335383445333136303030333633314445374444333735455f313534363835363135343735315f696d6167652e706e67 "Cycle Transaction Fraud")

Conducts a fraud transaction that is cyclical between multiple accounts. Accounts that are part of the cycle are determined through the order they are within the Alert group list. Similar to FanIn and FanOut transactions there is a private scheduler for when such transaction occur. There are three types of scheudling: *FIXED_INTERVAL* (Conduct transactions sequentially through a computed interval or batch, order is determined through order within Alert list of members), *RANDOM_INTERVAL* (Conducts transactions randomly as determined through a random function), *UNORDERED* (All transactions are conducted at random). Amounts are determined at random from the simulation object (which has set minimums and maximums for transctions). 

### RandomTransactionModel
*Object Location: amlsim.model.fraud.PeriodicalTransactionModel*

Conducts a fraud transaction from a single *Subject* account from within the Alert group. This subject account will randomly conduct a transaction to one of its neighbors. Amounts are determined at random from the simulation object (which has set minimums and maximums for transctions) divided by the number of possible destinations (neighbors).

### StackTransactionModel
*Object Location: amlsim.model.fraud.StackTransactionModel*

![alt text](https://camo.githubusercontent.com/7d7a87cc756af5dc7e3172cce71ecfcc77ede460/68747470733a2f2f64326d787565667165616137736a2e636c6f756466726f6e742e6e65742f735f333743433344443744303435344436433433373939353332354136433538424142413135414337454335383445333136303030333633314445374444333735455f313534363835363231383739355f696d6167652e706e67 "Stack Transaction Fraud")

Conducts a series of fraud transactions between three sets of accounts. The first set sends to an intermediate group which then sends to the remaining third of accounts. Each account is a part of the same Alert group. Amounts are first determined at random from the simulation object (which has set minimums and maximums for transctions), but then multiplied by the amount of beginning and intermediate accounts (this is the amount that gets transfered in the first set of transactions), the second amount is determined through dividing that first amount by how many accounts are involved in the second set of transactions. 

---

# How to build fraud transaction types
Building a new transaction type can be done through the following (**CAUTION: This process has not been tested and is currently based on code walk + read throughs**):

1. Build a new class which has either the FraudTransactionModel or AbstractTransactionModel as the super class (determined through if you want to build a fraud or normal transaction). Please place this transaction in the appropriate module (Fraud transaction types go into amlsim.model.fraud, while normal transactions go into amlsim.model.normal). 
2. Within transaction classes, a getType() function is needed along with a sendTransactions() function, both need to override the super class function. sendTransaction() determines the logic behind the transaction so define this to handle the pattern you have determined is needed.
3. Add transaction type to the transaction model IDs within the AbstractTransactionModel, make sure there is a distinguishable name for this new transaction (try to make it stand out compared to others, i.e. don't name it forward...). If you are adding a Fraud transaction model, then add this to the FraudTransaction type and don't add to the AbstractTransactionModel.
4. Add transaction case to the Account or FraudAccount class (determined by if you are making a Fraud transaction type or Normal transaction type). This is within each constructor, you should see a switch statement with other transaction types being initialized.
5. Add transaction type to the Python script transaction_graph_generator.py within the self.alert_types dictionary in the __init__ function of the TransactionGenerator. 
6. Build the subgraph within the add_alert_pattern function, first add a conditional with pattern_type == "<type_name>", then construct a subgraph in a similar fashion to existing pattern types (fan_in, fan_out, and bipartite are good simple examples, look at dense, mixed, stack, and cycle for more complex examples).
6. Done (**Need to verify this**)!

---


# TODO

## General Additions
* Output file naming conventions
* Additional Account for Businesses
    * Maybe new account/transaction model that inherits from abstractTXmodel or clients
* Multi-institutions
* New Transaction Types
* Have goals of clients and account, help set logic of why they are conducting the transactions they are
* Avoid hard 

## Distributions/Random Assumptions
* Transaction Amounts
* Account Types
    * Transaction amounts
* Different tier based on income
* Accounts with larger degree than a given threshold (currently 10) will be in poll of possible alert candidates
* Frequency of TX model types
* Agent start step (within account)
* Target step of a single normal transaction (within SingleTransactionModel)
* Model transactions are balanced to spread out to the number of destinations (FanIn and FanOut)
* Transaction interval default is 10
* Fluxuction of transactions is set to 2
* SingleTransactionalModel has only transaction move all money out
* Degree distribution of network is purely random

## Additional Transaction Modles

## Time
* Steps as days, but need start date for Transaction logs

## Validation Work/Analyses
* Need to verify that structural representations are present and how often do they occur intentionally vs. unintentionally
* Go through step by step process on building new fraud transaction types

# Issues Concerns

---

## Issues
* Transaction amounts vary between Fraud and Normal accounts. For fraud accounts, the amount is set within a fixed min and max range. For normal accounts, the amount is calucated through using the balance within the account. This offset between the two creates a strong divide over time as the normal transactions will increase in amount exponentially over time, while fraud transactions remain constant through time. **FIX NEEDED: IGNORE TRANSACTION AMOUNTS UNTIL FIXED**

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
* Some transaction models don't appear to function as described, this may be fine as it would act as expected anyway or could be some java code magic that was missed **Needs to be verified**
* Graph construction is done through degree distribution and the NetworkX function [directed_configuration_model](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.generators.degree_seq.directed_configuration_model.html). 
    * One concern with this is, does this generate an accurate representation of a network of account transfers? 
    * One possible alteration is that of making the graph have higher levels of assortativity (meaning nodes form connections with those of similar types), one method to explore is if highly connected nodes are more likely to be connected with each other or is it more of an authority and hub situation with nodes that are disproportionally transferring in vs transferring out (and vice versa). Network logic is important if we want better accuracy, otherwise we are only mapping to random noise... 
    * Another concern is that should we allow parallel edges or self loops (which both are allowed using the directed_configuration_model). 
    
## Project Ideas

* Need to decern random from non-random processes. Can use this simulator as a testing ground as we have random processes vs non-random. 
** Transaction amount is random for fraud within a range
** Transaction time stamp is random for all
** Who they transfer to is random depending on certain account traits
