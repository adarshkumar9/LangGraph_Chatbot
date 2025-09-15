from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from .tools import EvaluationTool, QuestionGeneratorTool
from .db import save_message, save_evaluation, close_session

def ask_question_node(state):
    question_count = state.get("question_count", 0)
    max_questions = state.get("max_questions", 4)
    job_description = state.get("job_description", "")
    candidate_answers = state.get("candidate_answers", [])
    messages = state.get("messages", [])
    
    if question_count >= max_questions:
        return {"screening_complete": True, "needs_user_input": False}
    
    question_generator = QuestionGeneratorTool()
    answered_questions = [ans.get("question", "") for ans in candidate_answers]
    next_q_num = question_count + 1

    try:
        next_question, question_type = question_generator._run(
            job_description=job_description,
            answered_questions=answered_questions,
            question_count=next_q_num
        )
    except Exception:
        next_question = f"Question {next_q_num}: Tell me about your relevant experience."
        question_type = "general"
    
    question_content = f"📋 **Question {next_q_num}/{max_questions}:**\n{next_question}"
    response = AIMessage(content=question_content)
    save_message(state["session_id"], response)

    return {
        "messages": messages + [response],
        "current_question": next_question,
        "question_count": next_q_num,
        "needs_user_input": True,
        "screening_complete": False
    }

def process_answer_node(state):
    messages = state.get("messages", [])
    current_question = state.get("current_question", "")
    question_count = state.get("question_count", 0)
    candidate_answers = state.get("candidate_answers", [])
    job_description = state.get("job_description", "")
    max_questions = state.get("max_questions", 4)
    
    user_input = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content or ""
            save_message(state["session_id"], msg)
            break
    
    if not user_input.strip():
        user_input = "No answer provided"
    
    type_mapping = {1: "experience", 2: "technical", 3: "problem_solving", 4: "cultural_fit"}
    question_type = type_mapping.get(question_count, "general")
    
    evaluator = EvaluationTool()
    evaluation = evaluator._run(answer=user_input, job_requirements=job_description, question_type=question_type)
    
    answer_record = {
        "question_number": question_count,
        "question": current_question,
        "answer": user_input,
        "evaluation": evaluation,
        "timestamp": datetime.now().isoformat()
    }
    
    updated_answers = candidate_answers + [answer_record]
    
    feedback_content = f"✅ Thank you for your answer!\n{evaluation['feedback']}\n"
    feedback_message = AIMessage(content=feedback_content)

    save_message(state["session_id"], feedback_message)
    save_evaluation(state["session_id"], question_count, evaluation["score"], evaluation["feedback"])
    
    if question_count >= max_questions:
        total_score = sum(ans.get("evaluation", {}).get("score", 0) for ans in updated_answers)
        avg_score = total_score / len(updated_answers) if updated_answers else 0
        
        final_content = f"""
🎯 **SCREENING COMPLETED!**

📊 **EVALUATION SUMMARY:**
- Total Questions Answered: {len(updated_answers)}
- Average Score: {avg_score:.1f}/5.0
- Overall Assessment: {'✅ RECOMMENDED' if avg_score >= 3.0 else '⚠️ NEEDS FURTHER REVIEW'}
"""
        final_message = AIMessage(content=final_content)
        save_message(state["session_id"], final_message)
        close_session(state["session_id"])
        
        return {
            "messages": messages + [feedback_message, final_message],
            "candidate_answers": updated_answers,
            "screening_complete": True,
            "needs_user_input": False,
            "evaluation_score": {
                "total_score": total_score,
                "average_score": avg_score,
                "recommendation": "RECOMMENDED" if avg_score >= 3.0 else "NEEDS FURTHER REVIEW"
            }
        }
    
    return {
        "messages": messages + [feedback_message],
        "candidate_answers": updated_answers,
        "needs_user_input": False,
        "screening_complete": False
    }

def should_wait_for_input(state):
    if state.get("needs_user_input", False):
        return "wait_for_input"
    elif state.get("screening_complete", False):
        return "end"
    else:
        return "ask_question"
