import os
import glob
import rich
import pyperclip
import subprocess

from difflib import unified_diff

from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.completion import Completer, Completion


# classes
class PathCompleter(Completer):
    def get_completions(self, document, complete_event):
        if not complete_event.completion_requested:
            return

        full_text = document.text_before_cursor
        if full_text.startswith("!"):
            parts = full_text.split(maxsplit=1)
            if len(parts) > 1:
                file_fragment = parts[1]
                start_pos = -len(file_fragment)
            else:
                file_fragment = ""
                start_pos = 0
        else:
            file_fragment = full_text
            start_pos = 0

        expanded = os.path.expanduser(file_fragment)
        matches = glob.glob(expanded + "*")
        for match in matches:
            yield Completion(match, start_position=start_pos)


# functions
def get_input(prompt_text: str, history: FileHistory | InMemoryHistory) -> str:
    session = PromptSession(history=history, completer=PathCompleter())
    return session.prompt(prompt_text)


def confirm(text: str, *args, **kwargs) -> bool:
    confirmed = get_input(f"{text} (y/n): ", InMemoryHistory())
    if confirmed.lower() in ["y", "yes"]:
        return True
    else:
        return False


def echo(text: str, *args, **kwargs) -> None:
    rich.print(text, *args, **kwargs)


def print(
    text: str, as_markdown: bool = True, as_panel: bool = True, header: str = "codai"
) -> None:
    # console
    console = Console()

    # style map
    style_map = {
        "user": "bold cyan",
        "codai": "bold violet",
    }

    if as_markdown:
        text = Markdown(text)

    if as_panel:
        text = Panel(text, title=header, border_style=style_map[header])

    console.print(text)


def clear() -> None:
    console = Console()
    console.clear()


def run_command(command: str) -> str:
    confirmed = confirm(f"Run command: {command}?")
    if not confirmed:
        echo("Aborted.")
        return "User aborted running the command. Do not try to run it again."

    res = subprocess.run(command, shell=True, capture_output=True)
    stdout = res.stdout.decode("utf-8")
    stderr = res.stderr.decode("utf-8")

    if stdout and not stderr:
        return stdout
    elif not stdout and stderr:
        return stderr
    else:
        return f"{stdout}\n\n{stderr}"


def _copy_to_clipboard(text: str) -> None:
    pyperclip.copy(text)


def copy_to_clipboard(text: str) -> str:
    _copy_to_clipboard(text)
    return "Successfully copied text to to clipboard"


def read_file(file_path: str) -> str:
    """read file content"""
    with open(file_path, "r") as file:
        return file.read()


def git_diff(old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = unified_diff(old_lines, new_lines, lineterm="")

    return "\n".join(diff)


def write_file(file_path: str, content: str) -> str:
    if os.path.exists(file_path):
        old_content = read_file(file_path)
    else:
        old_content = ""
    diff = git_diff(old_content, content)

    confirmed = confirm(f"Are you sure you want to write to {file_path}?\n\n{diff}")
    if not confirmed:
        print("Aboring the write operation...")
        return "User aborted the write! Check why with them."

    with open(file_path, "w") as file:
        file.write(content)

    return "Success!"
