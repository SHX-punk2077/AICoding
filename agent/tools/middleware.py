from langchain.agents import AgentState
from utils.prompt_loader import load_report_prompts,load_system_prompts
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from typing import Callable
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
import hashlib
import json
import time

@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    start_time = time.time()
    logger.info(f"[monitor_tool] 监控工具执行：{request.tool_call['name']}")
    logger.info(f"[monitor_tool] 传入参数：{request.tool_call['args']}")
    
    tool_call_key = f"{request.tool_call['name']}:{json.dumps(request.tool_call['args'], sort_keys=True)}"
    call_hash = hashlib.md5(tool_call_key.encode()).hexdigest()
    
    if not hasattr(request.runtime, 'tool_cache'):
        request.runtime.tool_cache = {}
    
    if call_hash in request.runtime.tool_cache:
        logger.info(f"[monitor_tool] 使用缓存结果：{request.tool_call['name']}")
        return request.runtime.tool_cache[call_hash]
    
    try:
        result = handler(request)
        execution_time = time.time() - start_time
        logger.info(f"[monitor_tool] 工具：{request.tool_call['name']}调用成功，耗时：{execution_time:.2f}s")

        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True
        
        request.runtime.tool_cache[call_hash] = result
        
        if not hasattr(request.runtime, 'tool_stats'):
            request.runtime.tool_stats = {}
        if request.tool_call['name'] not in request.runtime.tool_stats:
            request.runtime.tool_stats[request.tool_call['name']] = {'count': 0, 'total_time': 0}
        request.runtime.tool_stats[request.tool_call['name']]['count'] += 1
        request.runtime.tool_stats[request.tool_call['name']]['total_time'] += execution_time

        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[monitor_tool] 工具：{request.tool_call['name']}调用失败，耗时：{execution_time:.2f}s，原因:{str(e)}")
        raise e


@before_model
def log_before_model(
        state: AgentState,  # 整个Agent智能体的状态记录
        runtime: Runtime,  # 记录整个执行过程中的上下文信息
):  # 在模型执行前输出日志
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息")
    # state['messages'][-1]  获取最新的消息
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__}|{state['messages'][-1].content.strip()}")
    return None

@dynamic_prompt#每一次在生成提示词之前，调用此函数
def report_prompt_switch(request:ModelRequest):  # 动态切换提示词
    is_report=request.runtime.context.get("report",False)
    if is_report:#是报告的生成场景，返回报告生成提示词
        return load_report_prompts()
    return load_system_prompts()
