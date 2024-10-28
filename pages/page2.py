import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import datetime
from typing import Tuple, Dict, Union
import plotly.graph_objects as go
import pandas as pd

# Streamlit page config
st.set_page_config(
    page_title="Singapore CPF Calculator",
    layout="wide",  # Changed to wide layout for more content
    page_icon="🌐"
)

# Add the missing wage ceiling constants
ORDINARY_WAGES_CEILING = 6000.00  # Monthly ceiling
ADDITIONAL_WAGES_CEILING = 102000.00  # Yearly ceiling
TOTAL_WAGES_CEILING = 102000.00  # Total annual ceiling

# CPF Life milestone constants
BRS_2024 = 102000
FRS_2024 = 198800
ERS_2024 = 298800


# Constants (keeping your existing constants)
CPF_RATES: Dict[str, Tuple[float, float, float]] = {
    "35 years and below": (0.37, 0.20, 0.17),
    "Above 35 to 45 years": (0.37, 0.20, 0.17),
    "Above 45 to 50 years": (0.37, 0.20, 0.17),
    "Above 50 to 55 years": (0.37, 0.20, 0.17),
    "Above 55 to 60 years": (0.26, 0.13, 0.13),
    "Above 60 to 65 years": (0.165, 0.085, 0.08),
    "Above 65 years": (0.125, 0.075, 0.05)
}

ALLOCATIONS: Dict[str, Tuple[float, float, float]] = {
    "35 years and below": (0.08108, 0.23243, 0.68649),
    "Above 35 to 45 years": (0.08108, 0.23243, 0.68649),
    "Above 45 to 50 years": (0.08108, 0.23243, 0.68649),
    "Above 50 to 55 years": (0.08108, 0.23243, 0.68649),
    "Above 55 to 60 years": (0.10577, 0.13462, 0.75961),
    "Above 60 to 65 years": (0.12121, 0.03030, 0.84849),
    "Above 65 years": (0.16000, 0.00000, 0.84000)
}

# CPF Life milestone constants
BRS_2024 = 102000
FRS_2024 = 198800
ERS_2024 = 298800

def get_age_group(birth_date: datetime.date) -> str:
    """
    Determine age group based on birth date.
    
    Args:
        birth_date: Date of birth
    
    Returns:
        str: Age group category
    """
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    if age <= 35:
        return "35 years and below"
    elif age <= 45:
        return "Above 35 to 45 years"
    elif age <= 50:
        return "Above 45 to 50 years"
    elif age <= 55:
        return "Above 50 to 55 years"
    elif age <= 60:
        return "Above 55 to 60 years"
    elif age <= 65:
        return "Above 60 to 65 years"
    else:
        return "Above 65 years"

def calculate_contributions(
    ordinary_wages: float,
    additional_wages: float,
    age_group: str,
    total_wages_ytd: float = 0.0
) -> Tuple[float, float, float]:
    """
    Calculate CPF contributions with consideration for YTD wages.
    
    Args:
        ordinary_wages: Monthly ordinary wages
        additional_wages: Additional wages (bonus, etc.)
        age_group: Age group category
        total_wages_ytd: Year-to-date wages before current contribution
        
    Returns:
        Tuple containing total CPF, employee share, and employer share
    """
    rate, employee_rate, employer_rate = CPF_RATES[age_group]
    
    # Check total wages ceiling
    remaining_ceiling = max(0, TOTAL_WAGES_CEILING - total_wages_ytd)
    
    # Cap ordinary wages
    capped_ordinary_wages = min(ordinary_wages, ORDINARY_WAGES_CEILING)
    
    # Calculate remaining ceiling for additional wages
    remaining_aw_ceiling = max(0, remaining_ceiling - capped_ordinary_wages)
    capped_additional_wages = min(additional_wages, remaining_aw_ceiling)
    
    # Calculate contributions
    total_cpf = (rate * capped_ordinary_wages) + (rate * capped_additional_wages)
    employee_share = (employee_rate * capped_ordinary_wages) + (employee_rate * capped_additional_wages)
    employer_share = total_cpf - employee_share
    
    return total_cpf, employee_share, employer_share

def calculate_allocations(
    total_cpf: float,
    age_group: str
) -> Tuple[float, float, float]:
    """
    Calculate allocations for CPF accounts.
    
    Args:
        total_cpf: Total CPF contribution amount
        age_group: Age group category
    
    Returns:
        Tuple containing Medisave, Special, and Ordinary account allocations
    """
    if total_cpf <= 0:
        return 0, 0, 0

    medisave_rate, special_rate, ordinary_rate = ALLOCATIONS[age_group]
    
    medisave_allocation = round(medisave_rate * total_cpf, 2)
    special_allocation = round(special_rate * total_cpf, 2)
    ordinary_allocation = round(total_cpf - medisave_allocation - special_allocation, 2)
    
    return medisave_allocation, special_allocation, ordinary_allocation

def plot_contributions(
    total_cpf: float,
    employee_share: float,
    employer_share: float,
    medisave: float,
    special: float,
    ordinary: float
) -> None:
    """Generate interactive pie charts to visualize CPF contributions."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Custom autopct function to display both percentage and value
    def make_autopct(values):
        def autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n(${val:.2f})'
        return autopct
    
    # First pie chart: Contribution shares
    contribution_labels = ['Employee Share', 'Employer Share']
    contribution_sizes = [employee_share, employer_share]
    contribution_colors = ['#FF9999', '#66B2FF']
    
    ax1.pie(contribution_sizes, labels=contribution_labels, colors=contribution_colors,
            autopct=make_autopct(contribution_sizes), shadow=True, startangle=90)
    ax1.set_title('Contribution Shares')
    
    # Second pie chart: Account allocations
    allocation_labels = ['MediSave', 'Special', 'Ordinary']
    allocation_sizes = [medisave, special, ordinary]
    allocation_colors = ['#99FF99', '#FFCC99', '#FF99CC']
    
    ax2.pie(allocation_sizes, labels=allocation_labels, colors=allocation_colors,
            autopct=make_autopct(allocation_sizes), shadow=True, startangle=90)
    ax2.set_title('Account Allocations')
    
    plt.tight_layout()
    st.pyplot(fig)

def calculate_future_balance(
    current_contribution: float,
    years: int,
    annual_increment: float = 0.03,
    interest_rates: Dict[str, float] = {"OA": 0.025, "SA": 0.04, "MA": 0.04}
) -> Dict[str, list]:
    """
    Project future CPF balances based on current contribution patterns.
    
    Args:
        current_contribution: Monthly contribution amount
        years: Number of years to project
        annual_increment: Expected annual salary increment
        interest_rates: Dictionary of interest rates for each account
    
    Returns:
        Dictionary containing projected balances for each account
    """
    monthly_data = {
        "OA": [],
        "SA": [],
        "MA": [],
        "Total": [],
        "Months": []
    }
    
    oa_balance = 0
    sa_balance = 0
    ma_balance = 0
    monthly_contribution = current_contribution
    
    for month in range(years * 12):
        # Apply annual increment
        if month % 12 == 0 and month > 0:
            monthly_contribution *= (1 + annual_increment)
        
        # Calculate monthly allocation
        oa_contribution = monthly_contribution * 0.68649
        sa_contribution = monthly_contribution * 0.23243
        ma_contribution = monthly_contribution * 0.08108
        
        # Add interest (monthly)
        oa_balance = (oa_balance + oa_contribution) * (1 + interest_rates["OA"]/12)
        sa_balance = (sa_balance + sa_contribution) * (1 + interest_rates["SA"]/12)
        ma_balance = (ma_balance + ma_contribution) * (1 + interest_rates["MA"]/12)
        
        total_balance = oa_balance + sa_balance + ma_balance
        
        monthly_data["OA"].append(oa_balance)
        monthly_data["SA"].append(sa_balance)
        monthly_data["MA"].append(ma_balance)
        monthly_data["Total"].append(total_balance)
        monthly_data["Months"].append(month)
    
    return monthly_data

def plot_future_projections(monthly_data: Dict[str, list]) -> go.Figure:
    """Create an interactive plot showing CPF balance projections."""
    fig = go.Figure()
    
    # Add traces for each account
    fig.add_trace(go.Scatter(
        x=monthly_data["Months"],
        y=monthly_data["OA"],
        name="Ordinary Account",
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly_data["Months"],
        y=monthly_data["SA"],
        name="Special Account",
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly_data["Months"],
        y=monthly_data["MA"],
        name="MediSave Account",
        fill='tonexty'
    ))
    
    # Add milestone reference lines
    fig.add_hline(y=BRS_2024, line_dash="dash", annotation_text="Basic Retirement Sum")
    fig.add_hline(y=FRS_2024, line_dash="dash", annotation_text="Full Retirement Sum")
    
    fig.update_layout(
        title="Projected CPF Balance Over Time",
        xaxis_title="Months",
        yaxis_title="Balance (SGD)",
        hovermode='x unified'
    )
    
    return fig

def generate_explanation(
    ordinary_wages: float,
    total_cpf: float,
    employee_share: float,
    employer_share: float,
    age_group: str,
    medisave: float,
    special: float,
    ordinary: float
) -> str:
    """Generate a detailed explanation of the CPF contribution calculation."""
    
    total_rate, employee_rate, employer_rate = CPF_RATES[age_group]
    
    explanation = f"""
    ### 📊 Understanding Your CPF Contribution

    #### 💰 Contribution Breakdown
    Based on your monthly ordinary wages of ${ordinary_wages:,.2f}:
    
    * Your contribution rate is {employee_rate*100:.1f}% = ${employee_share:,.2f}
    * Your employer's contribution rate is {employer_rate*100:.1f}% = ${employer_share:,.2f}
    * Total contribution rate is {total_rate*100:.1f}% = ${total_cpf:,.2f}

    #### 🏦 Account Allocation Details
    Your monthly contribution of ${total_cpf:,.2f} is distributed as follows:
    
    * Ordinary Account (for housing, investment, education):
        * {ALLOCATIONS[age_group][2]*100:.1f}% = ${ordinary:,.2f}
    * Special Account (for retirement):
        * {ALLOCATIONS[age_group][1]*100:.1f}% = ${special:,.2f}
    * MediSave Account (for healthcare):
        * {ALLOCATIONS[age_group][0]*100:.1f}% = ${medisave:,.2f}

    #### 📈 Key Financial Insights
    * Your annual CPF contribution (excluding bonuses) would be: ${total_cpf*12:,.2f}
    * This represents ${(total_cpf/ordinary_wages*100):.1f}% of your monthly income
    """
    
    return explanation

def calculate_milestones(
    current_balance: Dict[str, float],
    monthly_contribution: float,
    age_group: str
) -> Dict[str, Union[float, str]]:
    """
    Calculate time to reach various CPF milestones.
    
    Args:
        current_balance: Dictionary with current balances for each account
        monthly_contribution: Total monthly CPF contribution
        age_group: Age group for allocation rates
    
    Returns:
        Dictionary with years to reach BRS and FRS
    """
    # Get SA allocation rate for the age group
    sa_allocation_rate = ALLOCATIONS[age_group][1]  # Special Account allocation rate
    monthly_sa_contribution = monthly_contribution * sa_allocation_rate
    
    def years_to_target(target: float, current: float, monthly: float) -> Union[float, str]:
        if current >= target:
            return "Already achieved"
            
        # Calculate how much more is needed
        remaining = target - current
        
        # Calculate years needed considering compound interest
        # Using simplified compound interest formula with monthly contributions
        r = 0.04  # SA interest rate (4% per annum)
        r_monthly = r / 12
        
        # Using formula: FV = PMT * ((1 + r)^n - 1) / r
        # Solving for n: n = log(1 + (FV * r) / PMT) / log(1 + r)
        # Where FV is remaining amount needed, PMT is monthly contribution
        
        if monthly_sa_contribution <= 0:
            return "Cannot be achieved with current contribution"
            
        try:
            n_months = np.log(1 + (remaining * r_monthly) / monthly_sa_contribution) / np.log(1 + r_monthly)
            years = n_months / 12
            
            if years < 0 or years > 100:  # Sanity check
                return "Cannot be achieved with current contribution"
            
            return round(years, 1)
        except:
            return "Cannot be achieved with current contribution"
    
    # Calculate years to reach each milestone
    brs_years = years_to_target(BRS_2024, current_balance['SA'], monthly_sa_contribution)
    frs_years = years_to_target(FRS_2024, current_balance['SA'], monthly_sa_contribution)
    
    return {
        "BRS": brs_years,
        "FRS": frs_years
    }
            

def main():
    """Main function to run the enhanced Streamlit app."""
    st.title("Singapore CPF Contribution Calculator")
    st.markdown("""
    ### 2024 CPF Calculator with Insights
    Calculate your CPF contributions, understand the breakdown, and plan for your future.
    """)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Calculator", "Future Projections", "Educational Resources"])
    
    # Common inputs that will be needed across tabs
    st.sidebar.subheader("Personal Information")
    birth_date = st.sidebar.date_input(
        "Birth Date",
        min_value=datetime.date(1900, 1, 1),
        max_value=datetime.date.today()
    )
    
    # Calculate age group once - will be used in multiple places
    age_group = get_age_group(birth_date)
    
    with tab1:
        # Your existing calculator layout with the new explanation feature
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            citizenship_status = st.selectbox(
                "Citizenship Status",
                ['Singapore Citizen', 'Permanent Resident (3rd Year onwards)', 
                 'Permanent Resident (1st/2nd Year)']
            )
            
            contribution_month = st.date_input(
                "Contribution Month",
                min_value=datetime.date(datetime.date.today().year, 1, 1),
                max_value=datetime.date(datetime.date.today().year, 12, 31)
            )
        
        with col2:
            st.subheader("Wage Information")
            ordinary_wages = st.number_input(
                "Monthly Ordinary Wages ($)",
                min_value=0.0,
                max_value=ORDINARY_WAGES_CEILING,
                format="%.2f"
            )
            
            additional_wages = st.number_input(
                "Additional Wages (Bonus, etc.) ($)",
                min_value=0.0,
                format="%.2f"
            )
            
            total_wages_ytd = st.number_input(
                "Total Wages Year-to-Date ($)",
                min_value=0.0,
                format="%.2f"
            )

        if st.button("Calculate CPF Contributions", type="primary"):
            # Calculate contributions
            total_cpf, employee_share, employer_share = calculate_contributions(
                ordinary_wages,
                additional_wages,
                age_group,
                total_wages_ytd
            )
            
            # Calculate allocations
            medisave, special, ordinary = calculate_allocations(total_cpf, age_group)
            
            # Generate and display explanation
            explanation = generate_explanation(
                ordinary_wages,
                total_cpf,
                employee_share,
                employer_share,
                age_group,
                medisave,
                special,
                ordinary
            )
            
            st.markdown(explanation)
            
            # Display visualizations
            plot_contributions(total_cpf, employee_share, employer_share,
                             medisave, special, ordinary)
    
    with tab2:
        st.subheader("Future CPF Projections")
        
        # Display current age group for reference
        st.info(f"Your current age group is: {age_group}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            projection_years = st.slider(
                "Projection Period (Years)",
                min_value=1,
                max_value=40,
                value=20
            )
            
            salary_increment = st.slider(
                "Expected Annual Salary Increment (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.5
            ) / 100
            
            monthly_wage = st.number_input(
                "Monthly Ordinary Wages ($)",
                min_value=0.0,
                max_value=ORDINARY_WAGES_CEILING,
                value=ordinary_wages if ordinary_wages > 0 else 0.0,
                format="%.2f"
            )
        
        with col2:
            st.markdown("""
            ### Current Account Balances
            Enter your current CPF account balances for more accurate projections:
            """)
            
            current_oa = st.number_input("Current Ordinary Account Balance ($)", 
                                       min_value=0.0, format="%.2f")
            current_sa = st.number_input("Current Special Account Balance ($)", 
                                       min_value=0.0, format="%.2f")
            current_ma = st.number_input("Current MediSave Account Balance ($)", 
                                       min_value=0.0, format="%.2f")
        
        if st.button("Generate Projections", type="primary"):
            current_balances = {
                "OA": current_oa,
                "SA": current_sa,
                "MA": current_ma
            }
            
            # Calculate total contribution based on age group rates
            total_rate, _, _ = CPF_RATES[age_group]
            monthly_contribution = monthly_wage * total_rate
            
            # Calculate projections
            monthly_data = calculate_future_balance(
                monthly_contribution,
                projection_years,
                salary_increment
            )
            
            # Calculate milestones
            milestones = calculate_milestones(
                current_balances,
                monthly_contribution,
                age_group
            )
            
            # Display milestone information
            st.markdown(f"""
            ### 🎯 CPF Milestones
            Based on your current contribution patterns:
            
            * Basic Retirement Sum (${BRS_2024:,.2f}): {
                f"Will reach in approximately {milestones['BRS']} years" 
                if isinstance(milestones['BRS'], (int, float)) 
                else milestones['BRS']
            }
            * Full Retirement Sum (${FRS_2024:,.2f}): {
                f"Will reach in approximately {milestones['FRS']} years" 
                if isinstance(milestones['FRS'], (int, float)) 
                else milestones['FRS']
            }
            """)
            
            # Display projection chart
            fig = plot_future_projections(monthly_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display key insights
            st.markdown(f"""
            ### 📊 Key Insights
            
            * By year {projection_years}, your projected total CPF balance will be: ${monthly_data['Total'][-1]:,.2f}
            * Your Ordinary Account can potentially fund a property worth up to: ${min(monthly_data['OA'][-1] * 4, 1000000):,.2f}
            * Your Special Account growth benefits from the higher interest rate of 4% per annum
            * MediSave provides a healthcare safety net with a projected balance of ${monthly_data['MA'][-1]:,.2f}
            """)
    
    with tab3:
        st.subheader("CPF Educational Resources")
        
        # CPF Knowledge Base
        with st.expander("Understanding CPF Contribution Rates", expanded=True):
            st.markdown("""
            ### 📚 CPF Contribution Rates Explained
            
            Your CPF contribution rate depends on:
            1. Your age
            2. Your citizenship status
            3. Whether you're an employee, self-employed, or both
            
            #### Current Contribution Rates (2024)
            | Age Group | Total Rate | Employee's Share | Employer's Share |
            |-----------|------------|------------------|------------------|
            | ≤ 35 years | 37% | 20% | 17% |
            | 35-45 years | 37% | 20% | 17% |
            | 45-50 years | 37% | 20% | 17% |
            | 50-55 years | 37% | 20% | 17% |
            | 55-60 years | 26% | 13% | 13% |
            | 60-65 years | 16.5% | 8.5% | 8% |
            | > 65 years | 12.5% | 7.5% | 5% |
            """)

        # CPF Account Types
        with st.expander("CPF Account Types"):
            st.markdown("""
            ### 🏦 Understanding Your CPF Accounts

            #### 1. Ordinary Account (OA)
            - Used for housing, investment, insurance, and education
            - Base interest rate: 2.5% per annum
            - Common uses:
                * Down payment for property
                * Monthly mortgage payments
                * Investment in approved instruments
                * Education loans

            #### 2. Special Account (SA)
            - Specifically for retirement
            - Higher base interest rate: 4% per annum
            - Cannot be used for housing or education
            - Can be invested in selected investment products

            #### 3. MediSave Account (MA)
            - For healthcare expenses
            - Base interest rate: 4% per annum
            - Uses include:
                * Hospitalization costs
                * Approved medical insurance premiums
                * Selected outpatient treatments
                * MediShield Life premiums
            """)

        # Housing Section
        with st.expander("CPF and Housing"):
            st.markdown("""
            ### 🏠 Using CPF for Housing

            #### Maximum Property Value Based on CPF Usage
            Your maximum property value depends on:
            1. Available OA balance
            2. Monthly OA contribution
            3. Loan tenure
            4. Interest rates

            #### Key Considerations
            1. **Withdrawal Limits**
               - Up to 20% downpayment from OA
               - Monthly repayments from OA contributions

            2. **HDB vs Private Property**
               - Different rules apply
               - Different loan limits
               - Different downpayment requirements

            3. **CPF Housing Grant**
               - Available for eligible first-time buyers
               - Amount varies based on property type and income
            """)

        # Retirement Planning
        with st.expander("Retirement Planning"):
            st.markdown(f"""
            ### 🎯 Retirement Sums (2024)

            #### Basic Retirement Sum (BRS)
            - Current BRS: ${BRS_2024:,.2f}
            - Provides basic monthly payout
            - Can pledge property to halve required BRS

            #### Full Retirement Sum (FRS)
            - Current FRS: ${FRS_2024:,.2f}
            - Higher monthly payouts
            - Recommended for most retirees

            #### Enhanced Retirement Sum (ERS)
            - Current ERS: ${ERS_2024:,.2f}
            - Maximum monthly payouts
            - Optional top-up if you want higher payouts

            ### CPF LIFE
            - Provides lifelong monthly payouts
            - Starts from age 65
            - Different plans available:
                * Basic Plan
                * Standard Plan
                * Escalating Plan
            """)

        # Investment Options
        with st.expander("CPF Investment Options"):
            st.markdown("""
            ### 💹 Investment Schemes

            #### CPFIS-OA (Ordinary Account)
            - Can invest up to 35% in stocks and 10% in gold
            - Unit trusts
            - Investment-linked insurance products
            - Exchange traded funds (ETFs)
            - Government bonds

            #### CPFIS-SA (Special Account)
            - More restricted investment options
            - Focus on lower-risk investments
            - Government bonds
            - Selected unit trusts

            ### Key Considerations
            1. Returns not guaranteed
            2. Consider fees and charges
            3. Compare against base interest rates
            4. Assess your risk tolerance
            """)

    # Footer with additional information
    st.markdown("""
    ---
    ### 📝 Notes
    * All calculations are based on the latest CPF contribution rates and policies as of 2024
    * This calculator is for estimation purposes only
    * For official rates and policies, please visit the [CPF Website](https://www.cpf.gov.sg)
    * Interest rates used in projections:
        * Ordinary Account: 2.5% p.a.
        * Special Account: 4% p.a.
        * MediSave Account: 4% p.a.
    """)

if __name__ == "__main__":
    main()
