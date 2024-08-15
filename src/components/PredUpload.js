import React, { useState } from 'react';
import axios from 'axios';


function PredUpload() {
  const [resumeFile, setResumeFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setResumeFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    if (resumeFile) {
      formData.append('resume', resumeFile);
    }

    try {
      const res = await axios.post('http://localhost:5000/pred', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log('Response:', res.data);  // Log response to inspect it
      setResponse(res.data);
    } catch (err) {
      console.error(err.response ? err.response.data : err);
      setError('Error uploading file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Resume Prediction Upload</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="resume">Upload Resume:</label>
          <input
            type="file"
            id="resume"
            name="resume"
            onChange={handleFileChange}
            className="file-input"
          />
        </div>
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Uploading...' : 'Submit'}
        </button>
      </form>
      {response && (
        <div className="response">
          <h2>Results:</h2>
          <p className="predicted-category">Category: {response.predicted_category}</p>
          {response.jobs && response.jobs.length > 0 && (
            <div className="jobs-container">
              <h3>Top Job Recommendations:</h3>
              {response.jobs.map((job, index) => (
                <div key={index} className="job-card">
                  <h3>Category: {job.category}</h3>
                  <p><strong>Title:</strong> {job.titles[0]}</p>
                  <p><strong>Company:</strong> {job.companies[0]}</p>
                  <p><strong>Description:</strong> {job.descriptions[0]}</p>
                  <p><strong>Score:</strong> {job.score}</p>
                  <a href={job.urls[0]} target="_blank" rel="noopener noreferrer">View Job</a>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default PredUpload;
