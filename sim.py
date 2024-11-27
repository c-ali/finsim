import matplotlib.pyplot as plt
import numpy as np


def compute_interest(monthly_rate, yrly_interest, rest_months, rate_increment=0, reorganize_portfolio_times=0, tax_rate=0.25,
                     monthly_fees=None, yrly_taxfree=0):
    """
    Calculates the total investment value and fees over a specified period, factoring in compound interest, taxes,
    fees, and portfolio restructuring events.

    Args:
        monthly_rate (float): Initial monthly contribution amount.
        yrly_interest (float): Annual interest rate (percentage).
        rest_months (int): Total number of months for the investment.
        rate_increment (float, optional): Annual percentage increase in the monthly contribution. Default is 0. Often called dynamic in contracts.
        reorganize_portfolio_times (int, optional): Number of times the portfolio is reorganized, triggering taxation. Default is 0. We assume these events are equally spaced
        tax_rate (float, optional): Tax rate applied to untaxed gains during portfolio reorganization (percentage). Default is 25%.
        monthly_fees (list of lists, optional): A 2D array where each sublist is a tuple of the form (number_of_months, fee_amount),
                                                specifying monthly fees in absolute terms. Default is None. This can be used to represent the absolute fees of the contract.
        yrly_taxfree (float, optional): Annual tax-free allowance for untaxed gains (currency units). Default is 0.

    Returns:
        tuple:
            - already_taxed (float): Total value of taxed gains, including original contributions.
            - non_taxed (float): Total untaxed gains at the end of the investment period.
            - total_fees (float): Total fees deducted over the investment period.

    Examples:
        >>> compute_interest(150, 9.1, 30)
        (taxed_gains, untaxed_gains, total_fees)

        >>> compute_interest(200, 7.5, 20, rate_increment=2, reorganize_portfolio_times=3, tax_rate=20,
                             monthly_fees=[[60, 30], [120, 20]], yrly_taxfree=1000)
        (taxed_gains, untaxed_gains, total_fees)

    Notes:
        - The portfolio is reorganized evenly throughout the investment period based on the `reorganize_portfolio_times`.
        - Untaxed gains are subjected to the `tax_rate` during portfolio reorganization.
        - Fees are subtracted monthly and accumulate in the `total_fees`.
    """

    # already taxed gains. this includes the original investment.
    # if reorganize_portfolio = 0, these values coincide
    already_taxed = 0
    non_taxed = 0
    monthly_interest = (1 + yrly_interest / 100) ** (1 / 12) - 1  # is a ratio, not as a percentage
    total_fees = 0

    yrs, rest_months = divmod(rest_months, 12)
    print(rest_months)
    # reorganize portfolio X number of times "in the middle" of the investment process
    reorganize_portfolio_yrs = np.linspace(0, yrs, reorganize_portfolio_times + 2, dtype=int)[1:-1]
    for yr in range(yrs+1):
        if yr == yrs:
            months = rest_months
            if months == 0:
                break
        else:
            months = 12
        # every year, increase rate by rate_increment
        if rate_increment > 0:
            monthly_rate *= 1 + (rate_increment / 100)
        for month in range(months):
            # every month add the monthly contribution and interest
            already_taxed += monthly_rate
            total_money = already_taxed + non_taxed
            interest = total_money * monthly_interest
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

        if yrly_taxfree > 0:
            money_moved = min(yrly_taxfree, non_taxed)
            non_taxed -= money_moved
            already_taxed += money_moved
    # return already_taxed, money

    return already_taxed, non_taxed, total_fees

def compare_investments(
    months,
    monthly_rate,
    dynamic,
    avg_interest,
    avg_fond_fees,
    contract_fee,
    etf_fee,
    steuerfreibetrag,
    monthly_fees,
    regular_tax_rate,
    contract_tax_rate,
    reorganize_portfolio_times
):
    """
    Compares two investment scenarios: one without a contract and one with a contract.

    Calculates and prints the final worth after taxes for both scenarios, the difference between them,
    and the total contract fees.

    Parameters:
        months (int): The total investment duration in months.
        monthly_rate (float): The initial monthly contribution amount.
        dynamic (float): The annual increment rate for the monthly contribution (in percent).
        avg_interest (float): The average annual interest rate (in percent).
        avg_fond_fees (float): The average fund fees for the contract scenario (in percent).
        contract_fee (float): The annual contract fee (in percent).
        etf_fee (float): The fee for investments outside the contract (in percent).
        steuerfreibetrag (float): The annual tax-free allowance.
        monthly_fees (list of lists): Monthly fees for the contract scenario. Each sublist contains
            [duration_in_months, fee_amount].
        regular_tax_rate (float): The regular tax rate for capital investments (in percent).
        contract_tax_rate (float): The reduced tax rate applicable due to the contract (in percent).
        reorganize_portfolio_times (int): Number of times the portfolio is reorganized, triggering taxation.

    Returns:
        tuple: A tuple containing:
            - worth_nocontract_after_taxes (float): Final worth after taxes without the contract.
            - worth_contract_after_taxes (float): Final worth after taxes with the contract.
            - difference (float): Difference between the two scenarios.
            - ratio (float): Ratio of the worth without contract to worth with contract.
            - sum_monthly_fees (float): Total contract signing and administration fees.
    """

    contract_pct_fee = avg_fond_fees + contract_fee
    taxed_nocontract, untaxed_nocontract, _ = compute_interest(monthly_rate,
                                                               avg_interest - etf_fee,
                                                               months,
                                                               rate_increment=dynamic,
                                                               reorganize_portfolio_times=reorganize_portfolio_times,
                                                               tax_rate=regular_tax_rate,
                                                               yrly_taxfree=steuerfreibetrag)
    taxed_contract, untaxed_contract, sum_monthly_fees = compute_interest(monthly_rate,
                                                                          avg_interest - contract_pct_fee,
                                                                          months,
                                                                          rate_increment=dynamic,
                                                                          monthly_fees=monthly_fees)

    worth_nocontract_after_taxes = taxed_nocontract + untaxed_nocontract * (1 - regular_tax_rate / 100) # applay final tax here
    worth_contract_after_taxes = taxed_contract + untaxed_contract * (1 - contract_tax_rate / 100) # applay final tax here
    difference = worth_nocontract_after_taxes - worth_contract_after_taxes
    ratio = worth_nocontract_after_taxes / worth_contract_after_taxes

    print(f"Ohne Vertrag {worth_nocontract_after_taxes:_.0f}€")
    print(f"Mit Vertrag {worth_contract_after_taxes:_.0f}€")
    print(f"Differenz {difference:_.0f}€ bzw {ratio * 100 - 100:.3f}%")
    print(f"Vertragsabschluss & Verwaltungskosten ohne Jährliche verwaltungskosten der Fondanlage: {sum_monthly_fees:_.0f}")

    return (
        worth_nocontract_after_taxes,
        worth_contract_after_taxes,
        difference,
        ratio,
        sum_monthly_fees
    )

months = 30  # 33*12
monthly_rate = 150  # 300
dynamic = 0
avg_interest = 6  # 9.1 #7  # 9.1
avg_fond_fees = 1.35  # 1.35  # avg fees of the active managed fonds in the contract as a percentage
contract_fee = 0.35  # annual fees for the contract itself, paid until pension as a percentage
etf_fee = 0.22  # 0.22 # fees paid for the etf/investments outside of the contract as a percentage
# fee = 1.35+0.35 #2.36 #2.34
steuerfreibetrag = 0  # 1000 #1000
monthly_fees = [[12 * 5, 28.88], [(60 - 21) * 12,
                                  17.86]]  # [[12*5, 28.88], [(60-21)*12, 17.86]] # monthly fees for the contract in absolute euros
regular_tax_rate = 0  # 25  #  regular annual tax rate for capital investments in germany as a percentage
contract_tax_rate = 0  # 10  # 0.04 # better tax rate you get because of the contract as a percentage
reorganize_portfolio_times = 0  # number of times you reorganise your portfolio. Every time the portfolio is reorganized, taxes are paid

(
    worth_nocontract_after_taxes,
    worth_contract_after_taxes,
    difference,
    ratio,
    sum_monthly_fees
) = compare_investments(
    months,
    monthly_rate,
    dynamic,
    avg_interest,
    avg_fond_fees,
    contract_fee,
    etf_fee,
    steuerfreibetrag,
    monthly_fees,
    regular_tax_rate,
    contract_tax_rate,
    reorganize_portfolio_times
)
