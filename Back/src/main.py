import json
import random
import ollama

# ============================================================
# Configuration
# ============================================================

MODEL = "qwen2.5:1.5b"
QUESTION_COUNT = 10

# Adapt these topics to your original five sections.
SECTIONS = {
    1: "Meetings and communication",
    2: "Project management",
    3: "Team management and leadership",
    4: "Software engineering",
    5: "Business and strategy",
}

LEVELS = {
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
}

# Terminal colours
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


# ============================================================
# LLM helpers
# ============================================================

def ask_llm(prompt):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json",
        options={
            "temperature": 0.3,
            "num_ctx": 2048
        }
    )

    return json.loads(response["message"]["content"])

def generate_question(section, direction, previous_questions):

    if direction == "FR_TO_EN":
        source_language = "French"
        target_language = "English"
    else:
        source_language = "English"
        target_language = "French"

    print (f"source_language={source_language}")
    print (f"target_language={target_language}")

    prompt = f"""
You are a French language teacher helping a native English speaker
learn French for professional situations and Engineering Manager interviews.

TOPIC: {section}

STRICT TRANSLATION RULES:
- The sentence to translate MUST be written entirely in {source_language}.
- The expected translation MUST be written in {target_language}.
- Never reverse the translation direction.
- Generate exactly one sentence.
- Use realistic professional vocabulary.
- Adapt the complexity to the selected difficulty level.

PREVIOUS SENTENCES (avoid repeating them):
{previous_questions}

Return valid JSON with exactly these fields:
{{
    "sentence": "Sentence written in {source_language}",
    "translation": "Translation written in {target_language}"
}}
"""

    result = ask_llm(prompt)

    return result["sentence"], result["translation"]

def evaluate_answer(sentence, expected, answer, direction, section):

    if direction == "FR_TO_EN":
        source_language = "French"
        target_language = "English"
    else:
        source_language = "English"
        target_language = "French"

    prompt = f"""
You are a French language teacher helping a native English speaker
learn French for professional situations.

Topic: {section}

Original sentence ({source_language}):
{sentence}

Expected translation ({target_language}):
{expected}

User translation ({target_language}):
{answer}

Evaluate the translation.

Rules:
- Accept equivalent translations with the same meaning.
- Accept natural alternative formulations.
- Be particularly attentive to French grammar and vocabulary.
- Explain mistakes in English.
- When appropriate, explain why a French expression is more natural
  than a literal English translation.
- Give constructive feedback.

Return valid JSON:
{{
    "correct": true,
    "feedback": "Explanation in English",
    "suggestion": "A natural French formulation"
}}
"""

    return ask_llm(prompt)


# ============================================================
# Quiz
# ============================================================

def select_section():
    print(f"\n{CYAN}Available sections:{RESET}")

    for number, name in SECTIONS.items():
        print(f"  {number}. {name}")

    while True:
        try:
            choice = int(input("\nChoose a section: "))

            if choice in SECTIONS:
                return SECTIONS[choice]

        except ValueError:
            pass

        print(f"{RED}Invalid selection.{RESET}")


def select_level():
    print(f"\n{CYAN}Available levels:{RESET}")

    for number, name in LEVELS.items():
        print(f"  {number}. {name}")

    while True:
        try:
            choice = int(input("\nChoose a level: "))

            if choice in LEVELS:
                return choice

        except ValueError:
            pass

        print(f"{RED}Invalid selection.{RESET}")



def get_direction(level, question_number):

    if level == 3:
        return "EN_TO_FR"

    if level == 2:
        return "EN_TO_FR" if question_number % 2 == 1 else "FR_TO_EN"

    if level == 1:
        return "FR_TO_EN"


def run_quiz(section, level):
    level_name = LEVELS[level]

    print("\n" + "=" * 60)
    print(f"{CYAN}{section} - Level {level}: {level_name}{RESET}")
    print("=" * 60)

    print(f"\nYou will have to translate {QUESTION_COUNT} sentences.")
    input("Press Enter to start...")

    score = 0
    mistakes = []
    previous_questions = []

    for number in range(1, QUESTION_COUNT + 1):

        direction = get_direction(level, number)

        print(f"\n{YELLOW}Question {number}/{QUESTION_COUNT}{RESET}")

        try:
            sentence, expected = generate_question(
                section,
                direction,
                previous_questions
            )
        except Exception as error:
            print(f"{RED}Could not generate question: {error}{RESET}")
            break

        previous_questions.append(sentence)

        if direction == "EN_TO_FR":
            print(f"\nTranslate into French:\n{CYAN}{sentence}{RESET}")
        else:
            print(f"\nTranslate into English:\n{CYAN}{sentence}{RESET}")

        answer = input("\nYour translation: ").strip()

        if not answer:
            print(f"{RED}No answer provided.{RESET}")

        try:
            result = evaluate_answer(
                sentence,
                expected,
                answer,
                direction,
                section
            )
        except Exception as error:
            print(f"{RED}Could not evaluate answer: {error}{RESET}")
            continue

        if result["correct"]:
            score += 1
            print(f"\n{GREEN}CORRECT!{RESET}")
        else:
            print(f"\n{RED}INCORRECT{RESET}")
            mistakes.append({
                "sentence": sentence,
                "answer": answer,
                "expected": expected
            })

        print(f"Feedback: {result['feedback']}")
        print(f"Suggestion: {result['suggestion']}")

        print(f"\nScore: {score}/{number}")

    # ========================================================
    # Final results
    # ========================================================

    total = QUESTION_COUNT
    percentage = (score / total) * 100

    print("\n" + "=" * 60)
    print(f"{CYAN}FINAL RESULTS{RESET}")
    print("=" * 60)

    print(f"Section: {section}")
    print(f"Level: {level} - {level_name}")
    print(f"Score: {score}/{total}")
    print(f"Success rate: {percentage:.1f}%")

    if percentage >= 80:
        print(f"\n{GREEN}Excellent work!{RESET}")
    elif percentage >= 60:
        print(f"\n{YELLOW}Good effort! Keep practising.{RESET}")
    else:
        print(f"\n{RED}More practice is needed.{RESET}")

    if mistakes:
        print(f"\n{YELLOW}Review your mistakes:{RESET}")

        for index, mistake in enumerate(mistakes, 1):
            print(f"\n{index}. {mistake['sentence']}")
            print(f"Your answer: {mistake['answer']}")
            print(f"Suggested answer: {mistake['expected']}")

    print("\n" + "=" * 60)


# ============================================================
# Main
# ============================================================

def main():
    print(f"{CYAN}")
    print("========================================")
    print("     ENGINEERING MANAGER ENGLISH QUIZ")
    print("========================================")
    print(f"{RESET}")

    while True:
        section = select_section()
        level = select_level()

        run_quiz(section, level)

        again = input("\nWould you like another exercise? (y/n): ")

        if again.lower() != "y":
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()