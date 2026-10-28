from enum import StrEnum


class AgentTraceStatus(StrEnum):
    """AgentTrace 执行轨迹状态"""

    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReplyType(StrEnum):
    """Agent 本轮生成的回复类型枚举。"""

    ANSWER = "ANSWER"   # 回答
    CLARIFY = "CLARIFY" # 澄清
    DECLINE = "DECLINE" # 拒绝
    REQUEST_HANDOFF = "REQUEST_HANDOFF" # 转移


class ToolResultCode(StrEnum):
    """工具执行结果状态码枚举。"""

    KNOWLEDGE_SEARCH_COMPLETED = "KNOWLEDGE_SEARCH_COMPLETED" # 知识搜索完成
    TOOL_CALL_FAILED = "TOOL_CALL_FAILED"   # 工具调用失败