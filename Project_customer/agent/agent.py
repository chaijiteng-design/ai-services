from langchain.agents import create_agent

from Project_customer.agent.llm.adapter import get_model_client
from Project_customer.agent.llm.prompt import build_system_prompt

from agent.harness.middleware.scope import SkillScopeMiddleware
from agent.harness.run.context import AgentRuntimeContext, AgentRuntimeState
from agent.harness.tools.catalog import TOOL_CATALOG
from agent.llm.output import AgentOutput


def build_agent():
    """
    整个fastapi实例 共用一个agent?
    :return:
    """
    return create_agent(  # type: ignore
        model=get_model_client(),
        system_prompt=build_system_prompt(),
        tools=TOOL_CATALOG.get_agent_tools(),
        middleware=[
            SkillScopeMiddleware()
        ],
        response_format=AgentOutput,
        context_schema=AgentRuntimeContext,
        state_schema=AgentRuntimeState,
        name="智能客服专家"
    )