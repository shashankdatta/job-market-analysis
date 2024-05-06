# Data Analysis Team

## Feature 1
Comparison of job to other jobs of the same position.

Example: I am looking for a new "software engineer" position. When I look at a job posting, I'd like to see how this posting compares to other "software engineer" positions. For example, "this posting has a lower salary than other postings of similar positions, and requires more qualifications.

Input:

```
{
    "role": "job role"
    "salary": 100000,
    "education": "BS",
    "experience": 5,
    "num_skills": 5,
    "num_responsibilities": 5,
    "num_benefits": 5
}
```
Output:
```
{
    "role": "Frontend Web Developer",
    "salary": "less than average",
    "education": "less than average",
    "experience": "less than average",
    "skills": "greater than average",
    "responsibilities": "greater than average",
    "benefits": "greater than average",
}
```

UDF functions are used to interpret various columns in the dataset.

## Feature 2
What skills an applicant needs for a specific job position.

Example: I am looking for a new "software engineer" position. When I search for "software engineer," I'd like to see a list of the most common qualifications for this position, e.g., "Python proficiency, AWS CDK, and GitHub CI/CD."

Input:
```
{
    "role": "Frontend Web Developer",
}
```
Output:
```
{
    "skills": [
        "HTML",
        "CSS",
        "JavaScript Frontend frameworks (e.g., React, Angular)",
        "User experience (UX)",
    ],
}
```

We use YAKE (Yet Another Keyword Extractor) to extract skill keywords from each job.  We initially tried just splitting by word and then counting the most common ones, but for most jobs this doesn't work because a skill is usually more than just 1 word.  Additionally, words like "the" will be counted many times even though they don't have any semantic meaning in this sense (finding skills).

We investigate 2 methods for aggregating required skills for each job role:

### YAKE UDF Method
We try using a UDF function for each row to apply a Python YAKE library.

### Spark NLP Method
Instead of using UDF, we use the built-in YAKE functionality given in the Spark NLP library.  This method is much faster than the UDF method, and it's the method we eventually settle on.

## Feature 3
Job recommendation based on user profile.

Example: I enter in a list of qualifications I have (and maybe some other information such as desired salary). I'd like to see a list of job positions that most fit my profile.

Input:
```
{
    "skills": [
        "HTML",
        "CSS",
        "JavaScript Frontend frameworks (e.g., React, Angular)",
        "User experience (UX)",
    ],
    "salary": 100000,
}
```
Output:
```
{
    "roles": [
        "Frontend Web Developer",
        "User Interface Designer",
        "Backend Developer",
    ],
}
```

We investigate 2 methods for recommending jobs:

### Spark Method
In the Spark method, we analyze every single job in the dataset to find the most similar jobs.  This proved to be too slow as having Spark analyze the entire dataset upon every request took way too long.

### JSON Method
Using the output JSON from Feature 1 and 2, we search for the roles that look most similar to the user request.  Since the JSON is a significantly reduced representative version of the dataset, this method is much faster.  We use string cosine distance to compare the user's skills and each job role's skills to find the role that is most similar to the user's request.
