from typing import Optional

import click

from .config import Configuration
from .conversation import Conversation
from .llm_client import LLMClient
from .tools import SKILLS_TOOLS


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("prompt", required=False)
def chat(prompt: Optional[str]) -> None:
    config = Configuration.from_env()
    client = LLMClient(
        api_key=config.api_key,
        api_base_url=config.api_base_url,
        model_name=config.model_name,
        timeout_seconds=config.timeout_seconds,
    )
    conversation = Conversation(client=client, tools=SKILLS_TOOLS, skills_folder=config.skills_folder)

    if prompt:
        response = conversation.send(prompt)
        click.echo(response)
        return

    click.echo("Skills Runner v0.1.0")
    click.echo("Type 'exit' to quit")

    while True:
        user_input = click.prompt("You")
        if user_input.strip().lower() == "exit":
            break
        response = conversation.send(user_input)
        click.echo(response)


def main() -> None:
    cli()
