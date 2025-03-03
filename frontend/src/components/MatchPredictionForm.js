// src/components/MatchPredictionForm.js
import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';
import { FaSpinner } from 'react-icons/fa';

const MatchPredictionForm = ({ onPredictionResult }) => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    homeTeam: '',
    awayTeam: '',
    matchDate: new Date().toISOString().split('T')[0],
    matchTime: '15:00',
    teamToPredict: 'home',
    goalsFor: 1.5,
    goalsAgainst: 1.0,
    shots: 12.0,
    shotsOnTarget: 5.0,
    distance: 16.0,
    freeKicks: 1.0,
    penalties: 0.0,
    penaltyAttempts: 0.0
  });

  useEffect(() => {
    // Fetch teams when component mounts
    const fetchTeams = async () => {
      try {
        const teamsData = await apiService.getTeams();
        setTeams(teamsData);
      } catch (error) {
        // If API fails, use some default teams
        setTeams([
          'Arsenal', 'Aston Villa', 'Brentford', 'Brighton', 
          'Chelsea', 'Crystal Palace', 'Everton', 'Leeds United',
          'Leicester City', 'Liverpool', 'Manchester City', 'Manchester United',
          'Newcastle United', 'Norwich City', 'Southampton', 'Tottenham Hotspur',
          'Watford', 'West Ham United', 'Wolverhampton Wanderers'
        ]);
      }
    };
    
    fetchTeams();
  }, []);

  // Update form data
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle number inputs
  const handleNumberChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value)
    }));
  };

  // Submit prediction
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await apiService.predictMatchEnsemble(formData);
      onPredictionResult(result);
    } catch (error) {
      console.error('Prediction failed:', error);
      alert('Failed to make prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">Match Prediction</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Match Details */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Match Details</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Match Date</label>
                <input
                  type="date"
                  name="matchDate"
                  value={formData.matchDate}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Kickoff Time</label>
                <input
                  type="time"
                  name="matchTime"
                  value={formData.matchTime}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Home Team</label>
                <select
                  name="homeTeam"
                  value={formData.homeTeam}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                >
                  <option value="">Select Home Team</option>
                  {teams.map(team => (
                    <option key={`home-${team}`} value={team}>{team}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Away Team</label>
                <select
                  name="awayTeam"
                  value={formData.awayTeam}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                  disabled={!formData.homeTeam}
                >
                  <option value="">Select Away Team</option>
                  {teams
                    .filter(team => team !== formData.homeTeam)
                    .map(team => (
                      <option key={`away-${team}`} value={team}>{team}</option>
                    ))
                  }
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Team to Predict</label>
                <div className="mt-2 space-x-4">
                  <label className="inline-flex items-center">
                    <input
                      type="radio"
                      name="teamToPredict"
                      value="home"
                      checked={formData.teamToPredict === 'home'}
                      onChange={handleChange}
                      className="form-radio h-4 w-4 text-primary"
                    />
                    <span className="ml-2">Home Team</span>
                  </label>
                  
                  <label className="inline-flex items-center">
                    <input
                      type="radio"
                      name="teamToPredict"
                      value="away"
                      checked={formData.teamToPredict === 'away'}
                      onChange={handleChange}
                      className="form-radio h-4 w-4 text-primary"
                    />
                    <span className="ml-2">Away Team</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          {/* Team Form */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Team Form Stats (Last 3 Games)</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Goals For (Avg)</label>
                <input
                  type="number"
                  name="goalsFor"
                  value={formData.goalsFor}
                  onChange={handleNumberChange}
                  min="0"
                  max="5"
                  step="0.1"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Goals Against (Avg)</label>
                <input
                  type="number"
                  name="goalsAgainst"
                  value={formData.goalsAgainst}
                  onChange={handleNumberChange}
                  min="0"
                  max="5"
                  step="0.1"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Shots (Avg)</label>
                <input
                  type="number"
                  name="shots"
                  value={formData.shots}
                  onChange={handleNumberChange}
                  min="0"
                  max="30"
                  step="0.5"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Shots on Target (Avg)</label>
                <input
                  type="number"
                  name="shotsOnTarget"
                  value={formData.shotsOnTarget}
                  onChange={handleNumberChange}
                  min="0"
                  max="15"
                  step="0.5"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                />
              </div>
              
              <details className="mt-4">
                <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                  Additional Statistics (Optional)
                </summary>
                
                <div className="mt-3 space-y-4 p-4 bg-gray-50 rounded-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Shot Distance (Avg)</label>
                    <input
                      type="number"
                      name="distance"
                      value={formData.distance}
                      onChange={handleNumberChange}
                      min="0"
                      max="50"
                      step="0.1"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Free Kicks (Avg)</label>
                    <input
                      type="number"
                      name="freeKicks"
                      value={formData.freeKicks}
                      onChange={handleNumberChange}
                      min="0"
                      max="10"
                      step="0.1"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Penalties (Avg)</label>
                    <input
                      type="number"
                      name="penalties"
                      value={formData.penalties}
                      onChange={handleNumberChange}
                      min="0"
                      max="5"
                      step="0.1"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Penalty Attempts (Avg)</label>
                    <input
                      type="number"
                      name="penaltyAttempts"
                      value={formData.penaltyAttempts}
                      onChange={handleNumberChange}
                      min="0"
                      max="5"
                      step="0.1"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                    />
                  </div>
                </div>
              </details>
            </div>
          </div>
        </div>
        
        <div className="mt-8 flex justify-center">
          <button
            type="submit"
            disabled={loading || !formData.homeTeam || !formData.awayTeam}
            className="px-6 py-3 bg-primary text-white rounded-md shadow-sm hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center">
                <FaSpinner className="animate-spin mr-2" />
                Predicting...
              </span>
            ) : (
              'Predict Match Outcome'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default MatchPredictionForm;