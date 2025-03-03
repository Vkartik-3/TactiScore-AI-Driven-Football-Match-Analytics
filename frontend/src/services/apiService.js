// src/services/apiService.js
import axios from 'axios';

// Base URL for API
const API_BASE_URL = 'http://localhost:8000';

const apiService = {
  // Fetch available teams
  getTeams: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/teams/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching teams:', error);
      throw error;
    }
  },

  // Predict match outcome
  predictMatch: async (matchData) => {
    try {
      // Format the data correctly
      const formattedData = {
        home_team: matchData.homeTeam,
        away_team: matchData.awayTeam,
        match_date: matchData.matchDate,
        match_time: matchData.matchTime,
        team_to_predict: matchData.teamToPredict,
        goals_for: parseFloat(matchData.goalsFor),
        goals_against: parseFloat(matchData.goalsAgainst),
        shots: parseFloat(matchData.shots),
        shots_on_target: parseFloat(matchData.shotsOnTarget)
      };
      
      // Add optional fields if they exist
      if (matchData.distance) formattedData.distance = parseFloat(matchData.distance);
      if (matchData.freeKicks) formattedData.free_kicks = parseFloat(matchData.freeKicks);
      if (matchData.penalties) formattedData.penalties = parseFloat(matchData.penalties);
      if (matchData.penaltyAttempts) formattedData.penalty_attempts = parseFloat(matchData.penaltyAttempts);
      
      // Try the simplified prediction endpoint first (which should be more reliable)
      try {
        const response = await axios.post(`${API_BASE_URL}/predict-simple/`, formattedData);
        return response.data;
      } catch (simpleError) {
        console.warn('Simple prediction failed, trying regular endpoint:', simpleError);
        // Fall back to regular endpoint
        const response = await axios.post(`${API_BASE_URL}/predict/`, formattedData);
        return response.data;
      }
    } catch (error) {
      console.error('Error predicting match:', error);
      throw error;
    }
  },

  // Upload data file
  uploadData: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/upload-data/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading data:', error);
      throw error;
    }
  },

  // Get team statistics
  getTeamStats: async (teamName) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/team-stats/${teamName}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching stats for ${teamName}:`, error);
      throw error;
    }
  },

  // Get head-to-head statistics
  getHeadToHead: async (team1, team2) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/head-to-head/${team1}/${team2}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching head-to-head stats:', error);
      throw error;
    }
  },
// In src/services/apiService.js - Add this method

// Predict match with ensemble model
predictMatchEnsemble: async (matchData) => {
  try {
    // Format the data correctly
    const formattedData = {
      home_team: matchData.homeTeam,
      away_team: matchData.awayTeam,
      match_date: matchData.matchDate,
      match_time: matchData.matchTime,
      team_to_predict: matchData.teamToPredict,
      goals_for: parseFloat(matchData.goalsFor),
      goals_against: parseFloat(matchData.goalsAgainst),
      shots: parseFloat(matchData.shots),
      shots_on_target: parseFloat(matchData.shotsOnTarget)
    };
    
    // Add optional fields if they exist
    if (matchData.distance) formattedData.distance = parseFloat(matchData.distance);
    if (matchData.freeKicks) formattedData.free_kicks = parseFloat(matchData.freeKicks);
    if (matchData.penalties) formattedData.penalties = parseFloat(matchData.penalties);
    if (matchData.penaltyAttempts) formattedData.penalty_attempts = parseFloat(matchData.penaltyAttempts);
    
    // Try ensemble prediction endpoint
    try {
      const response = await axios.post(`${API_BASE_URL}/predict-ensemble/`, formattedData);
      return response.data;
    } catch (error) {
      console.warn('Ensemble prediction failed, trying simple prediction:', error);
      // Fall back to simple prediction
      const response = await axios.post(`${API_BASE_URL}/predict-simple/`, formattedData);
      return response.data;
    }
  } catch (error) {
    console.error('Error predicting match:', error);
    throw error;
  }
},

// Add these methods to src/services/apiService.js

// Get all model versions
getModelVersions: async (modelType = null) => {
  try {
    const url = modelType 
      ? `${API_BASE_URL}/model-versions/?model_type=${modelType}`
      : `${API_BASE_URL}/model-versions/`;
    
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching model versions:', error);
    throw error;
  }
},

// Get details for a specific model version
getModelVersionDetails: async (versionName) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/model-versions/${versionName}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching version details for ${versionName}:`, error);
    throw error;
  }
},

// Get model performance comparison data
getModelPerformanceComparison: async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/model-performance-comparison/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching model performance comparison:', error);
    throw error;
  }
},
  // Get data insights
  getDataInsights: async (team = '') => {
    try {
      const url = team ? `${API_BASE_URL}/data-insights/${team}` : `${API_BASE_URL}/data-insights/`;
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching data insights:', error);
      throw error;
    }
  }
};

export default apiService;