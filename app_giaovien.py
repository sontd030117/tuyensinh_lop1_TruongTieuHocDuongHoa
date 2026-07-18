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

# Nhúng phông chữ viết tay Google Font vào toàn bộ trang quản trị để hiển thị chữ ký tự động
st.markdown(
    """
    <style>
        @import url('https://googleapis.com');
        .digital-sig-text {
            font-family: 'Dancing Script', cursive;
            font-size: 36px;
            color: #1a237e;
            text-align: center;
            padding: 10px;
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
# PHẦN 2.2: LOGIC TẢI DỮ LIỆU ĐÁM MÂY, HIỂN THỊ BIỂU ĐỒ THỐNG KÊ VÀ XUẤT EXCEL
# ==============================================================================
if password == "123456":  
    st.subheader(f"📋 Danh sách hồ sơ phiếu điền trực tuyến từ phụ huynh ({NAM_HOC})")

    with st.spinner("Đang kết nối đám mây lấy dữ liệu mới nhất..."):
        try:
            # Tải toàn bộ dữ liệu hồ sơ tuyển sinh xếp mới nhất lên đầu
            response = supabase.table("ho_so_tuyen_sinh").select("*").order("created_at", desc=True).execute()
            rows = response.data
        except Exception as e:
            st.error(f"Lỗi truy cập dữ liệu bảng: Vui lòng kiểm tra lại cấu hình Supabase! Chi tiết: {e}")
            rows = []

    if rows:
        df = pd.DataFrame(rows)

        # KHỐI BIỂU ĐỒ THỐNG KÊ SỐ LƯỢNG HỒ SƠ THEO NGÀY
        st.markdown("### 📈 Biểu đồ tiến độ phụ huynh nộp đơn")
        if "created_at" in df.columns:
            try:
                df_chart = df.copy()
                df_chart["Ngay_Nop"] = pd.to_datetime(df_chart["created_at"]).dt.date
                df_grouped = df_chart.groupby("Ngay_Nop").size().reset_index(name="Số lượng hồ sơ")
                df_grouped = df_grouped.sort_values(by="Ngay_Nop").set_index("Ngay_Nop")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="Tổng số hồ sơ tiếp nhận", value=f"{len(df)} trẻ")
                with col_m2:
                    st.metric(label="Số ngày có phụ huynh khai đơn", value=f"{len(df_grouped)} ngày")
                
                st.line_chart(df_grouped, use_container_width=True)
            except Exception as chart_err:
                st.warning(f"Tạm thời chưa thể dựng biểu đồ tiến độ: {chart_err}")

        st.write("---")
        st.markdown("### 📝 Chi tiết danh sách hồ sơ tuyển sinh")

        column_mapping = {
            "created_at": "Thời gian đăng ký", "parent_name": "Người khai đơn", "current_address": "Chỗ ở hiện nay",
            "student_name": "Tên học sinh", "student_gender": "Giới tính", "student_ethnic": "Dân tộc",
            "student_dob": "Ngày sinh", "student_pob": "Nơi sinh", "permanent_address": "Thường trú",
            "father_name": "Họ tên cha", "father_phone": "SĐT Cha", "mother_name": "Họ tên mẹ",
            "mother_phone": "SĐT Mẹ", "insurance_image": "Đường dẫn ảnh thẻ BHYT", "parent_signature": "Dữ liệu chữ ký mạng"
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
                img_url = str(img_data_arr).strip() if len(img_data_arr) > 0 else ""
                
                if img_url and img_url.startswith("http"):
                    st.image(img_url, caption=f"Ảnh thẻ BHYT: {selected_student}", width=350)
                else:
                    st.warning("Học sinh này chưa có ảnh thẻ BHYT hoặc đường dẫn ảnh không hợp lệ.")
                    
            with col_view2:
                st.markdown("**Vùng ký xác nhận của phụ huynh:**")
                if "Dữ liệu chữ ký mạng" in df_display.columns:
                    sig_data_arr = df_display[df_display["Tên học sinh"] == selected_student]["Dữ liệu chữ ký mạng"].values
                    p_name_arr = df_display[df_display["Tên học sinh"] == selected_student]["Người khai đơn"].values
                    
                    # Giải mã giá trị mảng thô
                    actual_sig = str(sig_data_arr).strip() if len(sig_data_arr) > 0 else ""
                    actual_name = str(p_name_arr).strip() if len(p_name_arr) > 0 else ""
                    
                    if actual_sig and actual_sig != "None" and actual_sig != "nan":
                        st.markdown("<div style='border: 1px dashed #ccc; padding: 15px; width: 380px; text-align: center; background-color: #fff;'>", unsafe_allow_html=True)
                        # ĐÃ SỬA THEO YÊU CẦU: Đổi tiêu đề chữ ký từ Khách Hàng Yêu Cầu thành Chữ Ký Tự Động
                        st.markdown("<div style='font-weight: bold; font-size: 14px;'>CHỮ KÝ TỰ ĐỘNG</div>", unsafe_allow_html=True)
                        st.markdown("<div style='font-style: italic; color: gray; font-size: 11px;'>(Hệ thống ký điện tử)</div>", unsafe_allow_html=True)
                        
                        if actual_sig.startswith("TEXT_SIGNATURE:"):
                            clean_text = actual_sig.replace("TEXT_SIGNATURE:", "")
                            st.markdown(f"<div class='digital-sig-text'>{clean_text}</div>", unsafe_allow_html=True)
                        elif actual_sig.startswith("data:image"):
                            st.image(actual_sig, width=250)
                        else:
                            st.markdown(f"<div class='digital-sig-text'>{actual_sig}</div>", unsafe_allow_html=True)
                            
                        st.markdown(f"<b style='text-transform: uppercase; font-size: 14px;'>{actual_name}</b>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Học sinh này chưa thực hiện ký xác nhận.")
                else:
                    st.error("Hệ thống đám mây hiện thiếu cấu trúc lưu trữ trường `parent_signature`.")

        # Xử lý tối ưu giãn rộng cột Excel không lỗi
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
