import pandas as pd
import re 

def detect_format_wh(line):
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
        
        if capture_data and re.match(r"^\d+",line.strip()):
            container_no = line[0:18].strip()
            item_no = line [19:25].strip()
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

            data_list.append([
                container_no,item_no,cut_width,fabric_lot,finish_color,status,mach_no,bin_row,finish_date,
                finish_lbs,finish_yds,dye_lot,grd,last_act_date,wo_no_print,shipment
            ])

            columns = ["CONTEAIER NO", "ITEM NO", "CUT WIDTH", "FABRIC LOT", "FABRIC LOT", "FINISH COLOR", "STATUS",
                       "MACH NO", "BIN ROW", "FINISH DATE", "FINISH LBS", "FINISH YDS", "DYE LOT", "GRD", "LAST ACT DATE",
                       "WO #PRINT", "SHIPMENT"]
            
            return pd.DataFrame(data_list, columns=columns)
        
def process_text_file_wh_fomat2(lines):
    data_list = []
    capture_data = False

    for line in lines:
        if "Item" in line and "Cyl" in line:
            capture_data = True
            continue

        if capture_data and re.match(r"^\w+\s+\d+\s+\w+\s+\w+\s+\d+\s+\d+\.\d+",line.strip()):
            parts = re.split(r"\s+",line.strip(),maxsplit=11)

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

                data_list.append([item_no,cyl,lot,color,grade,cut_width,container,net_weight,tare_weight,gross_weight
                                  , yds,pallet_id])

                columns =[
                    "ITEM", "CYL", "LOT", "COL", "G", "CUT WIDTH", "CONTAINER", "NET WEIGHT", "TARE WEIGTH",
                    "GROSS WEIGHT", "YDS", "PALLET ID"]
                
                return pd.DataFrame(data_list,columns=columns)
st.title()
            



    