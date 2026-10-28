from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id, get_current_month,
                                     fetch_external_data,
                                     fill_context_for_report)

from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent:
    def __init__(self, llm=None, tools=None, middleware=None):
        self.llm = llm or chat_model
        self.tools = tools or [rag_summarize, get_weather, get_user_id, get_user_location,
                               get_current_month, fetch_external_data, fill_context_for_report]
        self.middleware = middleware or [monitor_tool, log_before_model, report_prompt_switch]

        self.agent = create_agent(
            model=self.llm,
            system_prompt=load_system_prompts(),
            tools=self.tools,
            middleware=self.middleware
        )

    def execute_stream(self, query: str):
        input_dict = {"messages":[
                      {"role": "user", "content": query
                       }]}
    # 第三个参数context就是上下文runtime中的信息，就是我们做提示词切换的标记

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message=chunk["messages"][-1]
            if latest_message.content:
                #  yield与普通函数的区别：
                # 普通函数：return 返回一次，函数结束
                # 生成器函数：yield 可以多次返回，每次返回后暂停，下次调用继续执行
                # 在这个 RAG 项目中，使用 yield 可以让用户实时看到 AI 的思考和处理过程，
                # 特别适合需要较长时间处理的报告生成、文档检索等场景。
                yield latest_message.content.strip()+"\n"

if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="",flush= True)
