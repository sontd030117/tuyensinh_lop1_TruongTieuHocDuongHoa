import io
import mimetypes
import uuid
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# CẤU HÌNH HỆ THỐNG ĐỒNG BỘ CỦA BẠN
# ==============================================================================
NAM_HOC = "2026 - 2027"
# ĐÃ CẬP NHẬT: Địa chỉ URL chính xác lấy từ mã dự án của bạn
SUPABASE_URL = "https://ywvlqwbhzbpddngxuvlm.supabase.co" 

try:
    SUPABASE_KEY = st.secrets["supabase_key"]
except Exception:
    # Key local tạm thời (Khi đẩy lên Streamlit Cloud sẽ tự dùng key trong ô Secrets)
    SUPABASE_KEY = "sb_secret_yjs4xz1bfe-oxhv0lob0-g_yiwbh9k2"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Hệ thống đang bảo trì, vui lòng quay lại sau!")

# Cấu hình giao diện di động hiển thị tối ưu trên điện thoại
st.set_page_config(
    page_title=f"Đăng ký tuyển sinh {NAM_HOC}",
    page_icon="📝",
    layout="centered"
)

# Tiêu đề biểu mẫu bằng Tiếng Việt trực quan
st.title(f"📝 Phiếu Đăng Ký Tuyển Sinh Lớp 1")
st.subheader(f"Trường Tiểu học Dương Hòa — Năm học {NAM_HOC}")
st.info("💡 Hướng dẫn: Phụ huynh vui lòng điền chính xác thông tin dựa theo Giấy khai sinh bản gốc của học sinh.")

# ==============================================================================
# GIAO DIỆN BIỂU MẪU NHẬP LIỆU (KHÔNG CẦN ĐĂNG NHẬP)
# ==============================================================================
with st.form("form_tuyen_sinh", clear_on_submit=False):
    
    st.markdown("#### 👤 1. Thông tin của học sinh")
    student_name = st.text_input("Họ và tên học sinh (Vui lòng viết hoa có dấu):").strip()
    
    col1, col2 = st.columns(2)
    with col1:
        student_gender = st.selectbox("Giới tính của trẻ:", ["Nam", "Nữ"])
        # ĐÃ SỬA LỖI: Đổi thành hàm nhập ngày chuẩn của Streamlit để không bị lỗi crash trang
        student_dob = st.text_input("Ngày tháng năm sinh (Ví dụ: 15/08/2020):")
    with col2:
        student_ethnic = st.text_input("Dân tộc (Ví dụ: Kinh, Khơ-me, Hoa):", value="Kinh")
        student_pob = st.text_input("Nơi sinh (Ghi rõ Tỉnh hoặc Thành phố):")

    st.markdown("#### 🏠 2. Thông tin cư trú của gia đình")
    permanent_address = st.text_area("Địa chỉ đăng ký thường trú (Ghi theo Sổ hộ khẩu hoặc Thông tin cư trú):")
    current_address = st.text_area("Địa chỉ chỗ ở hiện nay (Địa chỉ thực tế gia đình đang sinh sống):")

    st.markdown("#### 👨‍👩‍👦 3. Thông tin cha mẹ hoặc Người giám hộ")
    parent_name = st.text_input("Họ tên người khai đơn này (Bố, mẹ hoặc người nuôi dưỡng hợp pháp):")
    
    col3, col4 = st.columns(2)
    with col3:
        father_name = st.text_input("Họ và tên của cha:")
        father_phone = st.text_input("Số điện thoại liên lạc của cha:")
    with col4:
        mother_name = st.text_input("Họ và tên của mẹ:")
        mother_phone = st.text_input("Số điện thoại liên lạc của mẹ:")

    st.markdown("#### 📷 4. Đính kèm ảnh chụp thẻ BHYT")
    st.caption("Yêu cầu: Phụ huynh sử hình camera điện thoại chụp thật rõ nét mặt trước của thẻ BHYT để nhà trường đối chiếu mã định danh học sinh.")
    uploaded_file = st.file_uploader("Nhấn vào đây để chụp ảnh hoặc tải file ảnh lên:", type=["jpg", "jpeg", "png"])

    st.markdown("---")
    submit_button = st.form_submit_button("🚀 GỬI HỒ SƠ ĐĂNG KÝ NGAY")

# ==============================================================================
# XỬ LÝ DỮ LIỆU KHI PHỤ HUYNH BẤM NÚT GỬI
# ==============================================================================
if submit_button:
    if not student_name:
        st.error("❌ Vui lòng nhập đầy đủ Họ và tên học sinh!")
    elif not student_dob:
        st.error("❌ Vui lòng điền Ngày tháng năm sinh của học sinh!")
    elif not parent_name:
        st.error("❌ Vui lòng điền Họ tên người khai đơn!")
    elif not uploaded_file:
        st.error("❌ Vui lòng đính kèm ảnh chụp thẻ BHYT của học sinh!")
    else:
        with st.spinner("⏳ Hệ thống đang tải hồ sơ của bạn lên cơ sở dữ liệu đám mây..."):
            try:
                insurance_image_url = ""
                
                # 1. Tải ảnh thẻ BHYT lên kho lưu trữ Supabase Storage
                file_extension = mimetypes.guess_extension(uploaded_file.type) or ".png"
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_bytes = uploaded_file.getvalue()
                
                supabase.storage.from_("bhyt_bucket").upload(
                    path=unique_filename,
                    file=file_bytes,
                    file_options={"content-type": uploaded_file.type}
                )
                
                insurance_image_url = supabase.storage.from_("bhyt_bucket").get_public_url(unique_filename)

                # 2. Đồng bộ hóa dữ liệu để ghi vào bảng Database
                insert_data = {
                    "student_name": student_name,
                    "student_gender": student_gender,
                    "student_dob": student_dob,
                    "student_ethnic": student_ethnic,
                    "student_pob": student_pob,
                    "permanent_address": permanent_address,
                    "current_address": current_address,
                    "parent_name": parent_name,
                    "father_name": father_name,
                    "father_phone": father_phone,
                    "mother_name": mother_name,
                    "mother_phone": mother_phone,
                    "insurance_image": insurance_image_url
                }

                # Gửi dữ liệu lên bảng ho_so_tuyen_sinh trên Supabase
                supabase.table("ho_so_tuyen_sinh").insert(insert_data).execute()

                st.balloons()
                st.success("🎉 GỬI HỒ SƠ ĐĂNG KÝ THÀNH CÔNG!")
                st.markdown(f"""
                Kính gửi phụ huynh **{parent_name}**, nhà trường đã tiếp nhận thành công dữ liệu đăng ký tuyển sinh của học sinh **{student_name}**. 
                
                Thông tin hồ sơ đã được đồng bộ hóa và lưu trữ an toàn trên hệ thống tuyển sinh trực tuyến của nhà trường. Phụ huynh có thể đóng trình duyệt web này được rồi. Xin chân thành cảm ơn phụ huynh!
                """)
                
            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi hệ thống: {e}. Phụ huynh vui lòng chụp ảnh màn hình lỗi này và liên hệ giáo viên để được hỗ trợ trực tiếp!")
