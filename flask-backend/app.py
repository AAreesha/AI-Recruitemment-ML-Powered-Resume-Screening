from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import nltk
import spacy
from PyPDF2 import PdfReader
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from flask import Flask, request, render_template
import pickle
from PyPDF2 import PdfReader
import io
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from fuzzywuzzy import process

# Ensure NLTK downloads are in place
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)
CORS(app)

# Load pre-trained models and vectorizers
import os
base_dir = os.path.dirname(os.path.abspath(__file__))

rf_classifier_path = os.path.join(base_dir, 'models', 'rf_classifier_categorization.pkl')
tfidf_vectorizer_path = os.path.join(base_dir, 'models', 'tfidf_vectorizer_categorization.pkl')
rf_classifier_job_recommendation_path = os.path.join(base_dir, 'models', 'rf_classifier_job_recommendation.pkl')
tfidf_vectorizer_job_recommendation_path = os.path.join(base_dir, 'models', 'tfidf_vectorizer_job_recommendation.pkl')

# Load models with error handling
try:
    rf_classifier = pickle.load(open(rf_classifier_path, 'rb'))
    tfidf_vectorizer = pickle.load(open(tfidf_vectorizer_path, 'rb'))
    rf_classifier_job_recommendation = pickle.load(open(rf_classifier_job_recommendation_path, 'rb'))
    tfidf_vectorizer_job_recommendation = pickle.load(open(tfidf_vectorizer_job_recommendation_path, 'rb'))
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Error loading model: {e}")


# Skill categorization map
skill_categories = {
    "Programming Languages": [
        "Python", "Java", "C++", "C#", "JavaScript", "Ruby", "Swift", "Kotlin", "Go", "TypeScript", 
        "PHP", "R", "SQL", "Rust", "Scala", "Perl", "MATLAB", "VBA", "Groovy", "Julia", "Objective-C",
        "Lua", "Haskell", "Erlang", "Dart", "Shell Scripting", "Assembly Language", "COBOL", "Fortran",
        "F#", "Apex", "PowerShell", "ActionScript", "VHDL", "Verilog", "SML", "Smalltalk", "ML", "TCL",
        "XSLT", "AWK", "Lisp", "CLIPS", "HyperTalk", "Icon", "Scheme", "Prolog", "Common Lisp", "PostScript", 
        "OCaml"
    ],
    "Web Development": [
        "HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask",
        "Ruby on Rails", "Bootstrap", "jQuery", "Webpack", "SASS/SCSS", "Tailwind CSS", "Pug/Jade", "AJAX",
        "REST APIs", "GraphQL", "WebSockets", "JAMstack", "Next.js", "Nuxt.js", "Meteor.js", "Ember.js", 
        "Backbone.js", "Handlebars.js", "Underscore.js", "Mustache.js", "Bulma", "Semantic UI", "Foundation", 
        "WebRTC", "Progressive Web Apps (PWA)", "Content Management Systems (CMS)", "Server-Side Rendering (SSR)",
        "Static Site Generators (Gatsby, Hugo)", "API Gateway", "Single Page Applications (SPA)", "Responsive Design",
        "Mobile First Design", "User Authentication", "OAuth", "OpenID Connect", "HTTP/2", "WebAssembly",
        "Micro Frontends", "Internationalization (i18n)", "Localization (l10n)"
    ],
    "Software Development": [
        "Agile", "Scrum", "Kanban", "Git", "Continuous Integration", "Continuous Deployment", "DevOps",
        "Test-Driven Development (TDD)", "Pair Programming", "Code Review", "Feature Flags", "Refactoring",
        "Version Control", "Dependency Management", "Build Tools (Maven, Gradle)", "Code Coverage",
        "Static Code Analysis", "Software Development Life Cycle (SDLC)", "Design Patterns", "Microservices",
        "Containerization", "Docker", "Kubernetes", "Continuous Delivery", "Automated Testing", "User Stories",
        "Acceptance Testing", "Performance Testing", "Load Testing", "End-to-End Testing", "Integration Testing",
        "Regression Testing", "Code Documentation", "API Documentation", "Software Architecture", "Component-Based Design",
        "Event-Driven Design", "RESTful Services", "Code Optimization", "Legacy Systems Integration", "API Rate Limiting",
        "Schema Design", "Protocol Buffers", "GraphQL Resolvers", "Service-Oriented Architecture (SOA)",
        "Software Requirements Specification (SRS)", "System Integration", "Usability Testing", "Continuous Monitoring",
        "Issue Tracking"
    ],
    "Cloud Platforms": [
        "AWS", "Azure", "Google Cloud Platform", "Heroku", "IBM Cloud", "Docker", "Kubernetes", "Terraform",
        "CloudFormation", "Serverless Architectures", "Load Balancing", "Cloud Storage", "Cloud Databases",
        "AWS Lambda", "Azure Functions", "Google Cloud Functions", "Cloud Pub/Sub", "Cloud Monitoring", 
        "Cloud Security", "Cloud Networking", "Elastic Beanstalk", "S3", "EC2", "RDS", "DynamoDB", "BigQuery",
        "Cloud SQL", "Cloudflare", "CDN", "IAM", "VPC", "CloudWatch", "CloudTrail", "Autoscaling", "CloudFront",
        "Google App Engine", "Azure App Service", "Container Registry", "API Gateway", "Cloud Functions",
        "Cloud Interconnect", "Managed Kubernetes", "Cloud DevOps", "SaaS", "PaaS", "IaaS", "Edge Computing",
        "Multi-Cloud Strategy", "Cloud Cost Management", "Cloud Migration"
    ],
    "Databases": [
        "SQL (MySQL, PostgreSQL, MS SQL Server, Oracle)", "NoSQL (MongoDB, Cassandra, CouchDB, Redis)", "Firebase",
        "Elasticsearch", "SQLite", "MariaDB", "Amazon DynamoDB", "Apache HBase", "InfluxDB", "TimescaleDB",
        "Graph Databases (Neo4j)", "Data Warehousing (Redshift, BigQuery)", "Document Stores", "Columnar Databases",
        "Key-Value Stores", "Object-Oriented Databases", "Cloud Databases", "Database Clustering", "Replication",
        "Sharding", "Data Partitioning", "Data Migration", "Backup and Recovery", "Database Optimization",
        "SQL Query Optimization", "NoSQL Query Languages", "Schema Design", "Normalization", "Denormalization",
        "ACID Transactions", "CAP Theorem", "Database Security", "Indexing", "Full-Text Search", "Data Integrity",
        "Data Encryption", "Performance Tuning", "Data Archiving", "ETL", "Data Lakes", "Data Governance",
        "Data Modeling", "Data Federation", "Big Data Integration", "OLAP", "OLTP", "Query Caching",
        "Transaction Management", "Distributed Databases"
    ],
    "Data Science & Machine Learning": [
        "Pandas", "NumPy", "SciPy", "Scikit-Learn", "TensorFlow", "Keras", "PyTorch", "R", "Data Visualization",
        "Matplotlib", "Seaborn", "Plotly", "Statistical Analysis", "Big Data", "Data Mining", "Feature Engineering",
        "Dimensionality Reduction", "Time Series Analysis", "Natural Language Processing (NLP)", "Reinforcement Learning",
        "Deep Learning", "Anomaly Detection", "Predictive Modeling", "Clustering", "Classification", "Regression Analysis",
        "Ensemble Methods", "Neural Networks", "Hyperparameter Tuning", "Model Evaluation", "Cross-Validation",
        "A/B Testing", "Bayesian Inference", "Data Preprocessing", "Missing Value Imputation", "Data Scaling",
        "Data Cleaning", "Data Transformation", "Algorithm Selection", "Model Deployment", "Model Interpretation",
        "Data Annotation", "Feature Selection", "Model Serving", "Semi-Supervised Learning", "Transfer Learning",
        "Time Series Forecasting", "Sequence Modeling", "Generative Adversarial Networks (GANs)", "Outlier Detection",
        "Model Monitoring"
    ],
    "Systems & Networking": [
        "Linux", "Windows Server", "Networking Protocols", "Network Security", "Firewalls", "VPNs", "Load Balancers",
        "System Administration", "Shell Scripting", "Performance Tuning", "Network Design", "SNMP", "DHCP", 
        "Network Troubleshooting", "Wireless Networks", "Network Monitoring Tools", "Virtualization", "RAID Configurations",
        "Network Address Translation (NAT)", "IP Addressing", "Subnetting", "VLANs", "Network Protocols", "QoS",
        "MPLS", "TCP/IP Stack", "DNS Management", "Network Automation", "Configuration Management", "Network Forensics",
        "Network Access Control (NAC)", "Intrusion Detection Systems (IDS)", "Intrusion Prevention Systems (IPS)",
        "Network Segmentation", "System Monitoring", "System Backup and Recovery", "System Patching", "Server Hardening",
        "User Account Management", "Directory Services", "Authentication Protocols", "System Performance Metrics",
        "Log Management", "Network Traffic Analysis", "Wireless Security", "IPv6", "Network Optimization",
        "Data Encryption in Transit", "Data Encryption at Rest", "Remote Access Solutions"
    ],
    "Soft Skills" : [
    "Communication", "Teamwork", "Problem-Solving", "Critical Thinking", "Adaptability", "Time Management", 
    "Leadership", "Creativity", "Decision Making", "Interpersonal Skills", "Conflict Resolution", 
    "Emotional Intelligence", "Negotiation", "Project Management", "Customer Service", "Collaboration", 
    "Attention to Detail", "Work Ethic", "Organizational Skills", "Stress Management", "Flexibility", 
    "Active Listening", "Persuasion", "Empathy", "Mentoring", "Presentation Skills", "Goal Setting", 
    "Delegation", "Analytical Thinking", "Self-Motivation", "Networking", "Innovation", "Resourcefulness", 
    "Time Management", "Cultural Awareness", "Positive Attitude", "Ethical Judgment", "Open-Mindedness", 
    "Change Management", "Planning", "Decision Making", "Research Skills", "Public Speaking", "Negotiation Skills", 
    "Team Building", "Customer Relationship Management", "Relationship Management", "Assertiveness", "Patience"
    ],
    "Software Engineering": [
        "Object-Oriented Programming (OOP)", "Design Patterns", "Software Architecture", "Microservices", "Containerization",
        "Docker", "Kubernetes", "Continuous Integration", "Continuous Delivery", "Automated Testing", "Code Documentation",
        "API Documentation", "Agile Methodologies", "Scrum Framework", "Kanban", "Version Control", "Code Review",
        "Refactoring", "Code Optimization", "Software Requirements", "API Rate Limiting", "Service-Oriented Architecture",
        "Event-Driven Architecture", "RESTful Services", "GraphQL", "Legacy Systems Integration", "Component-Based Architecture",
        "Design by Contract", "Code Metrics", "Software Debugging", "Software Profiling", "Dependency Management",
        "Feature Toggles", "Performance Tuning", "End-to-End Testing", "Integration Testing", "System Design",
        "Architectural Patterns", "Domain-Driven Design", "CQRS", "Event Sourcing", "Data Modeling", "UML", "API Gateways",
        "Code Standards", "Technical Debt Management", "Service Discovery", "Distributed Systems", "Load Balancing",
        "Fault Tolerance"
    ],
    "Project Management": [
        "Project Planning", "Risk Management", "Resource Allocation", "Stakeholder Management", "Budgeting", "Scheduling",
        "Requirement Analysis", "Change Management", "Agile Coaching", "Project Metrics", "Gantt Charts", "Milestone Tracking",
        "Work Breakdown Structure (WBS)", "Issue Tracking", "Communication Plans", "Project Charter", "Scope Management",
        "Quality Assurance", "Team Leadership", "Conflict Resolution", "Performance Reporting", "Cost Management",
        "Earned Value Management (EVM)", "Time Management", "Procurement Management", "Vendor Management", "Project Closure",
        "Documentation Management", "Project Scheduling Software", "Critical Path Method", "Project Integration Management",
        "Project Stakeholder Analysis", "Agile Ceremonies", "Retrospectives", "User Acceptance Testing (UAT)", "Roadmaps",
        "Dependency Management", "Change Requests", "Project Performance Reviews", "Milestone Reviews", "Process Improvement",
        "Project Lifecycle Management", "Risk Mitigation Strategies", "Project Governance", "Resource Leveling", "Scope Creep Management",
        "Team Collaboration Tools", "Agile Metrics", "Project Evaluation", "Strategic Planning"
    ],
    "UI/UX Design": [
        "User Research", "Wireframing", "Prototyping", "User Testing", "Figma", "Adobe XD", "Sketch", "Usability Principles",
        "Interaction Design", "User Personas", "Journey Mapping", "A/B Testing", "Design Systems", "Accessibility (WCAG)",
        "Responsive Design", "Mobile Design", "User Flows", "Information Architecture", "Visual Design", "Typography",
        "Color Theory", "Iconography", "User Interface (UI) Design", "User Experience (UX) Design", "User-Centered Design",
        "Design Thinking", "High-Fidelity Mockups", "Low-Fidelity Wireframes", "Rapid Prototyping", "Heuristic Evaluation",
        "Usability Testing", "Interaction Prototyping", "Motion Design", "Storyboarding", "UI Kits", "Design Handoff",
        "Mobile-First Design", "Cross-Browser Testing", "User Research Methodologies", "Cognitive Psychology in Design",
        "Affordance", "Consistency", "Scalability", "Design Collaboration", "Brand Consistency", "Design Systems Management",
        "Feedback Loops", "Iterative Design", "Empathy Mapping", "Visual Hierarchy"
    ],
    "Cybersecurity": [
        "Penetration Testing", "Vulnerability Assessment", "Threat Modeling", "Encryption", "Security Protocols", "Incident Response",
        "Ethical Hacking", "Compliance (GDPR, HIPAA)", "Security Information and Event Management (SIEM)", "Risk Assessment",
        "Firewall Configuration", "Malware Analysis", "Security Auditing", "Identity and Access Management (IAM)",
        "Public Key Infrastructure (PKI)", "Network Security", "Application Security", "Data Security", "Endpoint Security",
        "Intrusion Detection Systems (IDS)", "Intrusion Prevention Systems (IPS)", "Security Policies", "Security Operations Center (SOC)",
        "Data Loss Prevention (DLP)", "Security Awareness Training", "Threat Intelligence", "Penetration Testing Tools",
        "Vulnerability Scanning Tools", "Security Compliance Audits", "Encryption Algorithms", "Security Best Practices",
        "Authentication Protocols", "Risk Management Frameworks", "Digital Forensics", "Security Incident Management",
        "Secure Software Development", "Incident Management", "Access Control Mechanisms", "Network Segmentation",
        "Security Patch Management", "Cyber Threat Landscape", "Data Breach Response", "Security Policies and Procedures",
        "Business Continuity Planning", "Disaster Recovery Planning", "Ethical Hacking Tools", "Security Metrics and Reporting",
        "Secure Network Design", "Zero Trust Security", "Advanced Persistent Threats (APT)"
    ],
    "Embedded Systems": [
        "Microcontrollers (Arduino, Raspberry Pi)", "Firmware Development", "IoT", "Real-Time Operating Systems (RTOS)",
        "Sensors & Actuators", "Communication Protocols (I2C, SPI, UART)", "Low-Level Programming", "Hardware Interfacing",
        "Wireless Communication (Bluetooth, Zigbee)", "Power Management", "Embedded C/C++", "System-on-Chip (SoC)",
        "Debugging Tools (JTAG, Logic Analyzers)", "PCB Design", "Embedded Linux", "RTOS Configuration", "Device Drivers",
        "Protocol Stacks", "Signal Processing", "Analog-Digital Converters", "Digital Signal Processing (DSP)",
        "Embedded Software Development", "Hardware-in-the-Loop (HIL) Testing", "Firmware Optimization", "Embedded System Design",
        "IoT Protocols (MQTT, CoAP)", "System Boot Processes", "Memory Management", "Interrupt Handling", "GPIO",
        "Real-Time Data Processing", "Hardware Security", "Embedded System Debugging", "Device Communication Interfaces",
        "Low Power Design", "UART Communication", "I2C Bus Management", "SPI Bus Management", "Embedded System Simulation",
        "Real-Time Communication", "Firmware Updates", "Microprocessor Architectures", "Embedded System Performance Testing",
        "Embedded System Integration", "Embedded System Validation", "System Configuration", "Wireless Sensor Networks",
        "IoT Security", "Embedded System Optimization", "System Power Consumption Analysis"
    ],
    "Hardware Design": [
        "PCB Design", "Digital Logic Design", "Circuit Simulation", "VHDL", "Verilog", "FPGA", "Embedded C/C++", "Analog Design",
        "Signal Processing", "RF Design", "Power Electronics", "Hardware Debugging", "Schematic Capture", "Layout Design",
        "DFM (Design for Manufacturing)", "Hardware-in-the-Loop (HIL) Testing", "Component Selection", "Thermal Management",
        "EMI/EMC Design", "High-Speed Design", "Signal Integrity", "Prototype Development", "Printed Circuit Board (PCB) Fabrication",
        "Design for Testability (DFT)", "Hardware Simulation Tools", "Electrostatic Discharge (ESD) Protection",
        "Battery Management Systems", "Microcontroller Interfaces", "Power Supply Design", "Memory Devices", "Interface Protocols (I2C, SPI, UART)",
        "Board Bring-Up", "Digital Signal Processing (DSP) Hardware", "ASIC Design", "Analog-to-Digital Converters (ADC)",
        "Digital-to-Analog Converters (DAC)", "High-Frequency Design", "Schematic Design", "Component Footprints",
        "Hardware Security", "Reliability Engineering", "Electromechanical Systems", "Rapid Prototyping", "CAD Tools for Hardware Design",
        "Hardware Testing"
    ]
}


import pandas as pd
from PyPDF2 import PdfReader


def pdftotext(file):
    try:
        # Read file content as bytes
        file_content = file.read()
        # Use PyPDF2 with bytes input
        reader = PdfReader(io.BytesIO(file_content))
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text
    except KeyError as e:
        print(f"KeyError while reading PDF: {e}")
        # Fallback to PyMuPDF with bytes input
        try:
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                text = ''
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            print(f"Error with PyMuPDF: {e}")
            return None


def scrape_linkedin_jobs(job_title_to_search, location, num_jobs_to_fetch=5):
    service = Service(r'C:\\Users\\user\\Desktop\\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)

    search_url = f"https://www.linkedin.com/jobs/{job_title_to_search.replace(' ', '-')}-jobs-{location.replace(' ', '-')}/"
    driver.get(search_url)

    company_names = []
    job_titles = []
    job_descriptions = []
    job_urls = []

    for i in range(2, 16):  # Adjust the range as needed
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Adjust sleep time as needed
            
            job_cards = driver.find_elements(By.CLASS_NAME, "base-card__full-link")
            for job_card in job_cards:
                job_urls.append(job_card.get_attribute("href"))
                if len(job_urls) >= num_jobs_to_fetch:
                    break

            if len(job_urls) >= num_jobs_to_fetch:
                break
        except Exception as e:
            print(f"Error scrolling page: {e}")
            break

    for job_url in job_urls:
        try:
            driver.get(job_url)
            time.sleep(2)  # Adjust sleep time as needed
            
            job_title = driver.find_element(By.CLASS_NAME, "top-card-layout__title").text
            company_name = driver.find_element(By.CLASS_NAME, "topcard__org-name-link").text
            
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "show-more-less-html__button"))
                )
                show_more_button.click()
                time.sleep(1)  # Adjust sleep time as needed
            except Exception as e:
                print(f"No 'Show more' button found for {job_title}: {e}")
            
            job_description = driver.find_element(By.CLASS_NAME, "show-more-less-html__markup").text

            job_titles.append(job_title)
            company_names.append(company_name)
            job_descriptions.append(job_description)

            if len(job_titles) >= num_jobs_to_fetch:
                break
        except Exception as e:
            print(f"Error retrieving job details for {job_url}: {e}")

    driver.quit()

    return job_titles, company_names, job_descriptions, job_urls


def cleanResume(txt):
    """
    Clean the resume text by removing URLs, retweets, special characters,
    non-ASCII characters, and extra spaces.
    """
    # Remove URLs
    clean_text = re.sub(r'http\S+\s', ' ', txt)
    # Remove RT and cc
    clean_text = re.sub(r'\b(RT|cc)\b', ' ', clean_text)
    # Remove hashtags
    clean_text = re.sub(r'#\S+\s', ' ', clean_text)
    # Remove mentions
    clean_text = re.sub(r'@\S+', ' ', clean_text)
    # Remove special characters
    clean_text = re.sub(r'[!"#$%&\'()*+,-./:;<=>?@\[\\\]^_`{|}~]', ' ', clean_text)
    # Remove non-ASCII characters
    clean_text = re.sub(r'[^\x00-\x7F]+', ' ', clean_text)
    # Remove extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text
    

def predict_category(resume_text):
    resume_text = cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer.transform([resume_text])
    predicted_category = rf_classifier.predict(resume_tfidf)[0]
    print("HELLO")
    return predicted_category

def preprocess_resume_text(resume_text):
    tokens = word_tokenize(resume_text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    normalized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    return ' '.join(normalized_tokens)

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

nlp = spacy.load('en_core_web_sm')

def extract_name(resume_text):
    # Use spaCy to process the text
    doc = nlp(resume_text)
    # Extract entities labeled as PERSON
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return "Unknown"

def preprocess_resumes_from_files(files):
    resume_texts = []
    resume_names = []
    for file in files:
        resume_text = extract_text_from_pdf(file)
        preprocessed_resume = preprocess_resume_text(resume_text)
        resume_texts.append(preprocessed_resume)
        resume_name = extract_name(resume_text)  # Extract the name
        resume_names.append(resume_name)  # Store the extracted name
        
    return resume_texts, resume_names



def categorize_recommendations(recommendations, categories):
    categorized_recommendations = {}
    for recommendation in recommendations:
        found = False
        for category, skills in categories.items():
            match, score = process.extractOne(recommendation, skills)
            if score > 90:  # Adjust the threshold as needed
                if category not in categorized_recommendations:
                    categorized_recommendations[category] = []
                categorized_recommendations[category].append(recommendation)
                found = True
                break
        # if not found:
        #     if "Uncategorized" not in categorized_recommendations:
        #         categorized_recommendations["Uncategorized"] = []
        #     categorized_recommendations["Uncategorized"].append(recommendation)
    
    return categorized_recommendations

def format_categorized_recommendations(categorized_recs):
    formatted_output = ""
    for category, skills in categorized_recs.items():
        formatted_output += f"<h4>Category: {category}</h4>"
        formatted_output += "<ol>"
        for skill in skills:
            formatted_output += f"<li>{skill}</li>"
        formatted_output += "</ol>"
    return formatted_output

def job_recommendation(resume_text):
    # Clean the resume text
    resume_text = cleanResume(resume_text)
    # Transform the text using TF-IDF vectorizer
    resume_tfidf = tfidf_vectorizer_job_recommendation.transform([resume_text])
    # Get the probability estimates for each category
    probs = rf_classifier_job_recommendation.predict_proba(resume_tfidf)[0]
    # Get the top three categories
    top_indices = probs.argsort()[-3:][::-1]
    top_categories = [rf_classifier_job_recommendation.classes_[index] for index in top_indices]
    top_probs = [probs[index] for index in top_indices]
    
    return top_categories, top_probs

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


def gale_shapely(candidates, recruiters):
    free_candidates = list(candidates.keys())
    engaged_candidates = {}
    engaged_recruiters = {r: None for r in recruiters}
    
    while free_candidates:
        candidate = free_candidates.pop(0)
        candidate_prefs = candidates[candidate]
        
        for _, job in candidate_prefs:
            if engaged_recruiters[job] is None:
                engaged_recruiters[job] = candidate
                engaged_candidates[candidate] = job
                break
            else:
                current_candidate = engaged_recruiters[job]
                if recruiters[job][candidate] > recruiters[job][current_candidate]:
                    engaged_recruiters[job] = candidate
                    engaged_candidates[candidate] = job
                    free_candidates.append(current_candidate)
                    break

    return engaged_candidates

model = SentenceTransformer('all-MiniLM-L6-v2')



def create_profile(file):
    text = pdftotext(file)
    if not text:
        return None

    text = text.replace("\n", " ").lower()
    name = os.path.splitext(file.filename)[0].split('_')[0].lower()

    profile = {
        "Candidate Name": name,
        "Text": text
    }

    return profile


def calculate_similarity(text1, text2):
    embedding1 = model.encode(text1)
    embedding2 = model.encode(text2)
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    similarity_scaled = similarity * 100
    return similarity_scaled

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'resumes' not in request.files or 'jobs' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        resume_files = request.files.getlist('resumes')
        job_files = request.files.getlist('jobs')

        if not resume_files or not job_files:
            return jsonify({'error': 'No resumes or job descriptions provided'}), 400

        resumes, resume_names = preprocess_resumes_from_files(resume_files)
        jobs = [extract_text_from_pdf(file) for file in job_files]

        model = SentenceTransformer('all-MiniLM-L6-v2')
        resume_embeddings = model.encode(resumes, show_progress_bar=True)
        job_embeddings = model.encode(jobs, show_progress_bar=True)

        def calculate_similarity_scores(resume_embeddings, job_embeddings):
            scores = []
            for resume_embedding in resume_embeddings:
                resume_scores = cosine_similarity([resume_embedding], job_embeddings).flatten()
                scores.append(resume_scores)
            return np.array(scores)

        similarity_scores = calculate_similarity_scores(resume_embeddings, job_embeddings)
        average_scores = np.mean(similarity_scores, axis=1)
        scores_array = average_scores.reshape(-1, 1)
        num_clusters = 3
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        clusters = kmeans.fit_predict(scores_array)
        resume_clusters = {i: cluster for i, cluster in enumerate(clusters)}

        cluster_scores = {}
        for cluster in range(num_clusters):
            cluster_members = [i for i, c in resume_clusters.items() if c == cluster]
            cluster_scores[cluster] = np.mean([average_scores[i] for i in cluster_members])

        weak_cluster = min(cluster_scores, key=cluster_scores.get)

        def extract_key_terms(texts):
            all_tokens = []
            for text in texts:
                tokens = preprocess_resume_text(text).split()
                all_tokens.extend(tokens)
            return Counter(all_tokens)

        job_terms = extract_key_terms(jobs)
        weak_indices = [i for i, cluster in resume_clusters.items() if cluster == weak_cluster]
        weak_resume_terms = extract_key_terms([resumes[i] for i in weak_indices])
        missing_terms = {term: count for term, count in job_terms.items() if term not in weak_resume_terms}

        recommendations = {}
        for i in weak_indices:
            weak_tokens = set(preprocess_resume_text(resumes[i]).split())
            missing_in_resume = [term for term in missing_terms.keys() if term not in weak_tokens]
            recommendations[i] = missing_in_resume

        formatted_recommendations = {}
        for i, recs in recommendations.items():
            if recs:
                categorized_recs = categorize_recommendations(recs, skill_categories)
                formatted_list = []
                for category, skills in categorized_recs.items():
                    formatted_output = format_categorized_recommendations({category: skills})
                    formatted_list.append(formatted_output)
                formatted_recommendations[i] = formatted_list
            else:
                formatted_recommendations[i] = ["No specific recommendations; consider reviewing overall content and experience."]

        # Return extracted names along with recommendations
        return jsonify({
            'resume_names': resume_names,
            'weaker_cluster': weak_cluster,
            'recommendations': formatted_recommendations
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route("/pred", methods=["POST"])
def pred():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['resume']
        filename = file.filename

        # Handle file based on its type
        if filename.endswith('.pdf'):
            text = pdftotext(file)  # Assuming this function reads PDF files
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        else:
            return jsonify({'error': 'Invalid file format. Allowed formats: TXT or PDF'}), 400

        # Predict category and get job recommendations
        predicted_category = predict_category(text)
        top_categories, top_probs = job_recommendation(text)
        
        jobs = []
        for category in top_categories:
            job_titles, company_names, job_descriptions, job_urls = scrape_linkedin_jobs(category, "Karachi Division, Sindh, Pakistan", num_jobs_to_fetch=1)
            jobs.append({
                'category': category,
                'titles': job_titles,
                'companies': company_names,
                'descriptions': job_descriptions,
                'urls': job_urls
            })

        return jsonify({
            'predicted_category': predicted_category,
            'top_categories': top_categories,
            'top_probs': top_probs,
            'jobs': jobs
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/process_resumes', methods=['POST'])
def process_resumes():
    try:
        if 'resumes' not in request.files or 'jobs' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        resume_files = request.files.getlist('resumes')
        job_files = request.files.getlist('jobs')

        if not resume_files or not job_files:
            return jsonify({'error': 'No resumes or job descriptions provided'}), 400

        # Extract profiles from resumes
        profiles = []
        for file in resume_files:
            profile = create_profile(file)
            if profile:
                profiles.append(profile)

        # Convert profiles to DataFrame
        profiles_df = pd.DataFrame(profiles)

        # Extract job texts
        job_postings = {}
        for file in job_files:
            job_title = os.path.splitext(file.filename)[0]
            job_text = pdftotext(file)
            if job_text:
                job_postings[job_title] = job_text

        # Calculate similarity scores and generate preference lists
        candidates_pref = {}
        recruiters_pref = {job: {} for job in job_postings}

        for _, resume in profiles_df.iterrows():
            candidate_name = resume['Candidate Name']
            candidates_pref[candidate_name] = []
            for job_title, job_text in job_postings.items():
                score = calculate_similarity(resume['Text'], job_text)
                candidates_pref[candidate_name].append((score, job_title))
                recruiters_pref[job_title][candidate_name] = score

        # Sort preferences
        for candidate in candidates_pref:
            candidates_pref[candidate].sort(reverse=True, key=lambda x: x[0])

        for recruiter in recruiters_pref:
            recruiters_pref[recruiter] = dict(sorted(recruiters_pref[recruiter].items(), key=lambda x: x[1], reverse=True))

        # Apply Gale-Shapley algorithm
        matches = gale_shapely(candidates_pref, recruiters_pref)

        # Prepare response
        sorted_matches = sorted(matches.items(), key=lambda x: (x[1], recruiters_pref[x[1]][x[0]]), reverse=True)
        grouped_matches = {}
        for candidate, job in sorted_matches:
            if job not in grouped_matches:
                grouped_matches[job] = []
            grouped_matches[job].append((candidate, recruiters_pref[job][candidate]))

        return jsonify({
            'matches': grouped_matches
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)




