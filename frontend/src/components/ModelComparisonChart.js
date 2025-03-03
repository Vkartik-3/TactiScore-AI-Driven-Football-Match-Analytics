// src/components/ModelComparisonChart.js
import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, ComposedChart
} from 'recharts';
import { FaSpinner } from 'react-icons/fa';

const ModelComparisonChart = ({ predictionResult }) => {
  // If no model comparison data is available, show placeholder
  if (!predictionResult || !predictionResult.model_comparison) {
    return (
      <div className="bg-gray-50 p-4 rounded-md text-gray-500 text-center">
        <p>No model comparison data available for this prediction.</p>
      </div>
    );
  }

  const { rf_only_probability, ensemble_probability, probability_difference } = predictionResult.model_comparison;

  // Prepare data for bar chart
  const comparisonData = [
    { name: 'RandomForest', value: rf_only_probability * 100 },
    { name: 'Ensemble', value: ensemble_probability * 100 },
  ];

  // Prepare data for improvement indication
  const improvementText = probability_difference > 0 
    ? `The ensemble model improved prediction probability by ${(probability_difference * 100).toFixed(1)}%`
    : `The ensemble model reduced prediction probability by ${(Math.abs(probability_difference) * 100).toFixed(1)}%`;

  // Color for bars based on prediction outcome
  const getBarColor = (probability) => {
    if (probability < 40) return '#ef4444'; // red
    if (probability < 60) return '#f59e0b'; // amber
    return '#10b981'; // green
  };

  return (
    <div className="card mt-8">
      <h2 className="text-xl font-bold mb-4">Model Comparison</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Bar Chart Comparison */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-md font-medium mb-4">Win Probability by Model</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={comparisonData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: 'Win Probability (%)', angle: -90, position: 'insideLeft' }} domain={[0, 100]} />
                <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Win Probability']} />
                <Legend />
                <Bar dataKey="value" name="Win Probability" fill={(entry) => getBarColor(entry.value)} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Improvement Details */}
        <div className="bg-white p-4 rounded-lg shadow flex flex-col">
          <h3 className="text-md font-medium mb-4">Model Improvement Analysis</h3>
          
          <div className="flex items-center justify-center bg-gray-50 p-4 rounded-md mb-4">
            <div className="text-center">
              <p className="text-lg font-semibold text-gray-700">Probability Difference</p>
              <p className={`text-3xl font-bold ${probability_difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {probability_difference >= 0 ? '+' : ''}{(probability_difference * 100).toFixed(1)}%
              </p>
            </div>
          </div>
          
          <div className="mt-2">
            <h4 className="font-medium mb-2">Key Findings:</h4>
            <ul className="list-disc pl-5 space-y-2 text-sm">
              <li>
                RandomForest model predicts a win probability of <span className="font-medium">{(rf_only_probability * 100).toFixed(1)}%</span>
              </li>
              <li>
                Ensemble model predicts a win probability of <span className="font-medium">{(ensemble_probability * 100).toFixed(1)}%</span>
              </li>
              <li>{improvementText}</li>
              <li>
                {probability_difference >= 0 
                  ? "The ensemble model appears to be more confident in its prediction"
                  : "The RandomForest model appears to be more confident in its prediction"}
              </li>
            </ul>
          </div>
          
          <div className="mt-auto">
            <p className="text-xs text-gray-500 italic">
              The ensemble model combines RandomForest and XGBoost algorithms to improve prediction accuracy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelComparisonChart;