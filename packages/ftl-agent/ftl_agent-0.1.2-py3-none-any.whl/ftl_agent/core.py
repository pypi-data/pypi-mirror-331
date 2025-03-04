from ftl_agent.agents import CodeAgent
from smolagents import LiteLLMModel
import yaml
import importlib.resources


def create_model(model_id, context=8192):

    return LiteLLMModel(
        model_id=model_id,
        num_ctx=context,
    )


def make_agent(tools, model):
    prompt_templates = yaml.safe_load(
        importlib.resources.files("ftl_agent.prompts").joinpath("code_agent.yaml").read_text()
    )
    agent = CodeAgent(
        tools=tools,
        model=model,
        verbosity_level=4,
        prompt_templates=prompt_templates,
    )
    return agent


def run_agent(tools, model, problem_statement):
    agent = make_agent(tools, model)
    return agent.run(problem_statement, stream=True)


