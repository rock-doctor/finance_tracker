import pandas as pd
import datetime
import glob
import os
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#Credit statement exports are .ascii files within the "credit folder"
credit_files = glob.glob(os.path.join('./credit/', '*.ascii'))

#Todo: make the reading and storing of credit and chequing statements into functions
#Read all of the credit statements and concatenate them as a single dataframe
credit_list = []
for file in credit_files:
	credit_file = pd.read_csv(file, names=['full_date', 'description', 'credit_amount'])
	credit_list.append(credit_file)

#Get rid of transactions that appear twice
credit = pd.concat(credit_list).drop_duplicates()

credit['full_date'] = pd.to_datetime(credit['full_date'])
credit['month'] = pd.DatetimeIndex(credit['full_date']).month

#remove credit transactions that are positive - these are payments
credit_spending = credit[credit['credit_amount'] < 0].groupby(['month']).sum().rename(columns={'credit_amount':'monthly_spending'})
credit_payment = credit[credit['credit_amount'] > 0].groupby(['month']).sum().rename(columns={'credit_amount':'monthly_payments'})

credit_summary = credit_spending.merge(credit_payment, how='outer', on='month').fillna(0)
credit_summary['monthly_net'] = credit_summary['monthly_spending'] + credit_summary['monthly_payments']

# print(credit)
print("2022 credit summary: \n", credit_summary)





chequing_files = glob.glob(os.path.join('./chequing/', '*.ascii'))

#Read all of the chequing statements and concatenate them as a single dataframe
chequing_list = []
for file in chequing_files:
	chequing_file = pd.read_csv(file,
		sep = ',',
		names=['full_date', 'chequing_amount', '-', 'type','description'])

	chequing_list.append(chequing_file)

chequing = pd.concat(chequing_list).drop_duplicates()

chequing['full_date'] = pd.to_datetime(chequing['full_date'])
chequing['month'] = pd.DatetimeIndex(chequing['full_date']).month
chequing['type'] = chequing['type'].str.strip()
chequing['description'] = chequing['description'].str.strip()

#Move the 2nd payment for rent that happened at the end of January into February
chequing.loc[(chequing['full_date'] == '2022-01-29') & (chequing['chequing_amount'] == -1500.00), 'month'] = datetime.date(2022,2,1).month

# print(chequing)

chequing_spending = chequing[chequing['chequing_amount'] < 0].groupby(['month']).sum().rename(columns={'chequing_amount':'monthly_spending'})
chequing_income = chequing[chequing['chequing_amount'] > 0].groupby(['month']).sum().rename(columns={'chequing_amount':'monthly_income'})

chequing_payroll = chequing.loc[chequing['type'] == 'Payroll Deposit']
chequing_payroll = chequing_payroll[chequing_payroll['chequing_amount'] > 0].groupby(['month']).sum().rename(columns={'chequing_amount':'monthly_payroll'}) 


chequing_summary = chequing_spending.merge(chequing_income, on='month', how='outer').fillna(0)
chequing_summary = chequing_summary.merge(chequing_payroll, on='month', how='outer').fillna(0)

chequing_summary['monthly_net'] = chequing_summary['monthly_spending'] + chequing_summary['monthly_income']

chequing_summary = chequing_summary.reset_index()

print("2022 chequing summary: \n",chequing_summary)
print("2022 net income: ", chequing_summary['monthly_net'].sum())

plt.plot(chequing_summary['month'], chequing_summary['monthly_net'])
plt.show()

