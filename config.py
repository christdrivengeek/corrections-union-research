import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "states")
OUTPUT_CSV = os.path.join(BASE_DIR, "master_data.csv")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")
PROGRESS_MD = os.path.join(BASE_DIR, "PROGRESS.md")
PRESENTATION_MD = os.path.join(BASE_DIR, "PRESENTATION_DATA.md")

# Local LLM (Ollama)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hermes3:8b")

# Optional Cloud Fallbacks
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
