// src/components/HeadToHeadComparison.js
import React, { useState, useEffect } from 'react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, 
  Legend, ResponsiveContainer, Tooltip
} from 'recharts';
import apiService from '../services/apiService';
import { FaSpinner } from 'react-icons/fa';

const HeadToHeadComparison = ({ team1, team2 }) => {
  const [comparisonData, setComparisonData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!team1 || !team2) return;

    const fetchHeadToHead = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await apiService.getHeadToHead(team1, team2);
        
        // Set comparison data
        setComparisonData([
          { category: 'Attack', [team1]: data.stats.team1.attack, [team2]: data.stats.team2.attack },
          { category: 'Defense', [team1]: data.stats.team1.defense, [team2]: data.stats.team2.defense },
          { category: 'Possession', [team1]: data.stats.team1.possession, [team2]: data.stats.team2.possession },
          { category: 'Form', [team1]: data.stats.team1.form, [team2]: data.stats.team2.form },
          { category: 'Home/Away', [team1]: data.stats.team1.homeAdvantage, [team2]: data.stats.team2.awayPerformance }
        ]);
        
        setHistory(data.history || []);
      } catch (error) {
        console.error('Error fetching head-to-head data:', error);
        setError('Failed to load comparison data. Please try again.');
        
        // Fallback to sample data if API fails
        setComparisonData([
          { category: 'Attack', [team1]: 80, [team2]: 65 },
          { category: 'Defense', [team1]: 70, [team2]: 75 },
          { category: 'Possession', [team1]: 65, [team2]: 60 },
          { category: 'Form', [team1]: 85, [team2]: 70 },
          { category: 'Home/Away', [team1]: 75, [team2]: 60 }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchHeadToHead();
  }, [team1, team2]);

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

  if (!comparisonData) {
    return (
      <div className="bg-gray-50 p-4 rounded-md text-gray-500 text-center">
        <p>Select two teams to compare their performance.</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Head-to-Head: {team1} vs {team2}</h3>
      
      {/* Radar Chart Comparison */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={comparisonData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="category" />
              <PolarRadiusAxis angle={30} domain={[0, 100]} />
              <Radar
                name={team1}
                dataKey={team1}
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.6}
              />
              <Radar
                name={team2}
                dataKey={team2}
                stroke="#82ca9d"
                fill="#82ca9d"
                fillOpacity={0.6}
              />
              <Legend />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Previous Matchups */}
      {history.length > 0 && (
        <div className="mt-6">
          <h4 className="text-md font-medium mb-2">Previous Matchups</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Competition</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Winner</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {history.map((match, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{match.date}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{match.competition}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {team1} {match.team1Score} - {match.team2Score} {team2}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {match.team1Score > match.team2Score ? (
                        <span className="text-blue-600">{team1}</span>
                      ) : match.team1Score < match.team2Score ? (
                        <span className="text-green-600">{team2}</span>
                      ) : (
                        <span className="text-gray-500">Draw</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default HeadToHeadComparison;