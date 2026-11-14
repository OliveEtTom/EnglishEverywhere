
#!/usr/bin/env python3

import json
import random
import sys

from ollama import chat

MODEL = "qwen2.5:1.5b"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

SECTIONS = {
    1: "Talking about your role and responsibilities",
    2: "People management, coaching and leadership",
    3: "Talking about problems and challenges",
    4: "Explaining actions and decisions",
    5: "Talking about results and outcomes",
}

def ask_llm(prompt, schema):
    """Ask the model for a response matching a JSON schema."""
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an English coach for a French-speaking "
                    "Engineering Manager preparing for a job interview. "
                    "Use natural, professional English. Keep exercises "
                    "appropriate for B1-B2 English learners. "
                    "Return only data matching the requested schema."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        format=schema,
        options={"temperature": 0.3},
    )
    return json.loads(response.message.content)

QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "french": {"type": "string"},
        "section": {"type": "integer"},
        "hint": {"type": "string"},
    },
    "required": ["french", "section", "hint"],
}

EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "correct": {"type": "boolean"},
        "expected_answer": {"type": "string"},
        "feedback": {"type": "string"},
    },
    "required": ["correct", "expected_answer", "feedback"],
}

def generate_question(previous_questions):
    sections = "\n".join(
        f"{number}. {description}"
        for number, description in SECTIONS.items()
    )

    prompt = f"""
Generate ONE new French-to-English translation exercise.

Choose one section at random from:
{sections}

Requirements:
- The French sentence must be natural and unambiguous.
- The expected English must be useful in an Engineering Manager interview.
- Use a short phrase or sentence.
- Do not reveal the English translation.
- Avoid repeating these previous French questions:
{previous_questions[-20:]}

Return the French sentence, section number, and a short French hint.
"""
    return ask_llm(prompt, QUESTION_SCHEMA)

def evaluate_answer(french, user_answer, section):
    prompt = f"""
Evaluate a French-to-English translation exercise.

Topic: {SECTIONS[section]}
Original French: {french}
Learner's English answer: {user_answer}

Rules:
- Accept natural, grammatically correct translations with the same meaning.
- Accept different wording, synonyms and valid alternative constructions.
- Do not require an exact match to one particular translation.
- Ignore minor spelling or punctuation errors when meaning is clear.
- Mark incorrect if the meaning changes significantly or the English
  is not understandable.
- Give concise feedback in English, suitable for a B1-B2 learner.
- Provide one natural, professional English translation.

Return:
correct: whether the answer is acceptable
expected_answer: a natural English translation
feedback: brief feedback explaining the decision
"""
    return ask_llm(prompt, EVALUATION_SCHEMA)

def main():
    print(f"{BOLD}{BLUE}")
    print("=" * 52)
    print(" ENGINEERING MANAGER VOCABULARY TRAINER")
    print("=" * 52)
    print(RESET)

    try:
        count = input("Number of questions (default 10): ").strip()
        count = int(count) if count else 10

        if not 1 <= count <= 100:
            print("Please choose between 1 and 100 questions.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    score = 0
    history = []
    mistakes = []

    try:
        for index in range(1, count + 1):
            question = generate_question(history)

            french = question["french"]
            section = question["section"]

            if section not in SECTIONS:
                print("The model returned an invalid section. Skipping.")
                continue

            print(f"\n{BLUE}{BOLD}Question {index}/{count}{RESET}")
            print(f"Section {section}: {SECTIONS[section]}")
            print(f"{YELLOW}French: {french}{RESET}")
            print(f"Hint: {question['hint']}")

            answer = input("English (or 'q' to quit): ").strip()

            if answer.lower() == "q":
                break

            if not answer:
                print(f"{RED}Empty answer.{RESET}")
                result = {
                    "correct": False,
                    "expected_answer": "(No answer provided)",
                    "feedback": "Try writing a complete English expression.",
                }
            else:
                result = evaluate_answer(french, answer, section)

            history.append(french)

            if result["correct"]:
                score += 1
                print(f"{GREEN}{BOLD}CORRECT{RESET}")
            else:
                print(f"{RED}{BOLD}INCORRECT{RESET}")
                mistakes.append((french, answer, result["expected_answer"]))

            print(f"{GREEN}Suggested translation: "
                  f"{result['expected_answer']}{RESET}")
            print(f"Feedback: {result['feedback']}")

    except KeyboardInterrupt:
        print("\nQuiz interrupted.")

    except Exception as error:
        print(f"\n{RED}LLM error: {error}{RESET}")
        print("Check that Ollama is running and the model is installed.")

    finally:
        if history:
            # Score only questions actually answered.
            total = len(history)
            percentage = score / total * 100

            print(f"\n{BOLD}{BLUE}===== FINAL SCORE ====={RESET}")
            print(f"Score: {score}/{total} ({percentage:.1f}%)")

            if mistakes:
                print(f"\n{RED}Review these answers:{RESET}")
                for french, answer, expected in mistakes:
                    print(f"\nFrench: {french}")
                    print(f"Your answer: {answer}")
                    print(f"Suggested: {expected}")

if __name__ == "__main__":
    main()