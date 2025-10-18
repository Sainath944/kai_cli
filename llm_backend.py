import requests

def get_active_ollama_model():
    try:
        response = requests.get("http://localhost:11434/api/ps", timeout=3)
        response.raise_for_status()
        data = response.json()

        models = data.get("models", [])
        if not models:
            # print("❌ No Ollama model is running.")
            return [False, None]

        # Extract model name and remove tag after ':'
        model_name = models[0].get("model", "").split(":")[0].strip()
        # print(model_name)
        return [True, model_name]

    except requests.exceptions.ConnectionError:
        # print("⚠️ Ollama server not running or unreachable at localhost:11434.")
        return [False, None]
    except Exception as e:
        # print(f"⚠️ Error: {e}")
        return [False, None]


