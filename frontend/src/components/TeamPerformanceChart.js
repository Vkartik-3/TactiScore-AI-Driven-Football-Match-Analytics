// src/components/TeamPerformanceChart.js
import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import apiService from '../services/apiService';
import { FaSpinner } from 'react-icons/fa';

const TeamPerformanceChart = ({ teamName }) => {
  const [performanceData, setPerformanceData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!teamName) return;

    const fetchTeamStats = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const stats = await apiService.getTeamStats(teamName);
        
        // Process data for chart
        const chartData = stats.matches.map(match => ({
          date: new Date(match.date).toLocaleDateString(),
          points: match.result === 'W' ? 3 : match.result === 'D' ? 1 : 0,
          goalsFor: match.goalsFor,
          goalsAgainst: match.goalsAgainst,
          result: match.result,
          opponent: match.opponent,
          venue: match.venue
        }));
        
        setPerformanceData(chartData);
      } catch (error) {
        console.error('Error fetching team performance data:', error);
        setError('Failed to load team performance data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchTeamStats();
  }, [teamName]);

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

  if (!performanceData.length) {
    return (
      <div className="bg-gray-50 p-4 rounded-md text-gray-500 text-center">
        <p>No performance data available for {teamName}.</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{teamName} - Form Analysis</h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Points Trend */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="text-md font-medium mb-2">Points Trend</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={performanceData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 3]} ticks={[0, 1, 3]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="points" 
                  stroke="#3b82f6" 
                  activeDot={{ r: 8 }}
                  name="Points"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Goals Analysis */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="text-md font-medium mb-2">Goals Analysis</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={performanceData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="goalsFor" 
                  stackId="1"
                  stroke="#10b981" 
                  fill="#d1fae5"
                  name="Goals For" 
                />
                <Area 
                  type="monotone" 
                  dataKey="goalsAgainst" 
                  stackId="2"
                  stroke="#ef4444" 
                  fill="#fee2e2"
                  name="Goals Against" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Recent Results Table */}
      <div className="mt-6">
        <h4 className="text-md font-medium mb-2">Recent Results</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Opponent</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Venue</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Result</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {performanceData.slice(0, 10).map((match, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{match.date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{match.opponent}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{match.venue}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      match.result === 'W' ? 'bg-green-100 text-green-800' : 
                      match.result === 'D' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {match.result === 'W' ? 'Win' : match.result === 'D' ? 'Draw' : 'Loss'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {match.goalsFor} - {match.goalsAgainst}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {match.points}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TeamPerformanceChart;