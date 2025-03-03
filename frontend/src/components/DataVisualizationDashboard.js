// src/components/DataVisualizationDashboard.js
import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import apiService from '../services/apiService';
import { FaSpinner } from 'react-icons/fa';

const DataVisualizationDashboard = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teams, setTeams] = useState([]);

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Fetch insights data based on selected team
  const fetchInsights = async (team = '') => {
    setLoading(true);
    setError(null);
    
    try {
      // Use team parameter if provided
      const data = await apiService.getDataInsights(team);
      setInsights(data);
      
      // Extract teams for dropdown if not already loaded
      if (data.teamPerformance) {
        if (!teams.length) {
          setTeams(Object.keys(data.teamPerformance));
        }
        if (!selectedTeam) {
          setSelectedTeam(team || Object.keys(data.teamPerformance)[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching data insights:', error);
      setError('Failed to load data insights. Please try again.');
      
      // Create sample data for development/testing
      const sampleData = {
        resultDistribution: [
          { name: 'Win', value: 45 },
          { name: 'Draw', value: 25 },
          { name: 'Loss', value: 30 }
        ],
        venueAnalysis: {
          Home: { Win: 60, Draw: 20, Loss: 20 },
          Away: { Win: 30, Draw: 30, Loss: 40 }
        },
        teamPerformance: {
          'Manchester City': { Win: 75, Draw: 15, Loss: 10, WinPercent: 75 },
          'Liverpool': { Win: 70, Draw: 20, Loss: 10, WinPercent: 70 },
          'Chelsea': { Win: 65, Draw: 15, Loss: 20, WinPercent: 65 }
        },
        statsCorrelation: [
          { stat: 'Shots on Target', correlation: 0.75 },
          { stat: 'Goals For', correlation: 0.72 },
          { stat: 'Possession', correlation: 0.58 },
          { stat: 'Distance', correlation: -0.32 },
          { stat: 'Goals Against', correlation: -0.65 }
        ]
      };
      
      setInsights(sampleData);
      setTeams(Object.keys(sampleData.teamPerformance));
      setSelectedTeam(Object.keys(sampleData.teamPerformance)[0]);
    } finally {
      setLoading(false);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchInsights();
  }, []);

  // Handle team selection change
  const handleTeamChange = (e) => {
    const team = e.target.value;
    setSelectedTeam(team);
    fetchInsights(team);  // Fetch new data when team changes
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

  if (!insights) {
    return (
      <div className="bg-gray-50 p-4 rounded-md text-gray-500 text-center">
        <p>No data insights available. Please upload match data first.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">Data Insights</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Result Distribution */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Match Result Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={insights.resultDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                >
                  {insights.resultDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Home vs Away Analysis */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Home vs Away Performance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={[
                  { 
                    venue: 'Home', 
                    Win: insights.venueAnalysis.Home.Win, 
                    Draw: insights.venueAnalysis.Home.Draw, 
                    Loss: insights.venueAnalysis.Home.Loss 
                  },
                  { 
                    venue: 'Away', 
                    Win: insights.venueAnalysis.Away.Win, 
                    Draw: insights.venueAnalysis.Away.Draw, 
                    Loss: insights.venueAnalysis.Away.Loss 
                  }
                ]}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="venue" />
                <YAxis label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Win" stackId="a" fill="#4ade80" />
                <Bar dataKey="Draw" stackId="a" fill="#fbbf24" />
                <Bar dataKey="Loss" stackId="a" fill="#f87171" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Team Performance */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Team Performance</h3>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Team</label>
            <select
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              value={selectedTeam || ''}
              onChange={handleTeamChange}
            >
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>
          
          {selectedTeam && (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Win', value: insights.teamPerformance[selectedTeam].Win },
                      { name: 'Draw', value: insights.teamPerformance[selectedTeam].Draw },
                      { name: 'Loss', value: insights.teamPerformance[selectedTeam].Loss }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                  >
                    <Cell fill="#4ade80" />
                    <Cell fill="#fbbf24" />
                    <Cell fill="#f87171" />
                  </Pie>
                  <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
          
          <div className="mt-4 text-center">
            {selectedTeam && (
              <p className="font-semibold text-lg">
                Win Rate: <span className="text-primary">{insights.teamPerformance[selectedTeam].WinPercent}%</span>
              </p>
            )}
          </div>
        </div>
        
        {/* Stats Correlation with Winning */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Statistics Correlation with Winning</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={insights.statsCorrelation}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[-1, 1]} />
                <YAxis dataKey="stat" type="category" />
                <Tooltip formatter={(value) => [`${value.toFixed(2)}`, 'Correlation']} />
                <Bar 
                  dataKey="correlation" 
                  fill={(value) => value >= 0 ? "#4ade80" : "#f87171"}
                  barSize={20}
                >
                  {insights.statsCorrelation.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.correlation >= 0 ? "#4ade80" : "#f87171"} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="mt-6 text-sm text-gray-600">
        <p className="font-medium">Key Insights:</p>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Home teams have a {insights.venueAnalysis.Home.Win - insights.venueAnalysis.Away.Win}% higher win rate than away teams</li>
          <li>{selectedTeam} has a win rate of {insights.teamPerformance[selectedTeam].WinPercent}%, placing them {teams.indexOf(selectedTeam) + 1}/{teams.length} in the dataset</li>
          <li>The most influential statistic for winning is {insights.statsCorrelation[0].stat} with a correlation of {insights.statsCorrelation[0].correlation.toFixed(2)}</li>
        </ul>
      </div>
    </div>
  );
};

export default DataVisualizationDashboard;