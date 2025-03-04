import click

from .core import create_model, run_agent
from .default_tools import TOOLS
from .tools import get_tool, load_tools
from .prompts import SOLVE_PROBLEM
from .codegen import (
    generate_python_header,
    reformat_python,
    generate_python_tool_call,
    generate_explain_header,
    generate_explain_action_step,
    generate_playbook_header,
    generate_playbook_task,
)
import faster_than_light as ftl
from ftl_agent.memory import ActionStep
from smolagents.agent_types import AgentText


@click.command()
@click.option("--tools", "-t", multiple=True)
@click.option("--tools-files", "-f", multiple=True)
@click.option("--problem", "-p", prompt="What is the problem?")
@click.option("--system-design", "-s", prompt="What is the system design?")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--modules", "-M", default=['modules'], multiple=True)
@click.option("--inventory", "-i", default="inventory.yml")
@click.option("--extra-vars", "-e", multiple=True)
@click.option("--output", "-o", default="output.py")
@click.option("--explain", "-o", default="output.txt")
@click.option("--playbook", default="playbook.yml")
def main(
    tools,
    tools_files,
    problem,
    system_design,
    model,
    modules,
    inventory,
    extra_vars,
    output,
    explain,
    playbook,
):
    """A agent that solves a problem given a system design and a set of tools"""
    tool_classes = {}
    tool_classes.update(TOOLS)
    for tf in tools_files:
        tool_classes.update(load_tools(tf))
    model = create_model(model)
    state = {
        "inventory": ftl.load_inventory(inventory),
        "modules": modules,
        "localhost": ftl.localhost,
    }
    for extra_var in extra_vars:
        name, _, value = extra_var.partition("=")
        state[name] = value

    generate_python_header(
        output,
        system_design,
        problem,
        tools_files,
        tools,
        inventory,
        modules,
        extra_vars,
    )
    generate_explain_header(explain, system_design, problem)
    generate_playbook_header(playbook, system_design, problem)

    for o in run_agent(
        tools=[get_tool(tool_classes, t, state) for t in tools],
        model=model,
        problem_statement=SOLVE_PROBLEM.format(
            problem=problem, system_design=system_design
        ),
    ):
        if isinstance(o, ActionStep):
            generate_explain_action_step(explain, o)
            if o.trace and o.tool_calls:
                for call in o.tool_calls:
                    generate_python_tool_call(output, call)
                generate_playbook_task(playbook, o)
        elif isinstance(o, AgentText):
            print(o.to_string())

    reformat_python(output)
