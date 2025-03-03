// src/components/PredictionResults.js
import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar, PieChart, Pie, Cell
} from 'recharts';

const PredictionResults = ({ prediction }) => {
  if (!prediction) return null;

  const { team, opponent, win_probability, prediction: outcome, key_factors } = prediction;

  // Determine color based on probability
  const getColor = (probability) => {
    if (probability < 0.4) return '#ef4444'; // red
    if (probability < 0.6) return '#f59e0b'; // amber
    return '#10b981'; // green
  };

  // Format probability for the gauge chart
  const gaugeData = [
    { name: 'Win Probability', value: win_probability * 100, fill: getColor(win_probability) }
  ];

  return (
    <div className="card mt-8">
      <h2 className="text-2xl font-bold mb-6">Prediction Results</h2>
      
      <div className="bg-gray-100 p-4 rounded-lg mb-6">
        <p className="text-xl font-semibold text-center">
          Prediction: {team} will 
          <span className={`font-bold mx-1 ${outcome === 'WIN' ? 'text-green-600' : 'text-red-600'}`}>
            {outcome === 'WIN' ? 'WIN' : 'NOT WIN'}
          </span> 
          against {opponent}
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Win Probability Chart */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Win Probability</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart 
                cx="50%" 
                cy="50%" 
                innerRadius="60%" 
                outerRadius="80%" 
                barSize={10} 
                data={gaugeData} 
                startAngle={180} 
                endAngle={0}
              >
                <RadialBar
                  background
                  clockWise
                  dataKey="value"
                  cornerRadius={10}
                  fill={getColor(win_probability)}
                />
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="text-2xl font-bold"
                  fill={getColor(win_probability)}
                >
                  {(win_probability * 100).toFixed(1)}%
                </text>
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Key Factors Chart */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Key Factors</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={key_factors}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 'auto']} />
                <YAxis dataKey="Feature" type="category" width={100} />
                <Tooltip
                  formatter={(value) => [value.toFixed(4), 'Importance']}
                  labelFormatter={(label) => `Feature: ${label}`}
                />
                <Bar dataKey="Importance" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">Prediction Explanation</h3>
        <div className="bg-blue-50 p-4 rounded-lg text-blue-800">
          <p>
            The model analyzed {team}'s form, venue advantage ({prediction.teamToPredict === 'home' ? 'Home' : 'Away'}), 
            and historical performance against {opponent}.
          </p>
          <p className="mt-2">
            Key factors in this prediction include recent goal-scoring record ({prediction.goalsFor} goals per game),
            defensive record ({prediction.goalsAgainst} goals conceded per game), and shooting efficiency
            ({prediction.shotsOnTarget} shots on target from {prediction.shots} attempts).
          </p>
        </div>
      </div>
      
      <div className="mt-6 text-center text-sm text-gray-500">
        <p>Note: This prediction is based on historical data and should be used for educational purposes only.</p>
      </div>
    </div>
  );
};

export default PredictionResults;