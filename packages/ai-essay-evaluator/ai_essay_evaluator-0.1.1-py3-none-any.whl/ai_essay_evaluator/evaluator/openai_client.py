import asyncio
import json
import logging

import openai
import pandas as pd
from pydantic import BaseModel, ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)

# Retry settings for handling OpenAI API errors & Pydantic validation failures
RETRY_SETTINGS = {
    "stop": stop_after_attempt(5),
    "wait": wait_exponential(multiplier=1, min=2, max=10),
    "retry": retry_if_exception_type((openai.OpenAIError, ValidationError)),
}


class ExtendedScoringResponse(BaseModel):
    idea_development_score: int
    idea_development_feedback: str
    language_conventions_score: int
    language_conventions_feedback: str


class StandardScoringResponse(BaseModel):
    score: int
    feedback: str


@retry(**RETRY_SETTINGS)
async def call_openai_parse(
    messages: list[dict[str, str] | dict[str, str]], model: str, api_key: str, scoring_format: str
):
    openai.api_key = api_key
    response_format = ExtendedScoringResponse if scoring_format == "extended" else StandardScoringResponse
    max_completion_tokens = 2000
    response = await openai.beta.chat.completions.parse(
        model=model,
        messages=messages,
        temperature=0,
        response_format=response_format,
        max_tokens=max_completion_tokens,
    )
    return extract_structured_response(response, scoring_format)


async def process_with_openai(df, ai_model, api_key, stories, rubrics, question, scoring_format):
    async def process_row(row):
        prompt = generate_prompt(row, scoring_format, stories, rubrics, question)
        try:
            return await call_openai_parse(prompt, ai_model, api_key, scoring_format)
        except ValidationError as e:
            logging.error(f"Validation failed for row {row['Local Student ID']}: {e}")
            return get_default_response(scoring_format)

    tasks = [process_row(row) for _, row in df.iterrows()]
    results = await asyncio.gather(*tasks)

    structured_df = pd.DataFrame(results)
    return pd.concat([df, structured_df], axis=1)


def generate_prompt(row, scoring_format, story_dict, rubric_text, question_text):
    student_response = row["Student Constructed Response"]
    if scoring_format == "extended":
        extended_system_content = (
            "four keys: 'idea_development_score' (an integer), 'idea_development_feedback' (a string), "
            "'language_conventions_score' (an integer), and 'language_conventions_feedback' (a string)"
        )
    else:
        extended_system_content = "two keys: 'score' (an integer) and 'feedback' (a string)"

    # Normalize language format
    tested_language = row["Tested Language"].strip().lower()
    grade_level = row["Enrolled Grade Level"]

    # Language instructions
    if tested_language == "spanish":
        language_instruction = (
            "El estudiante ha realizado la prueba en español. "
            "Proporcione la retroalimentación y la evaluación en español."
        )
    else:
        language_instruction = "The student has taken the test in English. Provide feedback and evaluation in English."

    # Structured prompt to reduce token usage
    user_prompt = {
        "grade_level": f"Grade {grade_level}",
        "language": tested_language.capitalize(),
        "stories": story_dict,
        "question": question_text,
        "rubric": rubric_text,
        "evaluation_guidance": (
            f"Analyze the student's response in a grade-appropriate manner. "
            f"Ensure feedback aligns with expectations for Grade {grade_level}. "
            f"{language_instruction}"
        ),
        "student_response": student_response,
    }

    user_message = {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}

    messages = [
        {
            "role": "system",
            "content": (
                f"AI Grader: Evaluate student responses based on rubric. "
                f"Your task is to assess the student's answer using the provided story, question, and rubric. "
                f"Return your evaluation strictly as a JSON object with exactly {extended_system_content}. "
                f"Do not include any additional text or commentary. Ensure that the JSON output is valid and parsable."
            ),
        },
        user_message,
    ]
    return messages


@retry(**RETRY_SETTINGS)
def extract_structured_response(response, scoring_format):
    structured_output = response.get("structured_output", {})

    try:
        if scoring_format == "extended":
            return ExtendedScoringResponse(**structured_output).model_dump()
        else:
            return StandardScoringResponse(**structured_output).model_dump()
    except ValidationError as e:
        logging.error(f"Validation failed: {e}")
        return get_default_response(scoring_format)


def get_default_response(scoring_format):
    if scoring_format == "extended":
        return {
            "idea_development_score": 0,
            "idea_development_feedback": "Invalid response",
            "language_conventions_score": 0,
            "language_conventions_feedback": "Invalid response",
        }
    else:
        return {"score": 0, "feedback": "Invalid response"}
