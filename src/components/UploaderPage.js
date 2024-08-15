import React, { useState } from 'react';
import axios from 'axios';
import '../App.css'; // Ensure you have a CSS file for styling

function UploaderPage() {
  const [resumeFiles, setResumeFiles] = useState([]);
  const [jobFiles, setJobFiles] = useState([]);
  const [jobPositions, setJobPositions] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    if (event.target.name === 'resumes') {
      setResumeFiles(event.target.files);
    } else if (event.target.name === 'jobs') {
      setJobFiles(event.target.files);
    }
  };

  const handleJobPositionsChange = (event) => {
    setJobPositions(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    Array.from(resumeFiles).forEach((file) => formData.append('resumes', file));
    Array.from(jobFiles).forEach((file) => formData.append('jobs', file));
    try {
      const res = await axios.post('http://localhost:5000/upload', formData, {
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

  const formatRecommendations = (recommendations, weakerCluster, resumeNames) => {
    const formattedRecommendations = Object.entries(recommendations).map(([index, recs], idx) => (
      <div key={idx} className="recommendation-box">
        <h4>Resume {index} ({resumeNames[index]}):</h4> {/* Show name if available */}
        {recs.map((rec, i) => (
          <div key={i} className="recommendation-category">
            <div dangerouslySetInnerHTML={{ __html: rec }} />
          </div>
        ))}
      </div>
    ));

    return (
      <div>
        <h3>Weaker Cluster (Cluster {weakerCluster}):</h3>
        {formattedRecommendations.length > 0 ? (
          formattedRecommendations
        ) : (
          <p>No recommendations available.</p>
        )}
      </div>
    );
  };

  return (
    <div className="App">
      <h1>Resume and Job Position Uploader</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="resumes">Upload Resumes:</label>
          <input
            type="file"
            id="resumes"
            name="resumes"
            multiple
            onChange={handleFileChange}
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
            onChange={handleFileChange}
            className="file-input"
          />
        </div>
        <div className="form-group">
          <label htmlFor="jobPositions">Job Positions (optional):</label>
          <textarea
            id="jobPositions"
            name="jobPositions"
            value={jobPositions}
            onChange={handleJobPositionsChange}
            placeholder="Enter job positions here..."
            className="textarea"
          />
        </div>
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Uploading...' : 'Submit'}
        </button>
      </form>
      {response && (
        <div className="response">
          <h2>Results:</h2>
          <div className="recommendations-container">
            {formatRecommendations(response.recommendations, response.weaker_cluster, response.resume_names)}
          </div>
        </div>
      )}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default UploaderPage;
