from flask import Flask, request, jsonify, render_template
import json
from openai import OpenAI
import numbers
import numpy as np
from difflib import SequenceMatcher

app = Flask(__name__)
client = OpenAI(api_key="sk-proj-Um9DvySRUnrWkLAp8UiaT3BlbkFJWdRq9HQB5rwCda8GY8kK")


# Load role statistics from a local JSON file
def load_role_stats():
    with open('role_stats.json', 'r') as file:
        return json.load(file)


role_stats = load_role_stats()

@app.route('/')
def index():
    return render_template('feature1.html')

@app.route('/compare_job_posting', methods=['POST'])
def compare_job_posting():
    job_description = request.json.get('job_description')

    output = {}
    for key in ["salary", "education", "experience", "num_skills", "num_responsibilities", "num_benefits", "education"]:
        output[key] = None

    format_description = '''
    {
        "role": "job role",
        "salary": 100000,
        "education": "BS",
        "experience": 5,
        "num_skills": 5,
        "num_responsibilities": 5,
        "num_benefits": 5
    }
    '''

    description = (
        "where role is the job position or title, salary is the estimated salary in dollars, education is the required education, experience is the desired years of experience, num_skills is the number of skills listed, num_responsibilities is the number of responsibilities listed, and num_benefits is the number of benefits listed. If something is not provided, put a 'null' instead. Do not include any delimiters or special characters other than what is needed to load this JSON string into Python.")

    is_json = False
    attempts = 0
    while not is_json and attempts < 3:
        prompt = f"Based off this job description:\n{job_description}\nCan you give me a JSON object in this format with this information:\n{format_description}{description}"
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo"
        )
        attempts += 1
        try:
            parsed_info = json.loads(response.choices[0].message.content.lower().strip())
            is_json = True
        except json.JSONDecodeError:
            continue

    if not is_json:
        return jsonify({"error": "Failed to parse response into JSON after 3 attempts"}), 400

    # Compute string similarity
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    # Assuming role_stats is a dict of role names to their stats
    ratios = [similar(response.choices[0].message.content.lower().strip(), role.lower().strip()) for role in role_stats]
    stats = role_stats[list(role_stats.keys())[np.argmax(ratios)]]

    tol = 0.1
    for key in ["salary", "education", "experience", "num_skills", "num_responsibilities", "num_benefits"]:
        if key not in parsed_info or parsed_info[key] is None:
            output[key] = None
        elif isinstance(parsed_info[key], numbers.Number):
            comparison = float(parsed_info[key])
            if comparison > (1 + tol) * stats[key]:
                output[key] = "above"
            elif comparison < (1 - tol) * stats[key]:
                output[key] = "below"
            else:
                output[key] = "average"

    # Education comparison
    if isinstance(parsed_info["education"], str):
        ed_levels = {"B": 1, "M": 2, "P": 3}
        ed = ed_levels.get(parsed_info["education"][0], 0)
        if ed > (1 + tol) * stats["education"]:
            output["education"] = "above"
        elif ed < (1 - tol) * stats["education"]:
            output["education"] = "below"
        else:
            output["education"] = "average"

    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)
