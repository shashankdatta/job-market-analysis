# Outputs

There are 2 output files we generate using Spark:

## `role_stats.json`
Aggregate statistics for each job role.

```
{
    "API Developer": {
        "salary": 82636.60245183887,
        "education": 1.6141257536606375,
        "experience": 7.0031161473087815,
        "num_skills": 5.0,
        "num_responsibilities": 3.0,
        "num_benefits": 5.0
    },
}
```

## `role_skills.json`
A list of the most common skills/keywords for each job role.

```
{
    "API Developer": [
        "restful api knowledge",
        "security protocols",
        "development restful api",
        "knowledge security",
        "restful api",
        "api knowledge security",
        "api design",
        "api knowledge",
        "knowledge security protocols",
        "design and development",
        "development restful"
    ],
}
