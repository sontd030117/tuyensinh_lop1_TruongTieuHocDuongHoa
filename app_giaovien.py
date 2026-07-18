import io
import pandas as pd
import qrcode
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# PHẦN 2.1: CẤU HÌNH HỆ THỐNG VÀ XÁC THỰC BẢO MẬT ĐÁM MÂY SUPABASE
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

# Nhúng phông chữ viết tay giả lập nét ký thật Mrs Saint Delafield vào CSS toàn trang
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
    2. **Phụ huynh quét mã:** Phụ huynh chỉ cần dùng điện thoại quét mã này để mở phiếu điền và chọn địa bàn cư trú, quê quán tiện lợi.
    3. **Lấy dữ liệu:** Giáo viên nhập mật khẩu hệ thống ở ô phía dưới để kiểm tra bảng dữ liệu thời gian thực và tải file Excel năm học {NAM_HOC}.
    """)

st.write("---")

password = st.text_input(
    "Vui lòng nhập mật khẩu quản trị để xem dữ liệu học sinh:",
    type="password",
)
# ==============================================================================
# PHẦN 2.2: LOGIC TẢI DỮ LIỆU ĐÁM MÂY REAL-TIME, SỬA MÚI GIỜ VN VÀ XUẤT EXCEL
# ==============================================================================
if password == "123456":  
    st.subheader(f"📋 Danh sách hồ sơ phiếu điền trực tuyến từ phụ huynh ({NAM_HOC})")

    # Loại bỏ hoàn toàn bộ nhớ đệm Cache để tải dữ liệu Real-time ngay lập tức khi vào trang
    with st.spinner("⏳ Đang kết nối trực tiếp đám mây lấy dữ liệu mới nhất..."):
        try:
            # Truy vấn toàn bộ dữ liệu, sắp xếp hồ sơ mới nộp lên đầu bảng
            response = supabase.table("ho_so_tuyen_sinh").select("*").order("created_at", desc=True).execute()
            rows = response.data
        except Exception as e:
            st.error(f"Lỗi truy cập dữ liệu bảng: Vui lòng kiểm tra lại cấu hình Supabase! Chi tiết: {e}")
            rows = []

    if rows:
        df = pd.DataFrame(rows)

        # KHỐI BIỂU ĐỒ THỐNG KÊ SỐ LƯỢNG HỒ SƠ THEO NGÀY (SỬA MÚI GIỜ VIỆT NAM CHUẨN XÁC)
        st.markdown("### 📈 Biểu đồ tiến độ phụ huynh nộp đơn")
        if "created_at" in df.columns:
            try:
                df_chart = df.copy()
                # Ép kiểu thời gian sang múi giờ Việt Nam (Asia/Ho_Chi_Minh) để không bị lệch ngày
                df_chart["Time_VN"] = pd.to_datetime(df_chart["created_at"]).dt.tz_convert("Asia/Ho_Chi_Minh")
                df_chart["Ngay_Nop"] = df_chart["Time_VN"].dt.date
                
                # Gom nhóm đếm số lượng hồ sơ nộp phát sinh theo từng ngày
                df_grouped = df_chart.groupby("Ngay_Nop").size().reset_index(name="Số lượng hồ sơ")
                df_grouped = df_grouped.sort_values(by="Ngay_Nop").set_index("Ngay_Nop")
                
                # Hiển thị số liệu tổng quan nhanh dạng số (Metrics)
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="Tổng số hồ sơ tiếp nhận", value=f"{len(df)} trẻ")
                with col_m2:
                    st.metric(label="Số ngày có phụ huynh khai đơn", value=f"{len(df_grouped)} ngày")
                
                # Vẽ biểu đồ đường
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

        # Cấu hình danh mục cột hiển thị (Đồng bộ đầy đủ cả cột quê quán và nghề nghiệp mới)
        column_mapping = {
            "created_at": "Thời gian đăng ký", "parent_name": "Người khai đơn", "hometown": "Quê quán học sinh",
            "current_address": "Chỗ ở hiện nay", "student_name": "Tên học sinh", "student_gender": "Giới tính", 
            "student_ethnic": "Dân tộc", "student_dob": "Ngày sinh", "student_pob": "Nơi sinh", 
            "permanent_address": "Thường trú", "father_name": "Họ tên cha", "father_phone": "SĐT Cha", 
            "father_job": "Nghề nghiệp cha", "mother_name": "Họ tên mẹ", "mother_phone": "SĐT Mẹ", 
            "mother_job": "Nghề nghiệp mẹ", "insurance_image": "Đường dẫn ảnh thẻ BHYT", "parent_signature": "Dữ liệu chữ ký mạng"
        }

        available_cols = [col for col in column_mapping.keys() if col in df.columns]
        df_display = df[available_cols].rename(columns=column_mapping)

        # Ẩn cột chứa chuỗi mã hóa chữ ký thô loằng ngoằng để bảng chính hiển thị gọn gàng
        cols_to_show = [c for c in df_display.columns if c != "Dữ liệu chữ ký mạng"]
        st.dataframe(df_display[cols_to_show], use_container_width=True)

        st.markdown("### 📷 Tra cứu & In ấn Minh chứng hồ sơ Học sinh")
        student_list = df_display["Tên học sinh"].unique() if "Tên học sinh" in df_display.columns else []
        if len(student_list) > 0:
            selected_student = st.selectbox("Chọn học sinh cần kiểm tra & in ấn hồ sơ:", student_list)
            
            # ----------------------------------------------------------------------
            # ĐÃ FIX LỖI CRASH: Chuyển đổi dòng dữ liệu về Dictionary chuẩn để gọi .get() an toàn
            # ----------------------------------------------------------------------
            matched_rows = df[df["student_name"] == selected_student]
            student_row = matched_rows.iloc[0].to_dict() if not matched_rows.empty else {}
            
            img_url = str(student_row.get("insurance_image", "")).strip()
            raw_sig = str(student_row.get("parent_signature", "")).strip()
            actual_name = str(student_row.get("parent_name", "")).strip()
            
            # Dọn dẹp mảng thô bọc dữ liệu dấu ngoặc vuông dôi dư từ mảng
            clean_sig = raw_sig.replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
            actual_name = actual_name.replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
            
            st.write("")
            st.markdown("**📄 Bản mô phỏng xem trước khi in ra giấy A4:**")
            
            # Mã HTML/CSS tạo hiệu ứng hộp giấy A4 đổ bóng hiển thị đầy đủ thông tin bao gồm Quê Quán mới thêm
            html_print_form = f"""
            <div style="background-color: #f0f2f6; padding: 20px; display: flex; justify-content: center;">
                <div id="print-area" style="
                    width: 790px; 
                    min-height: 1000px; 
                    padding: 50px 60px; 
                    background-color: white; 
                    color: black; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15); 
                    border-radius: 4px;
                    font-family: 'Times New Roman', Times, serif; 
                    font-size: 16px; 
                    line-height: 1.6;
                ">
                    <!-- Tiêu ngữ chuẩn văn bản hành chính -->
                    <div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 3px;">
                        CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM<br>Độc lập - Tự do - Hạnh phúc
                    </div>
                    <div style="text-align: center; margin-bottom: 25px; letter-spacing: 2px;">---------------</div>
                    
                    <!-- Tiêu đề biểu mẫu phiếu -->
                    <div style="text-align: center; font-weight: bold; font-size: 22px; margin-bottom: 20px; text-transform: uppercase;">
                        PHIẾU ĐĂNG KÝ TUYỂN SINH LỚP 1<br><span style="font-size: 15px; font-weight: normal;">NĂM HỌC: {NAM_HOC}</span>
                    </div>
                    <div style="text-align: center; font-style: italic; margin-top: -15px; margin-bottom: 35px;">Kính gửi: Ban Giám hiệu Trường Tiểu học Dương Hòa</div>
                    
                    <!-- Phần 1: Thông tin học sinh -->
                    <div style="font-weight: bold; text-decoration: underline; margin-bottom: 12px; font-size: 17px;">1. THÔNG TIN HỌC SINH:</div>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <tr>
                            <td style="width: 60%; padding: 6px 0;">- Họ và tên học sinh: <b style="text-transform: uppercase;">{str(student_row.get('student_name', '')).upper()}</b></td>
                            <td style="width: 40%; padding: 6px 0;">- Giới tính: {student_row.get('student_gender', '')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0;">- Ngày tháng năm sinh: {student_row.get('student_dob', '')}</td>
                            <td style="padding: 6px 0;">- Dân tộc: {student_row.get('student_ethnic', '')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0;">- Nơi sinh (Ghi theo khai sinh): {student_row.get('student_pob', '')}</td>
                            <td style="padding: 6px 0;">- Quê quán: {student_row.get('hometown', '[Chưa cập nhật]')}</td>
                        </tr>
                    </table>
                    <!-- Phần 2: Cư trú -->
                    <div style="font-weight: bold; text-decoration: underline; margin-bottom: 12px; font-size: 17px;">2. THÔNG TIN CƯ TRÚ:</div>
                    <div style="padding: 2px 0; margin-bottom: 20px; text-align: justify;">
                        - Địa chỉ đăng ký thường trú: {student_row.get('permanent_address', '')}<br>
                        - Địa chỉ chỗ ở hiện nay (thực tế): {student_row.get('current_address', '')}
                    </div>

                    <!-- Phần 3: Gia đình -->
                    <div style="font-weight: bold; text-decoration: underline; margin-bottom: 12px; font-size: 17px;">3. THÔNG TIN GIA ĐÌNH:</div>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 35px;">
                        <tr>
                            <td style="width: 55%; padding: 6px 0;">- Họ tên cha: {student_row.get('father_name', '')}</td>
                            <td style="width: 45%; padding: 6px 0;">- Điện thoại cha: {student_row.get('father_phone', '')}</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="padding: 6px 0; padding-bottom: 10px;">- Nghề nghiệp cha: {student_row.get('father_job', '')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0;">- Họ tên mẹ: {student_row.get('mother_name', '')}</td>
                            <td style="padding: 6px 0;">- Điện thoại mẹ: {student_row.get('mother_phone', '')}</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="padding: 6px 0;">- Nghề nghiệp mẹ: {student_row.get('mother_job', '')}</td>
                        </tr>
                    </table>

                    <table style="width: 100%; margin-top: 30px;">
                        <tr>
                            <td style="width: 50%; text-align: center; font-style: italic; vertical-align: top;">
                                {f'<div style="border: 1px dashed #aaa; padding: 6px; width: 152px; margin: 0 auto; background-color: #fafafa;"><img src="{img_url}" width="140" alt="BHYT"></div>' if img_url.startswith('http') else '<div style="border: 1px dashed #ccc; padding: 30px 10px; width: 150px; margin: 0 auto; color: gray; font-size: 13px;">[ Không có ảnh BHYT ]</div>'}
                                <br><span style="font-size: 13px; color: #555;">Ảnh minh chứng BHYT</span>
                            </td>
                            <td style="width: 50%; text-align: center; vertical-align: top;">
                                <span style="font-size: 14px; font-style: italic;">Dương Hòa, Ngày...... Tháng...... Năm 2026</span><br>
                                <b style="font-size: 14px; display: block; margin-top: 5px;">CHỮ KÝ TỰ ĐỘNG</b>
                                <span style="font-size: 12px; color: gray; font-style: italic;">(Hệ thống ký điện tử)</span>
                                <div style="font-family: 'Mrs Saint Delafield', cursive; font-size: 62px; color: #0b1d3a; margin: 5px 0; line-height: 1;">
                                    {clean_sig.replace('TEXT_SIGNATURE:', '') if clean_sig.startswith('TEXT_SIGNATURE:') else actual_name}
                                </div>
                                <b style="text-transform: uppercase; font-size: 14px; letter-spacing: 0.5px;">{actual_name}</b>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            """
            st.markdown(html_print_form, unsafe_allow_html=True)
            
            # Hàm Javascript kích hoạt lệnh máy in
            st.markdown(
                """
                <script>
                function ThucHienInAn() {
                    var printContents = document.getElementById('print-area').innerHTML;
                    var originalContents = document.body.innerHTML;
                    document.body.innerHTML = printContents;
                    window.print();
                    document.body.innerHTML = originalContents;
                    window.location.reload();
                }
                </script>
                """, 
                unsafe_allow_html=True
            )
            
            st.button("🖨️ BẤM VÀO ĐÂY ĐỂ TIẾN HÀNH IN PHIẾU NÀY RA GIẤY A4", on_click=st.rerun)

        # Khối tạo file báo cáo Excel tổng hợp hỗ trợ giãn cột tự động không lỗi
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
