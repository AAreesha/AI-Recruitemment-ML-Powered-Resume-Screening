# AI-Driven Recruitment: ML-Powered Resume Screening and Candidate Profiling

## Project Overview

This project aims to revolutionize talent acquisition by leveraging machine learning for resume screening and candidate profiling. It addresses the challenge of matching candidates with job opportunities by automating the process of resume evaluation and job recommendation, making it more efficient and accurate.

The system is designed to extract key information from resumes, including skills, experience, and education, and match it with job requirements. The project includes various modules that work together to provide a comprehensive solution for both recruiters and job seekers.

## Key Features

- **Resume Categorization**: Predicts the job category based on the content of the resume.
- **Job Recommendation**: Provides the top 3 job opportunities that best match the candidate's profile.
- **Weak Resume Cluster Identification**: Identifies weaker resumes and offers skill improvement suggestions.
- **Gale-Shapley Matching**: Ensures that both candidate and recruiter preferences are matched.
- **LinkedIn Job Scraping**: Fetches job postings to keep the recommendations up-to-date.
- **Candidate Profiling**: Creates detailed profiles for candidates based on extracted data.

## Technologies Used

- **Python**: Core programming language for developing models and backend logic.
- **Machine Learning Models**: 
  - **Neural Networks**: Used for skill extraction and classification.
  - **Random Forest**: Applied for categorization and job prediction.
  - **Support Vector Machines (SVM)**: Utilized for data classification and analysis.
- **Sentence Transformers**: Specifically, the `all-MiniLM-L6-v2` model is used to generate 384-dimensional embeddings for resumes.
- **PyPDF2 & PyMuPDF**: Libraries for PDF text extraction.
- **spaCy**: For skill extraction using PhraseMatcher.
- **React**: Frontend framework for the web application.
- **Flask**: Backend framework for API development.
- **Firebase & Firestore**: Used for data storage and real-time database management.
- **Nodemailer**: For sending notification emails.

## Installation

### Prerequisites

- Python 3.x
- Node.js and npm
- React
- Flask

