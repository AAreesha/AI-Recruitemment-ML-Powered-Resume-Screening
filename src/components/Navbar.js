import React from 'react';
import './Navbar.css'
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="navbar">
    <div className="navbar-brand">TalentShift</div>
    <ul className="navbar-links">
      <li><Link to="/">Home</Link></li>
      <li><Link to="/about">Job Recommendation</Link></li>
      <li><Link to="/service">Service</Link></li>
      <li><Link to="/mm">Contact</Link></li>
    </ul>
  </nav>

  );
}

export default Navbar;
