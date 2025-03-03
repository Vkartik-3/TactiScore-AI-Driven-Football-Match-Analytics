// src/components/Navbar.js
import React from 'react';
import { FaFutbol, FaChartLine, FaUpload } from 'react-icons/fa';

const Navbar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'predict', label: 'Predict Match', icon: <FaFutbol /> },
    { id: 'data', label: 'View Data', icon: <FaChartLine /> },
    { id: 'upload', label: 'Upload Data', icon: <FaUpload /> }
  ];
  
  return (
    <nav className="bg-primary text-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-2">
            <FaFutbol className="text-2xl" />
            <span className="text-xl font-bold">Football Prediction System</span>
          </div>
          
          <div className="flex space-x-6">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md transition-colors ${
                  activeTab === tab.id 
                    ? 'bg-primary-dark text-white' 
                    : 'text-white/80 hover:text-white hover:bg-primary-dark/50'
                }`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;