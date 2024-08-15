import React from 'react';
import './Home.css'; // Import the CSS file
import home from '../assets/home.jpg';
import Navbar from './Navbar';
import banner from '../assets/banner.png';
import FeatureBox from './FeatureBox';
import one from '../assets/one.png';
import two from '../assets/two.png';
import three from '../assets/three.png';
import four from '../assets/four.png';


const Home = () => {
  return (
  <div className="container">
    <Navbar/>
    <img className="top-image" src={home} alt="Description of the image" />
    <h1 className='title'>AI-Driven Recruitment</h1>
    <h2 className="slogan"> Revolutionizing Hiring with ML-Powered Resume Screening</h2>
    <h3 className='project'>STRP II Project</h3>

    <div classname = "about-container">
        <h2 className='about'>About the Project</h2>
        <p className='about-p'>
        This research initiative aims to revolutionize recruitment through machine learning algorithms for resume screening and job matching. In today's job market, individuals face challenges navigating numerous postings and tailoring applications to specific requirements. By leveraging AI, particularly neural networks, this project seeks to optimize recruitment processes and enhance user experience. The main objective is to develop a neural network model for resume screening and job matching, trained on extensive datasets of resumes and job descriptions. This model will accurately match candidates to suitable opportunities and provide actionable insights to job seekers for optimizing their resumes, highlighting areas for skill and experience improvement. This comprehensive approach empowers candidates to refine their profiles and increase their competitiveness in the job market.
        </p>
    </div> 
    <img className="banner-image" src={banner} alt="Description of the image" />
    <h2 className='feature-boxes'>Feature Boxes</h2>
    <p className = 'feature-boxes-p'>Check out the main features of our project that make job matching and resume screening easier.</p>
    <div className="features-section">
   
        <FeatureBox 
          icon={one} 
          title="Smart Resume Categorization" 
          description="Automatically organizes resumes into relevant categories to enhance job matching."
          link = "/jobrec"
        
        />
        <FeatureBox 
          icon={two} 
          title="Top Jobs Finder" 
          description="Identifies and presents top job opportunities from LinkedIn."
        />
        <FeatureBox 
          icon={three} 
          title="Intelligent Matchmaking System" 
          description="Uses advanced algorithms to pair candidates with optimal job fits."
          link = "/mm"
        />
        <FeatureBox 
          icon={four} 
          title="Skill Enhancement Advisor" 
          description="Detects skill gaps and offers improvement tips for job seekers."
          link = "/service"
        />
      </div>
  </div>

  );
};

export default Home;
