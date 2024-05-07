# Web Application Team

## Introduction

This `web-app` subsection of the **Job Market Analysis** project focuses on the user interface and interaction layer of the application. It is designed to provide users with a seamless experience as they navigate through job market data, compare job postings, identify required skills, and find the best job roles that match their profiles.

## Features

The web application offers the following features:

- **Job Comparison**: Users can compare job postings to understand how a particular job stands out in the market.
- **Skill Analysis**: The app identifies key skills required for job roles, aiding users in skill development and job preparation.
- **Role Recommendation**: Based on user profiles, the app suggests job roles that users are most suited for.

## Technologies

- **Flask**: A micro web framework written in Python. It is classified as a microframework because it does not require particular tools or libraries. This makes Flask very lightweight and easy to use, yet powerful and flexible enough to create complex web applications. In the context of our project, Flask is used to:

  - This application provides a set of APIs designed to analyze job descriptions and match them against a database of job roles based on various criteria such as skills, education, experience, and expected salary. The application uses the OpenAI API to parse and extract relevant details from job descriptions, compare these with pre-defined statistics, and suggest potential job matches for users.
  - Develop a **test environment** that allows for the simulation of the application's behavior before deployment.
  - Serve as the **backend server**, handling requests and responses, and managing the flow of data between the frontend and the backend.
  - Provide **API endpoints** that the frontend can communicate with to perform actions like data retrieval, job analysis, and user profile matching.

- **Streamlit**: An open-source app framework specifically for Machine Learning and Data Science teams. It turns data scripts into shareable web apps in minutes, all in pure Python. No front-end experience is required. For our job market analysis project, Streamlit is used to:

  - Create a **user-friendly interface** that allows users to interact with the application without any coding knowledge.
  - Visualize data and results in a **clear and interactive manner**, making it easier for users to understand the job market analysis.
  - Implement **quick prototyping** of the UI, enabling rapid iteration and feedback on the design and functionality of the application.

- **OpenAI Model as Assistant**: We've integrated an OpenAI-powered model to act as an assistant within the application, providing users with intelligent responses and insights.
- **LangChain 🦜🔗**: This project utilizes LangChain, a framework for chaining language models together to create complex applications. LangChain allows us to combine the capabilities of different language models, such as those provided by OpenAI, to enhance the assistant's ability to understand context, generate responses, and provide more accurate analyses.

Both Flask and Streamlit are chosen for their simplicity and efficiency, allowing our team to focus on delivering a robust and user-centric application for job market analysis. LangChain is essentially a tool that enables the creation of more sophisticated AI applications by linking together multiple language models. This can lead to improved performance in tasks like language understanding, decision-making, and content generation, as it leverages the strengths of each individual model within the chain.

## Usage

1. Input the OpenAI API Key and pick a GPT model of choice.
2. Customize the model parameters or use the default preset settings.
3. Interact with the Jobly to use the implemented features.
4. Review the comparative analysis and skill requirements presented by the app.

## Features

- **Job Comparison**: Users can compare job postings to understand how a particular job stands out in the market.
- **Skill Analysis**: The app identifies key skills required for job roles, aiding users in skill development and job preparation.
- **Role Recommendation**: Based on user profiles, the app suggests job roles that users are most suited for.

## Querying Process
Our application does not merely perform exact matches against the database entries; instead, it aims to find the most similar or relevant results based on the processed input. When an exact match is not found in the database, the system utilizes advanced matching algorithms to identify and return the closest approximate entries. This ensures that users receive the most pertinent and useful information even if their exact query specifics are not directly available in the database.

## Development

- Integrating **Streamlit** for frontend UI components.
- Utilizing **Flask** to develop test environments and manage backend data processing.
- Implementing a user-chosen **OpenAI model** to assist with the features mentioned above.

## Installation

To set up the web application locally, follow these instructions:

1. Clone the repository to your local machine.
2. Install the necessary Python packages using `pip install -r requirements.txt`.
3. Run the Streamlit and Flask application using `streamlit run app.py` and `flask run` separtely in their respective directories. It is recommended to use multiple terminals to do the following:

   - Open two separate terminal windows or tabs.
   - In one terminal, navigate to your Streamlit app directory and run:
     ```
     streamlit run your_streamlit_app.py
     ```
     Default local URL: `http://127.0.0.1:8501/`
   - In the other terminal, navigate to your Flask app directory and run:
     ```
     flask run
     ```
     Default local URL: `http://127.0.0.1:5000/`
   - This way, both Streamlit and Flask will run independently, serving their respective endpoints.

4. Navigate to the locally hosted web application URLs for `Flask` and `Streamlit`.

For more details on other sections of the project, please refer to the `README` files under `data-analysis`, `data-scraping`, and `outputs`.

---

## API Endpoints

The web application provides several API endpoints to interact with the job market analysis features. Below are the available endpoints and their usage:

### 1. Compare Job Posting

- **URL**: `/compare_job_posting`
- **Method**: `POST`
- **Data Params**:
  ```json
  {
    "job_description": "String containing the full job description."
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**: A plain text summary of how the job compares to industry averages.

### 2. Get Job Skills Description

- **URL**: `/get_job_skills_description`
- **Method**: `POST`
- **Data Params**:
  ```json
  {
    "role_req": "String containing the job role."
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**: Plain text detailing the skills required for the most similar job role found.

### 3. Find Jobs

- **URL**: `/find_jobs`
- **Method**: `POST`
- **Data Params**:
  ```json
  {
    "user_request": "String containing the user's skills and desired salary."
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**: A list of job roles that match the user's skills and salary requirements.
