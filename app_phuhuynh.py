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

# ----------------------------------------------------------------------
# DỮ LIỆU ĐỊA DANH MÔ PHỎNG (Cập nhật địa danh mới sau sáp nhập tại Kiên Giang)
# ----------------------------------------------------------------------
DATA_HANH_CHINH = {
    "Tỉnh Kiên Giang": {
        "Huyện Kiên Lương": [
            "Thị trấn Kiên Lương", 
            "Xã Dương Hòa", 
            "Xã Hòa Điền", 
            "Xã Kiên Bình", 
            "Xã Bình An", 
            "Xã Bình Trị", 
            "Xã Hòn Nghệ"
        ],
        "Thành phố Rạch Giá": ["Phường Vĩnh Thanh Vân", "Phường Vĩnh Thanh", "Phường Vĩnh Lạc", "Phường An Hòa"],
        "Thành phố Phú Quốc": ["Phường Dương Đông", "Phường An Thới", "Xã Hàm Ninh", "Xã Dương Tơ"]
    },
    "Tỉnh An Giang": {
        "Thành phố Long Xuyên": ["Phường Mỹ Bình", "Phường Mỹ Long", "Phường Mỹ Phước"],
        "Thành phố Châu Đốc": ["Phường Châu Phú A", "Phường Châu Phú B", "Phường Núi Sam"]
    }
}

st.title(f"📝 Phiếu Đăng Ký Tuyển Sinh Lớp 1")
st.subheader(f"Trường Tiểu học Dương Hòa — Năm học {NAM_HOC}")
st.info("💡 Hướng dẫn: Phụ huynh vui lòng điền chính xác thông tin dựa theo Giấy khai sinh bản gốc của học sinh.")

# ==============================================================================
# PHẦN 1.A: GIAO DIỆN HIỂN THỊ BIỂU MẪU NHẬP LIỆU VÀ CHỮ KÝ TỰ ĐỘNG
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
    st.markdown("**📍 Địa chỉ đăng ký thường trú (Theo Sổ hộ khẩu/Thông tin cư trú)**")
    col_tt1, col_tt2, col_tt3 = st.columns(3)
    with col_tt1:
        tt_tinh = st.selectbox("Chọn Tỉnh/Thành", list(DATA_HANH_CHINH.keys()), key="tt_tinh")
    with col_tt2:
        tt_huyen = st.selectbox("Chọn Quận/Huyện", list(DATA_HANH_CHINH[tt_tinh].keys()), key="tt_huyen")
    with col_tt3:
        tt_xa = st.selectbox("Chọn Xã/Phường", DATA_HANH_CHINH[tt_tinh][tt_huyen], key="tt_xa")
    tt_chi_tiet = st.text_input("Số nhà, tổ, ấp/khu phố (Thường trú):", placeholder="Ví dụ: Số 12, Ấp Tà Săng")
    
    permanent_address = f"{tt_chi_tiet}, {tt_xa}, {tt_huyen}, {tt_tinh}".strip(", ")

    st.write("")
    st.markdown("**📍 Địa chỉ chỗ ở hiện nay (Địa chỉ thực tế đang sinh sống)**")
    
    trung_dia_chi = st.checkbox("Chỗ ở hiện nay giống với địa chỉ thường trú")
    
    if trung_dia_chi:
        current_address = permanent_address
        st.info(f"🏠 Hệ thống đã tự ghi nhận: {current_address}")
    else:
        col_co1, col_co2, col_co3 = st.columns(3)
        with col_co1:
            co_tinh = st.selectbox("Chọn Tỉnh/Thành", list(DATA_HANH_CHINH.keys()), key="co_tinh")
        with col_co2:
            co_huyen = st.selectbox("Chọn Quận/Huyện", list(DATA_HANH_CHINH[co_tinh].keys()), key="co_huyen")
        with col_co3:
            co_xa = st.selectbox("Chọn Xã/Phường", DATA_HANH_CHINH[co_tinh][co_huyen], key="co_xa")
        co_chi_tiet = st.text_input("Số nhà, tổ, ấp/khu phố (Chỗ ở hiện nay):", placeholder="Ví dụ: Số 45, Khấu Phố Ba Hòn")
        
        current_address = f"{co_chi_tiet}, {co_xa}, {co_huyen}, {co_tinh}".strip(", ")

    st.write("")
    st.markdown("#### 👨‍👩‍👦 3. Thông tin cha mẹ hoặc Người giám hộ")
    father_name = st.text_input("Họ và tên của cha:").strip()
    father_phone = st.text_input("Số điện thoại liên lạc của cha:")
    father_job = st.text_input("Nghề nghiệp của cha (Ví dụ: Công nhân, Làm nông, Giáo viên...):")
    
    st.write("---") 
    
    mother_name = st.text_input("Họ và tên của mẹ:").strip()
    mother_phone = st.text_input("Số điện thoại liên lạc của mẹ:")
    mother_job = st.text_input("Nghề nghiệp của mẹ (Ví dụ: Nội trợ, Kinh doanh tự do, Nhân viên...):")

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
        
        parent_name = father_name if father_name else mother_name
        
        if parent_name:
            st.markdown(
                f"""
                <style>
                    @import url('https://googleapis.com');
                    .signature-box {{
                        font-family: 'Mrs Saint Delafield', cursive;
                        font-size: 58px;
                        color: #0b1d3a;
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
                "Vui lòng điền tên cha hoặc mẹ ở mục 3 để xuất hiện chữ ký"
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
    elif not father_name and not mother_name:
        st.error("❌ Vui lòng điền Họ tên của cha hoặc mẹ ở Mục 3 để xác nhận chữ ký!")
    elif not tt_chi_tiet:
        st.error("❌ Vui lòng điền số nhà, tổ hoặc số ấp cụ thể cho địa chỉ thường trú!")
    elif not uploaded_file:
        st.error("❌ Vui lòng đính kèm ảnh chụp thẻ BHYT của học sinh!")
    else:
        with st.spinner("⏳ Hệ thống đang tải hồ sơ của bạn lên cơ sở dữ liệu đám mây..."):
            try:
                insurance_image_url = ""
                
                # 1. Tải dữ liệu ảnh thẻ BHYT lên Supabase Storage
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
                    "student_name": student_name, "student_gender": student_gender, "student_dob": student_dob,
                    "student_ethnic": student_ethnic, "student_pob": student_pob, 
                    "permanent_address": permanent_address, 
                    "current_address": current_address, 
                    "parent_name": parent_name,
                    "father_name": father_name, "father_phone": father_phone, "father_job": father_job,
                    "mother_name": mother_name, "mother_phone": mother_phone, "mother_job": mother_job,
                    "insurance_image": insurance_image_url, "parent_signature": signature_data
                }

                # Gửi dữ liệu lên bảng ho_so_tuyen_sinh trên Supabase
                supabase.table("ho_so_tuyen_sinh").insert(insert_data).execute()

                st.balloons()
                st.success("🎉 GỬI HỒ SƠ ĐĂNG KÝ THÀNH CÔNG!")
                st.markdown(f"""
                Kính gửi phụ huynh **{parent_name}**, nhà trường đã tiếp nhận thành công dữ liệu đăng ký tuyển sinh của học sinh **{student_name}**. 
                
                Thông tin hồ sơ và chữ ký xác nhận đã được đồng bộ hóa và lưu trữ an toàn trên hệ thống tuyển sinh trực tuyến của nhà trường. Phụ huynh có thể đóng trình duyệt web này được rồi. Xin chân thành cảm ơn phụ huynh!
                """)
                
            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi hệ thống: {e}. Phụ huynh vui lòng chụp ảnh màn hình lỗi này và liên hệ giáo viên để được hỗ trợ trực tiếp!")
