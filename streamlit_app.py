"""
Streamlit Read-only App: Tra cứu Nhật ký & Kế hoạch Du lịch Nha Trang

HƯỚNG DẪN NGẮN:
- App chỉ đọc (read-only). Bạn sửa dữ liệu bằng cách chỉnh các biến ở "DỮ LIỆU MẪU" phía đầu file.
- Chạy bằng `streamlit run app_nhatrang_lookup.py`.


Nội dung file đã được mở rộng với nhiều mẫu dữ liệu để bạn dễ demo/copy.
"""

# ---------------------------------
# IMPORTS
# ---------------------------------
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import logging
import textwrap

# ---------------------------------
# LOGGING
# ---------------------------------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('nhatrang_lookup')
logger.setLevel(logging.INFO)

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(page_title="Tra cứu Nhật ký & Kế hoạch Du Lịch - Nha Trang 2025", layout="wide", initial_sidebar_state='expanded')

# ---------------------------------
# DỮ LIỆU MẪU (NHIỀU MẪU ĐỂ DEMO)
# Bạn có thể thay toàn bộ danh sách bằng dữ liệu thật của bạn.
# ---------------------------------

# Nhật ký (diary_entries)
# Mỗi mục: {'date': 'YYYY-MM-DD', 'time': 'HH:MM', 'activity': '...'}
diary_entries = [
    {'date':'2025-08-18','time':'07:30','activity':'Khởi hành từ Sài Gòn - ga Sài Gòn'},
    {'date':'2025-08-18','time':'12:20','activity':'Ăn trưa trên đường'},
    {'date':'2025-08-18','time':'17:45','activity':'Đến Nha Trang - check-in khách sạn Sunrise'},
    {'date':'2025-08-19','time':'08:00','activity':'Ăn sáng tại quán địa phương'},
    {'date':'2025-08-19','time':'10:00','activity':'Tham quan Viện Hải Dương học'},
    {'date':'2025-08-19','time':'13:00','activity':'Ăn trưa - thử bún chả cá'},
    {'date':'2025-08-19','time':'15:00','activity':'Thư giãn tại bãi biển Trần Phú'},
    {'date':'2025-08-20','time':'07:00','activity':'Lên tàu đi Hòn Mun - lặn ngắm san hô'},
    {'date':'2025-08-20','time':'13:30','activity':'Thăm Tháp Bà Ponagar'},
    {'date':'2025-08-20','time':'19:30','activity':'Dạo chợ đêm Nha Trang - ăn hải sản'},
    {'date':'2025-08-21','time':'09:00','activity':'Tham quan chùa Long Sơn'},
    {'date':'2025-08-21','time':'12:00','activity':'Ăn trưa - nem nướng'},
    {'date':'2025-08-21','time':'16:00','activity':'Mua quà lưu niệm tại chợ Xóm Mới'},
    {'date':'2025-08-22','time':'08:30','activity':'Trả phòng, chuẩn bị về Sài Gòn'},
    {'date':'2025-08-22','time':'11:00','activity':'Lên tàu trở về'},
]

# Thông tin chung chuyến đi
trip_meta = {
    'destination': 'Nha Trang',
    'num_days': 5,
    'num_people': 8,
    'theme': 'Biển - Ẩm thực - Khám phá',
}

# Lịch trình chi tiết mỗi ngày
itinerary = [
    {'day':1, 'morning':'Khởi hành, đi tàu SE8', 'afternoon':'Nhận phòng, ăn trưa', 'evening':'Dạo bờ biển, ăn tối đại dương'},
    {'day':2, 'morning':'Viện Hải Dương học', 'afternoon':'Thưởng thức đặc sản địa phương', 'evening':'Chợ đêm'},
    {'day':3, 'morning':'Tàu ra Hòn Mun - lặn biển', 'afternoon':'Thư giãn trên đảo', 'evening':'BBQ hải sản'},
    {'day':4, 'morning':'Tháp Bà Ponagar và chùa Long Sơn', 'afternoon':'Mua sắm quà', 'evening':'Xem biểu diễn âm nhạc đường phố'},
    {'day':5, 'morning':'Trả phòng', 'afternoon':'Lên tàu về Sài Gòn', 'evening':'-'},
]

# Khách sạn (có nhiều mẫu)
hotels = [
    {'name':'Sunrise Nha Trang','checkin':'2025-08-18','checkout':'2025-08-22','phone':'+84 912 345 678','notes':'Phòng 2 giường, view biển'},
    {'name':'Seaside Resort','checkin':'2025-08-20','checkout':'2025-08-21','phone':'+84 258 3xxxxxx','notes':'Đặt qua app, có bữa sáng'},
]

# Tàu hoả thông tin (nhiều chuyến để demo)
trains = {
    'to_nhatrang': [
        {'train_no':'SE8','dep_time':'06:00','arr_time':'12:45'},
        {'train_no':'SE2','dep_time':'07:30','arr_time':'14:20'},
        {'train_no':'TN1','dep_time':'09:00','arr_time':'15:50'},
    ],
    'to_saigon': [
        {'train_no':'SE7','dep_time':'18:00','arr_time':'00:40'},
        {'train_no':'SE5','dep_time':'20:00','arr_time':'02:40'},
    ]
}

# ---------------------------------
# CONSTANTS & UTILITIES
# ---------------------------------
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M'


def parse_datetime(date_str, time_str=None):
    """Parse date and optional time into timezone-aware datetime (VN)."""
    try:
        if time_str and isinstance(time_str, str) and time_str.strip():
            dt = datetime.strptime(f"{date_str} {time_str}", DATETIME_FMT)
        else:
            dt = datetime.strptime(date_str, DATE_FMT)
        return VN_TZ.localize(dt)
    except Exception as e:
        logger.debug(f'parse_datetime failed for ({date_str}, {time_str}): {e}')
        return None


def short(text, max_len=140):
    if text is None:
        return ''
    s = str(text)
    return s if len(s) <= max_len else s[:max_len-3] + '...'

# ---------------------------------
# GLOBAL CSS (UI đẹp)
# ---------------------------------
GLOBAL_CSS = """
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial; }
.section-card { background: linear-gradient(180deg, #ffffff, #fbfbff); border-radius: 12px; padding: 16px; box-shadow: 0 8px 20px rgba(16,24,40,0.06); margin-bottom: 16px; }
.card-title { font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
.small-muted { color: #6b7280; font-size: 13px; }
.stat-number { font-size: 28px; font-weight: 700; color: #111827; }
.stat-label { color: #6b7280; font-size: 13px; }
</style>
"""


# ---------------------------------
# BUILD DATAFRAMES
# ---------------------------------

def build_diary_df(entries):
    df = pd.DataFrame(entries)
    if df.empty:
        return df
    for c in ['date','time','activity']:
        if c not in df.columns:
            df[c] = ''
    df['datetime_vn'] = df.apply(lambda r: parse_datetime(r['date'], r['time']), axis=1)
    df['date_only'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    return df


def build_itin_df(itins):
    df = pd.DataFrame(itins)
    for c in ['day','morning','afternoon','evening']:
        if c not in df.columns:
            df[c] = ''
    return df


def build_hotels_df(hlist):
    df = pd.DataFrame(hlist)
    for c in ['name','checkin','checkout','phone','notes']:
        if c not in df.columns:
            df[c] = ''
    return df


def build_trains_df(tr):
    to_df = pd.DataFrame(tr.get('to_nhatrang', []))
    back_df = pd.DataFrame(tr.get('to_saigon', []))
    for d in [to_df, back_df]:
        for c in ['train_no','dep_time','arr_time']:
            if c not in d.columns:
                d[c] = ''
    return to_df, back_df

# ---------------------------------
# UI: từng phần (giữ logic code đầu tiên)
# ---------------------------------

def show_overview(meta):
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    cols = st.columns([2,1,1,2])
    with cols[0]:
        st.markdown("<div class='small-muted'>Địa điểm</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:22px; font-weight:800; color:#0f172a;'>{meta.get('destination','-')}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.metric(label='Số ngày', value=meta.get('num_days','-'))
    with cols[2]:
        st.metric(label='Số người', value=meta.get('num_people','-'))
    with cols[3]:
        st.markdown(f"<div style='text-align:right;'><div class='small-muted'>Chủ đề</div><div style='font-style:italic'>{meta.get('theme','-')}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def show_diary_ui(df_diary):
    st.header('Nhật ký (Diary)')
    c1,c2,c3 = st.columns([1,2,1])
    with c1:
        date_range = None
        if not df_diary.empty:
            try:
                min_date = df_diary['date_only'].min()
                max_date = df_diary['date_only'].max()
                date_range = st.date_input('Khoảng ngày', value=(min_date, max_date))
            except Exception:
                date_range = st.date_input('Khoảng ngày')
        else:
            _ = st.date_input('Khoảng ngày (chưa có dữ liệu)')
    with c2:
        kw = st.text_input('Tìm theo từ khoá (hoạt động/địa điểm)')
    with c3:
        st.write('')
        if st.button('Làm mới bộ lọc'):
            logger.info('User reset diary filters')

    filtered = df_diary.copy() if not df_diary.empty else df_diary
    if not filtered.empty and date_range:
        try:
            if isinstance(date_range, (list,tuple)) and len(date_range)==2:
                dmin,dmax = date_range
            else:
                dmin = date_range
                dmax = date_range
            filtered = filtered[(filtered['date_only'] >= dmin) & (filtered['date_only'] <= dmax)]
        except Exception as e:
            logger.debug(f'date filtering error: {e}')
    if kw:
        filtered = filtered[filtered['activity'].str.contains(kw, case=False, na=False)]

    if filtered.empty:
        st.info('Không có mục nhật ký khớp với bộ lọc.')
    else:
        show_df = filtered.sort_values(['date','time']).reset_index(drop=True)
        show_df_display = show_df[['date','time','activity']].rename(columns={'date':'Ngày','time':'Thời gian','activity':'Hoạt động/Địa điểm'})
        show_df_display.index = range(1, len(show_df_display)+1)
        show_df_display.index.name = 'STT'
        st.dataframe(show_df_display)

        st.markdown('---')
        st.markdown('**Xem chi tiết mục nhật ký**')
        max_stt = len(show_df_display)
        sel = st.number_input('Chọn STT:', min_value=1, max_value=max_stt, value=1)
        selected_row = show_df.iloc[sel-1]
        dt_vn = selected_row.get('datetime_vn')
        st.write(f"**Ngày:** {selected_row.get('date','-')}")
        st.write(f"**Thời gian:** {selected_row.get('time','-')}")
        if dt_vn:
            try:
                st.write(f"**Giờ VN:** {dt_vn.strftime('%Y-%m-%d %H:%M %Z%z')}")
            except Exception:
                st.write('**Giờ VN:** -')
        st.write(f"**Hoạt động/Địa điểm:** {selected_row.get('activity','-')}")


def show_itinerary_ui(df_itin):
    st.header('Lịch trình')
    if df_itin.empty:
        st.info('Chưa có lịch trình.')
        return
    days = sorted(df_itin['day'].unique().tolist())
    day_opt = ['Tất cả'] + [f'Ngày {d}' for d in days]
    sel_day = st.selectbox('Chọn ngày', day_opt)
    if sel_day != 'Tất cả':
        day_num = int(sel_day.split()[1])
        show = df_itin[df_itin['day']==day_num]
    else:
        show = df_itin
    for _, r in show.sort_values('day').iterrows():
        with st.expander(f"Ngày {int(r['day'])}"):
            st.write('Sáng:')
            st.write(r.get('morning','-'))
            st.write('Chiều:')
            st.write(r.get('afternoon','-'))
            st.write('Tối:')
            st.write(r.get('evening','-'))


def show_hotels_ui(df_hotels):
    st.header('Khách sạn')
    if df_hotels.empty:
        st.info('Chưa có dữ liệu khách sạn.')
        return
    df = df_hotels.rename(columns={'name':'Tên khách sạn','checkin':'Ngày Check-in','checkout':'Ngày Check-out','phone':'SĐT liên hệ','notes':'Ghi chú'})
    df.index = range(1, len(df)+1)
    df.index.name = 'STT'
    st.dataframe(df[['Tên khách sạn','Ngày Check-in','Ngày Check-out','SĐT liên hệ','Ghi chú']])


def show_trains_ui(df_to, df_back):
    st.header('Tàu hoả')
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('**Tàu đi (đến Nha Trang)**')
        if df_to.empty:
            st.write('Không có thông tin tàu đi.')
        else:
            df = df_to.rename(columns={'train_no':'Số hiệu tàu','dep_time':'Giờ khởi hành','arr_time':'Giờ đến'})
            df.index = range(1, len(df)+1)
            df.index.name = 'STT'
            st.table(df)
    with col2:
        st.markdown('**Tàu về (về Sài Gòn)**')
        if df_back.empty:
            st.write('Không có thông tin tàu về.')
        else:
            df = df_back.rename(columns={'train_no':'Số hiệu tàu','dep_time':'Giờ khởi hành','arr_time':'Giờ đến'})
            df.index = range(1, len(df)+1)
            df.index.name = 'STT'
            st.table(df)

# ---------------------------------
# MAIN APP LAYOUT
# ---------------------------------

def app_main():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


    # header
    col1,col2 = st.columns([3,1])
    with col1:
        st.markdown("""
        <div style='display:flex; align-items:center; gap:12px;'>
            <div style='width:70px; height:70px; border-radius:12px; background:linear-gradient(135deg,#06b6d4,#3b82f6); display:flex; align-items:center; justify-content:center;'>
                <span style='font-size:20px; color:white; font-weight:700;'>NT2025</span>
            </div>
            <div>
                <div style='font-size:20px; font-weight:800;'>Nhật ký & Kế hoạch — Nha Trang</div>
                <div class='small-muted'>Tra cứu thông tin về chuyến đi Nha Trang tại đây.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button('Tải lại trang'):
            st.rerun()

    st.markdown('---')

    # sidebar navigation
    st.sidebar.title('Điều hướng')
    nav = st.sidebar.radio('Phần', ['Tổng quan', 'Nhật ký', 'Lịch trình', 'Khách sạn', 'Tàu hỏa'], index=0)
    st.sidebar.markdown('<div style="font-size:12px; color:#6b7280">Chọn một phần để xem.</div>', unsafe_allow_html=True')

    # build dataframes
    df_diary = build_diary_df(diary_entries)
    df_itin = build_itin_df(itinerary)
    df_hotels = build_hotels_df(hotels)
    df_tr_to, df_tr_back = build_trains_df(trains)

    # show selected
    if nav == 'Tổng quan':
        show_overview(trip_meta)
    elif nav == 'Nhật ký':
        show_diary_ui(df_diary)
    elif nav == 'Lịch trình':
        show_itinerary_ui(df_itin)
    elif nav == 'Khách sạn':
        show_hotels_ui(df_hotels)
    elif nav == 'Tàu hỏa':
        show_trains_ui(df_tr_to, df_tr_back)

    st.markdown('---')
    st.markdown('<div style="font-size:13px; color:#6b7280">Phiên bản: 1.0 — Read-only app. Dữ liệu mẫu ở đầu file.</div>', unsafe_allow_html=True)

# ---------------------------------
# RUN
# ---------------------------------

if __name__ == '__main__':
    try:
        app_main()
    except Exception as e:
        logger.exception('Ứng dụng gặp lỗi khi chạy:')
        st.error(f'Ứng dụng gặp lỗi: {e}')

# ==========================
# GHI CHÚ
# - File này là read-only: không có chức năng thêm/sửa/xóa.
# - Bạn có thể dán dữ liệu nhật ký giấy vào danh sách `diary_entries`.
# - Nếu muốn popup không hiện mặc định, sửa hàm show_center_popup().
# ==========================
