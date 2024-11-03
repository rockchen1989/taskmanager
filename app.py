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
    try:
        conn = sqlite3.connect("tasks.db", check_same_thread=False)
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"数据库连接错误: {str(e)}")
        return None

# 从数据库中加载数据
@st.cache_data(ttl=60)  # 缓存1分钟
def load_data():
    try:
        conn = init_db()
        if conn is not None:
            query = """
            SELECT 
                id, task, 
                start_date, end_date,
                people, status, 
                importance, view,
                notes, attachments,
                created_at
            FROM tasks
            ORDER BY created_at DESC
            """
            df = pd.read_sql(query, conn)
            return df
    except Exception as e:
        st.error(f"加载数据错误: {str(e)}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# 将数据保存到数据库
def save_data(task, start_date, end_date, people, status, importance, view, notes, attachments):
    try:
        conn = init_db()
        if conn is not None:
            c = conn.cursor()
            c.execute("""
                INSERT INTO tasks (task, start_date, end_date, people, status, importance, view, notes, attachments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                 people, status, importance, view, notes, attachments))
            conn.commit()
            conn.close()
            # 清除缓存
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"保存数据错误: {str(e)}")
        return False

# 更新任务数据
def update_task(task_id, task, start_date, end_date, people, status, importance, view, notes, attachments):
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
                     end_date.strftime('%Y-%m-%d'), people, 
                     status, importance, view, notes, attachments, task_id))
            return True
    except Exception as e:
        st.error(f"更新失败: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# 从数据库中删除任务
def delete_task(task_id):
    try:
        conn = init_db()
        if conn is not None:
            with conn:
                c = conn.cursor()
                c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            return True
    except Exception as e:
        st.error(f"删除失败: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# 将任务状态更新为完成
def complete_task(task_id):
    try:
        conn = init_db()
        if conn is not None:
            with conn:
                c = conn.cursor()
                c.execute("UPDATE tasks SET status='Complete' WHERE id=?", (task_id,))
            return True
    except Exception as e:
        st.error(f"更新状态失败: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

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
        
        # 操作按钮
        col1, col2, col3 = st.columns(3)
        
        # 删除按钮
        with col1:
            if st.button("删除", key=f"delete_{task['id']}"):
                if delete_task(task['id']):
                    st.cache_data.clear()
                    st.success("任务已删除！")
                    st.rerun()

        # 修改按钮
        with col2:
            edit_key = f"edit_{task['id']}"
            if st.button("修改", key=edit_key):
                st.session_state[f"show_edit_form_{task['id']}"] = True

            # 显示修改表单
            if st.session_state.get(f"show_edit_form_{task['id']}", False):
                with st.form(key=f"edit_form_{task['id']}"):
                    new_task = st.text_input("任务名称", value=task['task'])
                    new_start_date = st.date_input("开始时间", value=pd.to_datetime(task['start_date']).date())
                    new_end_date = st.date_input("结束时间", value=pd.to_datetime(task['end_date']).date())
                    new_people = st.text_input("负责人", value=task['people'])
                    new_status = st.selectbox("状态", 
                                            ["Plan", "In Progress", "Stuck", "Complete"],
                                            index=["Plan", "In Progress", "Stuck", "Complete"].index(task['status']))
                    new_importance = st.selectbox("优先级",
                                                ["Urgent and Important", "Important and Not Urgent",
                                                 "Not Important but Urgent", "Not Important and Not Urgent"],
                                                index=["Urgent and Important", "Important and Not Urgent",
                                                      "Not Important but Urgent", "Not Important and Not Urgent"].index(task['importance']))
                    new_view = st.selectbox("视图",
                                          ["daily", "weekly", "monthly", "yearly"],
                                          index=["daily", "weekly", "monthly", "yearly"].index(task['view']))
                    new_notes = st.text_area("备注", value=task['notes'] if task['notes'] else "")
                    new_attachments = st.text_input("附件", value=task['attachments'] if task['attachments'] else "")
                    
                    if st.form_submit_button("保存修改"):
                        if update_task(task['id'], new_task, new_start_date, new_end_date,
                                     new_people, new_status, new_importance, new_view,
                                     new_notes, new_attachments):
                            st.cache_data.clear()
                            st.success("修改成功！")
                            # 关闭修改表单
                            st.session_state[f"show_edit_form_{task['id']}"] = False
                            st.rerun()

        # 完成按钮
        with col3:
            if st.button("完成", key=f"complete_{task['id']}"):
                if complete_task(task['id']):
                    st.cache_data.clear()
                    st.success("任务已完成！")
                    st.rerun()

# 页面主逻辑
def main():
    # 确保 session_state 被初始化
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        
    st.title("🎯 Task Manager")
    
    # 添加导出按钮
    col1, col2 = st.columns([1, 5])
    with col1:
        tasks_df = load_data()
        if not tasks_df.empty:
            csv = tasks_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 导出任务",
                data=csv,
                file_name=f"tasks_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
    
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
                daily_tasks = tasks[(tasks['view'].str.lower() == 'daily') & (tasks['importance'] == priority) & (tasks['status'] != 'Complete')]
                for _, task in daily_tasks.iterrows():
                    display_task_details(task)

        with tab2:
            st.subheader("周视图 - 优先级分类")
            for priority in ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"]:
                st.write(f"**{priority}**")
                weekly_tasks = tasks[(tasks['view'].str.lower() == 'weekly') & (tasks['importance'] == priority) & (tasks['status'] != 'Complete')]
                for _, task in weekly_tasks.iterrows():
                    display_task_details(task)

        with tab3:
            st.subheader("月视图 - 优先级分类")
            for priority in ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"]:
                st.write(f"**{priority}**")
                monthly_tasks = tasks[(tasks['view'].str.lower() == 'monthly') & (tasks['importance'] == priority) & (tasks['status'] != 'Complete')]
                for _, task in monthly_tasks.iterrows():
                    display_task_details(task)

        with tab4:
            st.subheader("年视图 - 优���级分类")
            for priority in ["Urgent and Important", "Important and Not Urgent", "Not Important but Urgent", "Not Important and Not Urgent"]:
                st.write(f"**{priority}**")
                yearly_tasks = tasks[(tasks['view'].str.lower() == 'yearly') & (tasks['importance'] == priority) & (tasks['status'] != 'Complete')]
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
        priority_tasks = tasks[(tasks['importance'] == selected_priority) & (tasks['status'] != 'Complete')]
        
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
    with st.sidebar.form(key="add_task_form"):
        st.title("新增任务")
        task = st.text_input("任务名称")
        start_date = st.date_input("开始时间")
        end_date = st.date_input("结束时间")
        people = st.text_input("负责人")
        status = st.selectbox("状态", ["Plan", "In Progress", "Stuck", "Complete"])
        importance = st.selectbox("优先级", ["Urgent and Important", "Important and Not Urgent",
                                         "Not Important but Urgent", "Not Important and Not Urgent"])
        view = st.selectbox("视图", ["daily", "weekly", "monthly", "yearly"])
        notes = st.text_area("备注")
        attachments = st.text_input("附件")

        if st.form_submit_button("添加任务"):
            if task.strip():  # 确保任务名不为空
                if save_data(task, start_date, end_date, people, status,
                           importance, view, notes, attachments):
                    st.success("任务已添加！")
                    st.rerun()
            else:
                st.error("任务名称不能为空！")

# 执行主函数
if __name__ == "__main__":
    main()
