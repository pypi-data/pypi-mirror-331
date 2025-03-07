import os
from pathlib import Path

if "TERMINAL_GPT_CONFIG_PATH" in os.environ:
    CONFIG_PATH = Path(os.environ["TERMINAL_GPT_CONFIG_PATH"]).expanduser().resolve()
else:
    CONFIG_PATH = Path("~/.config/terminal_gpt").expanduser().resolve()

CONFIG_PATH.mkdir(parents=True, exist_ok=True)

DB_PATH = CONFIG_PATH / "db.sqlite3"
QUESTION_HISTORY_PATH = CONFIG_PATH / "question_history"
CODE_HISTORY_PATH = CONFIG_PATH / "code_history"

OPENAI_API_KEY = os.environ.get("TERMINAL_GPT_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("env OPENAI_API_KEY or TERMINAL_GPT_OPENAI_API_KEY not set")

TERMINAL_GPT_MODEL = os.environ.get("TERMINAL_GPT_MODEL", "gpt-4o-mini")
