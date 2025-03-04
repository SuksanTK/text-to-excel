import streamlit as st
import pandas as pd
import re
import os
import tempfile

def detect_format_wh(lines):
    for line in lines:
        if "CONTAINER" in line and "ITEM" in line:
            return 1
        elif "Item" in line and "Cyl" in line:
            return 2
    return None

def process_text_file_wh_format1(lines):
    data_list = []
    capture_data = False

    for line in lines:
        if "CONTAINER" in line and "ITEM" in line:
            capture_data = True
            continue
        
        if capture_data and re.match(r"^\d+", line.strip()):
            container_no = line[0:18].strip()
            item_no = line[19:25].strip()
            cut_width = line[26:34].strip()
            fabric_lot = line[35:42].strip()
            finish_color = line[43:49].strip()
            status = line[50:56].strip()
            mach_no = line[57:62].strip() or ""
            bin_row = line[63:70].strip()
            finish_date = line[71:82].strip()
            finish_lbs = line[83:93].strip()
            finish_yds = line[91:104].strip()
            dye_lot = line[105:115].strip()
            grd = line[116:118].strip()
            last_act_date = line[119:128].strip()
            wo_no_print = line[129:136].strip()
            shipment = line[144:].strip()

            data_list.append([container_no, item_no, cut_width, fabric_lot, finish_color, status, mach_no, bin_row, finish_date,
                              finish_lbs, finish_yds, dye_lot, grd, last_act_date, wo_no_print, shipment])

    columns = ["CONTAINER NO", "ITEM NO", "CUT WIDTH", "FABRIC LOT", "FINISH COLOR", "STATUS",
               "MACH NO", "BIN ROW", "FINISH DATE", "FINISH LBS", "FINISH YDS", "DYE LOT", "GRD", 
               "LAST ACT DATE", "WO #PRINT", "SHIPMENT"]
    
    return pd.DataFrame(data_list, columns=columns)

def process_text_file_wh_format2(lines):
    data_list = []
    capture_data = False

    for line in lines:
        if "Item" in line and "Cyl" in line:
            capture_data = True
            continue

        if capture_data and re.match(r"^\w+\s+\d+\s+\w+\s+\w+\s+\d+\s+\d+\.\d+", line.strip()):
            parts = re.split(r"\s+", line.strip(), maxsplit=11)

            if len(parts) >= 11:
                item_no = parts[0]
                cyl = parts[1]
                lot = parts[2]
                color = parts[3]
                grade = parts[4]
                cut_width = parts[5]
                container = parts[6]
                net_weight = parts[7]
                tare_weight = parts[8]
                gross_weight = parts[9]
                yds = parts[10]
                pallet_id = parts[11] if len(parts) > 11 else ""

                data_list.append([item_no, cyl, lot, color, grade, cut_width, container, net_weight, tare_weight, gross_weight,
                                  yds, pallet_id])

    columns = ["ITEM", "CYL", "LOT", "COL", "G", "CUT WIDTH", "CONTAINER", "NET WEIGHT", "TARE WEIGHT",
               "GROSS WEIGHT", "YDS", "PALLET ID"]
    
    return pd.DataFrame(data_list, columns=columns)

import pandas as pd
import re

def process_cutting_files(file_paths):
    import re
    import pandas as pd

    all_data = []

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                lines = content.splitlines()

            data = []
            
            # Extract basic document-level information
            assort_order_match = re.search(r'ASSORTMENT ORDER:\s*(\d+)', content) or re.search(r'ASSORTMENT ORDER\s*(\d+)', content)
            assort_order = assort_order_match.group(1)[:6] if assort_order_match else "N/A"
            
            cut_lot_match = re.search(r'CUT W/O #:\s*(\d+)', content) or re.search(r'CUT W/O #\s*(\d+)', content)
            cut_lot = cut_lot_match.group(1)[:6] if cut_lot_match else "N/A"
            
            style_match = re.search(r'STYLE:\s*([^\s]+\s+[^\s]+\s+[^\s]+\s+[^\s]+)', content) or re.search(r'STYLE\s*([^\s]+\s+[^\s]+\s+[^\s]+\s+[^\s]+)', content)
            style_code = style_match.group(1)[:6].strip() if style_match else "N/A"
            
            sizes_match = re.search(r'SIZES\s*:\s*(\d+)', content) or re.search(r'SIZES\s*(\d+)', content)
            sizes_code = sizes_match.group(1)[:2] if sizes_match else "N/A"
            
            color_match = re.search(r'COLOR:\s*(\S+)', content)
            color_code = color_match.group(1) if color_match else "N/A"
            
            req_doz_match = re.search(r'REQ DOZ:\s*(\d+)', content)
            req_doz = int(req_doz_match.group(1)) if req_doz_match else None
            
            # เก็บ proto ทั้งหมดไว้ในตัวแปร full_proto
            proto_full_match = re.search(r'Proto:\s*(.+?)(?=\s{2,}|\n)', content)
            full_proto = proto_full_match.group(1).strip() if proto_full_match else "N/A"
            
            # ดึงเฉพาะตัวเลข 5 หลักจาก proto สำหรับใช้ในการแมทช์
            proto_digits_match = re.search(r'(\d{5})', full_proto)
            proto_five_digit = proto_digits_match.group(1) if proto_digits_match else None

            # First pass: Find parts and their data
            i = 0
            current_fabric = None
            current_width = None
            current_item = None
            current_col = None
            current_trim_info = None
            
            # Store all valid part names we find
            valid_part_names = {}
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Look for fabric info line (starting with "01")
                fabric_match = re.match(r'^\s*01\s+(\d+\.?\d*)\s+(\w+)\s+(\w+)', line)
                if fabric_match:
                    current_width = fabric_match.group(1)
                    current_item = fabric_match.group(2)
                    current_col = fabric_match.group(3)
                    
                    # Get trim info from next line
                    if i+1 < len(lines):
                        trim_line = lines[i+1].strip()
                        current_trim_info = trim_line
                        
                        # Extract trim width and lbs/doz
                        trim_width = "N/A"
                        lbs_doz = "N/A"
                        
                        trim_width_match = re.search(r'Trim Width:\s*(.+?)(?=\s{2,}|$|\s+Lbs/Doz)', trim_line)
                        if trim_width_match:
                            trim_width = trim_width_match.group(1).strip()
                        
                        lbs_doz_match = re.search(r'Lbs/Doz:\s*(.+?)(?=\s{2,}|$)', trim_line)
                        if lbs_doz_match:
                            lbs_doz = lbs_doz_match.group(1).strip()
                
                # Look for part name in various formats (with proto check)
                # Format 1: Pattern ID + size + part name
                part_match1 = re.match(r'^([A-Za-z0-9]+\w\d+\w?)\s+(\d+)\s+(.+)$', line)
                # Format 2: Just size + part name
                part_match2 = re.match(r'^\s*(\d+)\s+(.+)$', line)
                
                if part_match1 and not line.startswith('01'):
                    pattern_id = part_match1.group(1)
                    size = part_match1.group(2)
                    part_name = part_match1.group(3).strip()
                    
                    # Check if this is a valid part name
                    if is_valid_part_name(part_name):
                        # ถ้ามี proto 5 หลัก ให้ตรวจสอบว่า pattern ID มี proto 5 หลักนั้นหรือไม่
                        is_proto_matched = False
                        if proto_five_digit:
                            pattern_proto_match = re.search(r'(\d{5})', pattern_id)
                            if pattern_proto_match and pattern_proto_match.group(1) == proto_five_digit:
                                valid_part_names[pattern_id] = part_name
                                is_proto_matched = True
                        
                        # Look for yardage in next line
                        if i+1 < len(lines) and current_item is not None:
                            yardage_line = lines[i+1].strip()
                            yard_match = re.match(r'^\s*(\d+)', yardage_line)
                            std_yds = yard_match.group(1) if yard_match else "N/A"
                            
                            part_entry = {
                                "Assortment Order": assort_order,
                                "Lot": cut_lot,
                                "Style": style_code,
                                "Size": sizes_code,
                                "Color Code": color_code,
                                "Plan Qty": req_doz,
                                "Proto": full_proto,  # เก็บค่า proto ทั้งหมด
                                "Proto Matched": is_proto_matched,  # เก็บข้อมูลว่าตรงกับ proto 5 หลักหรือไม่
                                "Item Fabric": current_item,
                                "Fabric Color": current_col,
                                "Width": current_width,
                                "Part Name": part_name,
                                "STD.(Yds.)": std_yds,
                                "Trim Width": trim_width,
                                "Lbs/Doz": lbs_doz,
                                "Pattern ID": pattern_id
                            }
                            data.append(part_entry)
                
                elif part_match2 and "TOTALS" not in line and not line.startswith('01') and current_item is not None:
                    size = part_match2.group(1)
                    part_name = part_match2.group(2).strip()
                    
                    # Check if this is a valid part name
                    if is_valid_part_name(part_name):
                        # สำหรับรูปแบบที่ 2 เราไม่มี pattern ID ให้ตรวจสอบกับ proto
                        # เราจะเก็บข้อมูลเหล่านี้ไว้ แต่จะให้ความสำคัญกับข้อมูลที่ตรงกับ proto ในภายหลัง
                        
                        # Look for yardage in next line
                        if i+1 < len(lines):
                            yardage_line = lines[i+1].strip()
                            yard_match = re.match(r'^\s*(\d+)', yardage_line)
                            std_yds = yard_match.group(1) if yard_match else "N/A"
                            
                            part_entry = {
                                "Assortment Order": assort_order,
                                "Lot": cut_lot,
                                "Style": style_code,
                                "Size": sizes_code,
                                "Color Code": color_code,
                                "Plan Qty": req_doz,
                                "Proto": full_proto,  # เก็บค่า proto ทั้งหมด
                                "Proto Matched": False,  # ไม่มี pattern ID จึงไม่สามารถตรวจสอบได้
                                "Item Fabric": current_item,
                                "Fabric Color": current_col,
                                "Width": current_width,
                                "Part Name": part_name,
                                "STD.(Yds.)": std_yds,
                                "Trim Width": trim_width,
                                "Lbs/Doz": lbs_doz,
                                "Pattern ID": "N/A"  # ไม่มี pattern ID ในรูปแบบนี้
                            }
                            data.append(part_entry)
                
                i += 1
            
            # สร้าง DataFrame และกรองข้อมูล
            if data:
                df = pd.DataFrame(data)
                
                # ถ้ามีข้อมูลที่ตรงกับ proto 5 หลัก ให้เก็บเฉพาะข้อมูลเหล่านั้น
                if proto_five_digit and df['Proto Matched'].any():
                    df = df[df['Proto Matched'] == True]
                
                # ลบคอลัมภ์ชั่วคราว
                df = df.drop('Proto Matched', axis=1)
                
                all_data.append(df)
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    # รวม DataFrame ทั้งหมด
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df
    else:
        # Return empty DataFrame with expected columns
        columns = ["Assortment Order", "Lot", "Style", "Size", "Color Code", "Plan Qty", "Proto", 
                  "Item Fabric", "Fabric Color", "Width", "Part Name", "STD.(Yds.)", 
                  "Trim Width", "Lbs/Doz","Pattern ID"]
        return pd.DataFrame(columns=columns)

def is_valid_part_name(part_name):
    """
    ตรวจสอบว่าชื่อ Part name ถูกต้องหรือไม่
    จะคืนค่า True เฉพาะกรณีที่เป็นชื่อ Part จริงๆ เท่านั้น
    """
    # ข้อความว่างเปล่าหรือมีแต่ช่องว่างไม่ใช่ชื่อ Part ที่ถูกต้อง
    if not part_name or part_name.isspace():
        return False
    
    # กรองชื่อที่เป็นเส้นใต้ (underscores) เช่น "____ ____ ____"
    if '_' in part_name:
        return False
    
    # กรองกรณีที่มีแต่ตัวเลขและสัญลักษณ์พิเศษ
    if re.match(r'^[\d\s\.\-\/]+$', part_name):
        return False
    
    # กรณีที่เป็นตัวเลขตามด้วยตัวเลข เช่น "321 33.5 321 33.5"
    number_pattern = r'^\d+(\.\d+)?\s+\d+(\.\d+)?(\s+\d+(\.\d+)?\s+\d+(\.\d+)?)*$'
    if re.match(number_pattern, part_name):
        return False
    
    # กรณีที่เป็นเฉพาะตัวเลขเช่น "584.4 482 584.4"
    if all(part.replace('.', '').isdigit() or part.isspace() for part in re.split(r'[\s]+', part_name)):
        return False
    
    # ต้องมีตัวอักษรอย่างน้อย 2 ตัวขึ้นไปจึงจะถือว่าเป็นชื่อ Part ที่ถูกต้อง
    alpha_count = sum(c.isalpha() for c in part_name)
    if alpha_count < 2:
        return False
    
    # ผ่านการตรวจสอบทั้งหมด ถือว่าเป็นชื่อ Part ที่ถูกต้อง
    return True

        
st.title(" Text File to Excel Converter")

tab1, tab2 = st.tabs([" Warehouse", "✂️ Cutting"])

with tab1:
    st.header("Upload Warehouse Files")
    upload_file_wh = st.file_uploader("📂 Upload a file WH (.txt)", type=["txt"], key="wh")

    if upload_file_wh is not None:
        lines = upload_file_wh.read().decode("utf-8").split("\n")
        format_type = detect_format_wh(lines)

        if format_type == 1:
            df_wh = process_text_file_wh_format1(lines)
            format_label = "Inventory on hand"
        elif format_type == 2:
            df_wh = process_text_file_wh_format2(lines)
            format_label = "Transfer Packing list"
        else:
            st.error("⚠️ No supported formats found for this file!") 
            df_wh = None

        if df_wh is not None:
            st.subheader(f"📊 Converted Data ({format_label})")
            st.dataframe(df_wh)

            excel_file_wh = "WH_output.xlsx"
            df_wh.to_excel(excel_file_wh, index=False)

            with open(excel_file_wh, "rb") as file:
                st.download_button("📥 Download WH (Excel)", file, file_name="WH_output.xlsx")

with tab2:
    st.header("Upload Cutting Files")
    uploaded_files = st.file_uploader("📂 Upload Cutting files (.txt)", type=["txt"], accept_multiple_files=True)

    if uploaded_files:
        all_dfs = []
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            cutting_file_paths = [tmp_file_path]
            df_cutting = process_cutting_files(cutting_file_paths)
            all_dfs.append(df_cutting)

            os.remove(tmp_file_path)

        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            st.subheader("📊 Converted Data")
            st.dataframe(final_df)

            excel_file_cutting = "Cutting_output.xlsx"
            final_df.to_excel(excel_file_cutting, index=False)

            with open(excel_file_cutting, "rb") as file:
                st.download_button("📥 Download Cutting (Excel)", file, file_name="Cutting_output.xlsx")