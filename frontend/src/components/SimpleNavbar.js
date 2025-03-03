// src/components/SimpleNavbar.js
import React from 'react';

const SimpleNavbar = ({ activeTab, setActiveTab }) => {
  return (
    <div style={{ backgroundColor: "#0077cc", padding: "16px", color: "white" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", maxWidth: "1200px", margin: "0 auto" }}>
        <div>
          <h1 style={{ fontSize: "20px", fontWeight: "bold" }}>Football Prediction System</h1>
        </div>
        
        <div style={{ display: "flex", gap: "16px" }}>
          <button 
            style={{ 
              padding: "8px 16px", 
              backgroundColor: activeTab === 'predict' ? "#004c8c" : "transparent",
              border: "none",
              borderRadius: "4px",
              color: "white",
              cursor: "pointer"
            }}
            onClick={() => setActiveTab('predict')}
          >
            Predict Match
          </button>
          
          <button 
            style={{ 
              padding: "8px 16px", 
              backgroundColor: activeTab === 'data' ? "#004c8c" : "transparent",
              border: "none",
              borderRadius: "4px",
              color: "white",
              cursor: "pointer"
            }}
            onClick={() => setActiveTab('data')}
          >
            View Data
          </button>
          
          <button 
            style={{ 
              padding: "8px 16px", 
              backgroundColor: activeTab === 'upload' ? "#004c8c" : "transparent",
              border: "none",
              borderRadius: "4px",
              color: "white",
              cursor: "pointer"
            }}
            onClick={() => setActiveTab('upload')}
          >
            Upload Data
          </button>
          
          <button 
            style={{ 
              padding: "8px 16px", 
              backgroundColor: activeTab === 'models' ? "#004c8c" : "transparent",
              border: "none",
              borderRadius: "4px",
              color: "white",
              cursor: "pointer"
            }}
            onClick={() => setActiveTab('models')}
          >
            Model History
          </button>
        </div>
      </div>
    </div>
  );
};

export default SimpleNavbar;