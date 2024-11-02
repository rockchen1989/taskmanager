import streamlit as st

# 页面配置 (必须是第一个 Streamlit 调用)
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 在页面配置之后再导入其他模块和进行调试
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 调试输出：检查是否成功加载 sheet_key 和 gcp_service_account
try:
    sheet_key = st.secrets["sheet_key"]
    gcp_service_account = st.secrets["gcp_service_account"]
    st.write("成功加载 sheet_key 和 gcp_service_account")
except KeyError as e:
    st.error(f"密钥加载错误: 缺少 {e}，请检查 Streamlit Cloud 的 Secrets 配置")

# 读取 sheet_key 和 gcp_service_account
try:
    sheet_key = st.secrets["sheet_key"]
    gcp_service_account = st.secrets["gcp_service_account"]
    st.write("成功加载 sheet_key 和 gcp_service_account")
except KeyError as e:
    st.error(f"密钥加载错误: 缺少 {e}，请检查 Streamlit Cloud 的 Secrets 配置")

# 设置页面样式
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 连接 Google Sheets
@st.cache_resource
def connect_to_sheets():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        gcp_service_account, scope)
    client = gspread.authorize(credentials)
    
    # 测试连接
    try:
        sheet = client.open_by_key(sheet_key).sheet1
        st.success("成功连接到 Google Sheets!")
        return sheet
    except Exception as e:
        st.error(f"连接 Google Sheets 时出错: {e}")
        return None

# 获取数据
@st.cache_data(ttl=5)
def load_data():
    sheet = connect_to_sheets()
    if sheet:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    else:
        st.error("未能加载 Google Sheets 数据")
        return pd.DataFrame()

def display_task_details(task):
    with st.expander(f"📋 {task['Tasks']}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**开始时间:**", task['Start Date'])
            st.write("**负责人:**", task['People'])
            st.write("**状态:**", task['Status'])
        with col2:
            st.write("**结束时间:**", task['End Date'])
            st.write("**优先级:**", task['Importance'])
            st.write("**视图:**", task['View'])
        
        if task['Notes']:
            st.write("**备注:**", task['Notes'])
        
        if task['Attachments']:
            st.write("**附件:**", task['Attachments'])

def main():
    st.title("🎯 Task Manager")
    
    # 侧边栏
    st.sidebar.title("视图选择")
    view_type = st.sidebar.radio(
        "选择视图类型",
        ["时间视图", "优先级视图", "已完成任务"]
    )
    
    # 加载数据
    try:
        df = load_data()
        
        # 过滤未完成任务
        active_tasks = df[df['Status'] != 'Complete']
        completed_tasks = df[df['Status'] == 'Complete']
        
        if view_type == "时间视图":
            tab1, tab2, tab3, tab4 = st.tabs(["日视图", "周视图", "月视图", "年视图"])
            
            with tab1:
                daily_tasks = active_tasks[active_tasks['View'].str.lower() == 'daily']
                for _, task in daily_tasks.iterrows():
                    display_task_details(task)
            
            with tab2:
                weekly_tasks = active_tasks[active_tasks['View'].str.lower() == 'weekly']
                for _, task in weekly_tasks.iterrows():
                    display_task_details(task)
            
            with tab3:
                monthly_tasks = active_tasks[active_tasks['View'].str.lower() == 'monthly']
                for _, task in monthly_tasks.iterrows():
                    display_task_details(task)
            
            with tab4:
                yearly_tasks = active_tasks[active_tasks['View'].str.lower() == 'yearly']
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
            priority_tasks = active_tasks[active_tasks['Importance'] == selected_priority]
            
            for _, task in priority_tasks.iterrows():
                display_task_details(task)
        
        else:  # 已完成任务
            st.subheader("已完成任务")
            sort_by = st.selectbox("排序方式", ["完成日期", "优先级"])
            
            if sort_by == "完成日期":
                completed_tasks = completed_tasks.sort_values('End Date', ascending=False)
            else:
                completed_tasks = completed_tasks.sort_values('Importance')
            
            for _, task in completed_tasks.iterrows():
                display_task_details(task)
    
    except Exception as e:
        st.error(f"加载数据时出错: {str(e)}")
        st.info("请确保已正确配置 Google Sheets 访问权限")

if __name__ == "__main__":
    main()
