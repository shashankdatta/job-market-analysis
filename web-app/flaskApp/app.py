from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import json

app = Flask(__name__)

# My api key of gpt
client = OpenAI(api_key="sk-proj-Um9DvySRUnrWkLAp8UiaT3BlbkFJWdRq9HQB5rwCda8GY8kK")


@app.route('/')
def index():
    return render_template('chat.html')

# feature 1 user input
@app.route('/submit-job-id', methods=['POST'])
def submit_job_id():
    data = request.json
    user_input = data.get('user_input')
    job_id_json = extract_job_id(user_input)

    return jsonify(job_id=job_id_json)


def extract_job_id(user_input):
    prompt = f"""
    The user has provided the following job posting information, which includes an ID number:
    "{user_input}"
    Using the job posting ID, transfer it into json

    The structured JSON should follow this format:
    {{
        "id": "Extracted job ID"
    }}
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )

    extracted_data = response.choices[0].message.content.strip()
    return extracted_data

#feature 1 gpt output
@app.route('/get-job-comparison', methods=['POST'])
def get_job_comparison():
    data = request.json
    comparison_data = data.get('comparison_data')

    natural_language_description = generate_natural_language_description(comparison_data)

    return natural_language_description


def generate_natural_language_description(comparison_data):
    prompt = f"Convert the following comparison data into a natural language description:\n\n{comparison_data}"

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )

    description = response.choices[0].message.content.strip()
    return description

#feature 2 input
@app.route('/submit-role', methods=['POST'])
def submit_role():
    data = request.json
    role = data.get('role')
    role_json = json.dumps({"role": role})
    return jsonify(role=role_json)

#feature2 output
@app.route('/get-skills', methods=['POST'])
def get_skills():
    data = request.json
    skills_data = data.get('skills_data')
    description = skills_to_natural_language(skills_data)
    return description


def skills_to_natural_language(skills_data):
    if not skills_data:
        return "No skills data provided."

    skills_list = ', '.join(skills_data)
    prompt = f"Describe the following skills in natural language for a job seeker: {skills_list}"

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )

    description = response.choices[0].text.strip()
    return description

#feature3 input
@app.route('/recommend-jobs', methods=['POST'])
def recommend_jobs():
    data = request.json
    user_input = data.get('user_input')

    structured_response = get_structured_response(user_input)

    if isinstance(structured_response, str):
        return jsonify({'error': structured_response}), 400

    return jsonify(structured_response=structured_response)


def get_structured_response(user_input):
    # guide GPT to format the user input into the desired JSON structure
    prompt = f"""
        Parse the following job description and extract the information in a structured JSON format. Leave the value as null if any information is missing or lack of experience:

        "{user_input}"

        Format the extracted information as follows:

        {{
          "role": "Extracted job role or null",
          "salary": "Extracted estimated salary in dollars or null",
          "education": "Extracted required education or null",
          "experience": "Extracted years of experience or null",
          "num_skills": "Extracted number of skills listed or null",
          "num_responsibilities": "Extracted number of responsibilities listed or null",
          "num_benefits": "Extracted number of benefits listed or null"
        }}
        """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo"
        )

        # load the GPT response as JSON
        structured_data = json.loads(response.choices[0].message.content.strip())
        return structured_data

    except json.JSONDecodeError:
        return "Invalid JSON format received from GPT."

#feature3 output
@app.route('/get-roles', methods=['POST'])
def get_roles():
    # Assuming roles_json is a JSON object with a key "roles" pointing to a list of roles
    data = request.json
    roles = data.get('roles')

    # Check if the roles list is empty
    if not roles:
        return "No roles data provided."
    roles_list = ', '.join(roles)
    # Create a natural language list from the roles
    prompt = f"Write a paragraph summarizing the job roles suitable for a user based on their profile: {roles_list}."

    # Use the prompt to generate a natural language summary with GPT-3
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )

    # Extract the natural language description from the response
    description = response.choices[0].text.strip()
    return description


if __name__ == '__main__':
    app.run(debug=True)
