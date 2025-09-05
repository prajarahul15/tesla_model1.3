import React, { useState } from 'react';

const FinancialStatements = ({ scenario, model, generateModel, loading }) => {
  const [activeStatement, setActiveStatement] = useState('income');

  const formatCurrency = (value) => {
    if (!value) return '$0';
    const absValue = Math.abs(value);
    if (absValue >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (absValue >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (absValue >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercent = (value) => {
    if (!value) return '0.0%';
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatNumber = (value) => {
    if (!value) return '0';
    return new Intl.NumberFormat('en-US').format(Math.round(value));
  };

  if (!model) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-600 mb-4">No financial model generated for {scenario} scenario</div>
        <button
          onClick={() => generateModel(scenario)}
          disabled={loading}
          className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          {loading ? 'Generating...' : 'Generate Financial Model'}
        </button>
      </div>
    );
  }

  const statements = [
    { id: 'income', name: 'Income Statement', data: model.income_statements },
    { id: 'balance', name: 'Balance Sheet', data: model.balance_sheets },
    { id: 'cashflow', name: 'Cash Flow', data: model.cash_flow_statements }
  ];

  const years = [2025, 2026, 2027, 2028, 2029];

  const renderIncomeStatement = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Income Statement
            </th>
            {years.map(year => (
              <th key={year} className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {year}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          <tr className="bg-blue-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total Revenue</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-blue-600">
                {formatCurrency(stmt.total_revenue)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Automotive Revenue</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(stmt.automotive_revenue)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Services Revenue</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(stmt.services_revenue)}
              </td>
            ))}
          </tr>
          <tr className="bg-red-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total COGS</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-600">
                ({formatCurrency(stmt.total_cogs)})
              </td>
            ))}
          </tr>
          <tr className="bg-green-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Gross Profit</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-green-600">
                {formatCurrency(stmt.total_gross_profit)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Gross Margin</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatPercent(stmt.gross_margin)}
              </td>
            ))}
          </tr>
          <tr className="bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Operating Expenses</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                ({formatCurrency(stmt.total_operating_expenses)})
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• R&D</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                ({formatCurrency(stmt.research_development)})
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• SG&A</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                ({formatCurrency(stmt.selling_general_admin)})
              </td>
            ))}
          </tr>
          <tr className="bg-purple-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Operating Income</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-purple-600">
                {formatCurrency(stmt.operating_income)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Operating Margin</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatPercent(stmt.operating_margin)}
              </td>
            ))}
          </tr>
          <tr className="bg-yellow-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Net Income</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-yellow-700">
                {formatCurrency(stmt.net_income)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Net Margin</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatPercent(stmt.net_margin)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">EPS</td>
            {model.income_statements.map((stmt, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                ${stmt.earnings_per_share?.toFixed(2)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );

  const renderBalanceSheet = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Balance Sheet
            </th>
            {years.map(year => (
              <th key={year} className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {year}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          <tr className="bg-blue-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">ASSETS</td>
            <td colSpan={5}></td>
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Current Assets</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                {formatCurrency(bs.total_current_assets)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Cash & Equivalents</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(bs.cash_and_equivalents)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Accounts Receivable</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(bs.accounts_receivable)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Inventory</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(bs.inventory)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Non-Current Assets</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                {formatCurrency(bs.total_non_current_assets)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Net PP&E</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(bs.net_ppe)}
              </td>
            ))}
          </tr>
          <tr className="bg-green-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">Total Assets</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-green-600">
                {formatCurrency(bs.total_assets)}
              </td>
            ))}
          </tr>
          <tr className="bg-red-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">LIABILITIES</td>
            <td colSpan={5}></td>
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Current Liabilities</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                {formatCurrency(bs.total_current_liabilities)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Non-Current Liabilities</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold">
                {formatCurrency(bs.total_non_current_liabilities)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">Total Liabilities</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold">
                {formatCurrency(bs.total_liabilities)}
              </td>
            ))}
          </tr>
          <tr className="bg-purple-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">Shareholders' Equity</td>
            {model.balance_sheets.map((bs, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-purple-600">
                {formatCurrency(bs.total_shareholders_equity)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );

  const renderCashFlow = () => (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cash Flow Statement
            </th>
            {years.map(year => (
              <th key={year} className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {year}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          <tr className="bg-blue-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Operating Cash Flow</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-blue-600">
                {formatCurrency(cf.operating_cash_flow)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Net Income</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(cf.net_income)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• Depreciation</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(cf.depreciation_amortization)}
              </td>
            ))}
          </tr>
          <tr className="bg-red-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Investing Cash Flow</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-red-600">
                {formatCurrency(cf.investing_cash_flow)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 pl-8">• CapEx</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                {formatCurrency(cf.capital_expenditures)}
              </td>
            ))}
          </tr>
          <tr className="bg-purple-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Financing Cash Flow</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-purple-600">
                {formatCurrency(cf.financing_cash_flow)}
              </td>
            ))}
          </tr>
          <tr className="bg-green-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">Free Cash Flow</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-green-600">
                {formatCurrency(cf.free_cash_flow)}
              </td>
            ))}
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">Ending Cash</td>
            {model.cash_flow_statements.map((cf, idx) => (
              <td key={idx} className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold">
                {formatCurrency(cf.ending_cash)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Financial Statements - {scenario.charAt(0).toUpperCase() + scenario.slice(1)} Case
        </h3>
      </div>

      {/* Statement Navigation */}
      <div className="flex border-b border-gray-200 mb-6">
        {statements.map((statement) => (
          <button
            key={statement.id}
            onClick={() => setActiveStatement(statement.id)}
            className={`px-4 py-2 font-medium text-sm border-b-2 ${
              activeStatement === statement.id
                ? 'border-red-500 text-red-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {statement.name}
          </button>
        ))}
      </div>

      {/* Statement Content */}
      <div className="bg-white rounded-lg border shadow-sm">
        {activeStatement === 'income' && renderIncomeStatement()}
        {activeStatement === 'balance' && renderBalanceSheet()}
        {activeStatement === 'cashflow' && renderCashFlow()}
      </div>
    </div>
  );
};

export default FinancialStatements;