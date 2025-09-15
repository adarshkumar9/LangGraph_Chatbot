# graph_builder.py
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from .nodes import ask_question_node, process_answer_node, should_wait_for_input
from .db import CHAT_DB
import sqlite3

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    job_description: str
    candidate_answers: List[dict]
    current_question: str
    screening_complete: bool
    evaluation_score: dict
    question_count: int
    max_questions: int
    needs_user_input: bool
    session_id: str
    thread_id: str

def create_screening_agent(thread_id):
    conn = sqlite3.connect(CHAT_DB, check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)

    graph = StateGraph(ChatState)
    graph.add_node("ask_question", ask_question_node)
    graph.add_node("process_answer", process_answer_node)
    graph.add_edge(START, "ask_question")

    graph.add_conditional_edges("ask_question", should_wait_for_input,
        {"wait_for_input": END, "end": END})

    graph.add_conditional_edges("process_answer", should_wait_for_input,
        {"ask_question": "ask_question", "end": END})

    return graph.compile(checkpointer=checkpointer)
