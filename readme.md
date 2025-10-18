# kai-cli — Terminal Personal Assistant

Short: Kai is a small terminal-first personal assistant. After setup you can run:
kai "tell me a joke"
and Kai will respond directly in the terminal.

This README explains the minimum steps to get Kai running and what each file does.

---

## Quick Start (Windows)

1. Put the kai-cli folder in your PATH (so you can run `kai` from any terminal)
   - Recommended: add via System Properties -> Environment Variables -> Path -> Edit -> New -> (paste full folder path)
   - Quick PowerShell command (run as your user, then restart terminal):
     [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\gudde\desktop projects\kai-cli", "User")
   - Or (cmd) example:
     setx PATH "%PATH%;C:\Users\gudde\desktop projects\kai-cli"
   - Note: replace the path above with your actual kai-cli folder path. Reopen terminal after changing PATH.

2. Edit `kai.bat` to point to the absolute path of `kai.py`
   - Open `kai.bat` and set the python call to the full path of your kai.py, for example:
     @echo off
     python "C:\Users\gudde\desktop projects\kai-cli\kai.py" %*
   - Use absolute path (not relative). Save file.

3. Create a `.env` file in the project root (next to `kai.py` / `kai_brain.py`) and add your credentials
   - Example `.env` (do not commit):
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     GEMINI_MODEL=gemini-2.5-flash
     ```
   - The project optionally loads `.env` via python-dotenv. Keep secrets out of git.

4. Install dependencies (example)
   - Create & activate virtualenv, then:
     pip install langgraph langchain-google-genai python-dotenv
     pip install langchain-ollama   # preferred Ollama support
   - Adjust package names/versions as required by your environment.

5. Run from any terminal (after PATH updated and kai.bat updated):
   kai "tell me a joke"
   - Or directly:
     python "C:\Users\gudde\desktop projects\kai-cli\kai.py" "tell me a joke"

---

## Files (what they do)

- llm_backend.py
  - Purpose: small helper to detect whether a local Ollama LLM is available.
  - Typical API: get_active_ollama_model() -> (is_local_available: bool, model_name: str)
  - Kai uses this to decide to call the local model first or fall back to Gemini.

- kai_brain.py
  - Core logic and orchestration.
  - Uses langgraph StateGraph with a conditional edge:
    - choose_model node (entry point)
    - decide_model (returns "ollama" or "gemini")
    - use_ollama (calls local LLM via Ollama client)
    - use_gemini (calls Google GenAI via ChatGoogleGenerativeAI)
  - Contains the persona/system prompt prepended to each user query and the public ask_query(query: str) function used by kai.py.

- kai.py
  - Application entrypoint (CLI wrapper).
  - Typical behavior:
    - parse command line arguments (the user query),
    - call kai_brain.ask_query(query)
    - print the response
  - Important: kai.bat must point to this file with absolute path.

- kai.bat
  - Windows launcher. Place this file (or the containing folder) into PATH.
  - Must contain absolute path to `kai.py` (not relative).
  - Example:
    @echo off
    python "C:\Users\gudde\desktop projects\kai-cli\kai.py" %*

- try.py
  - A simple interactive test script for manual testing.

---

## Troubleshooting

- "kai not found" after editing PATH:
  - Close and reopen your terminal. Confirm path exists in %PATH% (echo %PATH%).

- Kai prints "Model ... not found" (Gemini 404):
  - Set GEMINI_MODEL to a supported model in `.env`, or check Google GenAI ListModels.
  - Ensure GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS is set.

- Ollama deprecation warnings:
  - Install `langchain-ollama` or update to the supported client per your LangChain version.

- Missing credentials:
  - Ensure `.env` or environment variables include GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS.

---
