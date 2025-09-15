import uuid
from langchain_core.messages import HumanMessage, AIMessage
from .db import setup_db, create_session, close_session, save_message
from .graph_builder import create_screening_agent

def run_screening_interview():
    setup_db()
    thread_id = input("Enter thread_id (or leave blank for new): ").strip() or f"thread-{uuid.uuid4().hex[:8]}"
    session_id = create_session(thread_id)

    JD = """POSITION: Senior Python Backend Developer
REQUIRED: Python, FastAPI/Django, SQL, REST APIs, Git"""

    screening_agent = create_screening_agent(thread_id)

    state = {
        "messages": [],
        "job_description": JD,
        "candidate_answers": [],
        "current_question": "",
        "screening_complete": False,
        "evaluation_score": {},
        "question_count": 0,
        "max_questions": 4,
        "needs_user_input": False,
        "session_id": session_id,
        "thread_id": thread_id
    }  # initialize ChatState as before

    print("🎯 AI HR SCREENING AGENT")
    ...

    while not state.get("screening_complete", False):
        response = screening_agent.invoke(state, config={"configurable": {"thread_id": thread_id}})
        state.update(response)
        
        if state.get("messages"):
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(f"\n🤖 AI: {last_message.content}")
        
        if state.get("needs_user_input", False):
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Session ended.")
                close_session(session_id)
                break
            state["messages"].append(HumanMessage(content=user_input))
            state["needs_user_input"] = False

if __name__ == "__main__":
    run_screening_interview()
