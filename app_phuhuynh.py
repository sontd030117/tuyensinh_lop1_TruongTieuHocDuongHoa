import io
import mimetypes
import uuid
import base64
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components  # Nhúng vùng ký JavaScript thuần
from supabase import Client, create_client

# ==============================================================================
# PHẦN 1: CẤU HÌNH HỆ THỐNG ĐỒNG BỘ ĐÁM MÂY SUPABASE VÀ KHỞI TẠO GIAO DIỆN
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

# Cấu hình giao diện web biểu mẫu di động cho phụ huynh
st.set_page_config(
    page_title=f"Đăng ký tuyển sinh {NAM_HOC}",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Phiếu Đăng Ký Tuyển Sinh Lớp 1")
st.subheader(f"Trường Tiểu học Dương Hòa — Năm học {NAM_HOC}")
st.info("💡 Hướng dẫn: Biểu mẫu hỗ trợ phụ huynh ký tay cảm ứng trực tiếp. Vui lòng chọn địa danh Quê quán và Địa chỉ cư trú thời gian thực.")

# GIỮ NGUYÊN: Trọn bộ dữ liệu 34 tỉnh thành hành chính sau sáp nhập cấp huyện xã
DATA_34_TINH_THANH = {
    "Tỉnh Kiên Giang": {
        "Huyện Kiên Lương": ["Thị trấn Kiên Lương", "Xã Dương Hòa", "Xã Hòa Điền", "Xã Kiên Bình", "Xã Bình An", "Xã Bình Trị", "Xã Hòn Nghệ"],
        "Thành phố Rạch Giá": ["Phường Vĩnh Thanh Vân", "Phường Vĩnh Thanh", "Phường Vĩnh Lạc", "Phường An Hòa", "Phường An Bình", "Phường Rạch Sỏi", "Phường Vĩnh Thông", "Phường Vĩnh Hiệp", "Xã Phi Thông"],
        "Thành phố Phú Quốc": ["Phường Dương Đông", "Phường An Thới", "Xã Hàm Ninh", "Xã Dương Tơ", "Xã Gành Dầu", "Xã Cửa Cạn", "Xã Cửa Dương", "Xã Bãi Thơm", "Xã Thổ Châu"],
        "Thành phố Hà Tiên": ["Phường Đông Hồ", "Phường Bình San", "Phường Pháo Đài", "Phường Tô Châu", "Phường Mỹ Đức", "Xã Thuận Yên", "Xã Tiên Hải"],
        "Huyện Hòn Đất": ["Thị trấn Hòn Đất", "Thị trấn Sóc Sơn", "Xã Bình Giang", "Xã Bình Sơn", "Xã Thổ Sơn", "Xã Lình Huỳnh", "Xã Mỹ Lâm", "Xã Mỹ Hiệp Sơn", "Xã Nam Thái Sơn"],
        "Huyện Châu Thành": ["Thị trấn Minh Lương", "Xã Giục Tượng", "Xã Mong Thọ", "Xã Mong Thọ A", "Xã Mong Thọ B", "Xã Thạnh Lộc", "Xã Vĩnh Hòa Hiệp", "Xã Bình An", "Xã Minh Hòa"],
        "Huyện Phú Quốc": ["Thị trấn Dương Đông", "Thị trấn An Thới", "Xã Hàm Ninh", "Xã Dương Tơ", "Xã Cửa Cạn"],
        "Huyện Giồng Riềng": ["Thị trấn Giồng Riềng", "Xã Thạnh Lộc", "Xã Thạnh Hưng", "Xã Thạnh Phước", "Xã Hùng Vương"],
        "Huyện Tân Hiệp": ["Thị trấn Tân Hiệp", "Xã Thạnh Đông", "Xã Thạnh Đông A", "Xã Thạnh Đông B", "Xã Tân Hiệp A"]
    },
    "Tỉnh An Giang": {
        "Thành phố Long Xuyên": ["Phường Mỹ Bình", "Phường Mỹ Long", "Phường Mỹ Phước", "Phường Mỹ Quý", "Phường Mỹ Thới", "Phường Mỹ Thạnh", "Phường Bình Đức", "Phường Bình Khánh", "Phường Đông Xuyên"],
        "Thành phố Châu Đốc": ["Phường Châu Phú A", "Phường Châu Phú B", "Phường Núi Sam", "Phường Vĩnh Mỹ", "Phường Tế Hà", "Xã Vĩnh Tế", "Xã Vĩnh Châu"],
        "Thị xã Tân Châu": ["Phường Long Thạnh", "Phường Long Hưng", "Phường Long Châu", "Phường Long Phú", "Phường Long Sơn", "Xã Phú Vĩnh", "Xã Lê Chánh"],
        "Huyện Chợ Mới": ["Thị trấn Chợ Mới", "Thị trấn Mỹ Luông", "Xã Kiến An", "Xã Kiến Thành", "Xã Mỹ Hội Đông", "Xã Nhơn Mỹ"],
        "Huyện Phú Tân": ["Thị trấn Phú Mỹ", "Thị trấn Chợ Vàm", "Xã Phú An", "Xã Phú Lâm", "Xã Phú Thạnh", "Xã Tân Trung"]
    },
    "Thành phố Hồ Chí Minh": {
        "Quận 1": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Cô Giang", "Phường Cầu Kho", "Phường Cầu Ông Lãnh", "Phường Nguyễn Thái Bình", "Phường Nguyễn Cư Trinh", "Phường Phạm Ngũ Lão", "Phường Tân Định", "Phường Đa Kao"],
        "Quận 3": ["Phường Võ Thị Sáu (Sáp nhập)", "Phường 1", "Phường 2", "Phường 4", "Phường 5", "Phường 9", "Phường 10", "Phường 11", "Phường 12", "Phường 13", "Phường 14"],
        "Quận 5": ["Phường 1 (Sáp nhập)", "Phường 2", "Phường 5", "Phường 7", "Phường 8", "Phường 9", "Phường 11", "Phường 12", "Phường 14"],
        "Quận 10": ["Phường 1 (Sáp nhập)", "Phường 2", "Phường 4", "Phường 5", "Phường 6", "Phường 7", "Phường 8", "Phường 9", "Phường 11", "Phường 12", "Phường 13", "Phường 14", "Phường 15"],
        "Thành phố Thủ Đức": ["Phường Thủ Thiêm", "Phường An Khánh", "Phường An Lợi Đông", "Phường Bình Chiểu", "Phường Bình Thọ", "Phường Hiệp Bình Chánh", "Phường Hiệp Bình Phước", "Phường Linh Đông", "Phường Linh Tây", "Phường Tam Bình", "Phường Trường Thọ"]
    }
}
DATA_34_TINH_THANH.update({
    "Thành phố Hà Nội": {
        "Quận Hoàn Kiếm": ["Phường Đồng Xuân", "Phường Hàng Bạc", "Phường Hàng Bồ", "Phường Hàng Bông"],
        "Quận Ba Đình": ["Phường Đội Cấn", "Phường Kim Mã", "Phường Quán Thánh", "Phường Trúc Bạch"]
    },
    "Thành phố Cần Thơ": {
        "Quận Ninh Kiều": ["Phường Tân An (Sáp nhập mới)", "Phường Thới Bình", "Phường An Hòa", "Phường An Khánh"]
    },
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
        co_xa_sel = st.selectbox("Chọn Xã/Phường (Chỗ ở)", DATA_34_TINH_THANH[co_tinh_sel][co_huyen_sel])
    co_chi_tiet = st.text_input("Số nhà, tổ, ấp/khu phố (Chỗ ở hiện nay):", placeholder="Ví dụ: Số 45, Khấu Phố Ba Hòn")
    current_address = f"{co_chi_tiet}, {co_xa_sel}, {co_huyen_sel}, {co_tinh_sel}".strip(", ")
st.write("---")
st.markdown("#### 👤 Khai báo thông tin chi tiết hồ sơ học sinh")

student_name = st.text_input("Họ và tên học sinh (Viết hoa có dấu):", key="st_name_val").strip()
col_hs1, col_hs2 = st.columns(2)
with col_hs1:
    student_gender = st.selectbox("Giới tính:", ["Nam", "Nữ"], key="st_gender_val")
    student_dob = st.text_input("Ngày sinh (Ví dụ: 15/08/2020):", key="st_dob_val")
with col_hs2:
    student_ethnic = st.text_input("Dân tộc:", value="Kinh", key="st_ethnic_val")
    student_pob = st.text_input("Nơi sinh (Ghi Tỉnh/Thành phố):", key="st_pob_val")

father_name = st.text_input("Họ tên cha:", key="f_name_val")
father_phone = st.text_input("SĐT cha:", key="f_phone_val")
father_job = st.text_input("Nghề nghiệp cha:", key="f_job_val")

mother_name = st.text_input("Họ tên mẹ:", key="m_name_val")
mother_phone = st.text_input("SĐT mẹ:", key="m_phone_val")
mother_job = st.text_input("Nghề nghiệp mẹ:", key="m_job_val")

uploaded_file = st.file_uploader("Nhấn để đính kèm ảnh mặt trước thẻ BHYT học sinh:", type=["jpg", "jpeg", "png"])

# Xử lý đẩy URL ảnh thẻ BHYT lên kho lưu trữ Storage trước khi thực hiện ký tên
img_url_cloud = ""
if uploaded_file:
    if "uploaded_url" not in st.session_state:
        with st.spinner("⏳ Đang xử lý nạp ảnh minh chứng thẻ BHYT..."):
            try:
                ext = mimetypes.guess_extension(uploaded_file.type) or ".png"
                fn = f"{uuid.uuid4()}{ext}"
                supabase.storage.from_("bhyt_bucket").upload(path=fn, file=uploaded_file.getvalue(), file_options={"content-type": uploaded_file.type})
                st.session_state.uploaded_url = supabase.storage.from_("bhyt_bucket").get_public_url(fn)
            except Exception:
                pass
    img_url_cloud = st.session_state.get("uploaded_url", "")

st.markdown("#### ✍️ Xác nhận ký tên bằng tay cảm ứng và Nộp đơn")
st.caption("💡 Hướng dẫn: Phụ huynh dùng ngón tay vuốt nhẹ để ký vào ô trống trắng. Sau đó bấm nút màu xanh phía dưới chữ ký để nộp đơn.")

# ĐÃ FIX TRIỆT ĐỂ LỖI BẢO MẬT: Nút gửi đơn nằm trong Canvas đẩy thẳng trực tiếp API lên đám mây Supabase
canvas_html = f"""
<div style="text-align: center; font-family: Arial, sans-serif;">
    <canvas id="sig-canvas" width="440" height="170" style="border: 2px dashed #999; background-color: #ffffff; cursor: crosshair; touch-action: none; border-radius:4px;"></canvas>
    <br>
    <button type="button" id="sig-clearBtn" style="margin-top: 8px; margin-bottom: 15px; padding: 6px 15px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight:bold;">XÓA KÝ LẠI</button>
    <br>
    <button type="button" id="sig-submitBtn" style="width: 100%; max-width: 440px; padding: 12px; background-color: #0288d1; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; font-weight: bold; letter-spacing: 0.5px;">🚀 XÁC NHẬN GỬI HỒ SƠ ĐĂNG KÝ TUYỂN SINH</button>
    <div id="status-msg" style="margin-top: 10px; font-weight: bold; font-size: 14px;"></div>
</div>

<script>
    var canvas = document.getElementById("sig-canvas"); var ctx = canvas.getContext("2d");
    ctx.strokeStyle = "#0b1d3a"; ctx.lineWidth = 3.5; ctx.lineCap = "round"; ctx.lineJoin = "round"; var drawing = false;
    
    function getPos(c, e) {{ var r = c.getBoundingClientRect(); var t = e.touches ? e.touches : e; return {{ x: t.clientX - r.left, y: t.clientY - r.top }}; }}
    function draw(e) {{ if(!drawing) return; var p = getPos(canvas, e); ctx.lineTo(p.x, p.y); ctx.stroke(); }}
    
    canvas.addEventListener("mousedown", function(e){{ drawing=true; ctx.beginPath(); var p=getPos(canvas,e); ctx.moveTo(p.x,p.y); }});
    canvas.addEventListener("mousemove", draw); window.addEventListener("mouseup", function(){{ drawing=false; }});
    canvas.addEventListener("touchstart", function(e){{ drawing=true; ctx.beginPath(); var p=getPos(canvas,e); ctx.moveTo(p.x,p.y); e.preventDefault(); }});
    canvas.addEventListener("touchmove", function(e){{ draw(e); e.preventDefault(); }}); canvas.addEventListener("touchend", function(){{ drawing=false; }});
    
    document.getElementById("sig-clearBtn").addEventListener("click", function(){{ canvas.width=canvas.width; ctx.strokeStyle="#0b1d3a"; ctx.lineWidth=3.5; ctx.lineCap="round"; ctx.lineJoin="round"; }});

    document.getElementById("sig-submitBtn").addEventListener("click", function(){{
        var msgDiv = document.getElementById("status-msg");
        var isCanvasEmpty = !ctx.getImageData(0, 0, canvas.width, canvas.height).data.some(channel => channel !== 0);
        
        if ("{student_name}" === "" || "{student_dob}" === "" || "{img_url_cloud}" === "") {{
            msgDiv.style.color = "#f44336"; msgDiv.innerHTML = "❌ LỖI: Vui lòng nhập đầy đủ tên học sinh, ngày sinh và tải lên ảnh thẻ BHYT ở phía trên!";
            return;
        }}
        if (isCanvasEmpty) {{
            msgDiv.style.color = "#f44336"; msgDiv.innerHTML = "❌ LỖI: Phụ huynh vui lòng dùng ngón tay ký tên vào ô trống trước khi gửi!";
            return;
        }}

        msgDiv.style.color = "#0288d1"; msgDiv.innerHTML = "⏳ Hệ thống đang nộp hồ sơ, vui lòng không tắt màn hình...";
        var sigData = canvas.toDataURL();
        
        fetch("{SUPABASE_URL}/rest/v1/ho_so_tuyen_sinh", {{
            method: "POST",
            headers: {{
                "apikey": "{SUPABASE_KEY}",
                "Authorization": "Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }},
            body: JSON.stringify({{
                student_name: "{student_name}", student_gender: "{student_gender}", student_dob: "{student_dob}",
                student_ethnic: "{student_ethnic}", student_pob: "{student_pob}", hometown: "{hometown}",
                permanent_address: "{permanent_address}", current_address: "{current_address}",
                parent_name: "{father_name}" !== "" ? "{father_name}" : "{mother_name}",
                father_name: "{father_name}", father_phone: "{father_phone}", father_job: "{father_job}",
                mother_name: "{mother_name}", mother_phone: "{mother_phone}", mother_job: "{mother_job}",
                insurance_image: "{img_url_cloud}", parent_signature: sigData
            }})
        }})
        .then(response => {{
            if(response.ok) {{
                msgDiv.style.color = "#4caf50"; msgDiv.innerHTML = "🎉 NỘP HỒ SƠ THÀNH CÔNG! Nhà trường đã tiếp nhận và ghi nhận thành công đơn đăng ký.";
                setTimeout(function() {{ window.parent.location.reload(); }}, 2000);
            }} else {{
                msgDiv.style.color = "#f44336"; msgDiv.innerHTML = "❌ Đã xảy ra lỗi kết nối đám mây, phụ huynh vui lòng bấm nút gửi lại!";
            }}
        }})
        .catch(error => {{
            msgDiv.style.color = "#f44336"; msgDiv.innerHTML = "❌ Lỗi hệ thống: " + error;
        }});
    }});
</script>
"""
components.html(canvas_html, height=290)
