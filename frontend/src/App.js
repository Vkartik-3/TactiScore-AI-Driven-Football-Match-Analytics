// src/App.js
import React, { useState } from 'react';
import Navbar from './components/Navbar';
import MatchPredictionForm from './components/MatchPredictionForm';
import PredictionResults from './components/PredictionResults';
import DataVisualizationDashboard from './components/DataVisualizationDashboard';
import TeamPerformanceChart from './components/TeamPerformanceChart';
import HeadToHeadComparison from './components/HeadToHeadComparison';
import DataUpload from './components/DataUpload';

function App() {
  const [activeTab, setActiveTab] = useState('predict');
  const [predictionResult, setPredictionResult] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);

  const handlePredictionResult = (result) => {
    setPredictionResult(result);
    setSelectedTeam(result.team);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'predict' && (
          <>
            <MatchPredictionForm onPredictionResult={handlePredictionResult} />
            
            {predictionResult && (
              <>
                <PredictionResults prediction={predictionResult} />
                
                <div className="mt-10 grid grid-cols-1 gap-8">
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <TeamPerformanceChart teamName={selectedTeam} />
                  </div>
                  
                  {predictionResult.team && predictionResult.opponent && (
                    <div className="bg-white p-6 rounded-lg shadow-md">
                      <HeadToHeadComparison 
                        team1={predictionResult.team} 
                        team2={predictionResult.opponent} 
                      />
                    </div>
                  )}
                </div>
              </>
            )}
          </>
        )}
        
        {activeTab === 'data' && (
          <DataVisualizationDashboard />
        )}
        
        {activeTab === 'upload' && (
          <DataUpload />
          // src/App.js (continued)
        )}
      </main>
      
      <footer className="bg-gray-800 text-white py-6 mt-10">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div>
              <h3 className="text-lg font-bold">Football Prediction System</h3>
              <p className="text-sm text-gray-400 mt-1">
                Predicting match outcomes using machine learning
              </p>
            </div>
            
            <div className="mt-4 md:mt-0">
              <p className="text-sm text-gray-400">
                For educational purposes only. Do not use for betting.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
export default App;