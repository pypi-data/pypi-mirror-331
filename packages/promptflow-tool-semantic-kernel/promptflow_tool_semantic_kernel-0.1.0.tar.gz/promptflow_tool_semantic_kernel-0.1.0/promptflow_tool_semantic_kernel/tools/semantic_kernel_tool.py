import asyncio
import logging
from jinja2 import Template
from promptflow.core import tool
from promptflow.connections import CustomConnection
from promptflow.contracts.types import PromptTemplate
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

@tool
def my_tool(
    connection: CustomConnection,
    deployment_name: str,
    chat_history: list[str],
    prompt: PromptTemplate,
    **kwargs
) -> str:
    

    rendered_prompt = Template(prompt, trim_blocks=True, keep_trailing_newline=True).render(**kwargs)

    kernel = Kernel()
    chat_completion = AzureChatCompletion(api_key=connection.secrets["api_key"], deployment_name=deployment_name, base_url=connection.configs["base_url"])
    kernel.add_service(chat_completion)

    # Set the logging level for  semantic_kernel.kernel to DEBUG.
    setup_logging()
    logging.getLogger("kernel").setLevel(logging.DEBUG)

    # Add a plugin (the LightsPlugin class is defined below)
    # kernel.add_plugin(
    #     LightsPlugin(),
    #     plugin_name="Lights",
    # )

    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create a chat history object
    history = ChatHistory()

    # Process chat_history - assuming alternating user/assistant messages starting with user
    for i, message in enumerate(chat_history):
        if i % 2 == 0:  # Even indices are user messages
            history.add_user_message(message)
        else:  # Odd indices are assistant messages
            history.add_assistant_message(message)

    # Add the current prompt as the latest user message
    history.add_user_message(rendered_prompt)

    # Get the response from the AI using non-streaming completion
    async def get_completion():
        return await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )
    
    # Run the async function and get the complete response
    return asyncio.run(get_completion())
