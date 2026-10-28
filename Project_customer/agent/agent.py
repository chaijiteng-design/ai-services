from langchain.agents import create_agent

from Project_customer.agent.llm.adapter import get_model_client
from Project_customer.agent.prompt import build_system_prompt

from agent.harness.run.context import AgentRuntimeContext, AgentRuntimeState
from agent.harness.tools.catalog import TOOL_CATALOG
from agent.llm.output import AgentOutput


def build_agent():
    """
    整个fastapi实例 共用一个agent?
    :return:
    """
    return create_agent(
        model=get_model_client(),
        system_prompt=build_system_prompt(),
        tools=TOOL_CATALOG.get_agent_tools(),
        middleware=[
            SystemPromptMiddleware(),
        ],
        response_format=AgentOutput,
        state_schema=AgentRuntimeState,
        name="智能客服专家"
    )