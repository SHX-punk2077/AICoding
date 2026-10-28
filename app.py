import time
import streamlit as st
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agent.react_agent import ReactAgent

# 自定义 CSS 样式
st.markdown("""
<style>
/* 全局字体和背景 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.stApp {
    font-family: 'Noto Sans SC', sans-serif;
}

/* 主标题样式 */
.stTitle h1 {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
    font-weight: 700;
    padding: 1rem 0;
    text-align: center;
}

/* 聊天消息气泡美化 */
.stChatMessage {
    border-radius: 15px;
    margin: 10px 0;
    padding: 15px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
}

.stChatMessage:hover {
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}

/* 用户消息样式 */
.stChatMessage[data-testid="user"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

/* AI 消息样式 */
.stChatMessage[data-testid="assistant"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #2d3748;
}

/* 输入框美化 */
.stChatInput {
    border-radius: 25px;
    border: 2px solid #e2e8f0;
    padding: 15px 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.stChatInput:focus {
    border-color: #667eea;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
}

/* 侧边栏美化 */
.css-1d391kg {
    background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    border-right: 1px solid #dee2e6;
}

/* 按钮美化 */
.stButton > button {
    border-radius: 12px;
    border: none;
    padding: 12px 24px;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

/* 常见问题按钮渐变 */
div[data-testid="stVerticalBlock"] .stButton:nth-child(1) > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

div[data-testid="stVerticalBlock"] .stButton:nth-child(2) > button {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
}

div[data-testid="stVerticalBlock"] .stButton:nth-child(3) > button {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
}

div[data-testid="stVerticalBlock"] .stButton:nth-child(4) > button {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: white;
}

div[data-testid="stVerticalBlock"] .stButton:nth-child(5) > button {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    color: white;
}f

/* 滑块美化 */
.stSlider > div {
    padding: 10px 0;
}

/* 加载动画美化 */
.stSpinner > div {
    border-top-color: #667eea;
    border-right-color: #764ba2;
}

/* 分割线美化 */
.stDivider {
    border-top: 2px solid #667eea !important;
    opacity: 0.3;
}

/* 滚动条美化 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* 淡入动画 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.stChatMessage {
    animation: fadeIn 0.5s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# 页面配置
st.set_page_config(
    page_title="豫树扫地机器人智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.title("🤖 豫树扫地机器人智能客服")
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">您的智能家居清洁专家，7×24 小时在线服务</p>',
            unsafe_allow_html=True)
st.divider()

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 个性化设置")

    # 使用容器美化设置项
    with st.container():
        enable_thinking = st.checkbox("💭 显示思考过程", value=True, help="勾选后可查看 AI 的思考推理过程")
        streaming_speed = st.slider("⌨️ 打字速度", 0.01, 0.1, 0.02, help="调整回复文字的显示速度")

    st.divider()

    # 清空对话按钮
    if st.button("🗑️ 清空对话历史", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["conversation_count"] = 0
        st.rerun()

    st.divider()

    # 常见问题区域
    st.subheader("❓ 常见问题速查")
    st.markdown('<p style="color: #666; font-size: 0.9rem;">点击按钮快速提问</p>', unsafe_allow_html=True)

    faq_questions = [
        ("🏠 小户型适合哪些扫地机器人？", "小户型适合哪些扫地机器人？"),
        ("😰 扫地机器人迷路了怎么办？", "扫地机器人迷路了怎么办？"),
        ("🔧 如何维护保养扫地机器人？", "如何维护保养扫地机器人？"),
        ("🆚 扫拖一体机和纯扫地机有什么区别？", "扫拖一体机和纯扫地机有什么区别？"),
        ("📊 生成我的本月使用报告", "生成我的本月使用报告")
    ]

    for icon_text, question in faq_questions:
        if st.button(f"{icon_text} {question}", use_container_width=True):
            st.session_state["pending_question"] = question

    st.divider()

    # 添加温馨提示
    st.info("💡 **小贴士**：您可以直接在下方输入框提问，也可以点击左侧常见问题快速获得解答哦～")

# 初始化 Agent
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

# 初始化消息历史记录
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 初始化对话轮次计数
if "conversation_count" not in st.session_state:
    st.session_state["conversation_count"] = 0

# 处理待发送问题
if "pending_question" in st.session_state and st.session_state["pending_question"]:
    prompt = st.session_state["pending_question"]
    st.session_state["pending_question"] = ""
else:
    prompt = st.chat_input("请输入您的问题，例如：扫地机器人如何选择？")

if prompt:
    # 显示用户消息
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # 更新对话轮次
    st.session_state["conversation_count"] += 1

    # 获取 AI 响应
    with st.spinner("🤔 智能客服正在思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        # 创建占位符用于流式输出
        response_placeholder = st.empty()
        full_response = ""

        # 流式输出
        for chunk in res_stream:
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
            time.sleep(streaming_speed)

        response_placeholder.markdown(full_response.strip())

    # 保存 AI 响应到历史记录
    st.session_state["messages"].append({"role": "assistant", "content": full_response.strip()})

# 页脚信息
st.divider()
st.markdown("""
<div style='text-align: center; color: #999; padding: 20px 0;'>
    <p>🌟 豫树智能客服 | 技术支持：AI大模型RAG | 版本 v1.0</p>
    <p style='font-size: 0.8rem;'>© 2026 豫树科技。All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
