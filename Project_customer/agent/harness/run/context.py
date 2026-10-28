import json
from dataclasses import dataclass
from typing import Any

from langchain.agents import AgentState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing_extensions import NotRequired

from Project_customer.app.schemas import AgentRunRequest
from Project_customer.common.settings import get_settings


@dataclass(slots=True, frozen=True)  # slots:提高存储和查询速度 frozen： 冻结对象的属性个数
class AgentRuntimeContext:
    access_token: str
    trace_id: str

class AgentRuntimeState(AgentState):
    active_skill_code :NotRequired[str]

def build_messages(payload: AgentRunRequest) -> list[BaseMessage]:
    """
    职责：构建Agent运行时需要的消息
    1. 历史消息：多条、角色【USER / AI / HUMAN】
    2. 当前轮次的消息:有可能有多条、角色【USER】
    :return:
    """

    # 1、构建历史消息
    history_messages: list[dict[str, Any]] = _build_history_messages(payload.history)

    # 2、标准化消息对象为langchain统一的消息对象
    messages = [
        HumanMessage(content="")
        if message["role"] == "USER" else
        AIMessage(content="")
        for message in history_messages
    ]
    # 3、 构建当前轮次的消息
    current_messages = _build_current_messages(payload.messages)
    messages.append(HumanMessage(content=current_messages))

    # 4、返回历史消息+当前轮次消息
    return messages




def _build_history_messages(history):
    """
    职责：构建历史消息【历史消息的裁剪】
    裁剪历史消息的策略：
    策略1：条数
    策略2：字符数
    策略3：
    :param history:
    :return:
    """
    settings = get_settings()  # 获取设置

    # 1、获取候选的消息条数
    candidate_history_messages = history[-settings.history_message_limit:]
    # 2、计算候选历史消息的字符数（优先选择最近的消息计算字符数） len
    usages_total = 0
    messages = []
    for message in reversed(candidate_history_messages):
        message_content_len = len(_format_message(message))
        if message_content_len + usages_total > settings.history_character_budget:
            break

        messages.append(message)
        usages_total += message_content_len

    # 3、反转为正序
    messages.reverse()

    # 4、从消息列表中预留第一条消息角色是用户的开始 生成器对象就是一个迭代器对象 ---》迭代器表达是（） （列表推导式） []
    user_role_message_index = next(
        (index for index,message in enumerate(messages) if message['role'] =="USER"),
        None)

    # 5、切片返回
    return messages if user_role_message_index is None else messages[user_role_message_index:]




def _format_message(message):
    """
    职责：格式化单条消息的内容
    消息类型：文本类型、对象【商品、订单】类型
    :param message:
    :return:
    """
    # 1、消息类型是文本的
    if message["type"] == "text":
        return str(message["content"].get("text"))
    # 2、消息类型是对象的
    message_content = message["content"]

    return "该消息是一个对象结构：\n" + json.dumps(message_content, ensure_ascii=False)



def _build_current_messages(messages):
    """
    职责: 构建当前轮次的用户角色消息
    假设轮次只有一条用户消息：{"role":"USER","type":"object or text","content":"xxxx"}----->"content对应的字符串"
      假设轮次只有一条用户消息：[
                                {"role":"USER","type":"object or text","content":"xxxx"},
                                {"role":"USER","type":"object or text","content":"yyyy"},
                            ]----->"1. xxxx
                                    2. yyyy"

    :param messages:
    :return:
    """
    # 1、 获取当前轮次消息的内容列表
    message_contents = [_format_message(message) for message in messages]

    # 2、当前轮次只有一条消息
    if len(message_contents) == 1:
        return message_contents[0]
    # 3、当前轮次多条消息
    items = "\n".join([f"{index}. {message_content}" for index, message_content in enumerate(message_contents,start=1)])

    return "当前用户发送了多条消息，请你作为一个整体来理解，最新轮次的消息是:\n" + items


if __name__ == "__main__":
    list_container = [1, 2, 3, 4]

    print(list_container[1:])
    print(list_container[2:])
    print(list_container[3:])
    print(list_container[4:])