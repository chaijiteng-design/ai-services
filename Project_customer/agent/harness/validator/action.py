from locale import normalize
from typing import Any

from langgraph.pregel import _validate

from Project_customer.agent.llm.output import PageAction
from Project_customer.app.models.models import AgentToolCall
from Project_customer.agent.harness.rules.action import ACTION_CATALOG, ActionCode
from Project_customer.agent.harness.validator.validator import ValidateOutputError




def validate_page_action(
        page_action: PageAction | None,
        tool_calls: list[AgentToolCall]
) -> dict[str, Any] | None:
    # 1、没有页面行动（只是读取业务数据，没有修改业务数据）
    if page_action is None:
        # 1. 没有页面行动(只是读取业务数据、没有修改业务数据)
        if page_action is None:
            return None
    # 2. 校验是页面跳转的时候是否需要资源ID(进入我的订单列表特殊处理)
    # 2.1 获取行动码
    action_code = page_action.action_code

    # 2.2 校验行动码
    if action_code is None:
        raise ValidateOutputError("暂未生成页面动作")

    # 2.3 获取action_definition对象
    action_definition = ACTION_CATALOG.get_definition(action_code)

    # 2.4 校验 action_definition
    if action_definition is None:
        raise ValidateOutputError(f"页面动作需要的行动码：{action_code} 不符合白名单要求")

    # 2.5 构建进入我的订单列表的操作链接
    if action_definition.resource_type is None:
        return action_definition.build()

    # 3、校验resource_id
    normalize_resource_id = page_action.resource_id
    if normalize_resource_id is None:
        raise ValidateOutputError(f"{action_code} 必须提供订单编号")

    # 4、检验工具限制【校验订单状态是否是终态】
    order_data = _validate_get_order(normalize_resource_id,tool_calls)

    # 5、检验状态限制【校验订单状态是否是终态】
    _validate_order_status(order_data['status'], action_code, normalize_resource_id)

    # 6、构建其他五种行动的操作码
    return action_definition.build(resource_id=normalize_resource_id)

def _validate_get_order(
        normalized_resource_id:str,
        tool_calls: list[AgentToolCall])-> dict[str, Any]:
    '''
    职责：校验resource_id是否满足业务要求
    1、必须调用get_order工具
    2、必须调用success为true
    3、必须让get_order工具调用的参数（order_id）值是resource_id
    :param tool_calls:
    :param normalized_resource_id:
    :return:
    '''
    for tool_call in tool_calls:
        if (tool_call.tool_name == "get_order"
                and tool_call.success == True
                and tool_call.arguments["order_id"] == normalized_resource_id
        ):
            return tool_call.result['data']

    raise ValidateOutputError(
        f"页面动作引用的订单未经 get_order 工具确认：{normalized_resource_id}"
    )

def _validate_order_status(
        order_status: str,
        action_code:str,
        normalized_resource_id:str):
    '''
    职责：校验CANCEL_ORDER、EDIT_ADDRESS行动码是否是终态
    :param normalize_resource_id:
    :param tool_calls:
    :return:
    '''
    if action_code in [ActionCode.CANCEL_ORDER, ActionCode.EDIT_ADDRESS] and order_status in (
        "completed", "cancelled", "refunded"
    ):
        raise ValidateOutputError( f"订单 {normalized_resource_id} 当前状态为 {order_status}，不支持生成 {action_code} 页面跳转动作")
