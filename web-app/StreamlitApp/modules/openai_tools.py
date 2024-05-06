import requests

def get_available_openai_models(key):
    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {key}"
    }
    response = requests.get(url, headers=headers)

    # Extract the model names from the JSON object
    return [model['id'] for model in response.json()['data'] if model['id'].startswith('gpt')]

def ComparingJob(query):
    url = "http://127.0.0.1:5000/compare_job_posting"
    data = {"job_description": query}
    response = requests.post(url, json=data)
    return response.text
    
def SkillsDescription(query):
    url = "http://127.0.0.1:5000/get_job_skills_description"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'role_req': query})
    response = requests.post(url, headers=headers, data=data)
    return response.text

def FindJobs(query):
    url = "http://127.0.0.1:5000/find_jobs"
    data = {"user_request": query}
    response = requests.post(url, json=data)
    return response.text