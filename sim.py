import matplotlib.pyplot as plt
import numpy as np

def compute_interest(monthly_rate, yrly_interest, yrs, rate_increment = 0, reorganize_portfolio_times=0, tax_rate=.25):
    '''Computes the compound interest over yrs years assuming yrly_interest as yearly interest rate.
     Assumes monthy contributions of monthly_rate that incrase every year by rate_increment.
     Portfolio is reorganized i.e. taxed for reorganize_portfolio times.'''

    # already taxed gains. this includes the original investment.
    # if reorganize_portfolio = 0, these values coincide
    already_taxed = 0
    non_taxed = 0
    monthly_interest = yrly_interest/12

    # reorganize portfolio X number of times "in the middle" of the investment process
    reorganize_portfolio_yrs = np.linspace(0, yrs, reorganize_portfolio_times + 2, dtype=int)[1:-1]
    for yr in range(yrs):
        # every year, increase rate by rate_increment
        if rate_increment > 0:
            monthly_rate *= 1 + (rate_increment / 100)
        for month in range(12):
            # every month add the monthly contribution and interest
            already_taxed += monthly_rate
            total_money = already_taxed + non_taxed
            interest = total_money * monthly_interest/100
            non_taxed += interest

        # pay taxes if portfolio is reorganized in this yr
        if reorganize_portfolio_times > 0 and yr in reorganize_portfolio_yrs:
            already_taxed += non_taxed * (1-tax_rate)
            non_taxed = 0
    #return already_taxed, money
    return already_taxed, non_taxed

yrs = 33
montly_rate = 150 #300
dynamic = 0
avg_interest = 9.1
fee = 2.36 #2.34
regular_tax_rate = .25
contract_tax_rate = 0.04 #.1 # 0.04
reorganize_portfolio_times = 0

taxed_nocontract, untaxed_nocontract = compute_interest(montly_rate, avg_interest,yrs, dynamic, reorganize_portfolio_times, regular_tax_rate)
taxed_contract, untaxed_contract = compute_interest(montly_rate, avg_interest - fee, yrs, dynamic)

worth_nocontract_after_taxes = taxed_nocontract + untaxed_nocontract * (1-regular_tax_rate)
worth_contract_after_taxes = taxed_contract + untaxed_contract * (1-contract_tax_rate)
difference = worth_nocontract_after_taxes - worth_contract_after_taxes
ratio = worth_nocontract_after_taxes / worth_contract_after_taxes

print(f"Ohne Vertrag {worth_nocontract_after_taxes:_.0f}€")
print(f"Mit Vertrag {worth_contract_after_taxes:_.0f}€")
print(f"Differenz {difference:_.0f}€ bzw {ratio * 100 - 100:.3f}%")
