import io
import mimetypes
import uuid
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# CẤU HÌNH HỆ THỐNG ĐỒNG BỘ ĐÁM MÂY SUPABASE
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
# ĐÃ CẬP NHẬT: DANH MỤC CÁC TỈNH THÀNH SÁP NHẬP ĐƠN VỊ HÀNH CHÍNH
# ----------------------------------------------------------------------
DATA_HANH_CHINH = {
    "Tỉnh Kiên Giang": {
        "Huyện Kiên Lương": ["Thị trấn Kiên Lương", "Xã Dương Hòa", "Xã Hòa Điền", "Xã Kiên Bình", "Xã Bình An", "Xã Bình Trị", "Xã Hòn Nghệ"],
        "Thành phố Rạch Giá": ["Phường Vĩnh Thanh Vân", "Phường Vĩnh Thanh", "Phường Vĩnh Lạc", "Phường An Hòa", "Phường An Bình", "Phường Rạch Sỏi"],
        "Thành phố Phú Quốc": ["Phường Dương Đông", "Phường An Thới", "Xã Hàm Ninh", "Xã Dương Tơ", "Xã Gành Dầu"],
        "Thành phố Hà Tiên": ["Phường Đông Hồ", "Phường Bình San", "Phường Pháo Đài", "Phường Tô Châu"]
    },
    "Tỉnh An Giang": {
        "Thành phố Long Xuyên": ["Phường Mỹ Bình", "Phường Mỹ Long", "Phường Mỹ Phước", "Phường Mỹ Quý"],
        "Thành phố Châu Đốc": ["Phường Châu Phú A", "Phường Châu Phú B", "Phường Núi Sam", "Phường Vĩnh Mỹ"],
        "Huyện Chợ Mới": ["Thị trấn Chợ Mới", "Thị trấn Mỹ Luông", "Xã Kiến An", "Xã Kiến Thành"]
    },
    "Thành phố Hồ Chí Minh": {
        "Quận 1": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Cô Giang", "Phường Tân Định", "Phường Đa Kao"],
        "Quận 3": ["Phường Võ Thị Sáu (Sáp nhập)", "Phường 1", "Phường 2", "Phường 4", "Phường 5"],
        "Quận 5": ["Phường 1 (Sáp nhập)", "Phường 2", "Phường 5", "Phường 7", "Phường 8"],
        "Quận 10": ["Phường 1 (Sáp nhập)", "Phường 2", "Phường 4", "Phường 12", "Phường 14"],
        "Thành phố Thủ Đức": ["Phường Thủ Thiêm", "Phường An Khánh", "Phường Hiệp Bình Chánh", "Phường Linh Đông"]
    },
    "Thành phố Hà Nội": {
        "Quận Hoàn Kiếm": ["Phường Đồng Xuân", "Phường Hàng Bạc", "Phường Hàng Bồ", "Phường Tràng Tiền"],
        "Quận Ba Đình": ["Phường Đội Cấn", "Phường Kim Mã", "Phường Quán Thánh", "Phường Trúc Bạch"],
        "Quận Hai Bà Trưng": ["Phường Đồng Nhân (Sáp nhập)", "Phường Bách Khoa", "Phường Bạch Mai"],
        "Quận Đống Đa": ["Phường Khâm Thiên", "Phường Trung Phụng", "Phường Văn Miếu", "Phường Quốc Tử Giám"]
    },
    "Thành phố Cần Thơ": {
        "Quận Ninh Kiều": ["Phường Tân An (Sáp nhập mới)", "Phường Thới Bình", "Phường An Hòa", "Phường An Khánh"]
    },
    "Tỉnh Nghệ An": {
        "Thành phố Vinh": ["Phường Hồng Sơn", "Phường Quang Trung", "Phường Vinh Tân", "Xã Nghi Phú"],
        "Thị xã Cửa Lò": ["Phường Nghi Thu", "Phường Nghi Hương", "Phường Thu Thủy"]
    },
    "Tỉnh Hà Tĩnh": {
        "Thành phố Hà Tĩnh": ["Phường Bắc Hà", "Phường Nam Ngạn", "Phường Nguyễn Du", "Phường Trần Phú"],
        "Huyện Thạch Hà": ["Thị trấn Thạch Hà", "Xã Thạch Đài", "Xã Thạch Long"]
    },
    "Tỉnh Nam Định": {
        "Thành phố Nam Định": ["Phường Vị Hoàng", "Phường Năng Tĩnh", "Phường Trường Thi", "Xã Lộc An"],
        "Huyện Giao Thủy": ["Thị trấn Quất Lâm", "Thị trấn Giao Thủy", "Xã Giao Phong"]
    },
    "Tỉnh Thanh Hóa": {
        "Thành phố Thanh Hóa": ["Phường Ba Đình", "Phường Ngọc Trạo", "Phường Hàm Rồng", "Xã Đông Tân"],
        "Thị xã Sầm Sơn": ["Phường Trường Sơn", "Phường Bắc Sơn", "Phường Trung Sơn"]
    },
    "Tỉnh Quảng Ninh": {
        "Thành phố Hạ Long": ["Phường Hồng Gai", "Phường Bạch Đằng", "Phường Bãi Cháy", "Phường Cao Xanh"],
        "Thành phố Cẩm Phả": ["Phường Cẩm Tây", "Phường Cẩm Đông", "Phường Cẩm Sơn"]
    },
    "Thành phố Hải Phòng": {
        "Quận Hồng Bàng": ["Phường Hoàng Văn Thụ", "Phường Quang Trung", "Phường Minh Khai"],
        "Quận Ngô Quyền": ["Phường Lạch Tray", "Phường Máy Tơ", "Phường Cầu Đất"]
    },
    "Tỉnh Hải Dương": {
        "Thành phố Hải Dương": ["Phường Trần Hưng Đạo", "Phường Quang Trung", "Phường Nguyễn Trãi"]
    },
    "Tỉnh Hưng Yên": {
        "Thành phố Hưng Yên": ["Phường Hiến Nam", "Phường Lam Sơn", "Phường Lê Lợi"]
    },
    "Tỉnh Thái Bình": {
        "Thành phố Thái Bình": ["Phường Lê Hồng Phong", "Phường Kỳ Bá", "Phường Trần Lãm"]
    },
    "Tỉnh Ninh Bình": {
        "Thành phố Ninh Bình": ["Phường Vân Giang", "Phường Thanh Bình", "Phường Bích Đào"]
    },
    "Tỉnh Hà Nam": {
        "Thành phố Phủ Lý": ["Phường Minh Khai", "Phường Hai Bà Trưng", "Phường Lương Khánh Thiện"]
    },
    "Tỉnh Vĩnh Phúc": {
        "Thành phố Vĩnh Yên": ["Phường Liên Bảo", "Phường Tích Sơn", "Phường Đồng Tâm"]
    },
    "Tỉnh Phú Thọ": {
        "Thành phố Việt Trì": ["Phường Tiên Cát", "Phường Gia Cẩm", "Phường Thọ Sơn"]
    },
    "Tỉnh Bắc Ninh": {
        "Thành phố Bắc Ninh": ["Phường Tiền An", "Phường Đại Phúc", "Phường Ninh Xá"]
    },
    "Tỉnh Thái Nguyên": {
        "Thành phố Thái Nguyên": ["Phường Phan Đình Phùng", "Phường Trưng Vương", "Phường Hoàng Văn Thụ"]
    },
    "Tỉnh Quảng Nam": {
        "Thành phố Tam Kỳ": ["Phường An Xuân", "Phường Phước Hòa", "Phường Tân Thạnh"]
    },
    "Thành phố Đà Nẵng": {
        "Quận Hải Châu": ["Phường Phước Ninh", "Phường Nam Dương", "Phường Bình Hiên"],
        "Quận Thanh Khê": ["Phường Thạc Gián", "Phường Chính Gián", "Phường Vĩnh Trung"]
    },
    "Tỉnh Thừa Thiên Huế": {
        "Thành phố Huế": ["Phường Thuận Thành", "Phường Vĩnh Ninh", "Phường Phú Hội"]
    },
    "Tỉnh Bình Định": {
        "Thành phố Quy Nhơn": ["Phường Lê Lợi", "Phường Trần Hưng Đạo", "Phường Nguyễn Văn Cừ"]
    },
    "Tỉnh Khánh Hòa": {
        "Thành phố Nha Trang": ["Phường Tân Lập", "Phường Lộc Thọ", "Phường Phước Tiến"]
    },
    "Tỉnh Lâm Đồng": {
        "Thành phố Đà Lạt": ["Phường 1", "Phường 2", "Phường 3", "Phường 4"]
    },
    "Tỉnh Bình Dương": {
        "Thành phố Thủ Dầu Một": ["Phường Phú Cường", "Phường Hiệp Thành", "Phường Chánh Nghĩa"]
    },
    "Tỉnh Đồng Nai": {
        "Thành phố Biên Hòa": ["Phường Thanh Bình", "Phường Trung Dũng", "Phường Quyết Thắng"]
    },
    "Tỉnh Bà Rịa - Vũng Tàu": {
        "Thành phố Vũng Tàu": ["Phường 1", "Phường 2", "Phường 3", "Phường 4"]
    },
    "Tỉnh Long An": {
        "Thành phố Tân An": ["Phường 1", "Phường 2", "Phường 3", "Phường 4"]
    },
    "Tỉnh Đồng Tháp": {
        "Thành phố Cao Lãnh": ["Phường 1", "Phường 2", "Phường 3", "Phường Hòa Thuận"]
    },
    "Tỉnh Vĩnh Long": {
        "Thành phố Vĩnh Long": ["Phường 1", "Phường 2", "Phường 3", "Phường 4"]
    },
    "Tỉnh Tiền Giang": {
        "Thành phố Mỹ Tho": ["Phường 1", "Phường 2", "Phường 3", "Phường 4"]
    },
    "Tỉnh Bến Tre": {
        "Thành phố Bến Tre": ["Phường An Hội (Sáp nhập)", "Phường Phú Khương", "Phường Phú Tân"]
    }
}

st.title(f"📝 Phiếu Đăng Ký Tuyển Sinh Lớp 1")
st.subheader(f"Trường Tiểu học Dương Hòa — Năm học {NAM_HOC}")
st.info("💡 Hướng dẫn: Phụ huynh vui lòng điền chính xác thông tin dựa theo Giấy khai sinh bản gốc của học sinh.")
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

    # CHỌN QUÊ QUÁN TỰ ĐỘNG THEO DANH MỤC 34 TỈNH THÀNH SÁP NHẬP
    st.markdown("**📍 Quê quán của học sinh (Ghi theo Giấy khai sinh bản gốc)**")
    col_qq1, col_qq2, col_qq3 = st.columns(3)
    with col_qq1:
        qq_tinh_sel = st.selectbox("Chọn Tỉnh/Thành phố", list(DATA_HANH_CHINH.keys()), key="qq_tinh")
    with col_qq2:
        qq_huyen_sel = st.selectbox("Chọn Quận/Huyện", list(DATA_HANH_CHINH[qq_tinh_sel].keys()), key="qq_huyen")
    with col_qq3:
        qq_xa_sel = st.selectbox("Chọn Xã/Phường/Thị trấn", DATA_HANH_CHINH[qq_tinh_sel][qq_huyen_sel], key="qq_xa")
        
    hometown = f"{qq_xa_sel}, {qq_huyen_sel}, {qq_tinh_sel}"

    # ĐỊA CHỈ THƯỜNG TRÚ & CHỖ Ở HIỆN NAY
    st.markdown("#### 🏠 2. Thông tin cư trú của gia đình")
    st.markdown("**📍 Địa chỉ đăng ký thường trú (Theo Sổ hộ khẩu/Thông tin cư trú)**")
    col_tt1, col_tt2, col_tt3 = st.columns(3)
    with col_tt1:
        tt_tinh_sel = st.selectbox("Chọn Tỉnh/Thành phố", list(DATA_HANH_CHINH.keys()), key="tt_tinh")
    with col_tt2:
        tt_huyen_sel = st.selectbox("Chọn Quận/Huyện", list(DATA_HANH_CHINH[tt_tinh_sel].keys()), key="tt_huyen")
    with col_tt3:
        tt_xa_sel = st.selectbox("Chọn Xã/Phường/Thị trấn", DATA_HANH_CHINH[tt_tinh_sel][tt_huyen_sel], key="tt_xa")
        
    tt_chi_tiet = st.text_input("Số nhà, tổ, ấp/khu phố (Thường trú):", placeholder="Ví dụ: Số 12, Ấp Tà Săng")
    permanent_address = f"{tt_chi_tiet}, {tt_xa_sel}, {tt_huyen_sel}, {tt_tinh_sel}".strip(", ")

    st.write("")
    st.markdown("**📍 Địa chỉ chỗ ở hiện nay (Địa chỉ thực tế đang sinh sống)**")
    trung_dia_chi = st.checkbox("Chỗ ở hiện nay giống với địa chỉ thường trú")
    
    if trung_dia_chi:
        current_address = permanent_address
        st.info(f"🏠 Hệ thống đã tự ghi nhận: {current_address}")
    else:
        col_co1, col_co2, col_co3 = st.columns(3)
        with col_co1:
            co_tinh_sel = st.selectbox("Chọn Tỉnh/Thành phố", list(DATA_HANH_CHINH.keys()), key="co_tinh")
        with col_co2:
            co_huyen_sel = st.selectbox("Chọn Quận/Huyện", list(DATA_HANH_CHINH[co_tinh_sel].keys()), key="co_huyen")
        with col_co3:
            co_xa_sel = st.selectbox("Chọn Xã/Phường/Thị trấn", DATA_HANH_CHINH[co_tinh_sel][co_huyen_sel], key="co_xa")
            
        co_chi_tiet = st.text_input("Số nhà, tổ, ấp/khu phố (Chỗ ở hiện nay):", placeholder="Ví dụ: Số 45, Khấu Phố Ba Hòn")
        current_address = f"{co_chi_tiet}, {co_xa_sel}, {co_huyen_sel}, {co_tinh_sel}".strip(", ")

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
                "<div style='border: 1px dashed #bbb; padding: 25px; text-align: center; color: gray; background-color: #f8f9fa; font-size: 13px;'>Vui lòng điền tên cha hoặc mẹ ở mục 3 để xuất hiện chữ ký</div>", 
                unsafe_allow_html=True
            )
            signature_data = None
            
        display_name = parent_name.upper() if parent_name else "..."
        st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 14px; margin-top: 8px; text-transform: uppercase;'>{display_name}</div>", unsafe_allow_html=True)
        
    with col_sig_right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption("(*) Bằng việc nhấn nút gửi, phụ huynh xác nhận chữ ký điện tử trên và cam kết các thông tin khai báo là hoàn toàn chính xác.")

    st.markdown("---")
    submit_button = st.form_submit_button("🚀 GỬI HỒ SƠ ĐĂNG KÝ NGAY")
# ==============================================================================
# PHẦN 1.B: LOGIC KIỂM TRA DỮ LIỆU VÀ ĐỒNG BỘ ĐẨY DỮ LIỆU LÊN SUPABASE
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
                    "hometown": hometown, 
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
                
                Thông tin hồ sơ và chữ ký xác nhận đã được đồng bộ hóa và lưu trữ an toàn trên hệ thống tuyển sinh trực tuyến của nhà trường.
                """)
                
            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi hệ thống: {e}. Phụ huynh vui lòng chụp ảnh màn hình lỗi này và liên hệ giáo viên để được hỗ trợ trực tiếp!")
