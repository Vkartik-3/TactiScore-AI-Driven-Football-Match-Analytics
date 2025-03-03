// // src/App.js
// import React, { useState, useEffect } from 'react';
// // import Navbar from './components/Navbar';
// import MatchPredictionForm from './components/MatchPredictionForm';
// import PredictionResults from './components/PredictionResults';
// import DataVisualizationDashboard from './components/DataVisualizationDashboard';
// import TeamPerformanceChart from './components/TeamPerformanceChart';
// import HeadToHeadComparison from './components/HeadToHeadComparison';
// import DataUpload from './components/DataUpload';
// import ModelVersionHistory from './components/ModelVersionHistory';
// // import ModelComparisonChart from './components/ModelComparisonChart';
// import SimpleNavbar from './components/SimpleNavbar';

// function App() {
//   console.log("APP RENDERING");
//   // const [activeTab, setActiveTab] = useState('predict');
//   const [predictionResult, setPredictionResult] = useState(null);
//   const [selectedTeam, setSelectedTeam] = useState(null);

//   const urlParams = new URLSearchParams(window.location.search);
//   const tabParam = urlParams.get('tab');
//   const [activeTab, setActiveTab] = useState(tabParam || 'predict');
  
//   console.log("Current activeTab in App:", activeTab);
  
//   // Effect to log tab changes
//   useEffect(() => {
//     console.log("Tab changed to:", activeTab);
//   }, [activeTab]);
  
//   const handlePredictionResult = (result) => {
//     setPredictionResult(result);
//     setSelectedTeam(result.team);
//   };
  
//   const handleTabChange = (tab) => {
//     // console.log("CHANGING TAB TO:", tab);
//     // setActiveTab(tab);
//     window.location.href = `/?tab=${tab}`;
//   };
  
//   // Add a debug panel for direct tab switching
//   const DebugPanel = () => (
//     <div className="bg-yellow-100 p-4 mb-4 rounded-lg">
//       <p className="text-center mb-2">Debug Panel - Current Tab: <strong>{activeTab}</strong></p>
//       <div className="flex justify-center space-x-2">
//         <button 
//           className={`px-2 py-1 rounded ${activeTab === 'predict' ? 'bg-blue-600 text-white' : 'bg-blue-200'}`}
//           onClick={() => handleTabChange('predict')}
//         >
//           Predict
//         </button>
//         <button 
//           className={`px-2 py-1 rounded ${activeTab === 'data' ? 'bg-blue-600 text-white' : 'bg-blue-200'}`}
//           onClick={() => handleTabChange('data')}
//         >
//           Data
//         </button>
//         <button 
//           className={`px-2 py-1 rounded ${activeTab === 'upload' ? 'bg-blue-600 text-white' : 'bg-blue-200'}`}
//           onClick={() => handleTabChange('upload')}
//         >
//           Upload
//         </button>
//         <button 
//           className={`px-2 py-1 rounded ${activeTab === 'models' ? 'bg-blue-600 text-white' : 'bg-blue-200'}`}
//           onClick={() => handleTabChange('models')}
//         >
//           Models
//         </button>
//       </div>
//     </div>
//   );
  
//   return (
//     <div className="min-h-screen bg-gray-100">
//       <SimpleNavbar activeTab={activeTab} setActiveTab={handleTabChange} />
      
//       <main className="container mx-auto px-4 py-8">
//         {/* Add debug panel */}
//         <DebugPanel />
        
//         {/* Render the active tab */}
//         {activeTab === 'predict' && (
//           <>
//             <MatchPredictionForm onPredictionResult={handlePredictionResult} />
            
//             {predictionResult && (
//               <>
//                 <PredictionResults prediction={predictionResult} />
                
//                 <div className="mt-10 grid grid-cols-1 gap-8">
//                   <div className="bg-white p-6 rounded-lg shadow-md">
//                     <TeamPerformanceChart teamName={selectedTeam} />
//                   </div>
                  
//                   {predictionResult.team && predictionResult.opponent && (
//                     <div className="bg-white p-6 rounded-lg shadow-md">
//                       <HeadToHeadComparison 
//                         team1={predictionResult.team} 
//                         team2={predictionResult.opponent} 
//                       />
//                     </div>
//                   )}
//                 </div>
//               </>
//             )}
//           </>
//         )}
        
//         {activeTab === 'data' && (
//           <DataVisualizationDashboard />
//         )}
        
//         {activeTab === 'upload' && (
//           <DataUpload />
//         )}
        
//         {activeTab === 'models' && (
//           <div>
//             <h2 className="text-2xl font-bold mb-4">Model Version History</h2>
//             <ModelVersionHistory />
//           </div>
//         )}
//       </main>
      
//       <footer className="bg-gray-800 text-white py-6 mt-10">
//         <div className="container mx-auto px-4">
//           <div className="flex flex-col md:flex-row justify-between items-center">
//             <div>
//               <h3 className="text-lg font-bold">Football Prediction System</h3>
//               <p className="text-sm text-gray-400 mt-1">
//                 Predicting match outcomes using machine learning
//               </p>
//             </div>
            
//             <div className="mt-4 md:mt-0">
//               <p className="text-sm text-gray-400">
//                 For educational purposes only. Do not use for betting.
//               </p>
//             </div>
//           </div>
//         </div>
//       </footer>
//     </div>
//   );
// }

// export default App;

// src/App.js
import React, { useState } from 'react';
import Navbar from './components/Navbar';  // Switch back to original Navbar
import MatchPredictionForm from './components/MatchPredictionForm';
import PredictionResults from './components/PredictionResults';
import DataVisualizationDashboard from './components/DataVisualizationDashboard';
import TeamPerformanceChart from './components/TeamPerformanceChart';
import HeadToHeadComparison from './components/HeadToHeadComparison';
import DataUpload from './components/DataUpload';
import ModelVersionHistory from './components/ModelVersionHistory';

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
        )}
        
        {activeTab === 'models' && (
          <ModelVersionHistory />
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