import json
import time
import logging
from typing import Any, Callable, Awaitable

from pydantic import BaseModel

from app.models.enums import ToolResultCode
from app.models.models import AgentToolCall
from infrastructure.db import async_session_factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    success: bool
    code: str
    message: str
    data: Any | None = None


class ToolExecutor:

    async def execte_tool(self,
                          trace_id: str,
                          tool_call_id: str,
                          tool_name: str,
                          tool_arguments: dict[str, Any],
                          operation: Callable[[], Awaitable[Any]]
                          )->str:
        """
        职责：
        1. 调用电商服务平台的数据接口
        2. 保存各个接口返回的数据


        raw_result
        {
        "success": success,
        "code": code,
        "message": message,
        "data": data
        }
        :return:
        """

        strat_time = time.perf_counter()
        # 1. 调用电商服务平台的接口正常
        try:
            raw_result = await operation()
            tool_result = ToolResult.model_validate(raw_result)
        # 2. 工具调用失败
        except Exception as e:
            logger.exception(f"工具【%s】调用失败", tool_name)
            tool_result = ToolResult(
                success=False,
                code=ToolResultCode.TOOL_CALL_FAILED,
                message="暂时无法获取到可靠业务数据"
            )
        latency_ms = int((time.perf_counter() - strat_time) * 1000)

        # 3. 保存工具执行的轨迹(工具名字、工具参数、工具结果、工具耗时、工具调用成功与否)
        await self._save_tool_call(
            trace_id=trace_id,
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            tool_arguments=tool_arguments,
            tool_result=tool_result,
            latency_ms=latency_ms
        )
        # 4、返回工具结果给LLM
        return json.dumps(tool_result.model_dump(),ensure_ascii=False)


    async def _save_tool_call(self,
                              trace_id: str,
                              tool_call_id: str,
                              tool_name: str,
                              tool_arguments: dict[str, Any],
                              tool_result: ToolResult,
                              latency_ms: int
                              ):
        """
        保存工具调用的轨迹
        """
        async with async_session_factory() as session:
            agent_tool_call = AgentToolCall(
                trace_id=trace_id,
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                arguments=tool_arguments,
                result=tool_result.model_dump(),
                latency_ms=latency_ms
            )
            session.add(agent_tool_call)
            await session.commit()

tool_executor = ToolExecutor()
