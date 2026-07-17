import io
import pandas as pd
import qrcode
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# CẤU HÌNH BIẾN NĂM HỌC HỆ THỐNG ĐỒNG BỘ
# ==============================================================================
NAM_HOC = "2026 - 2027"
SUPABASE_URL = "https://ywvlqwbhzbpddngxuvlm.supabase.co" 

try:
    SUPABASE_KEY = st.secrets["supabase_key"]
except Exception:
    SUPABASE_KEY = "sb_secret_yjs4xz1bfe-oxhv0lob0-g_yiwbh9k2"

try:
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

# ==============================================================================
# TỰ ĐỘNG SINH MÃ QR ĐỂ IN ẤN HOẶC GỬI ZALO
# ==============================================================================
st.markdown("### 📱 Mã QR chính thức dành cho phụ huynh nộp đơn từ xa")
# LƯU Ý: Sau khi đẩy file 'form_phu_huynh.py' lên Streamlit Cloud, hãy copy link web nhận được dán thay thế vào dòng dưới này:
LINK_PHU_HUYNH = "https://streamlit.io"  

col_qr1, col_qr2 = st.columns()

with col_qr1:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(LINK_PHU_HUYNH)
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

# ==============================================================================
# HỆ THỐNG XEM VÀ XUẤT DỮ LIỆU EXCEL BẢO MẬT
# ==============================================================================
password = st.text_input(
    "Vui lòng nhập mật khẩu quản trị để xem dữ liệu học sinh:",
    type="password",
)

if password == "123456":  
    st.subheader(f"📋 Danh sách hồ sơ phiếu điền trực tuyến từ phụ huynh ({NAM_HOC})")

    with st.spinner("Đang kết nối đám mây lấy dữ liệu mới nhất..."):
        try:
            response = (
                supabase.table("ho_so_tuyen_sinh")
                .select("*")
                .order("created_at", descending=True)
                .execute()
            )
            rows = response.data
        except Exception as e:
            st.error(f"Lỗi truy cập dữ liệu bảng: Vui lòng kiểm tra lại cấu hình Supabase! Chi tiết: {e}")
            rows = []

    if rows:
        df = pd.DataFrame(rows)

        column_mapping = {
            "created_at": "Thời gian đăng ký",
            "parent_name": "Người khai đơn",
            "current_address": "Chỗ ở hiện nay",
            "student_name": "Tên học sinh",
            "student_gender": "Giới tính",
            "student_ethnic": "Dân tộc",
            "student_dob": "Ngày sinh",
            "student_pob": "Nơi sinh",
            "permanent_address": "Thường trú",
            "father_name": "Họ tên cha",
            "father_phone": "SĐT Cha",
            "mother_name": "Họ tên mẹ",
            "mother_phone": "SĐT Mẹ",
            "insurance_image": "Đường dẫn ảnh thẻ BHYT",
        }

        available_cols = [col for col in column_mapping.keys() if col in df.columns]
        df_display = df[available_cols].rename(columns=column_mapping)

        st.dataframe(df_display, use_container_width=True)

        # Xem nhanh ảnh thẻ BHYT trực quan trên giao diện quản trị
        if "Đường dẫn ảnh thẻ BHYT" in df_display.columns:
            st.markdown("### 📷 Tra cứu ảnh thẻ BHYT học sinh")
            student_list = df_display["Tên học sinh"].unique() if "Tên học sinh" in df_display.columns else []
            if len(student_list) > 0:
                selected_student = st.selectbox("Chọn học sinh cần xem ảnh thẻ BHYT:", student_list)
                img_url = df_display[df_display["Tên học sinh"] == selected_student]["Đường dẫn ảnh thẻ BHYT"].values
                if len(img_url) > 0 and pd.notna(img_url)[0] and str(img_url[0]).startswith("http"):
                    st.image(img_url[0], caption=f"Ảnh thẻ BHYT của học sinh {selected_student}", width=400)
                else:
                    st.warning("Học sinh này chưa có ảnh thẻ BHYT hoặc đường dẫn ảnh không hợp lệ.")

        # Tạo file báo cáo Excel tự động giãn rộng cột dữ liệu
        buffer = io.BytesIO()
        sheet_name_excel = f"TuyenSinhLop1_{NAM_HOC.replace(' ', '')}"
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_display.to_excel(writer, index=False, sheet_name=sheet_name_excel[:31])
            worksheet = writer.sheets[sheet_name_excel[:31]]
            for col in worksheet.columns:
                max_len = 0
                col_letter = col.column_letter
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
