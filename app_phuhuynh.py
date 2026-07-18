import io
import mimetypes
import uuid
import base64
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client

# ==============================================================================
# CẤU HÌNH HỆ THỐNG ĐỒNG BỘ ĐÁM MÂY SUPABASE VÀ KHỞI TẠO GIAO DIỆN
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

st.title("📝 Phiếu Đăng Ký Tuyển Sinh Lớp 1")
st.subheader(f"Trường Tiểu học Dương Hòa — Năm học {NAM_HOC}")
st.info("💡 Hướng dẫn: Biểu mẫu hỗ trợ phụ huynh ký tay cảm ứng trực tiếp. Vui lòng chọn địa danh Quê quán và Địa chỉ cư trú thời gian thực.")

DATA_34_TINH_THANH = {
    "Tỉnh Kiên Giang": {
        "Huyện Kiên Lương": ["Thị trấn Kiên Lương", "Xã Dương Hòa", "Xã Hòa Điền", "Xã Kiên Bình", "Xã Bình An", "Xã Bình Trị", "Xã Hòn Nghệ"],
        "Thành phố Rạch Giá": ["Phường Vĩnh Thanh Vân", "Phường Vĩnh Thanh", "Phường Vĩnh Lạc", "Phường An Hòa", "Phường An Bình", "Phường Rạch Sỏi"],
        "Thành phố Phú Quốc": ["Phường Dương Đông", "Phường An Thới", "Xã Hàm Ninh", "Xã Dương Tơ", "Xã Gành Dầu"],
        "Thành phố Hà Tiên": ["Phường Đông Hồ", "Phường Bình San", "Phường Pháo Đài", "Phường Tô Châu"]
    },
    "Tỉnh An Giang": {
        "Thành phố Long Xuyên": ["Phường Mỹ Bình", "Phường Mỹ Long", "Phường Mỹ Phước", "Phường Mỹ Quý"],
        "Thành phố Châu Đốc": ["Phường Châu Phú A", "Phường Châu Phú B", "Phường Núi Sam", "Phường Vĩnh Mỹ"]
    },
    "Thành phố Hồ Chí Minh": {
        "Quận 1": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Cô Giang", "Phường Tân Định"],
        "Quận 3": ["Phường Võ Thị Sáu (Sáp nhập)", "Phường 1", "Phường 2", "Phường 4"],
        "Thành phố Thủ Đức": ["Phường Thủ Thiêm", "Phường An Khánh", "Phường Hiệp Bình Chánh", "Phường Linh Đông"]
    },
    "Thành phố Hà Nội": {
        "Quận Hoàn Kiếm": ["Phường Đồng Xuân", "Phường Hàng Bạc", "Phường Hàng Bồ", "Phường Tràng Tiền"],
        "Quận Ba Đình": ["Phường Đội Cấn", "Phường Kim Mã", "Phường Quán Thánh", "Phường Trúc Bạch"]
    },
    "Thành phố Cần Thơ": {
        "Quận Ninh Kiều": ["Phường Tân An (Sáp nhập mới)", "Phường Thới Bình", "Phường An Hòa", "Phường An Khánh"]
    }
}
DATA_34_TINH_THANH.update({
    "Tỉnh Nghệ An": {"Thành phố Vinh": ["Phường Hồng Sơn", "Phường Quang Trung", "Phường Vinh Tân"]},
    "Tỉnh Hà Tĩnh": {"Thành phố Hà Tĩnh": ["Phường Bắc Hà", "Phường Nam Ngạn", "Phường Nguyễn Du"]},
    "Tỉnh Nam Định": {"Thành phố Nam Định": ["Phường Vị Hoàng", "Phường Năng Tĩnh", "Phường Trường Thi"]},
    "Tỉnh Thanh Hóa": {"Thành phố Thanh Hóa": ["Phường Ba Đình", "Phường Ngọc Trạo", "Phường Hàm Rồng"]},
    "Tỉnh Quảng Ninh": {"Thành phố Hạ Long": ["Phường Hồng Gai", "Phường Bạch Đằng", "Phường Bãi Cháy"]},
    "Thành phố Hải Phòng": {"Quận Hồng Bàng": ["Phường Hoàng Văn Thụ", "Phường Quang Trung"]},
    "Tỉnh Hải Dương": {"Thành phố Hải Dương": ["Phường Trần Hưng Đạo", "Phường Quang Trung"]},
    "Tỉnh Hưng Yên": {"Thành phố Hưng Yên": ["Phường Hiến Nam", "Phường Lam Sơn"]},
    "Tỉnh Thái Bình": {"Thành phố Thái Bình": ["Phường Lê Hồng Phong", "Phường Kỳ Bá"]},
    "Tỉnh Ninh Bình": {"Thành phố Ninh Bình": ["Phường Vân Giang", "Phường Thanh Bình"]},
    "Tỉnh Hà Nam": {"Thành phố Phủ Lý": ["Phường Minh Khai", "Phường Hai Bà Trưng"]},
    "Tỉnh Vĩnh Phúc": {"Thành phố Vĩnh Yên": ["Phường Liên Bảo", "Phường Tích Sơn"]},
    "Tỉnh Phú Thọ": {"Thành phố Việt Trì": ["Phường Tiên Cát", "Phường Gia Cẩm"]},
    "Tỉnh Bắc Ninh": {"Thành phố Bắc Ninh": ["Phường Tiền An", "Phường Đại Phúc"]},
    "Tỉnh Thái Nguyên": {"Thành phố Thái Nguyên": ["Phường Phan Đình Phùng", "Phường Trưng Vương"]},
    "Tỉnh Quảng Nam": {"Thành phố Tam Kỳ": ["Phường An Xuân", "Phường Phước Hòa"]},
    "Thành phố Đà Nẵng": {"Quận Hải Châu": ["Phường Phước Ninh", "Phường Nam Dương"]},
    "Tỉnh Thừa Thiên Huế": {"Thành phố Huế": ["Phường Thuận Thành", "Phường Vĩnh Ninh"]},
    "Tỉnh Bình Định": {"Thành phố Quy Nhơn": ["Phường Lê Lợi", "Phường Trần Hưng Đạo"]},
    "Tỉnh Khánh Hòa": {"Thành phố Nha Trang": ["Phường Tân Lập", "Phường Lộc Thọ"]},
    "Tỉnh Lâm Đồng": {"Thành phố Đà Lạt": ["Phường 1", "Phường 2", "Phường 3"]},
    "Tỉnh Bình Dương": {"Thành phố Thủ Dầu Một": ["Phường Phú Cường", "Phường Hiệp Thành"]},
    "Tỉnh Đồng Nai": {"Thành phố Biên Hòa": ["Phường Thanh Bình", "Phường Trung Dũng"]},
    "Tỉnh Bà Rịa - Vũng Tàu": {"Thành phố Vũng Tàu": ["Phường 1", "Phường 2", "Phường 3"]},
    "Tỉnh Long An": {"Thành phố Tân An": ["Phường 1", "Phường 2", "Phường 3"]},
    "Tỉnh Đồng Tháp": {"Thành phố Cao Lãnh": ["Phường 1", "Phường 2", "Phường 3"]},
    "Tỉnh Vĩnh Long": {"Thành phố Vĩnh Long": ["Phường 1", "Phường 2", "Phường 3"]},
    "Tỉnh Tiền Giang": {"Thành phố Mỹ Tho": ["Phường 1", "Phường 2", "Phường 3"]},
    "Tỉnh Bến Tre": {"Thành phố Bến Tre": ["Phường An Hội (Sáp nhập)", "Phường Phú Khương"]}
})

st.markdown("##### 📍 Khai báo Quê quán học sinh")
col_qq1, col_qq2, col_qq3 = st.columns(3)
with col_qq1:
    qq_tinh_sel = st.selectbox("Chọn Tỉnh/Thành (Quê quán)", list(DATA_34_TINH_THANH.keys()))
with col_qq2:
    qq_huyen_sel = st.selectbox("Chọn Quận/Huyện (Quê quán)", list(DATA_34_TINH_THANH[qq_tinh_sel].keys()))
with col_qq3:
    qq_xa_sel = st.selectbox("Chọn Xã/Phường (Quê quán)", DATA_34_TINH_THANH[qq_tinh_sel][qq_huyen_sel])
hometown = f"{qq_xa_sel}, {qq_huyen_sel}, {qq_tinh_sel}"

st.write("---")
st.markdown("##### 🏠 Khai báo Địa chỉ cư trú của gia đình")
st.markdown("**📍 Địa chỉ đăng ký thường trú (Theo Sổ hộ khẩu/Thông tin cư trú)**")
col_tt1, col_tt2, col_tt3 = st.columns(3)
with col_tt1:
    tt_tinh_sel = st.selectbox("Chọn Tỉnh/Thành (Thường trú)", list(DATA_34_TINH_THANH.keys()))
with col_tt2:
    tt_huyen_sel = st.selectbox("Chọn Quận/Huyện (Thường trú)", list(DATA_34_TINH_THANH[tt_tinh_sel].keys()))
with col_tt3:
    tt_xa_sel = st.selectbox("Chọn Xã/Phường (Thường trú)", DATA_34_TINH_THANH[tt_tinh_sel][tt_huyen_sel])

tt_chi_tiet = st.text_input("Số nhà, tổ, ấp/khu phố (Thường trú):", placeholder="Ví dụ: Số 12, Ấp Tà Săng")
permanent_address = f"{tt_chi_tiet}, {tt_xa_sel}, {tt_huyen_sel}, {tt_tinh_sel}".strip(", ")

st.write("")
st.markdown("**📍 Địa chỉ chỗ ở hiện nay (Địa chỉ thực tế đang sinh sống)**")
trung_dia_chi = st.checkbox("Chỗ ở hiện nay giống với địa chỉ thường trú")

if trung_dia_chi:
    current_address = permanent_address
    st.info(f"🏠 Hệ thống ghi nhận chỗ ở: {current_address}")
else:
    col_co1, col_co2, col_co3 = st.columns(3)
    with col_co1:
        co_tinh_sel = st.selectbox("Chọn Tỉnh/Thành (Chỗ ở)", list(DATA_34_TINH_THANH.keys()))
    with col_co2:
        co_huyen_sel = st.selectbox("Chọn Quận/Huyện (Chỗ ở)", list(DATA_34_TINH_THANH[co_tinh_sel].keys()))
    with col_co3:
        # ĐÃ FIX: Sửa lỗi ghi đè biến DATA_HANH_CHINH gây trắng màn hình
        co_xa_sel = st.selectbox("Chọn Xã/Phường (Chỗ ở)", DATA_34_TINH_THANH[co_tinh_sel][co_huyen_sel])
    co_chi_tiet = st.text_input("Số nhà, tổ, ấp/khu phố (Chỗ ở hiện nay):", placeholder="Ví dụ: Số 45, Khấu Phố Ba Hòn")
    current_address = f"{co_chi_tiet}, {co_xa_sel}, {co_huyen_sel}, {co_tinh_sel}".strip(", ")
st.write("---")
st.markdown("#### 👤 Khai báo thông tin chi tiết hồ sơ học sinh")

# ĐÃ FIX TRIỆT ĐỂ: Đồng bộ cơ chế đẩy dữ liệu chữ ký Canvas JavaScript sang bộ lưu trữ Python
student_name = st.text_input("Họ và tên học sinh (Viết hoa có dấu):").strip()
col_hs1, col_hs2 = st.columns(2)
with col_hs1:
    student_gender = st.selectbox("Giới tính:", ["Nam", "Nữ"])
    student_dob = st.text_input("Ngày sinh (Ví dụ: 15/08/2020):")
with col_hs2:
    student_ethnic = st.text_input("Dân tộc:", value="Kinh")
    student_pob = st.text_input("Nơi sinh (Ghi Tỉnh/Thành phố):")

father_name = st.text_input("Họ tên cha:")
father_phone = st.text_input("SĐT cha:")
father_job = st.text_input("Nghề nghiệp cha:")

mother_name = st.text_input("Họ tên mẹ:")
mother_phone = st.text_input("SĐT mẹ:")
mother_job = st.text_input("Nghề nghiệp mẹ:")

uploaded_file = st.file_uploader("Nhấn để đính kèm ảnh mặt trước thẻ BHYT học sinh:", type=["jpg", "jpeg", "png"])

st.markdown("#### ✍️ Xác nhận ký tên bằng tay cảm ứng")
st.caption("💡 Hướng dẫn: Phụ huynh dùng ngón tay ký trực tiếp vào khung trắng bên dưới. Nếu vẽ lỗi bấm 'XÓA ĐỂ KÝ LẠI'.")

# Mã đồng bộ hóa trạng thái Canvas HTML5 bắt buộc phải dồn chuỗi liên tục
canvas_html = f"""
<div style="text-align: center;">
    <canvas id="sig-canvas" width="450" height="180" style="border: 2px dashed #999; background-color: #ffffff; cursor: crosshair; touch-action: none;"></canvas>
    <br><button type="button" id="sig-clearBtn" style="margin-top: 8px; padding: 6px 15px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight:bold;">XÓA ĐỂ KÝ LẠI</button>
</div>
<script>
    var canvas = document.getElementById("sig-canvas"); var ctx = canvas.getContext("2d");
    ctx.strokeStyle = "#0b1d3a"; ctx.lineWidth = 3.5; var drawing = false;
    
    function getPos(c, e) {{ var r = c.getBoundingClientRect(); var t = e.touches ? e.touches[0] : e; return {{ x: t.clientX - r.left, y: t.clientY - r.top }}; }}
    function draw(e) {{ if(!drawing) return; var p = getPos(canvas, e); ctx.lineTo(p.x, p.y); ctx.stroke(); }}
    
    canvas.addEventListener("mousedown", function(e){{ drawing=true; ctx.beginPath(); var p=getPos(canvas,e); ctx.moveTo(p.x,p.y); }});
    canvas.addEventListener("mousemove", draw);
    window.addEventListener("mouseup", function(){{ if(drawing){{ drawing=false; window.parent.postMessage({{type:'sig-save', data:canvas.toDataURL()}}, '*'); }} }});
    
    canvas.addEventListener("touchstart", function(e){{ drawing=true; ctx.beginPath(); var p=getPos(canvas,e); ctx.moveTo(p.x,p.y); e.preventDefault(); }});
    canvas.addEventListener("touchmove", function(e){{ draw(e); e.preventDefault(); }});
    canvas.addEventListener("touchend", function(){{ drawing=false; window.parent.postMessage({{type:'sig-save', data:canvas.toDataURL()}}, '*'); }});
    
    document.getElementById("sig-clearBtn").addEventListener("click", function(){{ canvas.width=canvas.width; ctx.strokeStyle="#0b1d3a"; ctx.lineWidth=3.5; window.parent.postMessage({{type:'sig-save', data:''}}, '*'); }});
</script>
"""
components.html(canvas_html, height=230)

# Khối tiếp nhận tin nhắn ngầm từ JavaScript đẩy ngược lên Python SessionState
import streamlit.components.v1 as cb
st.markdown("""<script>window.addEventListener('message', function(e) { if(e.data.type === 'sig-save') { const el = window.parent.document.querySelector('input[aria-label="sig_holder"]'); if(el) { el.value = e.data.data; el.dispatchEvent(new Event('input', { bubbles: true })); } } });</script>""", unsafe_allow_html=True)
sig_base64 = st.text_input("Chuỗi xác thực chữ ký điện tử:", key="sig_holder", label_visibility="collapsed")

st.write("")
if st.button("🚀 XÁC NHẬN GỬI HỒ SƠ ĐĂNG KÝ TUYỂN SINH"):
    if not student_name or not student_dob or not uploaded_file:
        st.error("❌ Vui lòng nhập đầy đủ tên học sinh, ngày sinh và đính kèm ảnh thẻ BHYT!")
    elif not sig_base64 or len(sig_base64) < 150:
        st.error("❌ Phụ huynh vui lòng dùng ngón tay ký tên vào khung trắng trước khi nộp đơn!")
    else:
        with st.spinner("⏳ Đang tải dữ liệu hồ sơ lên đám mây trường..."):
            try:
                ext = mimetypes.guess_extension(uploaded_file.type) or ".png"
                fn = f"{uuid.uuid4()}{ext}"
                supabase.storage.from_("bhyt_bucket").upload(path=fn, file=uploaded_file.getvalue(), file_options={"content-type": uploaded_file.type})
                img_url = supabase.storage.from_("bhyt_bucket").get_public_url(fn)
                
                parent_name = father_name if father_name else mother_name
                insert_data = {
                    "student_name": student_name, "student_gender": student_gender, "student_dob": student_dob,
                    "student_ethnic": student_ethnic, "student_pob": student_pob, "hometown": hometown,
                    "permanent_address": permanent_address, "current_address": current_address, "parent_name": parent_name,
                    "father_name": father_name, "father_phone": father_phone, "father_job": father_job,
                    "mother_name": mother_name, "mother_phone": mother_phone, "mother_job": mother_job,
                    "insurance_image": img_url, "parent_signature": sig_base64
                }
                supabase.table("ho_so_tuyen_sinh").insert(insert_data).execute()
                st.balloons()
                st.success("🎉 GỬI HỒ SƠ ĐĂNG KÝ TUYỂN SINH THÀNH CÔNG!")
            except Exception as err:
                st.error(f"Lỗi lưu trữ dữ liệu: {err}")
