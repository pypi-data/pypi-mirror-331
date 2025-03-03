from __future__ import annotations

import importlib.metadata
import logging
import optparse
import sys
import textwrap

from .bots import load_bot
from .common import Store, open_editor
from .manager import Manager


logging.basicConfig(level=logging.INFO)


EPILOG = """\
    More information via `man git-draft` and https://mtth.github.io/git-draft.
"""


parser = optparse.OptionParser(
    prog="git-draft",
    epilog=textwrap.dedent(EPILOG),
    version=importlib.metadata.version("git_draft"),
)

parser.disable_interspersed_args()


def add_command(name: str, **kwargs) -> None:
    def callback(_option, _opt, _value, parser) -> None:
        parser.values.command = name

    parser.add_option(
        f"-{name[0].upper()}",
        f"--{name}",
        action="callback",
        callback=callback,
        **kwargs,
    )


add_command("discard", help="discard the current draft")
add_command("finalize", help="apply the current draft to the original branch")
add_command("generate", help="start a new draft from a prompt")

parser.add_option(
    "-a",
    "--bot",
    dest="bot",
    help="bot key",
    default="openai",
)
parser.add_option(
    "-c",
    "--checkout",
    help="check out generated changes",
    action="store_true",
)
parser.add_option(
    "-d",
    "--delete",
    help="delete draft after finalizing or discarding",
    action="store_true",
)
parser.add_option(
    "-p",
    "--prompt",
    dest="prompt",
    help="draft generation prompt, read from stdin if unset",
)
parser.add_option(
    "-r",
    "--reset",
    help="reset index before generating a new draft",
    action="store_true",
)
parser.add_option(
    "-s",
    "--sync",
    help="commit prior worktree changes separately",
    action="store_true",
)


EDITOR_PLACEHOLDER = """\
    Enter your prompt here...
"""


def main() -> None:
    (opts, _args) = parser.parse_args()

    manager = Manager.create(Store.persistent())

    command = getattr(opts, "command", "generate")
    if command == "generate":
        bot = load_bot(opts.bot, {})
        prompt = opts.prompt
        if not prompt:
            if sys.stdin.isatty():
                prompt = open_editor(textwrap.dedent(EDITOR_PLACEHOLDER))
            else:
                prompt = sys.stdin.read()
        manager.generate_draft(
            prompt, bot, checkout=opts.checkout, reset=opts.reset
        )
    elif command == "finalize":
        manager.finalize_draft(delete=opts.delete)
    elif command == "discard":
        manager.discard_draft(delete=opts.delete)
    else:
        assert False, "unreachable"


if __name__ == "__main__":
    main()
