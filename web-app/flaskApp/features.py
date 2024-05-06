from flask import Flask, request, jsonify, render_template, Response
import json
from openai import OpenAI
import numbers
import numpy as np
from difflib import SequenceMatcher
import textdistance as td

from scipy.stats import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
client = OpenAI(api_key="sk-proj-Um9DvySRUnrWkLAp8UiaT3BlbkFJWdRq9HQB5rwCda8GY8kK")


# Load role statistics from a local JSON file
def load_role_stats():
    with open('role_stats.json', 'r') as file:
        return json.load(file)


role_stats = load_role_stats()


def load_role_skills():
    with open('role_skills.json', 'r') as file:
        return json.load(file)


role_skills  = load_role_skills()


@app.route('/')
def index():
    return render_template('feature3.html')

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

    summary_prompt = f"Convert this JSON into a natural language summary: {json.dumps(output)}"
    summary_response = client.chat.completions.create(
        messages=[{"role": "user", "content": summary_prompt}],
        model="gpt-3.5-turbo"
    )
    summary_text = summary_response.choices[0].message.content.strip()

    return Response(summary_text, mimetype='text/plain')


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


@app.route('/get_job_skills_description', methods=['POST'])
def get_job_skills_description():
    role_req = request.json.get('role_req')

    # Generate prompt to find the most similar role
    role_list = list(role_skills.keys())
    prompt_find_role = ("Here is a list of job roles: \n" + str(role_list) +
                        f"\nCan you give me only one role from that list which is most similar to this user request: '{role_req}'? "
                        "Only return the name of the role, nothing else.")

    response_find_role = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt_find_role}],
        model="gpt-3.5-turbo"
    )

    returned_role = response_find_role.choices[0].message.content.strip()
    # Find the most similar role in the list
    similarities = [similar(role_req.lower(), role.lower()) for role in role_list]
    most_similar_role = role_list[np.argmax(similarities)]
    skills = role_skills[most_similar_role]

    # Generate prompt to translate skills into readable format
    prompt_translate_skills = ("Here is a list of skills for the role of " + most_similar_role + ": \n" + str(skills) +
                               "\nCan you translate this list into a more readable format, intended for a user that wants to find out what skills are required for this job role? Feel free to expand a little as you see fit.")

    response_translate_skills = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt_translate_skills}],
        model="gpt-3.5-turbo"
    )

    formatted_response = response_translate_skills.choices[0].message.content.strip()
    return Response(formatted_response, mimetype='text/plain')


vectorizer = TfidfVectorizer()
all_skills = [skill for sublist in role_skills.values() for skill in sublist]
vectorizer.fit(all_skills)


@app.route('/find_jobs', methods=['POST'])
def find_jobs():
    user_request = request.json.get('user_request')
    format_description = '''
    {
        "skills": ["skill 1", "skill 2"],
        "salary": 100000
    }
    '''

    description = ("where skills are the skills that the user has said they have, "
                   "and salary is their desired salary in dollars. "
                   "If something is not provided, put 'null' instead. "
                   "Do not include any delimiters or special characters "
                   "other than what is needed to load this JSON string into Python.")

    prompt = f"Based off this description of a user's desires in a job they are searching for:\n{user_request}\nCan you give me a JSON object in this format with this information:\n{format_description}{description}"
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )

    try:
        parsed_info = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse response into JSON"}), 400

    satisfy_salary = []
    if isinstance(parsed_info["salary"], numbers.Number):
        for role in role_stats.keys():
            if role_stats[role]["salary"] >= parsed_info["salary"]:
                satisfy_salary.append(role)

    ratios = []
    for role in satisfy_salary:
        similarities = []
        for role_skill in role_skills[role]:
            max_sim = 0
            for user_skill in parsed_info["skills"]:
                dist = td.cosine(role_skill.lower().strip(), user_skill.lower().strip())
                if dist > max_sim:
                    max_sim = dist
            similarities.append(max_sim)
        ratios.append(len([s for s in similarities if s > .75]) / len(similarities))

    top_roles = []
    indices = np.array(ratios).argsort()[-5:][::-1]
    for i in indices:
        if ratios[i] > 0:
            top_roles.append(satisfy_salary[i])

    if not top_roles:
        return Response("Try changing your search criteria. No suitable jobs found.", mimetype='text/plain')

    prompt = f"Here is a list of job roles that fit the user based on a set of criteria: \n{top_roles}\nCan you translate this list into a more readable format, intended for a user that wants to find what jobs are suitable for them based off their desired salary and the skills they possess? Feel free to expand a little as you see fit."
    formatted_response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    formatted_response = formatted_response.choices[0].message.content.strip()
    return Response(formatted_response, mimetype='text/plain')



if __name__ == '__main__':
    app.run(debug=True)
