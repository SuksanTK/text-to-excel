import streamlit as st

def process_text_file(uploaded_file):

    lines = uploaded_file.read().decode("utf-8").split("\n")
    data_list = []
    capture_data = False

    for line in lines:

        if "CONTAINER" in line and "ITEM" in line:
            capture_data = True
            continue

        if capture_data and re.match(r"^\d+", line.strip()):

            parts = line.split()


            if len(parts) >= 16:
                container_no = parts[0]
                item_no = parts[1]
                cut_width = parts[2]
                fabric_lot = parts[3]
                finish_color = parts[4]
                status = parts[5]
                mach_no = parts[6] if len(parts) > 6 else ""
                bin_row = parts[7]
                finish_date = parts[8]
                finish_lbs = parts[9]
                finish_yds = parts[10]
                dye_lot = parts[11]
                grd = parts[12]
                last_act_date = parts[13]
                wo_no = parts[14]
                print_code = parts[15]
                shipment = " ".join(parts[16:]) 

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