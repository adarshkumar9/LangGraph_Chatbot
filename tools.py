from langchain_core.tools import BaseTool

class EvaluationTool(BaseTool):
    name: str = "evaluate_answer"
    description: str = "Evaluate candidate answer against job requirements"

    def _run(self, answer: str, job_requirements: str, question_type: str) -> dict:
        if not isinstance(answer, str) or not answer.strip():
            return {"score": 0, "feedback": "No answer provided.", "question_type": question_type}
        
        answer = answer.lower()
        score = 0
        if question_type == "technical":
            if any(skill in answer for skill in ["python", "fastapi", "sql", "api", "database"]):
                score += 3
            if any(term in answer for term in ["experience", "years", "project", "built", "developed"]):
                score += 2
        elif question_type == "experience":
            if any(term in answer for term in ["worked", "developed", "built", "managed", "lead"]):
                score += 3
            if any(term in answer for term in ["years", "months", "experience"]):
                score += 2
        elif question_type == "problem_solving":
            if any(term in answer for term in ["approach", "solution", "analyze", "debug", "troubleshoot"]):
                score += 3
            if len(answer.split()) > 20:
                score += 2
        elif question_type == "cultural_fit":
            if any(term in answer for term in ["team", "feedback", "motivate", "learn", "grow"]):
                score += 3
            if len(answer.split()) > 10:
                score += 2
        
        score = min(score, 5)
        feedback = f"Score: {score}/5 - {'Excellent detailed answer!' if score >= 4 else 'Good answer' if score >= 2 else 'Could be more detailed'}"
        return {"score": score, "feedback": feedback, "question_type": question_type}


class QuestionGeneratorTool(BaseTool):
    name: str = "generate_question"
    description: str = "Generate next screening question"

    def _run(self, job_description: str, answered_questions: list, question_count: int) -> tuple:
        questions = {
            "experience": [
                "How many years of Python development experience do you have?",
                "Can you walk me through a recent Python project you worked on?",
                "What's your experience with FastAPI, Django, or similar frameworks?",
            ],
            "technical": [
                "What programming languages and technologies are you most proficient in?",
                "Can you describe your experience with REST API development?",
            ],
            "problem_solving": [
                "How do you approach debugging a complex issue in production?",
                "Describe a time when you had to learn a new technology quickly for a project.",
            ],
            "cultural_fit": [
                "Why are you interested in this backend developer position?",
                "How do you prefer to receive feedback on your work?",
            ]
        }
        type_mapping = {1: "experience", 2: "technical", 3: "problem_solving", 4: "cultural_fit"}
        question_type = type_mapping.get(question_count, "cultural_fit")

        available_questions = [q for q in questions[question_type] if q not in answered_questions]
        if available_questions:
            return available_questions[0], question_type
        else:
            return "Thank you for your responses. That concludes our screening.", "conclusion"
