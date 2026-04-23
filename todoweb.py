import streamlit as st
import datetime
import json
import os
import pandas as pd

# 配置页面
st.set_page_config(page_title="✨ 极简待办 Web版", layout="centered")

# 数据持久化文件
DATA_FILE = "todo_data_web.json"

# 四象限颜色定义
COLORS = {
    "Do First": "#FF6B6B",   # 红色
    "Schedule": "#4DABF7",   # 蓝色
    "Delegate": "#FCC419",   # 橙黄
    "Delete": "#ADB5BD"      # 灰色
}

# --- 数据处理逻辑 ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# 初始化 Session State
if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()

# --- UI 界面 ---
st.title("📅 我的待办清单")
st.write(f"当前时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %A')}")

# --- 输入区 ---
with st.expander("➕ 添加新事项", expanded=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        new_task_text = st.text_input("内容：", placeholder="输入待办事项...")
    with col2:
        priority = st.selectbox("类型：", list(COLORS.keys()))
    
    date_col1, date_col2 = st.columns([1, 1])
    with date_col1:
        task_date = st.date_input("日期：", datetime.date.today())
    
    if st.button("确认添加", use_container_width=True):
        if new_task_text:
            new_task = {
                "id": datetime.datetime.now().timestamp(),
                "text": new_task_text,
                "date": str(task_date),
                "priority": priority,
                "completed": False
            }
            st.session_state.tasks.append(new_task)
            save_data(st.session_state.tasks)
            st.rerun()
        else:
            st.warning("内容不能为空")

# --- 任务显示区 ---
if st.session_state.tasks:
    # 提取所有日期并排序
    all_dates = sorted(list(set(t["date"] for t in st.session_state.tasks)))
    
    # 使用 Streamlit 选项卡按日期分类
    if all_dates:
        tabs = st.tabs([f"📅 {d}" for d in all_dates])
        
        for i, date_str in enumerate(all_dates):
            with tabs[i]:
                # 过滤该日期的任务并按优先级排序
                priority_order = {"Do First": 1, "Schedule": 2, "Delegate": 3, "Delete": 4}
                day_tasks = [t for t in st.session_state.tasks if t["date"] == date_str]
                day_tasks.sort(key=lambda x: priority_order.get(x["priority"], 5))

                for task in day_tasks:
                    # 使用 container 包裹每个任务卡片
                    with st.container():
                        c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                        
                        # 状态切换
                        is_completed = c1.checkbox("", value=task["completed"], key=f"check_{task['id']}")
                        if is_completed != task["completed"]:
                            task["completed"] = is_completed
                            save_data(st.session_state.tasks)
                            st.rerun()
                        
                        # 文字显示（如果是完成状态则加删除线，Streamlit原生支持Markdown）
                        display_text = f"~~{task['text']}~~" if task["completed"] else task["text"]
                        color = COLORS[task["priority"]]
                        
                        # 自定义卡片样式
                        c2.markdown(f"""
                        <div style="border-left: 10px solid {color}; padding: 10px; background-color: white; border-radius: 5px; margin-bottom: 5px;">
                            <span style="font-size: 18px; color: #2C3E50;">{display_text}</span><br>
                            <span style="font-size: 12px; color: #ADB5BD;">🏷️ {task['priority']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 删除按钮
                        if c3.button("🗑️", key=f"del_{task['id']}"):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task['id']]
                            save_data(st.session_state.tasks)
                            st.rerun()

# --- 导出功能 ---
st.divider()
if st.button("📝 导出清单至 TXT"):
    if not st.session_state.tasks:
        st.info("没有可导出的数据")
    else:
        # 生成 TXT 内容
        output = "========== 我的待办清单 ==========\n\n"
        for d in sorted(list(set(t["date"] for t in st.session_state.tasks))):
            output += f"【 日期：{d} 】\n" + "-"*30 + "\n"
            day_tasks = [t for t in st.session_state.tasks if t["date"] == d]
            for t in day_tasks:
                status = "✅" if t["completed"] else "🔲"
                output += f"{status} [{t['priority']}] {t['text']}\n"
            output += "\n"
        
        # Web 特有的下载按钮
        st.download_button(
            label="点击下载 TXT 文件",
            data=output,
            file_name=f"TodoList_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )