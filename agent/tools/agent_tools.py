import csv
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path
import os
from utils.logger_handler import logger

rag = RagSummarizeService()
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
mounth_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09",
              "2025-10", "2025-11", "2025-12"]

external_data = {}


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="获取指定城市的天气信息，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度为50%，南风1级，AQI21，最近6小时降雨概率极低"


@tool(description="获取指定城市的名称，以纯字符串的形式进行返回")
def get_user_location() -> str:
    return random.choice(["北京", "上海", "广州", "深圳", "杭州", "漯河", "郑州"])


@tool(description="获取用户的ID，以纯字符串的形式进行返回")
def get_user_id() -> str:
    return "user_" + random.choice(user_ids)


@tool(description="获取当前月份，以纯字符串的形式返回")
def get_current_month() -> str:
    return random.choice(mounth_arr)


def generate_external_data():
    """
    {
           "user_id": {
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
            },
              "user_id": {
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
            },
              "user_id": {
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
                "month":{"特征"：xxx,"效率"：xxx...}
            },
            ....
    }
    :return:
    """
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"{external_data_path} 外部数据文件不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)

            for row in reader:
                if len(row) < 6:
                    logger.warning(f"[generate_external_data] 跳过无效数据行，列数不足：{row}")
                    continue

                user_id = row[0].replace('"', "").strip()
                feature = row[1].replace('"', "").strip()
                efficiency = row[2].replace('"', "").strip()
                consumables = row[3].replace('"', "").strip()
                comparison = row[4].replace('"', "").strip()
                time = row[5].replace('"', "").strip()

                if not user_id or not time:
                    logger.warning(f"[generate_external_data] 跳过无效数据行，用户 ID 或时间为空：{row}")
                    continue

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison
                }


@tool(description="从外部系统中获取指定用户的指定使用记录，以纯字符串的形式进行返回，如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()
    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"[generate_external_data]未能检索到用户：{user_id}在{month}的使用记录数据")
        return ""

@tool(
    description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "[fill_context_for_report]已经被调用"
