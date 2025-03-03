// src/components/DataUpload.js
import React, { useState } from 'react';
import { FaUpload, FaSpinner, FaCheck, FaExclamationTriangle } from 'react-icons/fa';
import apiService from '../services/apiService';

const DataUpload = () => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);

  // Handle drag events
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  // Handle drop event
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  // Handle file input change
  const handleChange = (e) => {
    e.preventDefault();
    
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };
  
  // Process selected file
  const handleFile = (file) => {
    if (file.type !== 'text/csv') {
      setUploadStatus('error');
      setUploadResult('Only CSV files are allowed');
      return;
    }
    
    setFile(file);
    setUploadStatus(null);
    setUploadResult(null);
  };

  // Upload file to server
  const uploadFile = async () => {
    if (!file) return;
    
    setUploading(true);
    setUploadStatus(null);
    setUploadResult(null);
    
    try {
      const result = await apiService.uploadData(file);
      setUploadStatus('success');
      setUploadResult(`Successfully uploaded ${file.name}. Processed ${result.rows} rows and ${result.columns} columns.`);
    } catch (error) {
      setUploadStatus('error');
      setUploadResult(error.response?.data?.detail || 'Error uploading file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">Upload Match Data</h2>
      
      {/* File Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center ${
          dragActive ? 'border-primary bg-primary/10' : 'border-gray-300'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center">
          <FaUpload className="text-4xl text-gray-400 mb-4" />
          
          <p className="mb-4 text-sm text-gray-600">
            Drag and drop your CSV file here, or click to select
          </p>
          
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".csv"
            onChange={handleChange}
          />
          
          <label
            htmlFor="file-upload"
            className="px-4 py-2 bg-primary text-white rounded-md shadow-sm hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary cursor-pointer"
          >
            Select File
          </label>
          
          <p className="mt-2 text-xs text-gray-500">Only CSV files are supported</p>
        </div>
      </div>
      
      {/* Selected File Info */}
      {file && (
        <div className="mt-4 p-4 bg-gray-50 rounded-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-sm font-medium mr-2">{file.name}</span>
              <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(2)} KB)</span>
            </div>
            
            <button
              className="text-red-600 hover:text-red-800 text-sm"
              onClick={() => setFile(null)}
            >
              Remove
            </button>
          </div>
          
          <button
            className="mt-4 w-full px-4 py-2 bg-primary text-white rounded-md shadow-sm hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={uploadFile}
            disabled={uploading}
          >
            {uploading ? (
              <span className="flex items-center justify-center">
                <FaSpinner className="animate-spin mr-2" />
                Uploading...
              </span>
            ) : (
              'Upload File'
            )}
          </button>
        </div>
      )}
      
      {/* Upload Status */}
      {uploadStatus && (
        <div className={`mt-4 p-4 rounded-md ${
          uploadStatus === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          <div className="flex items-start">
            {uploadStatus === 'success' ? (
              <FaCheck className="flex-shrink-0 h-5 w-5 mr-2" />
            ) : (
              <FaExclamationTriangle className="flex-shrink-0 h-5 w-5 mr-2" />
            )}
            <span>{uploadResult}</span>
          </div>
        </div>
      )}
      
      {/* Data Format Guide */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-2">Data Format Requirements</h3>
        <p className="text-sm text-gray-600 mb-2">
          The CSV file should contain the following columns:
        </p>
        
        <div className="bg-gray-50 p-4 rounded-md">
          <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
            <li><span className="font-medium">date</span>: Match date (YYYY-MM-DD)</li>
            <li><span className="font-medium">team</span>: Team name</li>
            <li><span className="font-medium">opponent</span>: Opponent team name</li>
            <li><span className="font-medium">venue</span>: "Home" or "Away"</li>
            <li><span className="font-medium">result</span>: "W" (win), "D" (draw), or "L" (loss)</li>
            <li><span className="font-medium">gf</span>: Goals for</li>
            <li><span className="font-medium">ga</span>: Goals against</li>
            <li><span className="font-medium">sh</span>: Shots</li>
            <li><span className="font-medium">sot</span>: Shots on target</li>
          </ul>
          
          <p className="mt-3 text-sm text-gray-600">
            <span className="font-medium">Additional helpful columns:</span>
          </p>
          <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
            <li><span className="font-medium">dist</span>: Average shot distance</li>
            <li><span className="font-medium">fk</span>: Free kicks</li>
            <li><span className="font-medium">pk</span>: Penalties scored</li>
            <li><span className="font-medium">pkatt</span>: Penalties attempted</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DataUpload;