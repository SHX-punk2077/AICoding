from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger
import os

def load_system_prompts():
    try:
        system_prompt_path = get_abs_path(prompts_conf["main_prompt_path"])
        # 检查文件是否存在
        if not os.path.exists(system_prompt_path):
            logger.error(f"[load_system_prompts] 提示词文件不存在：{system_prompt_path}")
            raise FileNotFoundError(f"提示词文件不存在：{system_prompt_path}")

        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except KeyError as e:
        logger.error(f"[load_system_prompts] 请检查配置文件 {get_abs_path('config/prompts.yml')}")
        raise e
    except Exception as e:
        logger.error(f"[load_system_prompts] 解析系统提示词出错，{str(e)}")
        raise e


def load_rag_prompts():
    try:
        rag_prompt_path = get_abs_path(prompts_conf["rag_summarize_prompt_path"])
        # 检查文件是否存在
        if not os.path.exists(rag_prompt_path):
            logger.error(f"[load_rag_prompts] 提示词文件不存在：{rag_prompt_path}")
            raise FileNotFoundError(f"提示词文件不存在：{rag_prompt_path}")

        with open(rag_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except KeyError as e:
        logger.error(f"[load_rag_prompts] 请检查配置文件 {get_abs_path('config/prompts.yml')}")
        raise e
    except Exception as e:
        logger.error(f"[load_rag_prompts] 解析RAG总结提示词出错，{str(e)}")
        raise e


def load_report_prompts():
    try:
        report_prompt_path = get_abs_path(prompts_conf["report_prompt_path"])
        # 检查文件是否存在
        if not os.path.exists(report_prompt_path):
            logger.error(f"[load_report_prompts] 提示词文件不存在：{report_prompt_path}")
            raise FileNotFoundError(f"提示词文件不存在：{report_prompt_path}")

        with open(report_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except KeyError as e:
        logger.error(f"[load_report_prompts] 请检查配置文件 {get_abs_path('config/prompts.yml')}")
        raise e
    except Exception as e:
        logger.error(f"[load_report_prompts] 解析报告提示词出错，{str(e)}")
        raise e


if __name__ == '__main__':
    print(load_report_prompts())