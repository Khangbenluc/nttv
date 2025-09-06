"""
Streamlit app (read-only) để tra cứu nhật kí du lịch và kế hoạch chuyến đi (Nha Trang).

- App chỉ cho phép tra cứu (read-only), không có thêm/sửa/xoá.
- Bạn nhập dữ liệu trực tiếp trong code ở phần "DỮ LIỆU MẪU".
- Chạy: `streamlit run app_nhatrang_lookup.py`

Yêu cầu cập nhật:
- Hiển thị số thứ tự bắt đầu từ 1 (không phải 0).
- Tên cột rõ ràng trong bảng hiển thị.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Tra cứu Nhật ký & Kế hoạch - Nha Trang", layout="wide")

# ------------------------
# ---- DỮ LIỆU MẪU ----
# ------------------------

diary_entries = [
    { 'date': '2025-08-20', 'time': '08:30', 'activity': 'Ăn sáng tại quán Bánh Căn Phan Rang - check-in resort' },
    { 'date': '2025-08-20', 'time': '13:00', 'activity': 'Tham quan Tháp Bà Ponagar' },
    { 'date': '2025-08-21', 'time': '09:00', 'activity': 'Lặn ngắm san hô (đi tàu ra Hòn Mun)' },
    { 'date': '2025-08-22', 'time': '19:00', 'activity': 'Dạo chợ đêm Nha Trang' },
]

trip_meta = {
    'destination': 'Nha Trang',
    'num_days': 3,
    'num_people': 2,
    'theme': 'Biển - Ẩm thực - Thư giãn',
}

itinerary = [
    { 'day': 1, 'morning': 'Đến Nha Trang, nhận phòng khách sạn', 'afternoon': '-', 'evening': 'Dạo biển, ăn tối' },
    { 'day': 2, 'morning': 'Hòn Mun - lặn biển', 'afternoon': 'VinWonders (nếu thích)', 'evening': '-' },
    { 'day': 3, 'morning': 'Tháp Bà Ponagar', 'afternoon': 'Trở về', 'evening': '-' },
]

hotels = [
    { 'name': 'Seaside Resort', 'checkin': '2025-08-20', 'checkout': '2025-08-23', 'phone': '+84 258 3xxxxxx', 'notes': 'Phòng view biển' },
]

trains = {
    'to_nhatrang': [
        { 'train_no': 'SE2', 'dep_time': '06:00', 'arr_time': '11:30' },
    ],
    'to_saigon': [
        { 'train_no': 'SE5', 'dep_time': '14:00', 'arr_time': '19:30' },
    ]
}

# ------------------------
# ---- XỬ LÝ DỮ LIỆU ----
# ------------------------

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

def parse_datetime(date_str, time_str):
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return VN_TZ.localize(dt)
    except Exception:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return VN_TZ.localize(dt)
        except Exception:
            return None

# Diary DataFrame
df_diary = pd.DataFrame(diary_entries)
if not df_diary.empty:
    if 'date' in df_diary.columns and 'time' in df_diary.columns:
        df_diary['datetime'] = df_diary.apply(lambda r: parse_datetime(r['date'], r['time']), axis=1)
        df_diary['date_only'] = pd.to_datetime(df_diary['date'], errors='coerce').dt.date
    else:
        df_diary['datetime'] = pd.NaT
        df_diary['date_only'] = pd.NaT

# Itinerary DataFrame
df_itin = pd.DataFrame(itinerary)

# Hotels DataFrame
df_hotels = pd.DataFrame(hotels)
if not df_hotels.empty:
    df_hotels['checkin_date'] = pd.to_datetime(df_hotels['checkin'], errors='coerce').dt.date
    df_hotels['checkout_date'] = pd.to_datetime(df_hotels['checkout'], errors='coerce').dt.date

# Trains DataFrame
df_trains_to = pd.DataFrame(trains.get('to_nhatrang', []))
df_trains_back = pd.DataFrame(trains.get('to_saigon', []))

# ------------------------
# ---- GIAO DIỆN ----
# ------------------------

st.title('🔎 Ứng dụng tra cứu — Nhật ký & Kế hoạch du lịch Nha Trang')
st.markdown('**Lưu ý:** App chỉ _tra cứu_ (read-only). Chèn / sửa dữ liệu trực tiếp trong mã ở phần DỮ LIỆU MẪU phía trên.')

# Sidebar filters
st.sidebar.header('Bộ lọc tra cứu')
show_section = st.sidebar.multiselect('Hiển thị phần', ['Tổng quan', 'Nhật ký', 'Lịch trình', 'Khách sạn', 'Tàu hoả'], default=['Tổng quan', 'Nhật ký', 'Lịch trình'])

# Diary filters
with st.sidebar.expander('Bộ lọc Nhật ký'):
    diary_date_min = None
    diary_date_max = None
    if not df_diary.empty:
        min_date = df_diary['date_only'].min()
        max_date = df_diary['date_only'].max()
        diary_date_min, diary_date_max = st.date_input('Khoảng ngày', value=(min_date, max_date))
    text_search = st.text_input('Tìm theo từ khoá (hoạt động/địa điểm)')

# Itinerary filters
with st.sidebar.expander('Bộ lọc Lịch trình'):
    day_select = st.selectbox('Chọn ngày (nếu muốn)', options=['Tất cả'] + df_itin['day'].astype(str).tolist() if not df_itin.empty else ['Tất cả'])

# Hotels & trains filters
with st.sidebar.expander('Bộ lọc khác'):
    hotel_search = st.text_input('Tìm khách sạn (tên)')
    train_search = st.text_input('Tìm tàu (số hiệu)')

# Main layout
if 'Tổng quan' in show_section:
    st.header('Tổng quan chuyến đi')
    c1, c2, c3 = st.columns(3)
    c1.metric('Địa điểm', trip_meta.get('destination', '-'))
    c2.metric('Số ngày', trip_meta.get('num_days', '-'))
    c3.metric('Số người', trip_meta.get('num_people', '-'))
    st.write('**Chủ đề:**', trip_meta.get('theme', '-'))

if 'Nhật ký' in show_section:
    st.header('Nhật ký (Diary)')
    if df_diary.empty:
        st.info('Chưa có mục nhật ký. Hãy dán danh sách `diary_entries` vào phần DỮ LIỆU ở đầu file.')
    else:
        filtered = df_diary.copy()
        try:
            if diary_date_min and diary_date_max and isinstance(diary_date_min, (list, tuple)):
                dmin, dmax = diary_date_min
                filtered = filtered[(filtered['date_only'] >= dmin) & (filtered['date_only'] <= dmax)]
            elif diary_date_min and diary_date_max:
                dmin, dmax = diary_date_min, diary_date_max
                filtered = filtered[(filtered['date_only'] >= dmin) & (filtered['date_only'] <= dmax)]
        except Exception:
            pass
        if text_search:
            filtered = filtered[filtered['activity'].str.contains(text_search, case=False, na=False)]

        st.write(f'Hiển thị {len(filtered)} kết quả')
        df_display = filtered[['date','time','activity']].sort_values(['date','time']).reset_index(drop=True)
        df_display.index = df_display.index + 1  # STT từ 1
        df_display = df_display.rename(columns={'date':'Ngày','time':'Thời gian','activity':'Hoạt động/Địa điểm'})
        st.dataframe(df_display)

        with st.expander('Xem chi tiết theo mục'):
            idx = st.number_input('Chọn số thứ tự (STT, bắt đầu từ 1)', min_value=1, max_value=max(1, len(df_display)), value=1)
            row = df_display.iloc[int(idx)-1]
            st.write('**Ngày:**', row['Ngày'])
            st.write('**Thời gian:**', row['Thời gian'])
            st.write('**Hoạt động/Địa điểm:**', row['Hoạt động/Địa điểm'])
            if 'datetime' in filtered.columns and not pd.isna(filtered.iloc[int(idx)-1]['datetime']):
                st.write('**Giờ VN:**', filtered.iloc[int(idx)-1]['datetime'].strftime("%Y-%m-%d %H:%M %Z%z"))

if 'Lịch trình' in show_section:
    st.header('Lịch trình chi tiết')
    if df_itin.empty:
        st.info('Chưa có lịch trình. Hãy dán `itinerary` vào phần DỮ LIỆU ở đầu file.')
    else:
        if day_select != 'Tất cả':
            day_num = int(day_select)
            df_show = df_itin[df_itin['day']==day_num]
        else:
            df_show = df_itin
        for _, r in df_show.sort_values('day').iterrows():
            with st.expander(f"Ngày {int(r['day'])}"):
                st.write('Sáng:')
                st.write(r.get('morning',''))
                st.write('Chiều:')
                st.write(r.get('afternoon',''))
                st.write('Tối:')
                st.write(r.get('evening',''))

if 'Khách sạn' in show_section:
    st.header('Thông tin khách sạn')
    if df_hotels.empty:
        st.info('Chưa có khách sạn. Hãy dán `hotels` vào phần DỮ LIỆU ở đầu file.')
    else:
        df_h = df_hotels.copy()
        if hotel_search:
            df_h = df_h[df_h['name'].str.contains(hotel_search, case=False, na=False)]
        df_h = df_h.rename(columns={'name':'Tên khách sạn','checkin':'Ngày Check-in','checkout':'Ngày Check-out','phone':'SĐT liên hệ','notes':'Ghi chú'})
        df_h.index = df_h.index + 1
        st.dataframe(df_h[['Tên khách sạn','Ngày Check-in','Ngày Check-out','SĐT liên hệ','Ghi chú']].reset_index(drop=True))

if 'Tàu hoả' in show_section:
    st.header('Thông tin tàu hoả')
    st.subheader('Tàu đi (đến Nha Trang)')
    if df_trains_to.empty:
        st.write('Không có thông tin tàu đi.')
    else:
        df_tt = df_trains_to.copy()
        if train_search:
            df_tt = df_tt[df_tt['train_no'].str.contains(train_search, case=False, na=False)]
        df_tt = df_tt.rename(columns={'train_no':'Số hiệu tàu','dep_time':'Giờ khởi hành','arr_time':'Giờ đến'})
        df_tt.index = df_tt.index + 1
        st.table(df_tt)

    st.subheader('Tàu về (về Sài Gòn)')
    if df_trains_back.empty:
        st.write('Không có thông tin tàu về.')
    else:
        df_tb = df_trains_back.copy()
        if train_search:
            df_tb = df_tb[df_tb['train_no'].str.contains(train_search, case=False, na=False)]
        df_tb = df_tb.rename(columns={'train_no':'Số hiệu tàu','dep_time':'Giờ khởi hành','arr_time':'Giờ đến'})
        df_tb.index = df_tb.index + 1
        st.table(df_tb)

st.markdown('---')
st.caption('Ứng dụng read-only — chỉnh dữ liệu trực tiếp trong file Python (các biến ở đầu file).')

# END
