# Web Application Team
-----------------------------------------------------------
Job Analysis Flask Application
Overview
This Flask application provides a set of APIs designed to analyze job descriptions and match them against a database of job roles based on various criteria such as skills, education, experience, and expected salary. The application uses the OpenAI API to parse and extract relevant details from job descriptions, compare these with pre-defined statistics, and suggest potential job matches for users.

Features
Compare Job Postings: Analyzes job descriptions and compares them with average job statistics.
Get Job Skills Description: Returns detailed skill requirements for a specified job role.
Find Jobs: Matches users' skills and salary expectations with available job roles.

Installation
Prerequisites
Python 3.x
Flask
OpenAI API key

Setup
Clone the repository:
git clone https://github.com/shashankdatta/job-market-analysis.git
cd web-app/flaskApp
Install required packages:
pip install -r requirements.txt
Initialize the application:
python -m flask run

Usage
Starting the Server
Run the Flask application locally:
python -m flask run
The server will start running on http://127.0.0.1:5000/.

API Endpoints
1. Compare Job Posting
URL: /compare_job_posting
Method: POST
Data Params:
{ "job_description": "String containing the full job description." }
Success Response:
Code: 200
Content: Plain text summarizing how the job compares to industry averages.
2. Get Job Skills Description
URL: /get_job_skills_description
Method: POST
Data Params:
{ "role_req": "User-requested job role or description." }
Success Response:
Code: 200
Content: Plain text detailing the skills required for the most similar job role found.
3. Find Jobs
URL: /find_jobs
Method: POST
Data Params:
{ "user_request": "JSON object containing user's skills and desired salary." }
Success Response:
Code: 200
Content: List of job roles that match the user's skills and salary requirements.
-------------------------------------------------------------