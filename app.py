import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from pathlib import Path

# 获取数据库路径
def get_db_path():
    # 确保在 Streamlit Cloud 上也能正确存储数据
    if os.environ.get('STREAMLIT_SHARING'):
        return Path.cwd() / "tasks.db"
    return Path(__file__).parent / "tasks.db"

# 页面配置
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库连接
def init_db():
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    people TEXT,
                    status TEXT NOT NULL,
                    importance TEXT NOT NULL,
                    view TEXT NOT NULL,
                    notes TEXT,
                    attachments TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )''')
        conn.commit()
        return conn
    except sqlite3.Error as e:
        st.error(f"数据库连接错误: {str(e)}")
        return None

# 输入验证
def validate_task_input(task, start_date, end_date):
    if not task.strip():
        st.error("任务名称不能为空")
        return False
    if end_date < start_date:
        st.error("结束日期不能早于开始日期")
        return False
    return True

# 从数据库中加载数据
@st.cache_data(ttl=60)  # 缓存1分钟
def load_data():
    try:
        conn = init_db()
        if conn is not None:
            with conn:
                df = pd.read_sql("SELECT * FROM tasks", conn)
            return df
    except sqlite3.Error as e:
        st.error(f"数据加载错误: {str(e)}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# 将数据保存到数据库
def save_data(task, start_date, end_date, people, status, importance, view, notes, attachments):
    if not validate_task_input(task, start_date, end_date):
        return False
    
    try:
        conn = init_db()
        if conn is not None:
            with conn:
                c = conn.cursor()
                c.execute("""
                    INSERT INTO tasks (task, start_date, end_date, people, status, 
                                     importance, view, notes, attachments)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (task, start_date.strftime('%Y-%m-%d'), 
                     end_date.strftime('%Y-%m-%d'), people, status,
                     importance, view, notes, attachments))
            return True
    except sqlite3.Error as e:
        st.error(f"保存失败: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# 更新任务数据
def update_task(task_id, task, start_date, end_date, people, status, importance, view, notes, attachments):
    if not validate_task_input(task, start_date, end_date):
        return False
    
    try:
        conn = init_db()
        if conn is not None:
            with conn:
                c = conn.cursor()
                c.execute("""
                    UPDATE tasks 
                    SET task=?, start_date=?, end_date=?, people=?, 
                        status=?, importance=?, view=?, notes=?, attachments=?
                    WHERE id=?
                """, (task, start_date.strftime('%Y-%m-%d'), 
                     end_date.strftime('%Y-%m-%d'), people, status,
                     importance, view, notes, attachments, task_id))
            return True
    except sqlite3.Error as e:
        st.error(f"更新失败: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# ... existing code for delete_task and complete_task with similar error handling ...

# 显示任务详情
def display_task_details(task):
    with st.expander(f"📋 {task['task']}", expanded=False):
        # ... existing display code ...
        
        # 修改操作按钮部分
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("删除", key=f"delete_{task['id']}"):
                if delete_task(task['id']):
                    st.success("任务已删除！")
                    st.rerun()

        with col2:
            if st.button("修改", key=f"edit_{task['id']}"):
                with st.form(f"edit_form_{task['id']}"):
                    # ... existing form fields ...
                    
                    if submit_button:
                        if update_task(task['id'], new_task, new_start_date, 
                                     new_end_date, new_people, new_status,
                                     new_importance, new_view, new_notes, 
                                     new_attachments):
                            st.success("任务已修改！")
                            st.rerun()

        with col3:
            if st.button("完成", key=f"complete_{task['id']}"):
                if complete_task(task['id']):
                    st.success("任务已完成！")
                    st.rerun()

# 主函数保持不变
def main():
    # ... existing main function code ...

    # 修改新增任务部分
    if st.sidebar.button("添加任务"):
        if save_data(task, start_date, end_date, people, status, 
                    importance, view, notes, attachments):
            st.sidebar.success("任务已添加！")
            st.rerun()

if __name__ == "__main__":
    main()
