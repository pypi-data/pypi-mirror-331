# Copyright 2021 Pangea Cyber Corporation
# Author: Pangea Cyber Corporation
import logging

from pangea_translator.model.model import PangeaAiInput, PangeaMessage, PangeaRoles, FieldMapping

from .base import Translator

logger = logging.getLogger(__name__)

LANGCHAIN_SCHEMA = {
    "$schema": "http://json-schema.org/draft-2020-12/schema",
    "title": "Langchain prompt input",
    "description": "Accepts either an LLM input object with 'messages' or only messages.",
    "oneOf": [
        {"$ref": "#/components/schemas/messages"},
        {"$ref": "#/components/schemas/llm_input"},
    ],
    "components": {
        "schemas": {
            "messages": {
                "title": "Langchain prompt messages",
                "description": "Langchain styled prompt messages",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["role", "content"],
                },
            },
            "llm_input": {
                "type": "object",
                "description": "Langchain styled full prompt input",
                "properties": {
                    "messages": {
                        "$ref": "#/components/schemas/messages",
                    },
                    "model": {
                        "type": "string",
                        "description": "Cohere model ",
                    },
                },
                "required": ["messages"],
                "additionalProperties": True,
            },
        }
    },
}


class LangchainTranslator(Translator):
    """Translates Langchain-formatted input to PangeaAiPrompt"""

    def __init__(self, input):
        super().__init__(input)

    def get_model_and_version(self) -> (str, str):
        """
        Return model name and version
        :return: tuple of model name and version tuple
        """
        if isinstance(self._input, dict) and 'model' in self._input:
            return self._input.get('model'), self._input.get('version', None)
        else:
            return self.name(), None

    @classmethod
    def name(cls) -> str:
        return "langchain"

    @classmethod
    def schema(cls):
        return LANGCHAIN_SCHEMA

    def get_pangea_messages(self) -> PangeaAiInput:
        """Returns a PangeaAiInput struct containing translated input fields

        Roles: system, ai, human

        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello!"),
            AIMessage(content="Hi there!"),
        ]

        """
        pangea_prompt = PangeaAiInput()
        messages = self._input
        prefix_path = "$"
        if isinstance(self._input, dict):
            prefix_path = f"{prefix_path}.messages"
            messages=self._input.get("messages", [])


        for idx, prompt in enumerate(messages):
            role = prompt.get("role")
            if role == "human" or role == "user":
                role = PangeaRoles.PromptRoleUser.value
            elif role == "ai" or role == "assistant":
                role = PangeaRoles.PromptRoleLlm.value
            elif role == "system":
                role = PangeaRoles.PromptRoleSystem.value

            content = prompt.get("content")
            source_path = f"{prefix_path}[{idx}].content"
            target_path = self._get_target_json_path(idx)
            self._mappings.append(FieldMapping(InputPath=source_path, PangeaPath=target_path))
            pangea_prompt.messages.append(
                PangeaMessage(
                    role=role,
                    content=content,
                )
            )
        return pangea_prompt
