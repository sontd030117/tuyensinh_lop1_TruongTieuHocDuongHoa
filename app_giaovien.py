import io
import pandas as pd
import qrcode
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# PHẦN 2.1: CẤU HÌNH HỆ THỐNG, SINH MÃ QR VÀ XÁC THỰC BẢO MẬT
# ==============================================================================
NAM_HOC = "2026 - 2027"
SUPABASE_URL = "https://ywvlqwbhzbpddngxuvlm.supabase.co" 

try:
    # Lấy key bảo mật ngầm khi chạy trực tuyến trên Streamlit Cloud
    SUPABASE_KEY = st.secrets["supabase_key"]
except Exception:
    # Key dùng tạm dưới máy tính local
    SUPABASE_KEY = "sb_secret_yjs4xz1bfe-oxhv0lob0-g_yiwbh9k2"

try:
    # Khởi tạo kết nối đám mây chính thức
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Lỗi kết nối hệ thống đám mây Supabase: {e}")

# Cấu hình giao diện quản trị rộng toàn màn hình máy tính
st.set_page_config(
    page_title=f"Hệ thống quản lý tuyển sinh {NAM_HOC}",
    page_icon="📊",
    layout="wide"
)
st.title(f"📊 Hệ thống quản trị viên - Trường Tiểu học Dương Hòa (Năm học {NAM_HOC})")

# Nhúng phông chữ viết tay giả lập nét ký thật Mrs Saint Delafield
st.markdown(
    """
    <style>
        @import url('https://googleapis.com');
        .digital-sig-text {
            font-family: 'Mrs Saint Delafield', cursive;
            font-size: 55px;
            color: #0b1d3a;
            text-align: center;
            padding: 5px;
            line-height: 1.1;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("### 📱 Mã QR chính thức dành cho phụ huynh nộp đơn từ xa")
LINK_PHU_HUYNH = "https://tuyensinhlop1truongtieuhocduonghoa-nbuiedwqmgfwauvzlsfofq.streamlit.app"  

col_qr1, col_qr2 = st.columns(2)

with col_qr1:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    # Ép mã QR mã hóa dạng bytes để giữ nguyên chữ thường của link, tránh lỗi Not Found
    qr.add_data(LINK_PHU_HUYNH.encode('utf-8'))
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img_qr.save(img_buffer, format="PNG")
    st.image(
        img_buffer.getvalue(),
        caption="Click chuột phải chọn Lưu ảnh để in ấn",
        width=200,
    )

with col_qr2:
    st.write("")
    st.success(f"**🔗 Đường dẫn trực tuyến của phiếu điền:** `{LINK_PHU_HUYNH}`")
    st.info(f"""
    **💡 Hướng dẫn vận hành nhanh dành cho Giáo viên:**
    1. **Tải mã QR:** Bạn nhấp chuột phải vào ảnh mã QR bên cạnh -> Chọn **Lưu hình ảnh thành...** để đem đi in ấn hoặc gửi Zalo cho phụ huynh.
    2. **Phụ huynh quét mã:** Phụ huynh chỉ cần dùng điện thoại quét mã này để mở phiếu điền và chụp ảnh thẻ BHYT từ xa.
    3. **Lấy dữ liệu:** Giáo viên nhập mật khẩu hệ thống ở ô phía dưới để kiểm tra bảng dữ liệu thời gian thực và tải file Excel năm học {NAM_HOC}.
    """)

st.write("---")

password = st.text_input(
    "Vui lòng nhập mật khẩu quản trị để xem dữ liệu học sinh:",
    type="password",
)
# ==============================================================================
# PHẦN 2.2: LOGIC TẢI DỮ LIỆU ĐÁM MÂY REAL-TIME, SỬA MÚI GIỜ VN VÀ XUẤT EXCEL
# ==============================================================================
if password == "123456":  
    st.subheader(f"📋 Danh sách hồ sơ phiếu điền trực tuyến từ phụ huynh ({NAM_HOC})")

    # Loại bỏ hoàn toàn bộ nhớ đệm Cache để tải dữ liệu Real-time ngay lập tức khi vào trang
    with st.spinner("⏳ Đang kết nối trực tiếp đám mây lấy dữ liệu mới nhất..."):
        try:
            # Truy vấn toàn bộ dữ liệu, sắp xếp hồ sơ mới nộp lên đầu bảng
            response = supabase.table("ho_so_tuyen_sinh").select("*").order("created_at", desc=True).execute()
            rows = response.data
        except Exception as e:
            st.error(f"Lỗi truy cập dữ liệu bảng: Vui lòng kiểm tra lại cấu hình Supabase! Chi tiết: {e}")
            rows = []

    if rows:
        df = pd.DataFrame(rows)

        # KHỐI BIỂU ĐỒ THỐNG KÊ SỐ LƯỢNG HỒ SƠ THEO NGÀY (SỬA MÚI GIỜ VIỆT NAM CHUẨN XÁC)
        st.markdown("### 📈 Biểu đồ tiến độ phụ huynh nộp đơn")
        if "created_at" in df.columns:
            try:
                df_chart = df.copy()
                # Ép kiểu thời gian sang múi giờ Việt Nam (Asia/Ho_Chi_Minh) để không bị lệch ngày
                df_chart["Time_VN"] = pd.to_datetime(df_chart["created_at"]).dt.tz_convert("Asia/Ho_Chi_Minh")
                df_chart["Ngay_Nop"] = df_chart["Time_VN"].dt.date
                
                # Gom nhóm đếm số lượng hồ sơ nộp phát sinh theo từng ngày
                df_grouped = df_chart.groupby("Ngay_Nop").size().reset_index(name="Số lượng hồ sơ")
                df_grouped = df_grouped.sort_values(by="Ngay_Nop").set_index("Ngay_Nop")
                
                # Hiển thị số liệu tổng quan nhanh dạng số (Metrics)
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="Tổng số hồ sơ tiếp nhận", value=f"{len(df)} trẻ")
                with col_m2:
                    st.metric(label="Số ngày có phụ huynh khai đơn", value=f"{len(df_grouped)} ngày")
                
                # Vẽ biểu đồ đường
                st.line_chart(df_grouped, use_container_width=True)
            except Exception as chart_err:
                # Cơ chế dự phòng nếu bản ghi hệ thống gặp lỗi chuỗi định dạng thời gian
                try:
                    df_chart = df.copy()
                    df_chart["Ngay_Nop"] = pd.to_datetime(df_chart["created_at"]).dt.date
                    df_grouped = df_chart.groupby("Ngay_Nop").size().reset_index(name="Số lượng hồ sơ")
                    df_grouped = df_grouped.sort_values(by="Ngay_Nop").set_index("Ngay_Nop")
                    st.line_chart(df_grouped, use_container_width=True)
                except:
                    st.warning("Biểu đồ đang cập nhật chuỗi thời gian...")

        st.write("---")
        st.markdown("### 📝 Chi tiết danh sách hồ sơ tuyển sinh")

        # Cấu hình danh mục cột hiển thị (Đồng bộ đầy đủ cả 2 cột nghề nghiệp mới)
        column_mapping = {
            "created_at": "Thời gian đăng ký", "parent_name": "Người khai đơn", "current_address": "Chỗ ở hiện nay",
            "student_name": "Tên học sinh", "student_gender": "Giới tính", "student_ethnic": "Dân tộc",
            "student_dob": "Ngày sinh", "student_pob": "Nơi sinh", "permanent_address": "Thường trú",
            "father_name": "Họ tên cha", "father_phone": "SĐT Cha", "father_job": "Nghề nghiệp cha",
            "mother_name": "Họ tên mẹ", "mother_phone": "SĐT Mẹ", "mother_job": "Nghề nghiệp mẹ",
            "insurance_image": "Đường dẫn ảnh thẻ BHYT", "parent_signature": "Dữ liệu chữ ký mạng"
        }

        available_cols = [col for col in column_mapping.keys() if col in df.columns]
        df_display = df[available_cols].rename(columns=column_mapping)

        # Ẩn cột chứa chuỗi mã hóa chữ ký thô loằng ngoằng để bảng chính hiển thị gọn gàng
        cols_to_show = [c for c in df_display.columns if c != "Dữ liệu chữ ký mạng"]
        st.dataframe(df_display[cols_to_show], use_container_width=True)

        st.markdown("### 📷 Tra cứu Minh chứng hồ sơ Học sinh")
        student_list = df_display["Tên học sinh"].unique() if "Tên học sinh" in df_display.columns else []
        
        if len(student_list) > 0:
            selected_student = st.selectbox("Chọn học sinh cần xem ảnh minh chứng & chữ ký:", student_list)
            col_view1, col_view2 = st.columns(2)
            
            with col_view1:
                st.markdown("**Ảnh thẻ BHYT:**")
                img_data_arr = df_display[df_display["Tên học sinh"] == selected_student]["Đường dẫn ảnh thẻ BHYT"].values
                
                # Giải mã bóc tách dữ liệu mảng ảnh dôi dư dấu ngoặc vuông
                img_url = ""
                if len(img_data_arr) > 0 and pd.notna(img_data_arr):
                    img_url = str(img_data_arr).replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
                
                if img_url and img_url.startswith("http"):
                    st.image(img_url, caption=f"Ảnh thẻ BHYT: {selected_student}", width=350)
                else:
                    st.warning("Học sinh này chưa có ảnh thẻ BHYT hoặc đường dẫn ảnh không hợp lệ.")
                    
            with col_view2:
                st.markdown("**Vùng ký xác nhận của phụ huynh:**")
                if "Dữ liệu chữ ký mạng" in df_display.columns:
                    sig_data_arr = df_display[df_display["Tên học sinh"] == selected_student]["Dữ liệu chữ ký mạng"].values
                    p_name_arr = df_display[df_display["Tên học sinh"] == selected_student]["Người khai đơn"].values
                    
                    # Giải mã bóc tách loại bỏ hoàn toàn dấu mảng thừa dấu ngoặc vuông ['...']
                    raw_sig = str(sig_data_arr).strip() if len(sig_data_arr) > 0 else ""
                    actual_name = str(p_name_arr).strip() if len(p_name_arr) > 0 else ""
                    
                    clean_sig = raw_sig.replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
                    actual_name = actual_name.replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
                    
                    if clean_sig and clean_sig != "None" and clean_sig != "nan":
                        st.markdown("<div style='border: 1px dashed #ccc; padding: 15px; width: 380px; text-align: center; background-color: #fff;'>", unsafe_allow_html=True)
                        st.markdown("<div style='font-weight: bold; font-size: 14px;'>CHỮ KÝ TỰ ĐỘNG</div>", unsafe_allow_html=True)
                        st.markdown("<div style='font-style: italic; color: gray; font-size: 11px;'>(Hệ thống ký điện tử)</div>", unsafe_allow_html=True)
                        
                        if clean_sig.startswith("TEXT_SIGNATURE:"):
                            display_text = clean_sig.replace("TEXT_SIGNATURE:", "")
                            st.markdown(f"<div class='digital-sig-text'>{display_text}</div>", unsafe_allow_html=True)
                        elif clean_sig.startswith("data:image"):
                            st.image(clean_sig, width=250)
                        else:
                            st.markdown(f"<div class='digital-sig-text'>{clean_sig}</div>", unsafe_allow_html=True)
                            
                        st.markdown(f"<b style='text-transform: uppercase; font-size: 14px;'>{actual_name}</b>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Học sinh này chưa thực hiện ký xác nhận.")
                else:
                    st.error("Hệ thống đám mây hiện thiếu cấu trúc lưu trữ trường `parent_signature`.")

        # Xử lý tối ưu giãn rộng cột Excel không lỗi bằng hàm get_column_letter chuẩn
        from openpyxl.utils import get_column_letter
        buffer = io.BytesIO()
        sheet_name_excel = f"TuyenSinhLop1_{NAM_HOC.replace(' ', '')}"
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_excel = df_display[cols_to_show]
            df_excel.to_excel(writer, index=False, sheet_name=sheet_name_excel[:31])
            worksheet = writer.sheets[sheet_name_excel[:31]]
            
            for col_idx, col in enumerate(worksheet.columns, start=1):
                max_len = 0
                col_letter = get_column_letter(col_idx)
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

        st.markdown("### 💾 Tải xuống dữ liệu báo cáo")
        st.download_button(
            label=f"📥 TẢI FILE EXCEL PHIẾU ĐIỀN {NAM_HOC} (XLSX)",
            data=buffer.getvalue(),
            file_name=f"Thong_tin_phieu_dien_tu_phu_huynh_{NAM_HOC.replace(' ', '')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.info("Hệ thống đám mây hiện đang trống. Chưa có phụ huynh nào nộp đơn.")
elif password:
    st.error("Mật khẩu truy cập hệ thống không chính xác!")
else:
    st.info("🔒 Vui lòng nhập mật khẩu quản trị phía trên để truy cập và quản lý dữ liệu học sinh.")
