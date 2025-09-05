import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DataOverview = () => {
  const [overviewData, setOverviewData] = useState(null);
  const [economicData, setEconomicData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOverviewData();
    fetchEconomicData();
  }, []);

  const fetchOverviewData = async () => {
    try {
      const response = await axios.get(`${API}/analytics/overview`);
      setOverviewData(response.data.data);
    } catch (err) {
      setError('Failed to fetch overview data');
      console.error('Overview data error:', err);
    }
  };

  const fetchEconomicData = async () => {
    try {
      const response = await axios.get(`${API}/analytics/economic-variables`);
      setEconomicData(response.data.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch economic data');
      console.error('Economic data error:', err);
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '£0';
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercent = (value) => {
    if (!value) return '0.0%';
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  if (!overviewData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">No data available</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-2">📊 Data Overview & Performance Analysis</h2>
        <p className="text-blue-100">Historical performance metrics and variance analysis across all profiles</p>
      </div>

      {/* Key Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Actual</h3>
          <div className="text-3xl font-bold text-blue-600">
            {formatCurrency(overviewData.total_actual)}
          </div>
          <p className="text-sm text-gray-600 mt-1">Across all profiles</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Plan</h3>
          <div className="text-3xl font-bold text-green-600">
            {formatCurrency(overviewData.total_plan)}
          </div>
          <p className="text-sm text-gray-600 mt-1">Budget targets</p>
        </div>

        <div className={`bg-white p-6 rounded-lg shadow-sm border-l-4 ${
          overviewData.total_variance >= 0 ? 'border-green-500' : 'border-red-500'
        }`}>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Variance</h3>
          <div className={`text-3xl font-bold ${
            overviewData.total_variance >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatPercent(overviewData.total_variance)}
          </div>
          <p className="text-sm text-gray-600 mt-1">Actual vs Plan</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-purple-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Profiles</h3>
          <div className="text-3xl font-bold text-purple-600">
            {overviewData.profile_breakdown.length}
          </div>
          <p className="text-sm text-gray-600 mt-1">Business profiles</p>
        </div>
      </div>

      {/* Profile Breakdown */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Profile Performance Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Profile</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Actual</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Plan</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Line Items</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {overviewData.profile_breakdown.map((profile, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {profile.profile}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                    {formatCurrency(profile.actual)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                    {formatCurrency(profile.plan)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-semibold ${
                    profile.variance >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercent(profile.variance)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                    {profile.line_items}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                    {profile.records}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Lineup Performance */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Lineup Performance Analysis</h3>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
          {overviewData.lineup_breakdown.map((lineup, idx) => (
            <div key={idx} className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-3">{lineup.lineup}</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Actual:</span>
                  <span className="text-sm font-medium">{formatCurrency(lineup.actual)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Plan:</span>
                  <span className="text-sm font-medium">{formatCurrency(lineup.plan)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Variance:</span>
                  <span className={`text-sm font-semibold ${
                    lineup.variance >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercent(lineup.variance)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Records:</span>
                  <span className="text-sm font-medium">{lineup.records}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Monthly Trends Chart */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Monthly Performance Trends</h3>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Month</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actual</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {overviewData.monthly_trends.map((month, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {month.DATE}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {formatCurrency(month.Actual)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {formatCurrency(month.Plan)}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-semibold ${
                      month.Variance >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercent(month.Variance)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Economic Variables Section */}
      {economicData && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Economic Variables Overview</h3>
            <p className="text-sm text-gray-600 mt-1">External economic indicators for multivariate analysis</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {economicData.variables.map((variable, idx) => (
                <div key={idx} className="bg-gray-50 p-3 rounded-lg text-center">
                  <div className="text-sm font-medium text-gray-900">
                    {variable.replace(/_/g, ' ')}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">Available for analysis</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataOverview;