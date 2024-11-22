import matplotlib.pyplot as plt
import numpy as np


def compute_interest(monthly_rate, yrly_interest, yrs, rate_increment=0, reorganize_portfolio_times=0, tax_rate=.25,
                     monthly_fees=None):
    '''Computes the compound interest over yrs years assuming yrly_interest as yearly interest rate.
     Assumes monthy contributions of monthly_rate that incrase every year by rate_increment.
     Portfolio is reorganized i.e. taxed for reorganize_portfolio times.
     monthly_fees is a 2d-Array with tuples (months, rate) where rate gets paid for a number of months. Is inclusive of the upper limit'''

    # already taxed gains. this includes the original investment.
    # if reorganize_portfolio = 0, these values coincide
    already_taxed = 0
    non_taxed = 0
    monthly_interest = yrly_interest / 12
    total_fees = 0

    # reorganize portfolio X number of times "in the middle" of the investment process
    reorganize_portfolio_yrs = np.linspace(0, yrs, reorganize_portfolio_times + 2, dtype=int)[1:-1]
    for yr in range(yrs):
        # every year, increase rate by rate_increment
        if rate_increment > 0:
            monthly_rate *= 1 + rate_increment / 100
        for month in range(12):
            # every month add the monthly contribution and interest
            already_taxed += monthly_rate
            total_money = already_taxed + non_taxed
            interest = total_money * monthly_interest / 100
            non_taxed += interest

            # add one or mutiple monthly fees
            if monthly_fees:
                for fee_month, fee_rate in monthly_fees:
                    if yr * 12 + month <= fee_month:
                        non_taxed -= fee_rate
                        total_fees += fee_rate

        # pay taxes if portfolio is reorganized in this yr
        if reorganize_portfolio_times > 0 and yr in reorganize_portfolio_yrs:
            already_taxed += non_taxed * (1 - tax_rate / 100)
            non_taxed = 0
    # return already_taxed, money

    return already_taxed, non_taxed, total_fees


yrs = 33
montly_rate = 150  # 300
dynamic = 0
avg_interest = 7  # 9.1
avg_fond_fees = 1.35  # 1.35  # avg fees of the active managed fonds in the contract as a percentage
contract_fee = 0.35  # annual fees for the contract itself, paid until pension as a percentage
etf_fee = 1.35  # 0.22 # fees paid for the etf/investments outside of the contract as a percentage
# fee = 1.35+0.35 #2.36 #2.34
monthly_fees = [[12 * 5, 28.88], [(60 - 21) * 12,
                                  17.86]]  # [[12*5, 28.88], [(60-21)*12, 17.86]] # monthly fees for the contract in absolute euros
regular_tax_rate = 25  #  regular annual tax rate for capital investments in germany as a percentage
contract_tax_rate = 10  # 0.04 # better tax rate you get because of the contract as a percentage
reorganize_portfolio_times = 0

contract_pct_fee = avg_fond_fees + contract_fee
taxed_nocontract, untaxed_nocontract, _ = (compute_interest
                                           (montly_rate, avg_interest - etf_fee, yrs, dynamic,
                                            reorganize_portfolio_times, regular_tax_rate))
taxed_contract, untaxed_contract, sum_monthly_fees = compute_interest(montly_rate, avg_interest - contract_pct_fee, yrs,
                                                                      dynamic, monthly_fees=monthly_fees)

worth_nocontract_after_taxes = taxed_nocontract + untaxed_nocontract * (1 - regular_tax_rate / 100) # applay final tax here
worth_contract_after_taxes = taxed_contract + untaxed_contract * (1 - contract_tax_rate / 100) # applay final tax here
difference = worth_nocontract_after_taxes - worth_contract_after_taxes
ratio = worth_nocontract_after_taxes / worth_contract_after_taxes

print(f"Ohne Vertrag {worth_nocontract_after_taxes:_.0f}€")
print(f"Mit Vertrag {worth_contract_after_taxes:_.0f}€")
print(f"Differenz {difference:_.0f}€ bzw {ratio * 100 - 100:.3f}%")
print(f"Monthly Fees paid: {sum_monthly_fees:_.0f}")
