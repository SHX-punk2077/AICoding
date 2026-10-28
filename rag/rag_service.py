"""
rag总结服务：
用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
"""
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from utils.logger_handler import logger

def print_prompt(prompt):
    print("--------------------" * 5)
    print(prompt.to_string())
    print("--------------------"*5)
    return  prompt

class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_txt = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_txt)
        self.model = chat_model
        self.chain = self.__init__chain()
        
        self.query_rewrite_prompt = PromptTemplate.from_template(
            "你是一个查询改写专家。请将用户的问题改写成更适合检索的关键词组合，"
            "保留核心语义但去除冗余表达。只输出改写后的查询词，不要其他内容。\n\n"
            "用户问题：{query}\n\n改写后的查询:"
        )
        self.rewrite_chain = self.query_rewrite_prompt | self.model | StrOutputParser()

    def __init__chain(self):
        chain = self.prompt_template |print_prompt|self.model | StrOutputParser()
        return chain

    def rewrite_query(self, query: str) -> str:
        """查询改写"""
        try:
            rewritten = self.rewrite_chain.invoke({"query": query})
            logger.info(f"[查询改写] 原始：{query} -> 改写后：{rewritten}")
            return rewritten.strip()
        except Exception as e:
            logger.error(f"[查询改写] 失败：{str(e)}")
            return query

    def retriever_docs(self, query: str) -> list[Document]:
        rewritten_query = self.rewrite_query(query)
        return self.retriever.invoke(rewritten_query)

    # 总结函数
    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)  # list[Document]
        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"[参考资料{counter}]：参考资料：{doc.page_content}|参考元数据：{doc.metadata}\n"
        return self.chain.invoke(
            {"input": query,
             "context": context}
        )
if __name__ == '__main__':
    rag_service = RagSummarizeService()
    print(rag_service.rag_summarize("小户型适合哪些扫地机器人？"))
