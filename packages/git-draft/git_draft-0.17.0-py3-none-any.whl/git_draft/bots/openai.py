import dataclasses
import json
import logging
import openai
from pathlib import PurePosixPath
import textwrap
from typing import Any, Mapping, Self, Sequence, override

from .common import Action, Bot, Goal, Toolbox


_logger = logging.getLogger(__name__)


def threads_bot(
    api_key: str | None = None, base_url: str | None = None
) -> Bot:
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    return _ThreadsBot.create(client)


# https://aider.chat/docs/more-info.html
# https://github.com/Aider-AI/aider/blob/main/aider/prompts.py
_INSTRUCTIONS = """\
    You are an expert software engineer, who writes correct and concise code.
    Use the provided functions to find the filesyou need to answer the query,
    read the content of the relevant ones, and save the changes you suggest.
    When writing a file, include a summary description of the changes you have
    made.
"""


def _function_tool_param(
    name: str,
    description: str,
    inputs: Mapping[str, Any] | None = None,
    required_inputs: Sequence[str] | None = None,
) -> openai.types.beta.FunctionToolParam:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": textwrap.dedent(description),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": inputs or {},
                "required": list(inputs.keys()) if inputs else [],
            },
            "strict": True,
        },
    }


_tools = [
    _function_tool_param(
        name="list_files",
        description="List all available files",
    ),
    _function_tool_param(
        name="read_file",
        description="Get a file's contents",
        inputs={
            "path": {
                "type": "string",
                "description": "Path of the file to be read",
            },
        },
    ),
    _function_tool_param(
        name="write_file",
        description="""\
            Set a file's contents

            The file will be created if it does not already exist.
        """,
        inputs={
            "path": {
                "type": "string",
                "description": "Path of the file to be updated",
            },
            "contents": {
                "type": "string",
                "description": "New contents of the file",
            },
            "change_description": {
                "type": "string",
                "description": """\
                    Brief description of the changes performed on this file
                """,
            },
        },
    ),
]


@dataclasses.dataclass(frozen=True)
class _AssistantConfig:
    instructions: str
    model: str
    tools: Sequence[openai.types.beta.AssistantToolParam]


_assistant_config = _AssistantConfig(
    instructions=_INSTRUCTIONS,
    model="gpt-4o",
    tools=_tools,
)


class _ThreadsBot(Bot):
    """An OpenAI-backed bot

    See the following links for resources:

    * https://platform.openai.com/docs/assistants/tools/function-calling
    * https://platform.openai.com/docs/assistants/deep-dive#runs-and-run-steps
    * https://platform.openai.com/docs/api-reference/assistants-streaming/events
    * https://github.com/openai/openai-python/blob/main/src/openai/resources/beta/threads/runs/runs.py
    """

    def __init__(self, client: openai.OpenAI, assistant_id: str) -> None:
        self._client = client
        self._assistant_id = assistant_id

    @classmethod
    def create(cls, client: openai.OpenAI) -> Self:
        path = cls.state_folder_path(ensure_exists=True) / "ASSISTANT_ID"
        config = dataclasses.asdict(_assistant_config)
        try:
            with open(path) as f:
                assistant_id = f.read()
            client.beta.assistants.update(assistant_id, **config)
        except (FileNotFoundError, openai.NotFoundError):
            assistant = client.beta.assistants.create(**config)
            assistant_id = assistant.id
            with open(path, "w") as f:
                f.write(assistant_id)
        return cls(client, assistant_id)

    def act(self, goal: Goal, toolbox: Toolbox) -> Action:
        # TODO: Use timeout.
        thread = self._client.beta.threads.create()

        self._client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=goal.prompt,
        )

        with self._client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=self._assistant_id,
            event_handler=_EventHandler(self._client, toolbox),
        ) as stream:
            stream.until_done()

        return Action()


class _EventHandler(openai.AssistantEventHandler):
    def __init__(self, client: openai.Client, toolbox: Toolbox) -> None:
        super().__init__()
        self._client = client
        self._toolbox = toolbox

    def clone(self) -> Self:
        return self.__class__(self._client, self._toolbox)

    @override
    def on_event(self, event: Any) -> None:
        _logger.debug("Event: %s", event)
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            self._handle_action(run_id, event.data)
        # TODO: Handle (log?) other events.

    def _handle_action(self, run_id: str, data: Any) -> None:
        tool_outputs = list[Any]()
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            name = tool.function.name
            inputs = json.loads(tool.function.arguments)
            _logger.info("Requested tool: %s", tool)
            if name == "read_file":
                path = PurePosixPath(inputs["path"])
                output = self._toolbox.read_file(path)
            elif name == "write_file":
                path = PurePosixPath(inputs["path"])
                contents = inputs["contents"]
                self._toolbox.write_file(path, contents)
                output = "OK"
            elif name == "list_files":
                assert not inputs
                output = "\n".join(str(p) for p in self._toolbox.list_files())
            tool_outputs.append({"tool_call_id": tool.id, "output": output})

        run = self.current_run
        assert run, "No ongoing run"
        with self._client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=run.thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs,
            event_handler=self.clone(),
        ) as stream:
            stream.until_done()
