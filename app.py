import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库连接
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    people TEXT,
                    status TEXT,
                    importance TEXT,
                    view TEXT,
                    notes TEXT,
                    attachments TEXT
                )''')
    conn.commit()
    return conn

# 从数据库中加载数据
def load_data():
    conn = init_db()
    df = pd.read_sql("SELECT * FROM tasks", conn)
    conn.close()
    return df

# 将数据保存到数据库
def save_data(task, start_date, end_date, people, status, importance, view, notes, attachments):
    conn = init_db()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task, start_date, end_date, people, status, importance, view, notes, attachments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (task, start_date, end_date, people, status, importance, view, notes, attachments))
    conn.commit()
    conn.close()

# 更新任务数据
def update_task(task_id, task, start_date, end_date, people, status, importance, view, notes, attachments):
    conn = init_db()
    c = conn.cursor()
    c.execute("UPDATE tasks SET task=?, start_date=?, end_date=?, people=?, status=?, importance=?, view=?, notes=?, attachments=? WHERE id=?",
              (task, start_date, end_date, people, status, importance, view, notes, attachments, task_id))
    conn.commit()
    conn.close()

# 从数据库中删除任务
def delete_task(task_id):
    conn = init_db()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    st.experimental_rerun()

# 将任务状态更新为完成
def complete_task(task_id):
    conn = init_db()
    c = conn.cursor()
    c.execute("UPDATE tasks SET status='Complete' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    st.experimental_rerun()

# 显示任务详情
def display_task_details(task):
    with st.expander(f"📋 {task['task']}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**开始时间:**", task['start_date'])
            st.write("**负责人:**", task['people'])
            st.write("**状态:**", task['status'])
        with col2:
            st.write("**结束时间:**", task['end_date'])
            st.write("**优先级:**", task['importance'])
            st.write("**视图:**", task['view'])
        
        if task['notes']:
            st.write("**备注:**", task['notes'])
        
        if task['attachments']:
            st.write("**附件:**", task['attachments'])
        
        # 添加操作按钮（删除、修改、完成）
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("删除", key=f"delete_{task['id']}"):
                delete_task(task['id'])
        with col2:
            if st.button("修改", key=f"edit_{task['id']}"):
                with st.form(f"edit_form_{task['id']}"):
                    new_task = st.text_input("任务名称", value=task['task'])
                    new_start_date = st.date_input("开始时间", value=pd.to_datetime(task['start_date']))
                    new_end_date = st.date_input("结束时间", value=pd.to_datetime(task['end_date']))
                    new_people = st.text_input("负责人", value=task['people'])
                    new_status = st.selectbox("状态", ["Plan", "In Progress", "Stuck", "Complete"], index=["Plan", "In Progress", "Stuck", "Complete"].index(task['status']))
                    new_importance = st.selectbox("优先级", ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"], index=["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"].index(task['importance']))
                    new_view = st.selectbox("视图", ["daily", "weekly", "monthly", "yearly"], index=["daily", "weekly", "monthly", "yearly"].index(task['view']))
                    new_notes = st.text_area("备注", value=task['notes'])
                    new_attachments = st.text_input("附件", value=task['attachments'])
                    submit_button = st.form_submit_button(label="保存修改")
                    
                    if submit_button:
                        update_task(task['id'], new_task, new_start_date, new_end_date, new_people, new_status, new_importance, new_view, new_notes, new_attachments)
                        st.success("任务已修改！")
                        st.experimental_rerun()
        with col3:
            if st.button("完成", key=f"complete_{task['id']}"):
                complete_task(task['id'])

# 页面主逻辑
def main():
    st.title("🎯 Task Manager")
    
    # 侧边栏视图选择
    st.sidebar.title("视图选择")
    view_type = st.sidebar.radio("选择视图类型", ["时间视图", "优先级视图", "已完成任务"])

    # 加载数据
    tasks = load_data()

    # 任务视图展示
    if view_type == "时间视图":
        tab1, tab2, tab3, tab4 = st.tabs(["日视图", "周视图", "月视图", "年视图"])
        
        with tab1:
            st.subheader("日视图 - 优先级分类")
            for priority in ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"]:
                st.write(f"**{priority}**")
                daily_tasks = tasks[(tasks['view'].str.lower() == 'daily') & (tasks['importance'] == priority)]
                for _, task in daily_tasks.iterrows():
                    display_task_details(task)

        with tab2:
            st.subheader("周视图 - 优先级分类")
            for priority in ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"]:
                st.write(f"**{priority}**")
                weekly_tasks = tasks[(tasks['view'].str.lower() == 'weekly') & (tasks['importance'] == priority)]
                for _, task in weekly_tasks.iterrows():
                    display_task_details(task)

        with tab3:
            st.subheader("月视图 - 优先级分类")
            for priority in ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"]:
                st.write(f"**{priority}**")
                monthly_tasks = tasks[(tasks['view'].str.lower() == 'monthly') & (tasks['importance'] == priority)]
                for _, task in monthly_tasks.iterrows():
                    display_task_details(task)

        with tab4:
            st.subheader("年视图 - 优先级分类")
            for priority in ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"]:
                st.write(f"**{priority}**")
                yearly_tasks = tasks[(tasks['view'].str.lower() == 'yearly') & (tasks['importance'] == priority)]
                for _, task in yearly_tasks.iterrows():
                    display_task_details(task)

    elif view_type == "优先级视图":
        priorities = [
            "Urgent and Important",
            "Important and Not Urgent",
            "Not Important but Urgent",
            "Not Important and Not Urgent"
        ]
        
        selected_priority = st.selectbox("选择优先级", priorities)
        priority_tasks = tasks[tasks['importance'] == selected_priority]
        
        for _, task in priority_tasks.iterrows():
            display_task_details(task)

    else:  # 已完成任务
        st.subheader("已完成任务")
        completed_tasks = tasks[tasks['status'] == 'Complete']
        sort_by = st.selectbox("排序方式", ["完成日期", "优先级"])
        
        if sort_by == "完成日期":
            completed_tasks = completed_tasks.sort_values('end_date', ascending=False)
        else:
            completed_tasks = completed_tasks.sort_values('importance')
        
        for _, task in completed_tasks.iterrows():
            display_task_details(task)

    # 新增任务表单
    st.sidebar.title("新增任务")
    task = st.sidebar.text_input("任务名称")
    start_date = st.sidebar.date_input("开始时间")
    end_date = st.sidebar.date_input("结束时间")
    people = st.sidebar.text_input("负责人")
    status = st.sidebar.selectbox("状态", ["Plan", "In Progress", "Stuck", "Complete"])
    importance = st.sidebar.selectbox("优先级", ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"])
    view = st.sidebar.selectbox("视图", ["daily", "weekly", "monthly", "yearly"])
    notes = st.sidebar.text_area("备注")
    attachments = st.sidebar.text_input("附件")

    if st.sidebar.button("添加任务"):
        save_data(task, start_date, end_date, people, status, importance, view, notes, attachments)
        st.sidebar.success("任务已添加！")
        st.experimental_rerun()  # 通过 rerun 刷新页面

# 执行主函数
if __name__ == "__main__":
    main()
