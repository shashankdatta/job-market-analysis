from flask import Flask, request, jsonify, render_template
import openai
import json

from openai import OpenAI

app = Flask(__name__)

# My api key of gpt
client = OpenAI(api_key="sk-proj-Um9DvySRUnrWkLAp8UiaT3BlbkFJWdRq9HQB5rwCda8GY8kK")

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/process-input', methods=['POST'])
def process_input():
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

        #load the GPT response as JSON
        structured_data = json.loads(response.choices[0].message.content.strip())
        return structured_data

    except json.JSONDecodeError:
        return "Invalid JSON format received from GPT."

if __name__ == '__main__':
    app.run(debug=True)
