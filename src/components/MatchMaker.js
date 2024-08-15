import React, { useState } from 'react';
import axios from 'axios';

function MatchMaker() {
  const [resumeFiles, setResumeFiles] = useState([]);
  const [jobFiles, setJobFiles] = useState([]);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleResumeFilesChange = (event) => {
    setResumeFiles(event.target.files);
  };

  const handleJobFilesChange = (event) => {
    setJobFiles(event.target.files);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    Array.from(resumeFiles).forEach(file => formData.append('resumes', file));
    Array.from(jobFiles).forEach(file => formData.append('jobs', file));

    try {
      const res = await axios.post('http://localhost:5000/process_resumes', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log('Response:', res.data);  // Log response to inspect it
      setResponse(res.data);
    } catch (err) {
      console.error(err.response ? err.response.data : err);
      setError('Error uploading files. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Process Resumes and Job Descriptions</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="resumes">Upload Resumes:</label>
          <input
            type="file"
            id="resumes"
            name="resumes"
            multiple
            onChange={handleResumeFilesChange}
            className="file-input"
          />
        </div>
        <div className="form-group">
          <label htmlFor="jobs">Upload Job Descriptions:</label>
          <input
            type="file"
            id="jobs"
            name="jobs"
            multiple
            onChange={handleJobFilesChange}
            className="file-input"
          />
        </div>
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>
      {response && (
        <div className="response">
          <h2>Results:</h2>
          {response.matches && Object.keys(response.matches).length > 0 && (
            <div className="matches-container">
              <h3>Matched Candidates:</h3>
              {Object.entries(response.matches).map(([job, candidates], index) => (
                <div key={index} className="job-match">
                  <h3>Job: {job}</h3>
                  {candidates.map(([candidate, score], scoreIndex) => (
                    <div key={scoreIndex} className="candidate-card">
                      <p><strong>Candidate:</strong> {candidate}</p>
                      <p><strong>Score:</strong> {score.toFixed(2)}</p>
                    </div>
                  ))}
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

export default MatchMaker;
