import streamlit as st
import pandas as pd
import re

def process_text_file(uploaded_file):
    lines = uploaded_file.read().decode("utf-8").split("\n")
    data_list = []
    capture_data = False

    for line in lines:
        if "CONTAINER" in line and "ITEM" in line:
            capture_data = True
            continue

        if capture_data and re.match(r"^\d+", line.strip()):
            split_data = re.split(r"\s{2,}", line.strip())

            if len(split_data) >= 17: 
                data_list.append(split_data)

    columns = [
        "CONTAINER NO.", "ITEM NO.", "CUT WIDTH", "FABRIC LOT", "FINISH COLOR",
        "STATUS", "MACH NO.", "BIN/ROW", "FINISH DATE", "FINISH LBS",
        "FINISH YDS", "DYE LOT", "GRD", "LAST ACT DATE", "WO #", "PRINT CODE", "SHIPMENT"
    ]

    df = pd.DataFrame(data_list, columns=columns)
    return df

st.title("📄 Text File to Excel Converter")
uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ .txt", type=["txt"])

if uploaded_file is not None:
    df = process_text_file(uploaded_file)
    
    st.write("📊 ข้อมูลที่ถูกแปลง:")
    st.dataframe(df)

    excel_file = "output.xlsx"
    df.to_excel(excel_file, index=False)
    
    with open(excel_file, "rb") as file:
        st.download_button("📥 ดาวน์โหลดไฟล์ Excel", file, file_name="output.xlsx")
