// import React, { useState } from 'react';
// import { BrowserRouter as Router, Route, Switch, Link} from 'react-router-dom'; // Use Routes instead of Switch
// import axios from 'axios';
// import './App.css'; // Ensure you have a CSS file for styling
// import BasicExample from './components/Navbar';
// import About from './About';

// function App() {
//   const [resumeFiles, setResumeFiles] = useState([]);
//   const [jobFiles, setJobFiles] = useState([]);
//   const [jobPositions, setJobPositions] = useState('');
//   const [response, setResponse] = useState(null);
//   const [error, setError] = useState(null);
//   const [loading, setLoading] = useState(false);

//   const handleFileChange = (event) => {
//     if (event.target.name === 'resumes') {
//       setResumeFiles(event.target.files);
//     } else if (event.target.name === 'jobs') {
//       setJobFiles(event.target.files);
//     }
//   };

//   const handleJobPositionsChange = (event) => {
//     setJobPositions(event.target.value);
//   };

//   const handleSubmit = async (event) => {
//     event.preventDefault();
//     setLoading(true);
//     setError(null);
//     setResponse(null);

//     const formData = new FormData();
//     Array.from(resumeFiles).forEach(file => formData.append('resumes', file));
//     Array.from(jobFiles).forEach(file => formData.append('jobs', file));
//     formData.append('jobPositions', jobPositions);

//     try {
//       const res = await axios.post('http://localhost:5000/upload', formData, {
//         headers: { 'Content-Type': 'multipart/form-data' },
//       });
//       setResponse(res.data);
//     } catch (err) {
//       setError('Error uploading files. Please try again.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const formatRecommendations = (recommendations, weakerCluster) => {
//     const formattedRecommendations = Object.entries(recommendations).map(([index, recs], idx) => (
//       <div key={idx} className="recommendation-box">
//         <h4>Resume {index}:</h4>
//         {recs.map((rec, i) => (
//           <div key={i} className="recommendation-category">
//             <div dangerouslySetInnerHTML={{ __html: rec }} />
//           </div>
//         ))}
//       </div>
//     ));

//     return (
//       <div>
//         <h3>Weaker Cluster (Cluster {weakerCluster}):</h3>
//         {formattedRecommendations.length > 0 ? (
//           formattedRecommendations
//         ) : (
//           <p>No recommendations available.</p>
//         )}
//       </div>
//     );
//   };

//   return (

//     <>
    
//     <BasicExample/>
    
//     <div className="App">
    
//       <h1>Resume and Job Position Uploader</h1>
//       <form onSubmit={handleSubmit} className="upload-form">
//         <div className="form-group">
//           <label htmlFor="resumes">Upload Resumes:</label>
//           <input
//             type="file"
//             id="resumes"
//             name="resumes"
//             multiple
//             onChange={handleFileChange}
//             className="file-input"
//           />
//         </div>
//         <div className="form-group">
//           <label htmlFor="jobs">Upload Job Descriptions:</label>
//           <input
//             type="file"
//             id="jobs"
//             name="jobs"
//             multiple
//             onChange={handleFileChange}
//             className="file-input"
//           />
//         </div>
//         <div className="form-group">
//           <label htmlFor="jobPositions">Job Positions (optional):</label>
//           <textarea
//             id="jobPositions"
//             name="jobPositions"
//             value={jobPositions}
//             onChange={handleJobPositionsChange}
//             placeholder="Enter job positions here..."
//             className="textarea"
//           />
//         </div>
//         <button type="submit" className="submit-button" disabled={loading}>
//           {loading ? 'Uploading...' : 'Submit'}
//         </button>
//       </form>
//       {response && (
//         <div className="response">
//           <h2>Results:</h2>
//           <div className="recommendations-container">
//             {formatRecommendations(response.recommendations, response.weaker_cluster)}
//           </div>
//         </div>
//       )}
//       {error && <p className="error-message">{error}</p>}
//     </div>
    
//     </>
//   );
// }

// export default App;
// App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import UploaderPage from './components/UploaderPage';

import PredUpload from './components/PredUpload';
import Home from './components/Home';
import MatchMaker from './components/MatchMaker';

function App() {
  return (
    <Router>
    
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/jobrec" element={<PredUpload />} />
        <Route path = "/service" element={<UploaderPage/>}/>
        <Route path = "/mm" element={<MatchMaker/>}/>
  
  
      </Routes>
    </Router>
  );
}

export default App;
