//
// Note: No specific bank models are used for this fraud transaction model class.
//

package amlsim.model.fraud;

import amlsim.Account;

import java.util.*;

/**
 * Multiple accounts send money to the subject account
 */
public class FanInTransactionModel extends FraudTransactionModel {

    // Senders and receiver
    private Account dest;  // The destination (receiver) account
    private List<Account> origs = new ArrayList<>();  // The origin (sender) accounts

    private long[] steps;
    public static final int SIMULTANEOUS = 1;
    public static final int FIXED_INTERVAL = 2;
    public static final int RANDOM_RANGE = 3;

    public FanInTransactionModel(float minAmount, float maxAmount, int start, int end){
        super(minAmount, maxAmount, start, end);
//        System.out.println(start + " " + end);
    }

    public void setSchedule(int modelID){
        // Transaction schedule

        // Set alert members
        List<Account> members = alert.getMembers();
        dest = alert.isFraud() ? alert.getSubjectAccount() : members.get(0);  // The subject account is the receiver
        for(Account orig : members){  // The rest of accounts are senders
            if(orig != dest) origs.add(orig);
        }

        // Set transaction schedule
        int numOrigs = origs.size();
        steps = new long[numOrigs];
        if(modelID == SIMULTANEOUS){
            long step = getRandomStep();
            Arrays.fill(steps, step);
        }else if(modelID == FIXED_INTERVAL){
            long range = endStep - startStep + 1;
            if(numOrigs < range){
                long interval = range / numOrigs;
                for(int i=0; i<numOrigs; i++){
                    steps[i] = startStep + interval*i;
                }
            }else{
                long batch = numOrigs / range;
                for(int i=0; i<numOrigs; i++){
                    steps[i] = startStep + i/batch;
                }
            }
        }else if(modelID == RANDOM_RANGE){
            for(int i=0; i<numOrigs; i++){
                steps[i] = getRandomStep();
            }
        }
    }

    @Override
    public String getType() {
        return "FanInFraud";
    }

    public void sendTransactions(long step, Account acct){
        long alertID = alert.getAlertID();
        boolean isFraud = alert.isFraud();
        float amount = getAmount() / origs.size();

        for(int i=0; i<origs.size(); i++){
            if(steps[i] == step){
                Account orig = origs.get(i);
                if(orig.getID().equals(acct.getID())) {
                    sendTransaction(step, amount, orig, dest, isFraud, alertID);
                }
            }
        }
    }
}
