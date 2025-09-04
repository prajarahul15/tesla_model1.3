"""
Tesla Financial Calculator
Comprehensive financial modeling and DCF valuation engine
"""

import math
from typing import List, Dict, Tuple
from models.financial_models import *
from data.tesla_data import TESLA_BASE_YEAR_DATA, get_tesla_assumptions

class TeslaFinancialCalculator:
    """Main calculator for Tesla financial modeling"""
    
    def __init__(self):
        self.base_year_data = TESLA_BASE_YEAR_DATA
        
    def calculate_income_statement(self, assumptions: TeslaAssumptions, 
                                 previous_year_data: Dict = None) -> IncomeStatement:
        """Calculate complete income statement for given year and scenario"""
        
        # Revenue Calculations
        if previous_year_data:
            prev_auto_revenue = previous_year_data.get("automotive_revenue", self.base_year_data["automotive_revenue"])
            prev_services_revenue = previous_year_data.get("services_revenue", self.base_year_data["services_revenue"])
        else:
            prev_auto_revenue = self.base_year_data["automotive_revenue"]
            prev_services_revenue = self.base_year_data["services_revenue"]
        
        # Automotive Revenue = Previous Year * (1 + growth rate)
        automotive_revenue = prev_auto_revenue * (1 + assumptions.automotive_revenue_growth)
        
        # Services Revenue = Previous Year * (1 + services growth)
        services_revenue = prev_services_revenue * (1 + assumptions.services_revenue_growth)
        
        total_revenue = automotive_revenue + services_revenue
        
        # Cost of Goods Sold
        automotive_cogs = automotive_revenue * (1 - assumptions.gross_margin_automotive)
        services_cogs = services_revenue * (1 - assumptions.gross_margin_services)
        total_cogs = automotive_cogs + services_cogs
        
        # Gross Profit
        automotive_gross_profit = automotive_revenue - automotive_cogs
        services_gross_profit = services_revenue - services_cogs
        total_gross_profit = automotive_gross_profit + services_gross_profit
        gross_margin = total_gross_profit / total_revenue
        
        # Operating Expenses
        research_development = total_revenue * assumptions.rd_as_percent_revenue
        selling_general_admin = total_revenue * assumptions.sga_as_percent_revenue
        total_operating_expenses = research_development + selling_general_admin
        
        # Operating Income
        operating_income = total_gross_profit - total_operating_expenses
        operating_margin = operating_income / total_revenue
        
        # Other Income/Expenses
        interest_income = 0.02 * 28000000000  # 2% on cash (simplified)
        interest_expense = assumptions.interest_rate_on_debt * 9570000000  # Interest on debt
        other_income = 100000000  # Misc other income
        
        # Pre-tax Income
        pretax_income = operating_income + interest_income - interest_expense + other_income
        
        # Taxes
        if pretax_income > 0:
            income_tax_expense = pretax_income * assumptions.tax_rate
            effective_tax_rate = assumptions.tax_rate
        else:
            income_tax_expense = 0
            effective_tax_rate = 0
        
        # Net Income
        net_income = pretax_income - income_tax_expense
        net_margin = net_income / total_revenue if total_revenue > 0 else 0
        
        # Per Share Data
        shares_outstanding = 3178000000  # Relatively stable
        earnings_per_share = net_income / shares_outstanding
        
        return IncomeStatement(
            scenario=assumptions.scenario,
            year=assumptions.year,
            automotive_revenue=automotive_revenue,
            services_revenue=services_revenue,
            total_revenue=total_revenue,
            automotive_cogs=automotive_cogs,
            services_cogs=services_cogs,
            total_cogs=total_cogs,
            automotive_gross_profit=automotive_gross_profit,
            services_gross_profit=services_gross_profit,
            total_gross_profit=total_gross_profit,
            gross_margin=gross_margin,
            research_development=research_development,
            selling_general_admin=selling_general_admin,
            total_operating_expenses=total_operating_expenses,
            operating_income=operating_income,
            operating_margin=operating_margin,
            interest_income=interest_income,
            interest_expense=interest_expense,
            other_income=other_income,
            pretax_income=pretax_income,
            income_tax_expense=income_tax_expense,
            effective_tax_rate=effective_tax_rate,
            net_income=net_income,
            net_margin=net_margin,
            shares_outstanding=shares_outstanding,
            earnings_per_share=earnings_per_share
        )
    
    def calculate_balance_sheet(self, assumptions: TeslaAssumptions, 
                              income_stmt: IncomeStatement,
                              previous_balance_sheet: BalanceSheet = None,
                              cash_flow_stmt: CashFlowStatement = None) -> BalanceSheet:
        """Calculate balance sheet with working capital and asset projections"""
        
        # Starting values (from previous year or base year)
        if previous_balance_sheet:
            prev_cash = previous_balance_sheet.cash_and_equivalents
            prev_ppe = previous_balance_sheet.net_ppe
            prev_debt = previous_balance_sheet.long_term_debt
            prev_retained_earnings = previous_balance_sheet.retained_earnings
        else:
            prev_cash = self.base_year_data["cash_and_equivalents"]
            prev_ppe = 50000000000  # Estimated base year net PPE
            prev_debt = self.base_year_data["total_debt"]
            prev_retained_earnings = 20000000000  # Estimated base retained earnings
        
        # Current Assets
        # Cash - updated from cash flow statement if available
        if cash_flow_stmt:
            cash_and_equivalents = cash_flow_stmt.ending_cash
        else:
            cash_and_equivalents = prev_cash
        
        # Accounts Receivable = (DSO / 365) * Revenue
        accounts_receivable = (assumptions.days_sales_outstanding / 365) * income_stmt.total_revenue
        
        # Inventory = (DIO / 365) * COGS
        inventory = (assumptions.days_inventory_outstanding / 365) * income_stmt.total_cogs
        
        prepaid_expenses = income_stmt.total_revenue * 0.01  # 1% of revenue
        other_current_assets = income_stmt.total_revenue * 0.02  # 2% of revenue
        total_current_assets = (cash_and_equivalents + accounts_receivable + 
                              inventory + prepaid_expenses + other_current_assets)
        
        # Non-Current Assets
        # CapEx and Depreciation
        annual_capex = income_stmt.total_revenue * assumptions.capex_as_percent_revenue
        annual_depreciation = prev_ppe * assumptions.depreciation_rate
        
        # Net PPE = Previous PPE + CapEx - Depreciation
        net_ppe = prev_ppe + annual_capex - annual_depreciation
        accumulated_depreciation = annual_depreciation  # Simplified - would track cumulative
        property_plant_equipment = net_ppe + accumulated_depreciation
        
        intangible_assets = 2000000000  # Relatively stable
        other_non_current_assets = 5000000000  # Investments, etc.
        total_non_current_assets = net_ppe + intangible_assets + other_non_current_assets
        
        # Total Assets
        total_assets = total_current_assets + total_non_current_assets
        
        # Current Liabilities
        # Accounts Payable = (DPO / 365) * COGS
        accounts_payable = (assumptions.days_payable_outstanding / 365) * income_stmt.total_cogs
        
        accrued_liabilities = income_stmt.total_revenue * 0.03  # 3% of revenue
        current_portion_debt = prev_debt * 0.1  # 10% of debt is current
        other_current_liabilities = income_stmt.total_revenue * 0.02  # 2% of revenue
        total_current_liabilities = (accounts_payable + accrued_liabilities + 
                                   current_portion_debt + other_current_liabilities)
        
        # Non-Current Liabilities
        long_term_debt = prev_debt - current_portion_debt  # Remaining debt
        other_non_current_liabilities = 3000000000  # Relatively stable
        total_non_current_liabilities = long_term_debt + other_non_current_liabilities
        
        # Total Liabilities
        total_liabilities = total_current_liabilities + total_non_current_liabilities
        
        # Shareholders' Equity
        common_stock = 1000000000  # Relatively stable
        retained_earnings = prev_retained_earnings + income_stmt.net_income  # Add current year earnings
        other_equity = 500000000  # AOCI, etc.
        total_shareholders_equity = common_stock + retained_earnings + other_equity
        
        # Balance Check
        total_liab_and_equity = total_liabilities + total_shareholders_equity
        
        return BalanceSheet(
            scenario=assumptions.scenario,
            year=assumptions.year,
            cash_and_equivalents=cash_and_equivalents,
            accounts_receivable=accounts_receivable,
            inventory=inventory,
            prepaid_expenses=prepaid_expenses,
            other_current_assets=other_current_assets,
            total_current_assets=total_current_assets,
            property_plant_equipment=property_plant_equipment,
            accumulated_depreciation=accumulated_depreciation,
            net_ppe=net_ppe,
            intangible_assets=intangible_assets,
            other_non_current_assets=other_non_current_assets,
            total_non_current_assets=total_non_current_assets,
            total_assets=total_assets,
            accounts_payable=accounts_payable,
            accrued_liabilities=accrued_liabilities,
            current_portion_debt=current_portion_debt,
            other_current_liabilities=other_current_liabilities,
            total_current_liabilities=total_current_liabilities,
            long_term_debt=long_term_debt,
            other_non_current_liabilities=other_non_current_liabilities,
            total_non_current_liabilities=total_non_current_liabilities,
            total_liabilities=total_liabilities,
            common_stock=common_stock,
            retained_earnings=retained_earnings,
            other_equity=other_equity,
            total_shareholders_equity=total_shareholders_equity,
            total_liab_and_equity=total_liab_and_equity
        )