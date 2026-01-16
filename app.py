import streamlit as st
import pandas as pd

st.set_page_config(page_title="QECM 精準解析器", layout="wide")
st.title("🤖 QECM Log 軸圈數精準解析器 (新專案版)")

uploaded_file = st.file_uploader("請上傳 QECM Log 檔案", type=["log", "txt"])

if uploaded_file:
    # 讀取 Log 檔案
    content = uploaded_file.read().decode("utf-8")
    lines = content.split('\n')

    # 存放每個軸最先找到的數據
    first_records = {}
    target_key = "2100,00,1814"

    for line in lines:
        # 只找包含寫入指令與目標代碼的行
        if "QsiCoEApi_WriteSlaveSdoObject16" in line and target_key in line:
            try:
                # 抓取括號內容，如: (1,2100,00,1814,00987376)
                params_str = line.split('(')[1].split(')')[0]
                params = params_str.split(',')
                
                if len(params) >= 5:
                    axis_id = params[0].strip() # 第一個是軸號
                    hex_val = params[4].strip() # 第五個是 HEX 值
                    
                    # 只要 J1~J6 且還沒紀錄過的
                    if axis_id in ["1", "2", "3", "4", "5", "6"] and axis_id not in first_records:
                        # 確保 HEX 是 8 位數，避免誤抓
                        if len(hex_val) == 8:
                            first_records[axis_id] = hex_val
            except:
                continue

    if first_records:
        st.success("✅ 數據提取成功！")
        
        display_data = []
        for i in range(1, 7):
            ax = str(i)
            h = first_records.get(ax, "N/A")
            if h != "N/A":
                d = int(h, 16)
                display_data.append({"軸號": f"J{ax}", "十六進制 (HEX)": h, "十進制圈數 (DEC)": f"{d:,}"})
            else:
                display_data.append({"軸號": f"J{ax}", "十六進制 (HEX)": "未找到", "十進制圈數 (DEC)": "-"})
        
        df = pd.DataFrame(display_data)
        st.table(df)
        st.download_button("📥 下載報表 (CSV)", df.to_csv(index=False).encode('utf-8-sig'), "QECM_Report.csv")
    else:
        st.error("❌ 找不到符合格式的數據，請確認上傳的 Log 是否正確。")
