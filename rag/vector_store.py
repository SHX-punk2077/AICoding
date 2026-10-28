import os.path

from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abs_path
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
import os


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):  # 检索器对象
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    # k:检索的时候应该返回几个匹配的结果
    def load_document(self):
        """
        从数据文件内读取数据文件，转为向量存入向量库
        要计算文件的 MD5 去重
        :return:None
        """
        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False  # MD5 没处理过
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True  # MD5 处理过
                return False

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)
            if read_path.endswith("pdf"):
                return pdf_loader(read_path)
            return []

        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        for path in allowed_files_path:
            # 获取文件的 MD5
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}已存在知识库内，跳过")
                continue
            try:
                documents = get_file_documents(path)
                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue
                split_documents = self.splitter.split_documents(documents)

                if not split_documents:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue
                # 将内容存入向量库
                self.vector_store.add_documents(split_documents)
                # 记录已经处理好的文件的 md5，避免下次重复加载
                save_md5_hex(md5_hex)
                logger.info(f"[加载知识库]{path}处理完成，内容加载成功")
            except Exception as e:
                # exc_info=True 会记录详细的报错堆栈，如果为 False 仅记录报错信息本身
                logger.error(f"[加载知识库]{path}处理失败:{str(e)}", exc_info=True)
                continue

if __name__ == '__main__':
    vs = VectorStoreService()
    print("开始加载文档...")
    vs.load_document()
    print("加载完成，开始检索...")
    retriever = vs.get_retriever()
    res = retriever.invoke("迷路")
    print(f"检索到 {len(res)} 条结果")
    if not res:
        print("未找到相关内容，请检查：")
        print("1. 向量库是否为空")
        print("2. data 文件夹下是否有有效的 txt/pdf 文件")
        print("3. 检索词是否在文档内容中")
    else:
        for r in res:
            print(r.page_content)
            print("-" * 20)
