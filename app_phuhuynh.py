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
st.info("💡 Hướng dẫn: Phụ huynh vui lòng nhập chính xác thông tin và ký tay cảm ứng trực tiếp để nộp hồ sơ.")
st.write("---")
st.markdown("#### 👤 Khai báo thông tin chi tiết hồ sơ học sinh")

st.text_input("Họ và tên học sinh (Viết hoa có dấu):", key="inp_st_name")
col_hs1, col_hs2 = st.columns(2)
with col_hs1:
    st.selectbox("Giới tính:", ["Nam", "Nữ"], key="inp_st_gender")
    st.text_input("Ngày sinh (Ví dụ: 15/08/2020):", key="inp_st_dob")
with col_hs2:
    st.text_input("Dân tộc:", value="Kinh", key="inp_st_ethnic")
    st.text_input("Nơi sinh (Ghi Tỉnh/Thành phố):", key="inp_st_pob")

# Hệ thống 2 ô trống để phụ huynh tự điền thông tin địa chỉ ngắn gọn
st.text_input("Quê quán (Ghi Xã/Huyện/Tỉnh):", key="inp_hometown", placeholder="Ví dụ: Xã Dương Hòa, Huyện Kiên Lương, Tỉnh Kiên Giang")
st.text_input("Địa chỉ cư trú hiện nay (Số nhà, đường, ấp/khu phố, xã, huyện, tỉnh):", key="inp_address", placeholder="Ví dụ: Số 278, tổ 8, ấp Tà Săng, Xã Dương Hòa, Huyện Kiên Lương, Kiên Giang")
st.write("---")
st.text_input("Họ tên cha:", key="inp_f_name")
st.text_input("SĐT cha:", key="inp_f_phone")
st.text_input("Nghề nghiệp cha:", key="inp_f_job")
st.write("---") 
st.text_input("Họ tên mẹ:", key="inp_m_name")
st.text_input("SĐT mẹ:", key="inp_m_phone")
st.text_input("Nghề nghiệp mẹ:", key="inp_m_job")

st.write("---")
uploaded_file = st.file_uploader("Nhấn để đính kèm ảnh mặt trước thẻ BHYT học sinh:", type=["jpg", "jpeg", "png"])

img_url_cloud = ""
if uploaded_file:
    if "uploaded_url" not in st.session_state:
        with st.spinner("⏳ Đang nạp ảnh minh chứng thẻ BHYT..."):
            try:
                ext = mimetypes.guess_extension(uploaded_file.type) or ".png"
                fn = f"{uuid.uuid4()}{ext}"
                supabase.storage.from_("bhyt_bucket").upload(path=fn, file=uploaded_file.getvalue(), file_options={"content-type": uploaded_file.type})
                st.session_state.uploaded_url = supabase.storage.from_("bhyt_bucket").get_public_url(fn)
            except Exception:
                pass
    img_url_cloud = st.session_state.get("uploaded_url", "")
st.write("---")
st.markdown("#### 📁 Hồ sơ kèm theo (Phụ huynh tích chọn các giấy tờ có sẵn)")

col_doc1, col_doc2 = st.columns(2)
with col_doc1:
    st.checkbox("Bản sao giấy khai sinh", key="doc_khai_sinh")
    st.checkbox("Số định danh cá nhân / Mã định danh", key="doc_dinh_danh")
    st.checkbox("Bản photo thẻ Bảo hiểm y tế", key="doc_bhyt")
with col_doc2:
    st.checkbox("Giấy xác nhận diện chính sách (Lớp 1 nếu có)", key="doc_chinh_sach")
    st.checkbox("Ảnh 2x3 (1 tấm)", key="doc_anh_2x3")
    st.checkbox("Ảnh 3x4 (1 tấm)", key="doc_anh_3x4")
st.write("---")
st.markdown("#### ✍️ Xác nhận ký tên bằng tay cảm ứng và Nộp đơn")
st.caption("💡 Hướng dẫn: Phụ huynh dùng ngón tay vuốt nhẹ để ký vào ô trống trắng. Sau đó bấm nút màu xanh phía dưới chữ ký để nộp đơn.")

canvas_html = f"""
<div style="text-align: center; font-family: Arial, sans-serif;">
    <canvas id="sig-canvas" width="440" height="170" style="border: 2px dashed #999; background-color: #ffffff; cursor: crosshair; touch-action: none !important; -webkit-touch-callout: none; -webkit-user-select: none; border-radius:4px;"></canvas>
    <br>
    <button type="button" id="sig-clearBtn" style="margin-top: 8px; margin-bottom: 15px; padding: 6px 15px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight:bold;">XÓA KÝ LẠI</button>
    <br>
    <button type="button" id="sig-submitBtn" style="width: 100%; max-width: 440px; padding: 13px; background-color: #0288d1; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 15.5px; font-weight: bold; letter-spacing: 0.5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">🚀 BẤM VÀO ĐÂY ĐỂ GỬI HỒ SƠ ĐĂNG KÝ</button>
    <div id="status-msg" style="margin-top: 12px; font-weight: bold; font-size: 14.5px;"></div>
</div>

<script>
    var canvas = document.getElementById("sig-canvas"); var ctx = canvas.getContext("2d");
    ctx.strokeStyle = "#0b1d3a"; ctx.lineWidth = 4; ctx.lineCap = "round"; ctx.lineJoin = "round"; var drawing = false;
    
    // ĐÃ FIX TRIỆT ĐỂ: Trích xuất chính xác điểm chạm e.touches[0] giúp di động bắt tọa độ mượt mà 100%
    function getPos(c, e) {{
        var r = c.getBoundingClientRect();
        var t = e.touches && e.touches.length > 0 ? e.touches[0] : e;
        return {{ x: t.clientX - r.left, y: t.clientY - r.top }};
    }}
    
    function draw(e) {{ if(!drawing) return; var p = getPos(canvas, e); ctx.lineTo(p.x, p.y); ctx.stroke(); }}
    
    canvas.addEventListener("mousedown", function(e){{ drawing=true; ctx.beginPath(); var p=getPos(canvas,e); ctx.moveTo(p.x,p.y); }});
    canvas.addEventListener("mousemove", draw); window.addEventListener("mouseup", function(){{ drawing=false; }});
    
    canvas.addEventListener("touchstart", function(e){{ drawing = true; ctx.beginPath(); var p = getPos(canvas, e); ctx.moveTo(p.x, p.y); if (e.cancelable) e.preventDefault(); }}, {{ passive: false }});
    canvas.addEventListener("touchmove", function(e){{ if (drawing) {{ draw(e); if (e.cancelable) e.preventDefault(); }} }}, {{ passive: false }});
    canvas.addEventListener("touchend", function(e){{ drawing = false; if (e.cancelable) e.preventDefault(); }}, {{ passive: false }});
    
    document.getElementById("sig-clearBtn").addEventListener("click", function(){{ canvas.width=canvas.width; ctx.strokeStyle="#0b1d3a"; ctx.lineWidth=4; ctx.lineCap="round"; ctx.lineJoin="round"; }});

    document.getElementById("sig-submitBtn").addEventListener("click", function(){{
        var msgDiv = document.getElementById("status-msg");
        var pDoc = window.parent.document;
        
        var st_name = pDoc.querySelector('input[aria-label="Họ và tên học sinh (Viết hoa có dấu):"]') ? pDoc.querySelector('input[aria-label="Họ và tên học sinh (Viết hoa có dấu):"]').value.trim() : "";
        var st_gender = pDoc.querySelector('input[aria-label="Giới tính:"]') ? pDoc.querySelector('input[aria-label="Giới tính:"]').value : "Nam";
        var st_dob = pDoc.querySelector('input[aria-label="Ngày sinh (Ví dụ: 15/08/2020):"]') ? pDoc.querySelector('input[aria-label="Ngày sinh (Ví dụ: 15/08/2020):"]').value.trim() : "";
        var st_ethnic = pDoc.querySelector('input[aria-label="Dân tộc:"]') ? pDoc.querySelector('input[aria-label="Dân tộc:"]').value : "Kinh";
        var st_pob = pDoc.querySelector('input[aria-label="Nơi sinh (Ghi Tỉnh/Thành phố):"]') ? pDoc.querySelector('input[aria-label="Nơi sinh (Ghi Tỉnh/Thành phố):"]').value : "";
        
        var st_hometown = pDoc.querySelector('input[aria-label="Quê quán (Ghi Xã/Huyện/Tỉnh):"]') ? pDoc.querySelector('input[aria-label="Quê quán (Ghi Xã/Huyện/Tỉnh):"]').value.trim() : "";
        var st_address = pDoc.querySelector('input[aria-label="Địa chỉ cư trú hiện nay (Số nhà, đường, ấp/khu phố, xã, huyện, tỉnh):"]') ? pDoc.querySelector('input[aria-label="Địa chỉ cư trú hiện nay (Số nhà, đường, ấp/khu phố, xã, huyện, tỉnh):"]').value.trim() : "";

        var f_name = pDoc.querySelector('input[aria-label="Họ tên cha:"]') ? pDoc.querySelector('input[aria-label="Họ tên cha:"]').value.trim() : "";
        var f_phone = pDoc.querySelector('input[aria-label="SĐT cha:"]') ? pDoc.querySelector('input[aria-label="SĐT cha:"]').value : "";
        var f_job = pDoc.querySelector('input[aria-label="Nghề nghiệp cha:"]') ? pDoc.querySelector('input[aria-label="Nghề nghiệp cha:"]').value : "";
        
        var m_name = pDoc.querySelector('input[aria-label="Họ tên mẹ:"]') ? pDoc.querySelector('input[aria-label="Họ tên mẹ:"]').value.trim() : "";
        var m_phone = pDoc.querySelector('input[aria-label="SĐT mẹ:"]') ? pDoc.querySelector('input[aria-label="SĐT mẹ:"]').value : "";
        var m_job = pDoc.querySelector('input[aria-label="Nghề nghiệp mẹ:"]') ? pDoc.querySelector('input[aria-label="Nghề nghiệp mẹ:"]').value : "";

        var has_khai_sinh = pDoc.querySelector('input[aria-label="Bản sao giấy khai sinh"]') ? pDoc.querySelector('input[aria-label="Bản sao giấy khai sinh"]').checked : false;
        var has_dinh_danh = pDoc.querySelector('input[aria-label="Số định danh cá nhân / Mã định danh"]') ? pDoc.querySelector('input[aria-label="Số định danh cá nhân / Mã định danh"]').checked : false;
        var has_bhyt = pDoc.querySelector('input[aria-label="Bản photo thẻ Bảo hiểm y tế"]') ? pDoc.querySelector('input[aria-label="Bản photo thẻ Bảo hiểm y tế"]').checked : false;
        var has_chinh_sach = pDoc.querySelector('input[aria-label="Giấy xác nhận diện chính sách (Lớp 1 nếu có)"]') ? pDoc.querySelector('input[aria-label="Giấy xác nhận diện chính sách (Lớp 1 nếu có)"]').checked : false;
        var has_anh_2x3 = pDoc.querySelector('input[aria-label="Ảnh 2x3 (1 tấm)"]') ? pDoc.querySelector('input[aria-label="Ảnh 2x3 (1 tấm)"]').checked : false;
        var has_anh_3x4 = pDoc.querySelector('input[aria-label="Ảnh 3x4 (1 tấm)"]') ? pDoc.querySelector('input[aria-label="Ảnh 3x4 (1 tấm)"]').checked : false;

        var isCanvasEmpty = !ctx.getImageData(0, 0, canvas.width, canvas.height).data.some(channel => channel !== 0);
        
        if (st_name === "" || st_dob === "" || st_address === "" || "{img_url_cloud}" === "") {{
            msgDiv.style.color = "#f44336"; 
            msgDiv.innerHTML = "❌ LỖI: Vui lòng điền tên học sinh, ngày sinh, địa chỉ cư trú và đính kèm ảnh thẻ BHYT trước khi gửi!";
            return;
        }}
        
        if (isCanvasEmpty) {{
            msgDiv.style.color = "#f44336"; 
            msgDiv.innerHTML = "❌ LỖI: Phụ huynh vui lòng ký tên vào ô trống trước khi bấm nút gửi!";
            return;
        }}

        msgDiv.style.color = "#0288d1"; 
        msgDiv.innerHTML = "⏳ Hệ thống đang nộp hồ sơ dữ liệu lên nhà trường, vui lòng đợi trong giây lát...";
        var sigData = canvas.toDataURL();
        
        fetch("{SUPABASE_URL}/rest/v1/ho_so_tuyen_sinh", {{
            method: "POST",
            headers: {{
                "apikey": "{SUPABASE_KEY}",
                "Authorization": "Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }},
            body: JSON.stringify({{
                student_name: st_name, student_gender: st_gender, student_dob: st_dob,
                student_ethnic: st_ethnic, student_pob: st_pob, hometown: st_hometown,
                permanent_address: st_address, current_address: st_address,
                parent_name: f_name !== "" ? f_name : m_name,
                father_name: f_name, father_phone: f_phone, father_job: f_job,
                mother_name: m_name, mother_phone: m_phone, mother_job: m_job,
                insurance_image: "{img_url_cloud}", parent_signature: sigData,
                doc_birth_certificate: has_khai_sinh,
                doc_national_id: has_dinh_danh,
                doc_health_insurance: has_bhyt,
                doc_policy_priority: has_chinh_sach,
                doc_photo_2x3: has_anh_2x3,
                doc_photo_3x4: has_anh_3x4
            }})
        }})
        .then(response => {{
            if(response.ok) {{
                msgDiv.style.color = "#4caf50"; 
                msgDiv.innerHTML = "🎉 NỘP HỒ SƠ THÀNH CÔNG! Hệ thống đã lưu chữ ký cảm ứng. Nhà trường xin cảm ơn phụ huynh!";
                setTimeout(function() {{ window.parent.location.reload(); }}, 2500);
            }} else {{
                msgDiv.style.color = "#f44336"; 
                msgDiv.innerHTML = "❌ Lỗi đường truyền API, phụ huynh vui lòng nhấn lại nút gửi!";
            }}
        }})
        .catch(error => {{
            msgDiv.style.color = "#f44336"; 
            msgDiv.innerHTML = "❌ Lỗi kết nối máy chủ: " + error;
        }});
    }});
</script>
"""
components.html(canvas_html, height=290, scrolling=True)
