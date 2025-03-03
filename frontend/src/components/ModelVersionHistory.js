// src/components/ModelVersionHistory.js
import React, { useState, useEffect } from 'react';
import {
 Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
   ComposedChart, Scatter
} from 'recharts';
import apiService from '../services/apiService';
import { FaSpinner } from 'react-icons/fa';

const ModelVersionHistory = () => {
  const [versionData, setVersionData] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('accuracy');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Available metrics to display
  const availableMetrics = [
    { id: 'accuracy', name: 'Accuracy' },
    { id: 'precision', name: 'Precision' },
    { id: 'recall', name: 'Recall' },
    { id: 'f1', name: 'F1 Score' },
    { id: 'auc', name: 'AUC' }
  ];

  // Load model version data
  useEffect(() => {
    const fetchVersionData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch model versions
        const versions = await apiService.getModelVersions();
        setVersionData(versions);
        
        // Fetch performance comparison
        const comparison = await apiService.getModelPerformanceComparison();
        setComparisonData(comparison);
      } catch (err) {
        console.error('Error fetching model version data:', err);
        setError('Failed to load model version data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchVersionData();
  }, []);

  // Prepare timeline data for chart
  const prepareTimelineData = () => {
    if (!comparisonData) return [];
    
    // Flatten all versions with metrics
    const allVersions = [];
    Object.entries(comparisonData.model_comparisons).forEach(([modelType, versions]) => {
      versions.forEach(version => {
        // Only include if it has the selected metric
        if (version.metrics && version.metrics[selectedMetric] !== undefined) {
          allVersions.push({
            ...version,
            modelType,
            metricValue: version.metrics[selectedMetric],
            date: new Date(version.creation_date).getTime()
          });
        }
      });
    });
    
    // Sort by date
    return allVersions.sort((a, b) => a.date - b.date);
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <FaSpinner className="animate-spin text-primary text-2xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-md text-red-700">
        <p>{error}</p>
      </div>
    );
  }

  const timelineData = prepareTimelineData();

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">Model Version History</h2>
      
      {/* Metric Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Performance Metric</label>
        <select
          value={selectedMetric}
          onChange={(e) => setSelectedMetric(e.target.value)}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
        >
          {availableMetrics.map(metric => (
            <option key={metric.id} value={metric.id}>{metric.name}</option>
          ))}
        </select>
      </div>
      
      {/* Performance Timeline Chart */}
      {timelineData.length > 0 ? (
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <h3 className="text-lg font-semibold mb-4">Model Performance Timeline</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={timelineData}
                margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(timestamp) => new Date(timestamp).toLocaleDateString()}
                  label={{ value: 'Date', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  domain={[0, 1]}
                  label={{ value: selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1), angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value) => [value.toFixed(3), selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)]}
                  labelFormatter={(timestamp) => new Date(timestamp).toLocaleString()}
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-2 border rounded shadow">
                          <p className="font-medium">{data.version_name}</p>
                          <p>Type: {data.modelType}</p>
                          <p>Date: {new Date(data.date).toLocaleString()}</p>
                          <p className="text-primary font-medium">
                            {selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)}: {data.metricValue.toFixed(3)}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                {/* Lines for each model type */}
                {Object.keys(comparisonData?.model_comparisons || {}).map((modelType, index) => (
                  <Line
                    key={modelType}
                    type="monotone"
                    dataKey="metricValue"
                    data={timelineData.filter(d => d.modelType === modelType)}
                    name={modelType}
                    stroke={index === 0 ? "#8884d8" : "#82ca9d"}
                    activeDot={{ r: 8 }}
                    connectNulls
                  />
                ))}
                {/* Scatter points for all data points for better visibility */}
                <Scatter
                  dataKey="metricValue"
                  fill="#FF7300"
                  name="Data Points"
                  shape={(props) => {
                    const { cx, cy, fill } = props;
                    return <circle cx={cx} cy={cy} r={4} fill={fill} />;
                  }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="bg-gray-50 p-4 rounded-md text-gray-500 text-center mb-6">
          <p>No performance metrics data available for timeline visualization.</p>
        </div>
      )}
      
      {/* Version List Table */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Model Versions</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {versionData.map((version) => {
                // Find model in comparison data to get metrics
                let versionMetrics = null;
                if (comparisonData?.model_comparisons?.[version.model_type]) {
                  const matchingVersion = comparisonData.model_comparisons[version.model_type]
                    .find(v => v.version_name === version.version_name);
                  
                  if (matchingVersion) {
                    versionMetrics = matchingVersion.metrics;
                  }
                }
                
                return (
                  <tr key={version.version_name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {version.version_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {version.model_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(version.creation_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {versionMetrics ? (
                        <div className="flex items-center">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            versionMetrics.accuracy >= 0.7 ? 'bg-green-100 text-green-800' : 
                            versionMetrics.accuracy >= 0.5 ? 'bg-yellow-100 text-yellow-800' : 
                            'bg-red-100 text-red-800'
                          }`}>
                            {(versionMetrics.accuracy * 100).toFixed(1)}% acc
                          </span>
                          {versionMetrics.f1 && (
                            <span className="ml-2 text-xs text-gray-500">
                              F1: {(versionMetrics.f1 * 100).toFixed(1)}%
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">No metrics</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {versionData.length === 0 && (
          <div className="text-center py-4 text-gray-500">
            <p>No model versions found.</p>
          </div>
        )}
      </div>
      
      {/* Summary Stats */}
      {comparisonData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <h3 className="text-lg font-semibold mb-2">Total Versions</h3>
            <p className="text-3xl font-bold text-primary">{comparisonData.overview.total_versions}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <h3 className="text-lg font-semibold mb-2">Model Types</h3>
            <p className="text-3xl font-bold text-primary">{comparisonData.overview.model_types.length}</p>
            <p className="text-sm text-gray-500 mt-1">{comparisonData.overview.model_types.join(', ')}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <h3 className="text-lg font-semibold mb-2">With Metrics</h3>
            <p className="text-3xl font-bold text-primary">
              {comparisonData.overview.versions_with_metrics} / {comparisonData.overview.total_versions}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelVersionHistory;