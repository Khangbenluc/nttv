import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import logging

# ============================
# LOGGING CẤU HÌNH
# ============================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================
# DỮ LIỆU MẪU
# ============================
diary_entries = [
    {"date": "2025-09-01", "time": "08:30", "activity": "Đến Nha Trang"},
    {"date": "2025-09-01", "time": "15:00", "activity": "Tắm biển"},
    {"date": "2025-09-02", "time": "09:00", "activity": "Tham quan Hòn Mun"},
]

trip_meta = {
    "location": "Nha Trang",
    "days": 5,
    "people": 4,
    "theme": "Nghỉ dưỡng và khám phá"
}

itinerary = [
    {"day": 1, "morning": "Đến Nha Trang, nhận phòng khách sạn", "afternoon": "-", "evening": "Dạo biển, ăn tối"},
    {"day": 2, "morning": "Hòn Mun - lặn biển", "afternoon": "VinWonders", "evening": "-"},
]

hotels = [
    {"name": "Sunrise Nha Trang", "checkin": "2025-09-01", "checkout": "2025-09-05", "phone": "0123456789", "notes": "Gần biển"}
]

trains = {
    "depart": {"train_no": "SE8", "depart_time": "2025-09-01 06:00", "arrive_time": "2025-09-01 14:00"},
    "return": {"train_no": "SE7", "depart_time": "2025-09-05 20:00", "arrive_time": "2025-09-06 04:00"}
}

# ============================
# TIMEZONE
# ============================
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# ============================
# POPUP THÔNG BÁO
# ============================
def show_popup_notice():
    """Hiển thị popup thông báo nổi ở chính giữa màn hình."""
    if "show_notice" not in st.session_state:
        st.session_state.show_notice = True

    if st.session_state.show_notice:
        popup_html = """
        <style>
        #popup {
          position: fixed; top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          background: white; padding: 30px; border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          z-index: 9999; max-width: 400px; text-align: center;
        }
        .close-btn {
          margin-top: 20px; padding: 10px 20px;
          background: #f00; color: white; border: none;
          border-radius: 6px; cursor: pointer;
        }
        </style>

        <div id="popup">
          <h3 style="color:red;">⚠️ Thông báo</h3>
          <p>Trang web đang trong quá trình hoàn thiện.<br>Dữ liệu hiện tại chỉ là thử nghiệm.</p>
          <button class="close-btn" onclick="document.getElementById('popup').style.display='none'">
            Đóng
          </button>
        </div>
        """
        st.components.v1.html(popup_html, height=300, width=None)
        logger.info("Hiển thị popup cảnh báo.")

# ============================
# HÀM HIỂN THỊ NHẬT KÝ
# ============================
def show_diary():
    st.header("📔 Nhật ký du lịch")
    df_diary = pd.DataFrame(diary_entries)

    if df_diary.empty:
        st.info("Chưa có dữ liệu nhật ký.")
        logger.warning("Không có dữ liệu nhật ký để hiển thị.")
    else:
        search_term = st.text_input("Tìm kiếm hoạt động hoặc địa điểm trong nhật ký:")
        logger.info(f"Tìm kiếm nhật ký với từ khóa: {search_term}")

        if search_term:
            filtered = df_diary[df_diary["activity"].str.contains(search_term, case=False, na=False)]
        else:
            filtered = df_diary

        if filtered.empty:
            st.warning("Không tìm thấy kết quả phù hợp.")
            logger.warning("Kết quả tìm kiếm rỗng.")
        else:
            df_show = filtered.copy()
            df_show.index = range(1, len(df_show) + 1)
            df_show.index.name = "STT"
            st.dataframe(df_show.rename(columns={"date": "Ngày", "time": "Thời gian", "activity": "Hoạt động/Địa điểm"}))

            idx = st.number_input("Chọn số thứ tự hàng (STT):", min_value=1, max_value=len(df_show), step=1)
            row = df_show.iloc[idx - 1]
            st.success(f"📅 {row['date']} ⏰ {row['time']} → {row['activity']}")
            logger.info(f"Hiển thị chi tiết nhật ký STT {idx}: {row.to_dict()}")

# ============================
# HÀM HIỂN THỊ THÔNG TIN CHUNG
# ============================
def show_meta():
    st.header("ℹ️ Thông tin chung chuyến đi")

    # Địa điểm
    st.markdown(f"<h2 style='color:#2E86C1;'>{trip_meta['location']}</h2>", unsafe_allow_html=True)

    # Số ngày
    st.write(f"📅 **Số ngày:** {trip_meta['days']}")

    # Số người (dùng metric để giống chỉ số)
    st.metric(label="👥 Số người đi", value=trip_meta['people'])

    # Chủ đề
    st.markdown(f"<i style='color:#27AE60;'>Chủ đề: {trip_meta['theme']}</i>", unsafe_allow_html=True)

# ============================
# HÀM HIỂN THỊ LỊCH TRÌNH
# ============================
def show_itinerary():
    st.header("📅 Lịch trình chi tiết")
    df_itin = pd.DataFrame(itinerary)

    if df_itin.empty:
        st.info("Chưa có lịch trình.")
        logger.warning("Không có dữ liệu lịch trình.")
    else:
        day_options = ["Tất cả"] + [f"Ngày {d}" for d in df_itin['day'].unique()]
        day_select = st.selectbox("Chọn ngày:", day_options)
        logger.info(f"Người dùng chọn {day_select} trong lịch trình.")

        if day_select != "Tất cả":
            day_num = int(day_select.split()[1])
            df_show = df_itin[df_itin["day"] == day_num]
        else:
            df_show = df_itin

        for _, r in df_show.sort_values("day").iterrows():
            with st.expander(f"Ngày {int(r['day'])}"):
                st.write("Sáng:", r.get("morning", ""))
                st.write("Chiều:", r.get("afternoon", ""))
                st.write("Tối:", r.get("evening", ""))
                logger.info(f"Hiển thị lịch trình ngày {r['day']}")

# ============================
# HÀM HIỂN THỊ KHÁCH SẠN
# ============================
def show_hotels():
    st.header("🏨 Thông tin khách sạn")
    df_hotels = pd.DataFrame(hotels)

    if df_hotels.empty:
        st.info("Chưa có dữ liệu khách sạn.")
        logger.warning("Không có dữ liệu khách sạn.")
    else:
        df_h = df_hotels.copy()
        df_h.index = range(1, len(df_h) + 1)
        df_h.index.name = "STT"
        st.dataframe(df_h.rename(columns={"name": "Tên khách sạn", "checkin": "Check-in", "checkout": "Check-out", "phone": "SĐT liên hệ", "notes": "Ghi chú"}))
        logger.info("Hiển thị danh sách khách sạn.")

# ============================
# HÀM HIỂN THỊ TÀU HỎA
# ============================
def show_trains():
    st.header("🚆 Thông tin tàu hỏa")
    df_trains = pd.DataFrame([trains["depart"], trains["return"]], index=["Chuyến đi", "Chuyến về"])
    st.dataframe(df_trains.rename(columns={"train_no": "Số hiệu tàu", "depart_time": "Thời gian khởi hành", "arrive_time": "Thời gian đến"}))
    logger.info("Hiển thị thông tin tàu hỏa.")

# ============================
# APP CHÍNH
# ============================
def main():
    st.set_page_config(page_title="Tra cứu Nhật ký & Kế hoạch Nha Trang", layout="wide")
    st.title("📒 Tra cứu Nhật ký & Kế hoạch Du lịch Nha Trang")

    # Hiển thị popup cảnh báo
    show_popup_notice()

    # Sidebar
    st.sidebar.header("🔍 Bộ lọc & Mục tra cứu")
    show_section = st.sidebar.multiselect(
        "Chọn phần muốn xem:",
        ["Nhật ký", "Thông tin chung", "Lịch trình", "Khách sạn", "Tàu hỏa"],
        default=["Nhật ký"]
    )

    # Gọi các hàm theo lựa chọn
    if "Nhật ký" in show_section:
        show_diary()
    if "Thông tin chung" in show_section:
        show_meta()
    if "Lịch trình" in show_section:
        show_itinerary()
    if "Khách sạn" in show_section:
        show_hotels()
    if "Tàu hỏa" in show_section:
        show_trains()

# ============================
# CHẠY APP
# ============================
if __name__ == "__main__":
    main()
