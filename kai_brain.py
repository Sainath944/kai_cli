import os
import warnings
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from llm_backend import get_active_ollama_model

# --- Optional warning suppression ---
try:
    from langchain import LangChainDeprecationWarning
    warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
except Exception:
    pass

# --- Ollama client fallback handling ---
_OLLAMA_CLASS = None
try:
    from langchain_ollama import OllamaLLM as _NewOllama
    _OLLAMA_CLASS = _NewOllama
except Exception:
    try:
        from langchain_community.llms import Ollama as _OldOllama
        _OLLAMA_CLASS = _OldOllama
    except Exception:
        _OLLAMA_CLASS = None


def make_ollama(model_name: str, **kwargs):
    if _OLLAMA_CLASS is None:
        raise RuntimeError("No Ollama client found. Install 'langchain-ollama' or 'langchain_community'.")
    return _OLLAMA_CLASS(model=model_name, **kwargs)


# --- Load environment vars ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


# --- LangGraph State ---
class State(TypedDict):
    query: str
    answer: str


# --- Kai's Persona Layer ---
KAI_SYSTEM_PROMPT = (
    "You are Kai, a witty, charming, and clever personal AI assistant "
    "living inside a terminal. Your user is your boss — treat them with humor, "
    "respect, and playfulness. Every response must begin with a fun greeting "
    "like 'Hey boss!', 'Yo boss!', 'Greetings boss!' etc., and deliver answers "
    "in a creative, conversational, slightly cheeky tone. "
    "Never sound robotic — think like a confident terminal buddy who’s always got the boss’s back."
)


# --- Node logic ---
def choose_model(state: State) -> State:
    return state


def decide_model(state: State) -> str:
    """Route based on local Ollama availability."""
    return "ollama" if get_active_ollama_model()[0] else "gemini"


def use_ollama(state: State) -> State:
    _, model_name = get_active_ollama_model()
    llm = make_ollama(model_name)
    prompt = f"{KAI_SYSTEM_PROMPT}\n\nUser Query: {state['query']}"
    try:
        result = llm.invoke(prompt)
        state["answer"] = result
    except Exception as e:
        state["answer"] = f"Error calling Ollama: {e}"
    return state


def use_gemini(state: State) -> State:
    if not (GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS):
        state["answer"] = (
            "Google credentials not found. Please set GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS."
        )
        return state

    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.7)
    prompt = f"{KAI_SYSTEM_PROMPT}\n\nUser Query: {state['query']}"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        state["answer"] = getattr(response, "content", str(response))
    except Exception as e:
        state["answer"] = f"Error calling Gemini: {e}"
    return state


# --- Graph Setup ---
graph = StateGraph(State)

graph.add_node("choose_model", choose_model)
graph.add_node("ollama", use_ollama)
graph.add_node("gemini", use_gemini)

graph.add_conditional_edges(
    "choose_model",
    decide_model,
    {"ollama": "ollama", "gemini": "gemini"},
)

graph.add_edge("ollama", END)
graph.add_edge("gemini", END)
graph.set_entry_point("choose_model")
app = graph.compile()


# --- Main Entry ---
def ask_query(query: str):
    """Main function to ask Kai something."""
    state = {"query": query, "answer": ""}
    final_state = app.invoke(state)
    print("\n🤖 Kai says:\n", final_state["answer"])

