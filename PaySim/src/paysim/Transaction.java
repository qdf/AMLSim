package paysim;

import java.io.Serializable;

public class Transaction implements Serializable {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	short type;
	double amount;
	String description;
	Client clientOrigBefore = new Client();
	Client clientOrigAfter = new Client();
	Client clientDestBefore = new Client();
	Client clientDestAfter = new Client();
	boolean isFraud = false;
	boolean isFlaggedFraud = false;
	
	public boolean isFlaggedFraud() {
		return isFlaggedFraud;
	}

	public void setFlaggedFraud(boolean isFlaggedFraud) {
		this.isFlaggedFraud = isFlaggedFraud;
	}

	public boolean isFraud() {
		return isFraud;
	}

	ClientBeta clientBetaOrigBefore = new ClientBeta();
	

	ClientBeta clientBetaOrigAfter = new ClientBeta();
	ClientBeta clientBetaDestBefore = new ClientBeta();
	ClientBeta clientBetaDestAfter = new ClientBeta();
	Merchant merchantBefore = new Merchant();
	public Merchant getMerchantBefore() {
		return merchantBefore;
	}

	public void setMerchantBefore(Merchant merchantBefore) {
		this.merchantBefore = merchantBefore;
	}

	public Merchant getMerchantAfter() {
		return merchantAfter;
	}

	public void setMerchantAfter(Merchant merchantAfter) {
		this.merchantAfter = merchantAfter;
	}

	Merchant merchantAfter = new Merchant();
	int fraudster = 0;
	double newBalanceDest = 0;
	double newBalanceOrig = 0;
	long step;
	String profileOrig, profileDest;
	int day = 0;
	int hour = 0;

	public int getFraudster() {
		return fraudster;
	}

	public void setFraudster(int fraudster) {
		this.fraudster = fraudster;
	}

	public long getStep() {
		return step;
	}

	public void setStep(long step) {
		this.step = step;
	}

	public Transaction() {
		this.type = 0;
		this.amount = 0;
		this.newBalanceDest = 0;
		this.newBalanceOrig = 0;
	}

//	public Transaction(Long step, Client clientOrig, Client clientDest,
//			short type, double amount, String description) {
//		super();
//		this.step = step;
//		this.clientOrig = clientOrig;
//		this.newBalanceOrig = clientOrig.balance;
//		this.profileOrig = clientOrig.profile.toString();
//		this.clientDest = clientDest;
//		this.newBalanceDest = clientDest.balance;
//		this.profileDest = clientDest.profile.toString();
//		this.type = type;
//		this.amount = amount;
//		this.description = description;
//	}
//
	
	//The constructor used in my agent
	public Transaction(Long step, Client clientOrig, short type, double amount,
			String description) {
		super();
		this.step = step;
		this.clientOrigBefore.setClient(clientOrig);;
		this.newBalanceOrig = clientOrig.balance;
		this.type = type;
		this.amount = amount;
		this.description = description;
	}
	
	//Used for transfer
	public Transaction(Long step, Client clientOriginalBefore, Client clientOrigAfter, short type, double amount,
			String description) {
		super();
		this.step = step;
		this.clientOrigBefore.setClient(clientOriginalBefore);
		this.clientOrigAfter.setClient(clientOrigAfter);
		
		this.newBalanceOrig = this.clientOrigBefore.getBalance();
		this.newBalanceDest = clientOrigAfter.balance;
		
		this.type = type;
		this.amount = amount;
		this.description = description;
	}
	
	public Transaction(Long step, ClientBeta clientOriginalBefore, ClientBeta clientOrigAfter, short type, double amount,
			String description) {
		super();
		this.step = step;
		this.clientBetaOrigBefore.setClientBeta(clientOriginalBefore);
		this.clientBetaOrigAfter.setClientBeta(clientOrigAfter);
		
		this.newBalanceOrig = this.clientOrigBefore.getBalance();
		this.newBalanceDest = clientOrigAfter.balance;
		
		this.type = type;
		this.amount = amount;
		this.description = description;
	}

	public Transaction(Long step, ClientBeta clientOrig, short type, double amount,
			String description) {
		super();
		this.step = step;
		this.clientBetaOrigBefore.setClientBeta(clientOrig);;
		this.newBalanceOrig = clientOrig.balance;
		this.type = type;
		this.amount = amount;
		this.description = description;
	}
//	public Transaction(Long step, Client clientOrig, Client clientDest,
//			short type, double amount, String description, int fraudster) {
//		super();
//		this.step = step;
//		this.clientOrig = clientOrig;
//		this.newBalanceOrig = clientOrig.balance;
//		this.profileOrig = clientOrig.profile.toString();
//		this.clientDest = clientDest;
//		this.newBalanceDest = clientDest.balance;
//		this.profileDest = clientDest.profile.toString();
//		this.type = type;
//		this.amount = amount;
//		this.description = description;
//		this.fraudster = fraudster;
//	}
//
//	public Transaction(Long step, Client clientOrig, short type, double amount,
//			String description, int fraudster) {
//		super();
//		this.step = step;
//		this.clientOrig = clientOrig;
//		this.newBalanceOrig = clientOrig.balance;
//		this.profileOrig = clientOrig.profile.toString();
//		this.type = type;
//		this.amount = amount;
//		this.description = description;
//		this.fraudster = fraudster;
//	}

	public short getType() {
		return type;
	}

	public void setType(short type) {
		this.type = type;
	}

	public double getAmount() {
		return amount;
	}

	public void setAmount(long amount) {
		this.amount = amount;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	

	public Client getClientOrigBefore() {
		return clientOrigBefore;
	}

	public void setClientOrigBefore(Client clientOrigBefore) {
		this.clientOrigBefore = clientOrigBefore;
	}

	public Client getClientOrigAfter() {
		return clientOrigAfter;
	}

	public void setClientOrigAfter(Client clientOrigAfter) {
		this.clientOrigAfter = clientOrigAfter;
	}

	public Client getClientDestBefore() {
		return clientDestBefore;
	}

	public void setClientDestBefore(Client clientDestBefore) {
		this.clientDestBefore = clientDestBefore;
	}

	public Client getClientDestAfter() {
		return clientDestAfter;
	}

	public void setClientDestAfter(Client clientDestAfter) {
		this.clientDestAfter = clientDestAfter;
	}

	public ClientBeta getClientBetaOrigBefore() {
		return clientBetaOrigBefore;
	}

	public void setClientBetaOrigBefore(ClientBeta clientBetaOrigBefore) {
		this.clientBetaOrigBefore = clientBetaOrigBefore;
	}

	public ClientBeta getClientBetaOrigAfter() {
		return clientBetaOrigAfter;
	}

	public void setClientBetaOrigAfter(ClientBeta clientBetaOrigAfter) {
		this.clientBetaOrigAfter = clientBetaOrigAfter;
	}

	public ClientBeta getClientBetaDestBefore() {
		return clientBetaDestBefore;
	}

	public void setClientBetaDestBefore(ClientBeta clientBetaDestBefore) {
		this.clientBetaDestBefore = clientBetaDestBefore;
	}

	public ClientBeta getClientBetaDestAfter() {
		return clientBetaDestAfter;
	}

	public void setClientBetaDestAfter(ClientBeta clientBetaDestAfter) {
		this.clientBetaDestAfter = clientBetaDestAfter;
	}
	
	public String toString() {
		String ps = null;

		if(this.newBalanceDest == 0){
			ps = Long.toString(step) + " " + clientOrigBefore.toString() + "\t" +"Amount:\t" + Double.toString(amount)
					+ "\tnew Balance " + Double.toString(newBalanceOrig) + "\t" + "Action: " + this.description +
					"Day:\t" + this.day + "\tHour:\t" + this.hour + "\n";
		}else{
			ps = Long.toString(step) + " " + clientOrigBefore.toString() + "\t" + this.clientOrigBefore.toString() +"(" + this.newBalanceOrig
					 + ") Transfered: " + Double.toString(amount) + " to " + this.clientOrigAfter.toString() + " (" + this.newBalanceDest + ")\t" + 
					 "\tnew Balance " + Double.toString(newBalanceOrig) + "\t" + "Action: " + this.description +
					 "Day:\t" + this.day + "\tHour:\t" + this.hour + "\n";
		}
		
		return ps;
	}
	
	
	public void setNewBalanceDest(double balance){
		this.newBalanceDest = balance;
	}
	
	public void setNewBalanceOrig(double balance){
		this.newBalanceOrig = balance;
	}
	
	public double getNewBalanceOrig(){
		return this.newBalanceOrig;
	}
	
	public double getNewBalanceDest(){
		return this.newBalanceDest;
	}

	public int getDay() {
		return day;
	}

	public void setDay(int day) {
		this.day = day;
	}

	public int getHour() {
		return hour;
	}

	public void setHour(int hour) {
		this.hour = hour;
	}

	public void setFraud(boolean isFraud) {
		this.isFraud = isFraud;
	}
	
//	public String getRecord() {
//		String ps = null;
//		ps = Long.toString(step) + ",'" + clientOrig + "','" + clientOrig.age + "','"
//				+ profileOrig + "','" + clientOrig.getLocation()
//				+ "'," + Short.toString(type) + "," + Double.toString(amount)
//				+ "," + Double.toString(newBalanceOrig) + ",'";
//		if (clientDest != null) {
//			ps += clientDest + "','" + profileDest + "'," + "'"
//					+ clientDest.getLocation() + "',"
//					+ Double.toString(newBalanceDest) + ",";
//		} else {
//			ps += "null','null','null',0,";
//		}
//		ps += fraudster + "";
//		return ps;
//	}

}
