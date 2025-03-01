import matplotlib.pyplot as plt
import numpy as np


def compute_interest(monthly_rate, yrly_interest, rest_months, rate_increment=0, reorganize_portfolio_times=0,
                     tax_rate=0.25,
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
    # reorganize portfolio X number of times "in the middle" of the investment process
    reorganize_portfolio_yrs = np.linspace(0, yrs, reorganize_portfolio_times + 2, dtype=int)[1:-1]
    for yr in range(yrs + 1):
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
        avg_nocontract_interest,
        avg_contract_interest,
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
                                                               avg_nocontract_interest - etf_fee,
                                                               months,
                                                               rate_increment=dynamic,
                                                               reorganize_portfolio_times=reorganize_portfolio_times,
                                                               tax_rate=regular_tax_rate,
                                                               yrly_taxfree=steuerfreibetrag)
    taxed_contract, untaxed_contract, sum_monthly_fees = compute_interest(monthly_rate,
                                                                          avg_contract_interest - contract_pct_fee,
                                                                          months,
                                                                          rate_increment=dynamic,
                                                                          monthly_fees=monthly_fees)

    worth_nocontract_after_taxes = taxed_nocontract + untaxed_nocontract * (
            1 - regular_tax_rate / 100)  # applay final tax here
    worth_contract_after_taxes = taxed_contract + untaxed_contract * (
            1 - contract_tax_rate / 100)  # applay final tax here
    difference = worth_nocontract_after_taxes - worth_contract_after_taxes
    ratio = worth_nocontract_after_taxes / worth_contract_after_taxes

    print(f"Ohne Vertrag {worth_nocontract_after_taxes:_.0f}€")
    print(f"Mit Vertrag {worth_contract_after_taxes:_.0f}€")
    print(f"Differenz {difference:_.0f}€ bzw {ratio * 100 - 100:.3f}%")
    print(
        f"Vertragsabschluss & Verwaltungskosten ohne Jährliche verwaltungskosten der Fondanlage: {sum_monthly_fees:_.0f}")

    return (
        worth_nocontract_after_taxes,
        worth_contract_after_taxes,
        difference,
        ratio,
        sum_monthly_fees
    )


##########################
### DEFAULT PARAMETERS ###
##########################


months = 33*12 #30  # 33*12
monthly_rate = 150  # 300
dynamic = 0
avg_nocontract_interest = 7 #6  # 9.1 #7  # 9.1
avg_contract_interest = 7
contract_fondfee = 1.35  # 1.35  # avg fees of the active managed fonds in the contract as a percentage
contract_fee = 0.35  # annual fees for the contract itself, paid until pension as a percentage
nocontract_fondfee = 0.22  # 0.22 # fees paid for the etf/investments outside of the contract as a percentage
# fee = 1.35+0.35 #2.36 #2.34
steuerfreibetrag = 0#1000 #1000  # 1000 #1000
monthly_fees = [[12 * 5, 28.88], [months,
                                  17.86]]  # [[12*5, 28.88], [(60-21)*12, 17.86]] # monthly fees for the contract in absolute euros
regular_tax_rate = 25  # 25  #  regular annual tax rate for capital investments in germany as a percentage
contract_tax_rate = 10  # 10  # 0.04 # better tax rate you get because of the contract as a percentage
reorganize_portfolio_times = 0  # number of times you reorganise your portfolio. Every time the portfolio is reorganized, taxes are paid

# Copy some variables for later
# Varying months while keeping other parameters constant
fixed_monthly_rate = monthly_rate  # Fixed monthly contribution
fixed_avg_nocontract_interest, fixed_avg_contract_interest = avg_nocontract_interest, avg_contract_interest  # Fixed average interest rate
fixed_months = months  # Fixed months


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
    avg_nocontract_interest,
    avg_contract_interest,
    contract_fondfee,
    contract_fee,
    nocontract_fondfee,
    steuerfreibetrag,
    monthly_fees,
    regular_tax_rate,
    contract_tax_rate,
    reorganize_portfolio_times
)

def plot_varinterest_varorga():

    # Lists to store results
    months_list = np.linspace(12*30, 12*50, 5, dtype=int)  # 360 to 600 months
    monthly_rate_list = np.linspace(100, 1000, 5)  # 100 to 1000
    avg_interest_list = np.linspace(3, 10, 5)  # 3% to 10%
    reorganize_portfolio_times_list = range(0, 31)  # From 0 to 30

    # Store results for plotting
    months_results = []
    monthly_rate_results = []
    avg_interest_results = []
    reorganize_results = []

    # Varying avg_interest
    for avg_interest in avg_interest_list:
        worth_nocontract_after_taxes, worth_contract_after_taxes, difference, ratio, _ = compare_investments(
            fixed_months,
            fixed_monthly_rate,
            dynamic,
            avg_interest,
            avg_interest,
            contract_fondfee,
            contract_fee,
            nocontract_fondfee,
            steuerfreibetrag,
            monthly_fees,
            regular_tax_rate,
            contract_tax_rate,
            reorganize_portfolio_times
        )
        avg_interest_results.append({
            'avg_interest': avg_interest,
            'worth_nocontract': worth_nocontract_after_taxes,
            'worth_contract': worth_contract_after_taxes,
            'difference': difference,
            'ratio': ratio
        })

    # Varying reorganize_portfolio_times
    for reorganize_times in reorganize_portfolio_times_list:
        worth_nocontract_after_taxes, worth_contract_after_taxes, difference, ratio, _ = compare_investments(
            fixed_months,
            fixed_monthly_rate,
            dynamic,
            fixed_avg_nocontract_interest,
            fixed_avg_contract_interest,
            contract_fondfee,
            contract_fee,
            nocontract_fondfee,
            steuerfreibetrag,
            monthly_fees,
            regular_tax_rate,
            contract_tax_rate,
            reorganize_times
        )
        reorganize_results.append({
            'reorganize_times': reorganize_times,
            'worth_nocontract': worth_nocontract_after_taxes,
            'worth_contract': worth_contract_after_taxes,
            'difference': difference,
            'ratio': ratio
        })

    # Replace the previous plotting code with this adjusted code

    # Plotting
    fig, axes = plt.subplots(2, 1, figsize=(18, 12))

    # Plot 1: Varying avg_interest
    axes[0].plot(
        [res['avg_interest'] for res in avg_interest_results],
        [res['worth_nocontract'] / 1000 for res in avg_interest_results],
        label='Without Contract',
        marker='o',
        color='blue'
    )
    axes[0].plot(
        [res['avg_interest'] for res in avg_interest_results],
        [res['worth_contract'] / 1000 for res in avg_interest_results],
        label='With Contract',
        marker='o',
        color='green'
    )
    axes[0].set_title('Investment Worth vs. Average Interest Rate')
    axes[0].set_xlabel('Average Interest Rate (%)')
    axes[0].set_ylabel('Worth After Taxes (€ x1000)')
    axes[0].legend()
    axes[0].grid(True)

    # Plot 2: Varying reorganize_portfolio_times
    axes[1].plot(
        [res['reorganize_times'] for res in reorganize_results],
        [res['worth_nocontract'] / 1000 for res in reorganize_results],
        label='Without Contract',
        marker='o',
        color='blue'
    )
    axes[1].plot(
        [res['reorganize_times'] for res in reorganize_results],
        [res['worth_contract'] / 1000 for res in reorganize_results],
        label='With Contract',
        marker='o',
        color='green'
    )
    axes[1].set_title('Investment Worth vs. Portfolio Reorganizations')
    axes[1].set_xlabel('Number of Portfolio Reorganizations')
    axes[1].set_ylabel('Worth After Taxes (€ x1000)')
    axes[1].legend()
    axes[1].grid(True)

    # Add default parameters and monthly fees as text within the figure
    textstr = f"""Default Parameters:
    - Investment Duration: {fixed_months // 12} years
    - Monthly Contribution: €{fixed_monthly_rate}
    - Average Interest Rate (Depot): {fixed_avg_nocontract_interest}%
    - Average Interest Rate (Contract): {fixed_avg_contract_interest}%
    - Regular Tax Rate: {regular_tax_rate}%
    - Contract Tax Rate: {contract_tax_rate}%
    - ETF Fee: {nocontract_fondfee}%
    - Fund Fees (Contract): {contract_fondfee}%
    - Contract Fee: {contract_fee}%
    - Monthly Fees:
      - First {monthly_fees[0][0]} months: €{monthly_fees[0][1]} per month
      - First {monthly_fees[1][0]} months: €{monthly_fees[1][1]} per month
    - Reorganize portfolio times: {reorganize_portfolio_times}
    """

    # Adjust the position of the text box
    fig.text(.77, .28, textstr, ha='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout(rect=[0, 0.1, 1, 0.95])  # Adjust layout to make room for the text box
    plt.show()

def plot_heatmap():
    # Heatmap code
    # Define ranges for avg_nocontract_interest and avg_contract_interest
    nocontract_interest_values = np.linspace(3, 10, 50)  # 3% to 10%, 50 steps
    contract_interest_values = np.linspace(3, 10, 50)  # 3% to 10%, 50 steps

    # Create a meshgrid for the heatmap
    X, Y = np.meshgrid(nocontract_interest_values, contract_interest_values)

    # Initialize a matrix to store the differences
    difference_matrix = np.zeros_like(X)
    # Loop over interest rates and compute differences
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            avg_nocontract_interest = X[i, j]
            avg_contract_interest = Y[i, j]

            worth_nocontract_after_taxes, worth_contract_after_taxes, _, _, _ = compare_investments(
                months,
                monthly_rate,
                dynamic,
                avg_nocontract_interest,
                avg_contract_interest,
                contract_fondfee,
                contract_fee,
                nocontract_fondfee,
                steuerfreibetrag,
                monthly_fees,
                regular_tax_rate,
                contract_tax_rate,
                reorganize_portfolio_times
            )

            difference = worth_nocontract_after_taxes - worth_contract_after_taxes
            difference_matrix[i, j] = difference  # Note the order of indices

    # Create the heatmap
    plt.figure(figsize=(10, 8))
    heatmap = plt.pcolormesh(
        X, Y, difference_matrix, shading='auto', cmap='coolwarm'
    )
    plt.colorbar(heatmap, label='Difference (€)')

    # Add contour line where difference is zero
    contour = plt.contour(
        X, Y, difference_matrix, levels=[0], colors='black', linewidths=2
    )
    plt.clabel(contour, fmt='Breakeven line', colors='black', fontsize=12)
    # Set x and y ticks at whole numbers
    x_ticks = np.arange(3, 11, 1)  # From 3 to 10 inclusive
    y_ticks = np.arange(3, 11, 1)

    plt.xticks(x_ticks)
    plt.yticks(y_ticks)

    # Add grid lines at whole numbers
    plt.grid(which='both', color='gray', linestyle='--', linewidth=0.5)
    plt.xlabel('No-Contract Average Interest Rate (%)')
    plt.ylabel('Contract Average Interest Rate (%)')
    plt.title('Difference in Returns: No-Contract vs. Contract')

    plt.show()


plot_varinterest_varorga()
#plot_heatmap()