import React from 'react';
import { Link } from 'react-router-dom'; // Import Link for navigation
import './FeatureBox.css'; // Import CSS for styling

const FeatureBox = ({ icon, title, description, link }) => {
  return (
    <Link to={link} className="feature-box-link">
      <div className="feature-box" style={{ cursor: 'pointer' }}>
        <img src={icon} alt={`${title} icon`} className="feature-icon" />
        <h3 className="feature-title">{title}</h3>
        <p className="feature-description">{description}</p>
      </div>
    </Link>
  );
};

export default FeatureBox;
