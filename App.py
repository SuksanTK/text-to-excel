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
            container_no = line[0:20].strip()
            item_no = line[21:27].strip()
            cut_width = line[28:33].strip()
            fabric_lot = line[34:41].strip()
            finish_color = line[42:48].strip()
            status = line[49:56].strip()
            mach_no = line[57:64].strip() or ""
            bin_row = line[65:75].strip()
            finish_date = line[76:86].strip()
            finish_lbs = line[87:97].strip()
            finish_yds = line[98:104].strip()
            dye_lot = line[105:108].strip()
            grd = line[109:114].strip()
            last_act_date = line[115:120].strip()
            wo_no = line[121:124].strip()
            print_code = line[125:132].strip()
            shipment = line[133:].strip()

            data_list.append([
                container_no, item_no, cut_width, fabric_lot, finish_color, status,
                mach_no, bin_row, finish_date, finish_lbs, finish_yds,
                dye_lot, grd, last_act_date, wo_no, print_code, shipment
            ])

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