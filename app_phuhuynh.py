import io
import mimetypes
import uuid
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# CẤU HÌNH HỆ THỐNG ĐỒNG BỘ
# ==============================================================================
NAM_HOC = "2026 - 2027"
SUPABASE_URL = "https://ywvlqwbhzbpddngxuvlm.supabase.co" 
LINK_PHU_HUYNH = "https://streamlit.app"

try:
    SUPABASE_KEY = st.secrets["supabase_key"]
except Exception:
    SUPABASE_KEY = "sb_secret_yjs4xz1bfe-oxhv0lob0-g_yiwbh9k2"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Hệ thống đang bảo trì, vui lòng quay lại sau!")

st.set_page_config(
    page_title=f"Đăng ký tuyển sinh {NAM_HOC}",
    page_icon="📝",
    layout="centered"
)

st.title(f"📝 Phiếu Đăng Ký Tuyển Sinh Lớp 1")
st.subheader(f"Trường Tiểu học Dương Hòa — Năm học {NAM_HOC}")
st.info("💡 Hướng dẫn: Phụ huynh vui lòng điền chính xác thông tin dựa theo Giấy khai sinh bản gốc của học sinh.")

# ==============================================================================
# PHẦN 1.A: GIAO DIỆN HIỂN THỊ BIỂU MẪU NHẬP LIỆU VÀ CHỮ KÝ TỰ ĐỘNG MỚI
# ==============================================================================
with st.form("form_tuyen_sinh", clear_on_submit=False):
    
    st.markdown("#### 👤 1. Thông tin của học sinh")
    student_name = st.text_input("Họ và tên học sinh (Vui lòng viết hoa có dấu):").strip()
    
    col1, col2 = st.columns(2)
    with col1:
        student_gender = st.selectbox("Giới tính của trẻ:", ["Nam", "Nữ"])
        student_dob = st.text_input("Ngày tháng năm sinh (Ví dụ: 15/08/2020):")
    with col2:
        student_ethnic = st.text_input("Dân tộc (Ví dụ: Kinh, Khơ-me, Hoa):", value="Kinh")
        student_pob = st.text_input("Nơi sinh (Ghi rõ Tỉnh hoặc Thành phố):")

    st.markdown("#### 🏠 2. Thông tin cư trú của gia đình")
    permanent_address = st.text_area("Địa chỉ đăng ký thường trú (Ghi theo Sổ hộ khẩu hoặc Thông tin cư trú):")
    current_address = st.text_area("Địa chỉ chỗ ở hiện nay (Địa chỉ thực tế gia đình đang sinh sống):")

    st.markdown("#### 👨‍👩‍👦 3. Thông tin cha mẹ hoặc Người giám hộ")
    parent_name = st.text_input("Họ tên người khai đơn này (Bố, mẹ hoặc người nuôi dưỡng hợp pháp):").strip()
    
    col3, col4 = st.columns(2)
    with col3:
        father_name = st.text_input("Họ và tên của cha:")
        father_phone = st.text_input("Số điện thoại liên lạc của cha:")
    with col4:
        mother_name = st.text_input("Họ và tên của mẹ:")
        mother_phone = st.text_input("Số điện thoại liên lạc của mẹ:")

    st.markdown("#### 📷 4. Đính kèm ảnh chụp thẻ BHYT")
    st.caption("Yêu cầu: Phụ huynh sử dụng camera điện thoại chụp thật rõ nét mặt trước của thẻ BHYT.")
    uploaded_file = st.file_uploader("Nhấn vào đây để chụp ảnh hoặc tải file ảnh lên:", type=["jpg", "jpeg", "png"])

    st.markdown("#### ✍️ 5. Xác nhận và Ký tên điện tử")
    col_sig_left, col_sig_right = st.columns(2)
    
    with col_sig_left:
        st.markdown(
            """
            <div style='text-align: center; font-weight: bold; font-size: 15px; margin-bottom: 2px;'>
                CHỮ KÝ TỰ ĐỘNG
            </div>
            <div style='text-align: center; font-style: italic; color: gray; font-size: 12px; margin-bottom: 8px;'>
                (Hệ thống ký điện tử)
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Tự động sinh chữ ký nghệ thuật bằng phông viết tay thật Mrs Saint Delafield khi gõ tên ở mục 3
        if parent_name:
            st.markdown(
                f"""
                <style>
                    @import url('https://googleapis.com');
                    .signature-box {{
                        font-family: 'Mrs Saint Delafield', cursive;
                        font-size: 58px; /* Cỡ chữ lớn hiển thị nét thanh mảnh sắc sảo */
                        color: #0b1d3a; /* Màu mực xanh đen giống bút máy thật */
                        text-align: center;
                        padding: 5px 15px;
                        border: 1px dashed #bbb;
                        background-color: #f8f9fa;
                        border-radius: 4px;
                        line-height: 1.1;
                    }}
                </style>
                <div class="signature-box">{parent_name}</div>
                """,
                unsafe_allow_html=True
            )
            signature_data = f"TEXT_SIGNATURE:{parent_name}"
        else:
            st.markdown(
                "<div style='border: 1px dashed #bbb; padding: 25px; text-align: center; color: gray; background-color: #f8f9fa; font-size: 13px;'>"
                "Vui lòng điền họ tên người khai đơn ở mục 3 để xuất hiện chữ ký"
                "</div>", 
                unsafe_allow_html=True
            )
            signature_data = None
            
        display_name = parent_name.upper() if parent_name else "..."
        st.markdown(
            f"<div style='text-align: center; font-weight: bold; font-size: 14px; margin-top: 8px; text-transform: uppercase;'>{display_name}</div>", 
            unsafe_allow_html=True
        )
        
    with col_sig_right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption("(*) Bằng việc nhấn nút gửi, phụ huynh xác nhận chữ ký điện tử trên và cam kết các thông tin khai báo là hoàn toàn chính xác.")

    st.markdown("---")
    submit_button = st.form_submit_button("🚀 GỬI HỒ SƠ ĐĂNG KÝ NGAY")


# ==============================================================================
# PHẦN 1.B: LOGIC KIỂM TRA DỮ LIỆU, XỬ LÝ ĐÁM MÂY VÀ LƯU HỒ SƠ
# ==============================================================================
if submit_button:
    if not student_name:
        st.error("❌ Vui lòng nhập đầy đủ Họ và tên học sinh!")
    elif not student_dob:
        st.error("❌ Vui lòng điền Ngày tháng năm sinh của học sinh!")
    elif not parent_name:
        st.error("❌ Vui lòng điền Họ tên người khai đơn tại Mục 3 để xác nhận chữ ký!")
    elif not uploaded_file:
        st.error("❌ Vui lòng đính kèm ảnh chụp thẻ BHYT của học sinh!")
    else:
        with st.spinner("⏳ Hệ thống đang tải hồ sơ của bạn lên cơ sở dữ liệu đám mây..."):
            try:
                insurance_image_url = ""
                
                # 1. Tải dữ liệu ảnh thẻ BHYT lên Supabase Storage (bhyt_bucket)
                file_extension = mimetypes.guess_extension(uploaded_file.type) or ".png"
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_bytes = uploaded_file.getvalue()
                
                supabase.storage.from_("bhyt_bucket").upload(
                    path=unique_filename,
                    file=file_bytes,
                    file_options={"content-type": uploaded_file.type}
                )
                
                insurance_image_url = supabase.storage.from_("bhyt_bucket").get_public_url(unique_filename)

                # 2. Đồng bộ hóa gói dữ liệu cấu trúc để chèn vào bảng Database
                insert_data = {
                    "student_name": student_name, "student_gender": student_gender, "student_dob": student_dob,
                    "student_ethnic": student_ethnic, "student_pob": student_pob, "permanent_address": permanent_address,
                    "current_address": current_address, "parent_name": parent_name, "father_name": father_name,
                    "father_phone": father_phone, "mother_name": mother_name, "mother_phone": mother_phone,
                    "insurance_image": insurance_image_url, "parent_signature": signature_data
                }

                # Thực thi lệnh chèn dòng thông tin lên bảng ho_so_tuyen_sinh trên Supabase
                supabase.table("ho_so_tuyen_sinh").insert(insert_data).execute()

                st.balloons()
                st.success("🎉 GỬI HỒ SƠ ĐĂNG KÝ THÀNH CÔNG!")
                st.markdown(f"""
                Kính gửi phụ huynh **{parent_name}**, nhà trường đã tiếp nhận thành công dữ liệu đăng ký tuyển sinh của học sinh **{student_name}**. 
                
                Thông tin hồ sơ và chữ ký xác nhận đã được đồng bộ hóa và lưu trữ an toàn trên hệ thống tuyển sinh trực tuyến của nhà trường. Phụ huynh có thể đóng trình duyệt web này được rồi. Xin chân thành cảm ơn phụ huynh!
                """)
                
            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi hệ thống: {e}. Phụ huynh vui lòng chụp ảnh màn hình lỗi này và liên hệ giáo viên để được hỗ trợ trực tiếp!")
