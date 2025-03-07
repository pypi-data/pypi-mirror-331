import shlex
import subprocess
import sys

from colorama import Fore, Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style as PromptStyle
from pygments.lexers.shell import BashLexer

from terminal_gpt.chatgpt import Message, fetch_chat_completion
from terminal_gpt.helper.system_helper import get_shell
from terminal_gpt.settings import CODE_HISTORY_PATH, QUESTION_HISTORY_PATH

RESET_LINE = "\r\u001b[2K"
PROMPT_STYLE = PromptStyle.from_dict(
    {
        "brackets": "ansibrightmagenta bold",
        "user": "ansiyellow bold",
        "code": "ansicyan bold",
    }
)
BRACKET_COLOR = Fore.MAGENTA + Style.BRIGHT
ASSISTANT_COLOR = Fore.GREEN + Style.BRIGHT
CODE_COLOR = Fore.CYAN + Style.BRIGHT


def main():
    try:
        # ask user a question for chat gpt
        argv = " ".join(sys.argv[1:])
        question = get_input(argv)
        if question.strip() == "":
            print("")
            sys.exit(1)

        # ask chat gpt and stream the output

        gpt_code = ask_chat_gpt(question.strip())
        if gpt_code.strip() == "":
            print("")
            sys.exit(1)

        # ask user if they wanna modify the gpt code
        partial_print("\r")
        command = ask_modify_code(gpt_code)

        # Properly escape and encode the command to add to history
        shell_exec = get_shell()
        escaped_command = shlex.quote(command)
        if "zsh" in shell_exec:
            history_command = f"print -s {escaped_command}"
        else:
            history_command = f"history -s {escaped_command}"
        subprocess.run([shell_exec, "-i", "-c", history_command])

        # if they hit enter, run the code!
        response = subprocess.run([shell_exec, "-i", "-c", command])
        sys.exit(response.returncode)

    except KeyboardInterrupt:
        sys.exit(130)  # Common exit code for SIGINT: 128 (offset) + 2 (SIGINT)


def get_input(default: str | None = None):
    return prompt(
        [
            ("class:brackets", "["),
            ("class:user", "question"),
            ("class:brackets", "] "),
        ],
        default=default or "",
        style=PROMPT_STYLE,
        history=FileHistory(QUESTION_HISTORY_PATH.as_posix()),
    )


def ask_chat_gpt(question: str) -> str:
    partial_print(f"{BRACKET_COLOR}[{ASSISTANT_COLOR}chatgpt{BRACKET_COLOR}] {Style.RESET_ALL}")
    current_line = ""
    current_code: str | None = None

    messages = generate_prompt(question)

    for chunk in fetch_chat_completion(messages, cache_delay=True):
        delta = chunk["choices"][0]["delta"]
        content = delta.get("content")
        if content:
            for c in content:
                if current_code is None:
                    partial_print(c)
                    if c == "\n":
                        current_line = ""
                    else:
                        current_line += c
                    if current_line.upper()[:5] == "CODE:":
                        current_code = current_line[5:].lstrip()

                        partial_print(RESET_LINE)
                else:
                    if c == "\n":
                        c = " "

                    if current_code == "" and c == " ":
                        continue

                    if current_code == "":
                        partial_print(f"{BRACKET_COLOR}[{CODE_COLOR}code{BRACKET_COLOR}] {Style.RESET_ALL}")

                    partial_print(c)
                    current_code += c

    return current_code or ""


def ask_modify_code(code: str):
    return prompt(
        [
            ("class:brackets", "["),
            ("class:code", "code"),
            ("class:brackets", "] "),
        ],
        default=code,
        style=PROMPT_STYLE,
        lexer=PygmentsLexer(BashLexer),
        history=FileHistory(CODE_HISTORY_PATH.as_posix()),
    )


SYSTEM = """
You are using a ZSH shell on MacOS 13.6.
You respond concisely to requests for help on how to format shell commands.
This is a terminal environment, so you don't over explain anything, you keep things short and sweet.
Explanations shouldn't be over 2 sentences, preferably 1 sentence.
All lowercase, very informal and prose.
Then you give the code the user should run.
Never return more text after the code.
"""


def generate_prompt(question: str) -> list[Message]:
    return [
        {"role": "system", "content": SYSTEM.replace("\n", " ").strip()},
        {"role": "system", "content": "Here are some examples:"},
        {"role": "user", "content": "How do I list files?"},
        {"role": "assistant", "content": 'simply "ls"\nCode: ls -l'},
        {"role": "user", "content": "show pids with their connections"},
        {
            "role": "assistant",
            "content": "List network connections, avoiding DNS, showing ports as numbers, with retries\n"
            + "Code: lsof -V -R -i -P -n",
        },
        {"role": "system", "content": "Let's begin!"},
        {"role": "user", "content": question},
    ]


def partial_print(x):
    print(x, end="", flush=True)


if __name__ == "__main__":
    main()
