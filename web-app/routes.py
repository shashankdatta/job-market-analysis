from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import json

app = Flask(__name__)

# My api key of gpt
client = OpenAI(api_key="sk-proj-Um9DvySRUnrWkLAp8UiaT3BlbkFJWdRq9HQB5rwCda8GY8kK")


@app.route('/')
def index():
    return render_template('chat.html')


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


@app.route('/get-job-comparison', methods=['POST'])
def get_job_comparison():
    data = request.json
    comparison_data = data.get('comparison_data')

    natural_language_description = generate_natural_language_description(comparison_data)

    return jsonify(description=natural_language_description)


def generate_natural_language_description(comparison_data):
    prompt = f"Convert the following comparison data into a natural language description:\n\n{comparison_data}"

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )

    description = response.choices[0].message.content.strip()
    return description


if __name__ == '__main__':
    app.run(debug=True)
