import io
import pandas as pd
import qrcode
import streamlit as st
from supabase import Client, create_client
from openpyxl.utils import get_column_letter

NAM_HOC = "2026 - 2027"
SUPABASE_URL = "https://ywvlqwbhzbpddngxuvlm.supabase.co" 

st.set_page_config(
    page_title=f"Hệ thống quản lý tuyển sinh {NAM_HOC}",
    page_icon="📊",
    layout="wide"
)
st.title(f"📊 Hệ thống quản trị viên - Trường Tiểu học Dương Hòa (Năm học {NAM_HOC})")

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
LINK_PHU_HUYNH = "https://appphuhuynhpy-mf4r5besth7jswlgrzwzuw.streamlit.app"

col_qr1, col_qr2 = st.columns(2)
with col_qr1:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
    qr.add_data(LINK_PHU_HUYNH.lower().strip())
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img_qr.save(img_buffer, format="PNG")
    st.image(img_buffer.getvalue(), caption="Click chuột phải chọn Lưu ảnh để in ấn", width=200)

with col_qr2:
    st.write("")
    st.success(f"**🔗 Đường dẫn trực tuyến của phiếu điền:** `{LINK_PHU_HUYNH}`")
    st.info(f"""
    **💡 Hướng dẫn vận hành nhanh dành cho Giáo viên:**
    1. **Tải mã QR:** Nhập chuột phải vào ảnh mã QR bên cạnh -> Chọn **Lưu hình ảnh thành...** để đem đi in hoặc gửi cho phụ huynh.
    2. **Phụ huynh quét mã:** Phụ huynh dùng điện thoại quét mã này để mở biểu mẫu tự nhập địa chỉ.
    3. **Lấy dữ liệu:** Giáo viên nhập mật khẩu bảo mật ở phía dưới để nạp dữ liệu đám mây Real-time.
    """)
st.write("---")
password = st.text_input("Vui lòng nhập mật khẩu quản trị để xem dữ liệu học sinh:", type="password")

if password == "123456":  
    st.subheader(f"📋 Danh sách hồ sơ phiếu điền trực tuyến từ phụ huynh ({NAM_HOC})")

    with st.spinner("⏳ Đang kết nối trực tiếp đám mây lấy dữ liệu mới nhất..."):
        try:
            try:
                SUPABASE_KEY = st.secrets["supabase_key"]
            except Exception:
                SUPABASE_KEY = "sb_secret_yjs4xz1bfe-oxhv0lob0-g_yiwbh9k2"
                
            supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = supabase_client.table("ho_so_tuyen_sinh").select("*").order("created_at", desc=True).execute()
            rows = response.data
        except Exception as e:
            st.error(f"Lỗi truy cập dữ liệu bảng: Vui lòng kiểm tra lại cấu hình Secrets! Chi tiết: {e}")
            rows = []
    if rows:
        df = pd.DataFrame(rows)

        st.markdown("### 📈 Biểu đồ tiến độ phụ huynh nộp đơn")
        if "created_at" in df.columns:
            try:
                df_chart = df.copy()
                df_chart["Time_VN"] = pd.to_datetime(df_chart["created_at"]).dt.tz_convert("Asia/Ho_Chi_Minh")
                df_chart["Ngay_Nop"] = df_chart["Time_VN"].dt.date
                df_grouped = df_chart.groupby("Ngay_Nop").size().reset_index(name="Số lượng hồ sơ")
                df_grouped = df_grouped.sort_values(by="Ngay_Nop").set_index("Ngay_Nop")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="Tổng số hồ sơ tiếp nhận", value=f"{len(df)} trẻ")
                with col_m2:
                    st.metric(label="Số ngày có phụ huynh khai đơn", value=f"{len(df_grouped)} ngày")
                st.line_chart(df_grouped, use_container_width=True)
            except Exception as chart_err:
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

        # Từ điển Map cột đã được bổ sung đầy đủ 6 trường Boolean tài liệu
        column_mapping = {
            "created_at": "Thời gian đăng ký", "parent_name": "Người khai đơn", "hometown": "Quê quán học sinh",
            "current_address": "Chỗ ở hiện nay", "student_name": "Tên học sinh", "student_gender": "Giới tính", 
            "student_ethnic": "Dân tộc", "student_dob": "Ngày sinh", "student_pob": "Nơi sinh", 
            "permanent_address": "Thường trú", "father_name": "Họ tên cha", "father_phone": "SĐT Cha", 
            "father_job": "Nghề nghiệp cha", "mother_name": "Họ tên mẹ", "mother_phone": "SĐT Mẹ", 
            "mother_job": "Nghề nghiệp mẹ", "insurance_image": "Đường dẫn ảnh thẻ BHYT", "parent_signature": "Dữ liệu chữ ký mạng",
            "doc_birth_certificate": "Có Bản sao Khai sinh", "doc_national_id": "Có Số Định danh", 
            "doc_health_insurance": "Có Photo thẻ BHYT", "doc_policy_priority": "Thuộc Diện chính sách", 
            "doc_photo_2x3": "Có Ảnh 2x3", "doc_photo_3x4": "Có Ảnh 3x4"
        }

        available_cols = [col for col in column_mapping.keys() if col in df.columns]
        df_display = df[available_cols].rename(columns=column_mapping)

        cols_to_show = [c for c in df_display.columns if c != "Dữ liệu chữ ký mạng"]
        st.dataframe(df_display[cols_to_show], use_container_width=True)

        st.markdown("### 🗑️ Quản lý xóa hồ sơ nhập sai")
        col_del1, col_del2 = st.columns(2)
        with col_del1:
            student_to_delete = st.selectbox("Chọn tên học sinh cần xóa khỏi hệ thống:", df_display["Tên học sinh"].unique(), key="del_select")
        with col_del2:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("❌ XÓA HỒ SƠ NÀY", use_container_width=True, type="primary"):
                filtered_del = df[df["student_name"] == student_to_delete]
                if not filtered_del.empty:
                    row_to_del = filtered_del.iloc[0].to_dict()
                    record_id = row_to_del.get("id")
                    img_path_raw = str(row_to_del.get("insurance_image", ""))
                    
                    with st.spinner("⏳ Đang tiến hành xóa hồ sơ..."):
                        try:
                            if "bhyt_bucket/" in img_path_raw:
                                file_name_in_storage = img_path_raw.split("bhyt_bucket/")[-1]
                                supabase_client.storage.from_("bhyt_bucket").remove([file_name_in_storage])
                            if record_id:
                                supabase_client.table("ho_so_tuyen_sinh").delete().eq("id", record_id).execute()
                            else:
                                supabase_client.table("ho_so_tuyen_sinh").delete().eq("student_name", student_to_delete).execute()
                            st.success(f"🎉 Đã xóa thành công toàn bộ hồ sơ của học sinh: {student_to_delete}!")
                            st.rerun()
                        except Exception as del_error:
                            st.error(f"Lỗi khi thực hiện xóa bản ghi: {del_error}")
        st.write("---")
        st.markdown("### 📷 Tra cứu & In ấn Minh chứng hồ sơ Học sinh")
        student_list = df_display["Tên học sinh"].unique() if "Tên học sinh" in df_display.columns else []
        
        if len(student_list) > 0:
            selected_student = st.selectbox("Chọn học sinh cần kiểm tra & in ấn hồ sơ:", student_list)
            matched_data = df[df["student_name"] == selected_student]
            if not matched_data.empty:
                student_row = matched_data.iloc[0].to_dict()
                img_url = str(student_row.get("insurance_image", "")).strip()
                raw_sig = str(student_row.get("parent_signature", "")).strip()
                actual_name = str(student_row.get("parent_name", "")).strip()
                clean_sig = raw_sig.replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
                
                st.write("")
                st.markdown("**📄 Bản mô phỏng xem trước tờ đơn đăng ký (Khổ giấy chuẩn hành chính):**")
                
                html_top = f"""<div style="background-color: #f0f2f6; padding: 20px; display: flex; justify-content: center;"><div id="print-area" style="width: 790px; min-height: 1050px; padding: 40px 50px; background-color: white; color: black; box-shadow: 0 4px 15px rgba(0,0,0,0.15); border-radius: 4px; font-family: 'Times New Roman', Times, serif; font-size: 15.5px; line-height: 1.7;"><div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 2px;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM<br>Độc lập - Tự do - Hạnh phúc</div><div style="text-align: center; margin-bottom: 20px; letter-spacing: 2px; font-weight: bold;">---------------</div><div style="text-align: center; font-weight: bold; font-size: 17px; margin-bottom: 3px;">ĐƠN ĐĂNG KÝ DỰ TUYỂN SINH VÀO LỚP 1</div><div style="text-align: center; font-weight: bold; font-size: 15px; margin-bottom: 20px;">Năm học: {NAM_HOC}</div><div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 25px;">Kính gửi: Hiệu trưởng Trường Tiểu học Dương Hòa</div>"""
                html_body = f"""<div style="text-align: justify; font-family: 'Times New Roman', Times, serif;"><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Tôi tên: <span style="font-weight: bold; color: #1a237e; font-size: 16px; padding: 0 4px;">{str(student_row.get('parent_name', ''))}</span> Chỗ ở hiện nay: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('current_address', ''))}</span></div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Là phụ huynh em: <span style="font-weight: bold; text-transform: uppercase; color: #1a237e; font-size: 16px; padding: 0 4px;">{str(student_row.get('student_name', '')).upper()}</span> Nam/Nữ: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('student_gender', ''))}</span> Dân tộc: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('student_ethnic', ''))}</span></div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Sinh ngày: <span style="color: #1a237e; font-weight: bold; padding: 0 4px;">{str(student_row.get('student_dob', ''))}</span></div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Nơi sinh: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('student_pob', ''))}</span></div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Địa chỉ thường trú: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('permanent_address', ''))}</span></div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Quê quán của học sinh: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('hometown', '[Chưa cập nhật]'))}</span></div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Đã học lớp (MẦM/CHỒI/LÁ) tại Trường: ..................................................................................................</div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Gia đình thuộc diện chính sách: ..........................................................................................................</div><div style="margin-bottom: 6px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Họ tên cha: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('father_name', ''))}</span> Nghề nghiệp: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('father_job', ''))}</span> Số điện thoại: <span style="color: #1a237e; font-weight: bold; padding: 0 4px;">{str(student_row.get('father_phone', ''))}</span></div><div style="margin-bottom: 15px; background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==') repeat-x bottom; padding-bottom: 2px;">- Họ tên mẹ: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('mother_name', ''))}</span> Nghề nghiệp: <span style="color: #1a237e; padding: 0 4px;">{str(student_row.get('mother_job', ''))}</span> Số điện thoại: <span style="color: #1a237e; font-weight: bold; padding: 0 4px;">{str(student_row.get('mother_phone', ''))}</span></div><div style="text-indent: 25px; margin-top: 15px; text-align: justify;">Nay tôi viết đơn này kính trình Lãnh đạo Trường Tiểu học Dương Hòa cho con tôi được vào lớp 1 năm học {NAM_HOC} của Trường.</div><div style="text-indent: 25px; margin-top: 5px; text-align: justify; margin-bottom: 25px;">Khi con tôi được trúng tuyển vào học tại trường, tôi sẽ quan tâm nhắc nhở, tạo điều kiện thuận lợi nhất cho con học tập, rèn luyện, thực hiện đúng các nội quy, quy định của nhà trường.</div><div style="text-indent: 25px; font-weight: bold; margin-bottom: 10px;">Xin chân thành cảm ơn!</div></div>"""
                
                html_footer = f"""<table style="width: 100%; margin-top: 10px; border-collapse: collapse; font-family: 'Times New Roman', Times, serif;"><tr><td style="width: 55%; vertical-align: top; text-align: left; font-size: 14.5px;"><b style="font-style: italic; display: block; margin-bottom: 6px;">*Hồ sơ kèm theo gồm:</b><div style="margin-bottom: 3px;">{"[✓]" if student_row.get("doc_birth_certificate") else "[ ]"} - Bản sao giấy khai sinh;</div><div style="margin-bottom: 3px;">{"[✓]" if student_row.get("doc_national_id") else "[ ]"} - Số định danh;</div><div style="margin-bottom: 3px;">{"[✓]" if (student_row.get("doc_health_insurance") or img_url.startswith("http")) else "[ ]"} - Bản photo thẻ Bảo hiểm y tế;</div><div style="margin-bottom: 3px;">{"[✓]" if student_row.get("doc_policy_priority") else "[ ]"} - Giấy xác nhận diện chính sách (lớp 1);</div><div style="margin-bottom: 3px;">{"[✓]" if student_row.get("doc_photo_2x3") else "[ ]"} - Ảnh 2x3 (1 tấm);</div><div style="margin-bottom: 15px;">{"[✓]" if student_row.get("doc_photo_3x4") else "[ ]"} - Ảnh 3x4 (1 tấm);</div>{f'<div style="border: 1px dashed #999; padding: 4px; width: 142px; background-color: #fafafa;"><img src="{img_url}" width="132" alt="BHYT"></div>' if img_url.startswith('http') else ''}</td><td style="width: 45%; text-align: center; vertical-align: top;"><span style="font-size: 14.5px; font-style: italic; display: block; margin-bottom: 4px;">Dương Hòa, ngày 15 tháng 07 năm 2026</span><b style="font-size: 15px; letter-spacing: 0.5px; display: block;">CHỮ KÝ PHỤ HUYNH</b><span style="font-size: 12px; color: gray; font-style: italic; display: block; margin-top: 2px;">(Ký bằng nét vẽ di động cảm ứng)</span><div style="margin: 8px 0;"><img src="{clean_sig}" width="180" style="mix-blend-mode: multiply;" alt="Chữ ký tay"></div><b style="text-transform: uppercase; font-size: 15px; letter-spacing: 0.5px; display: block; margin-top: 5px;">{actual_name}</b></td></tr></table></div></div>"""
                
                st.markdown(f"{html_top}{html_body}{html_footer}", unsafe_allow_html=True)
                
                full_html_document = f"""<html><head><title>Don_dang_ky_{selected_student}</title><style>body{{margin:0;padding:40px;background:white;color:black;}}</style></head><body>{html_top}{html_body}{html_footer}</body></html>"""
                
                st.write("<br>", unsafe_allow_html=True)
                st.download_button(
                    label=f"📥 BẤM VÀO ĐÂY ĐỂ TẢI BIỂU MẪU ĐƠN CỦA EM {selected_student} VỀ MÁY TÍNH",
                    data=full_html_document,
                    file_name=f"Don_tuyen_sing_{selected_student.replace(' ', '_')}.html",
                    mime="text/html",
                    use_container_width=True
                )
        # Xuất dữ liệu Excel báo cáo tổng hợp
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

        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown("### 💾 Tải xuống dữ liệu báo cáo tổng hợp")
        st.download_button(
            label=f"📥 TẢI FILE EXCEL PHIẾU ĐIỀN {NAM_HOC} (XLSX)",
            data=buffer.getvalue(),
            file_name=f"Thong_tin_phieu_dien_tu_phu_huynh_{NAM_HOC.replace(' ', '')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("Hệ thống đám mây hiện đang trống. Chưa có phụ huynh nào nộp đơn.")
elif password:
    st.error("Mật khẩu truy cập hệ thống không chính xác!")
else:
    st.info("🔒 Vui lòng nhập mật khẩu quản trị phía trên để truy cập và quản lý dữ liệu học sinh.")
