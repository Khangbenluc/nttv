"""
Streamlit Read-only App: Tra cứu Nhật ký & Kế hoạch Du lịch Nha Trang

Yêu cầu của app:
- Chỉ tra cứu (read-only). Người dùng thay dữ liệu trong file (các biến ở đầu file).
- Hiển thị giờ VN (Asia/Ho_Chi_Minh) cho các mục nhật ký.
- Popup thông báo chính giữa (không nền mờ) có nút Đóng.
- STT bắt đầu từ 1; tên cột rõ ràng.
- Giao diện (UI) đẹp, thân thiện, responsive.
- Không có chức năng thêm/sửa/xóa dữ liệu.

Hướng dẫn:
- Chỉnh `diary_entries`, `trip_meta`, `itinerary`, `hotels`, `trains` ở phần DỮ LIỆU MẪU.
- Chạy: `streamlit run app_nhatrang_lookup.py`

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
# LOGGING (mặc định INFO) - bạn có thể đổi level để debug
# ---------------------------------
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('nhatrang_lookup')
logger.setLevel(logging.INFO)

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(page_title="Tra cứu Nhật ký & Kế hoạch - Nha Trang", layout="wide", initial_sidebar_state='expanded')

# ---------------------------------
# DỮ LIỆU MẪU (CHỈNH TẠI ĐÂY)
# Thay hoặc dán dữ liệu giấy nhật ký của bạn vào các cấu trúc bên dưới.
# ---------------------------------

# diary_entries: list of dicts: { 'date': 'YYYY-MM-DD', 'time': 'HH:MM', 'activity': '...' }
diary_entries = [
    {'date': '2025-08-20', 'time': '08:30', 'activity': 'Ăn sáng tại quán Bánh Căn Phan Rang - check-in resort'},
    {'date': '2025-08-20', 'time': '13:00', 'activity': 'Tham quan Tháp Bà Ponagar'},
    {'date': '2025-08-21', 'time': '09:00', 'activity': 'Lặn ngắm san hô (đi tàu ra Hòn Mun)'},
    {'date': '2025-08-22', 'time': '19:00', 'activity': 'Dạo chợ đêm Nha Trang'},
]

# trip_meta: thông tin chung chuyến đi
trip_meta = {
    'destination': 'Nha Trang',
    'num_days': 3,
    'num_people': 2,
    'theme': 'Biển - Ẩm thực - Thư giãn',
}

# itinerary: list of dicts: { 'day': int, 'morning': str, 'afternoon': str, 'evening': str }
itinerary = [
    {'day': 1, 'morning': 'Đến Nha Trang, nhận phòng khách sạn', 'afternoon': '-', 'evening': 'Dạo biển, ăn tối'},
    {'day': 2, 'morning': 'Hòn Mun - lặn biển', 'afternoon': 'VinWonders (nếu thích)', 'evening': '-'},
    {'day': 3, 'morning': 'Tháp Bà Ponagar', 'afternoon': 'Trở về', 'evening': '-'},
]

# hotels: list of dicts: { 'name','checkin','checkout','phone','notes' }
hotels = [
    {'name': 'Seaside Resort', 'checkin': '2025-08-20', 'checkout': '2025-08-23', 'phone': '+84 258 3xxxxxx', 'notes': 'Phòng view biển'},
]

# trains: dict with 'to_nhatrang' and 'to_saigon' lists
trains = {
    'to_nhatrang': [
        {'train_no': 'SE2', 'dep_time': '06:00', 'arr_time': '11:30'},
    ],
    'to_saigon': [
        {'train_no': 'SE5', 'dep_time': '14:00', 'arr_time': '19:30'},
    ]
}

# ---------------------------------
# CONSTANTS & UTILITIES
# ---------------------------------
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M'

# helper: parse date/time to timezone-aware datetime (VN)
def parse_datetime(date_str, time_str=None):
    """Trả về datetime có timezone Asia/Ho_Chi_Minh nếu parse được, ngược lại None."""
    try:
        if time_str and isinstance(time_str, str) and time_str.strip():
            dt = datetime.strptime(f"{date_str} {time_str}", DATETIME_FMT)
        else:
            dt = datetime.strptime(date_str, DATE_FMT)
        return VN_TZ.localize(dt)
    except Exception as e:
        logger.debug(f'parse_datetime failed for ({date_str}, {time_str}): {e}')
        return None

# helper: safe get for dicts
def safe_get(d, k, default=''):
    return d.get(k, default) if isinstance(d, dict) else default

# helper: pretty truncate
def short(text, max_len=120):
    if text is None:
        return ''
    text = str(text)
    return text if len(text) <= max_len else text[:max_len-3] + '...'

# ---------------------------------
# UI: CSS global (tạo style đẹp)
# ---------------------------------
GLOBAL_CSS = """
<style>
/* Fonts and containers */
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
.section-card { background: linear-gradient(180deg, #ffffff, #fbfbff); border-radius: 12px; padding: 16px; box-shadow: 0 8px 20px rgba(16,24,40,0.06); margin-bottom: 16px; }
.card-title { font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
.small-muted { color: #6b7280; font-size: 13px; }
.stat-number { font-size: 28px; font-weight: 700; color: #111827; }
.stat-label { color: #6b7280; font-size: 13px; }
.popup-center { position: fixed; top:50%; left:50%; transform: translate(-50%,-50%); z-index:9999; }
</style>
"""

# ---------------------------------
# SHOW POPUP (GIỮ NGUYÊN NHƯ YÊU CẦU) - giữa màn hình, không nền mờ
# ---------------------------------
def show_center_popup():
    if 'notice_shown' not in st.session_state:
        st.session_state['notice_shown'] = Falsedef show_center_popup()
    if 'notice_shown' not in st.session_state:
        st.session_state['notice_shown'] = False

    if not st.session_state['notice_shown']:
        popup_html = textwrap.dedent('''
        <div class="popup-center" id="center-popup">
          <div style="background:white; padding:26px; border-radius:12px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); max-width:480px; text-align:center;">
            <h3 style="color:#b91c1c; margin:0 0 10px 0;">⚠️ Thông báo</h3>
            <p style="margin:0; font-size:14px; color:#374151;">Trang web đang trong quá trình hoàn thiện. Dữ liệu hiện tại là thử nghiệm.</p>
            <div style="margin-top:18px; display:flex; justify-content:center; gap:12px;">
              <button onclick="window.parent.postMessage({type:'popup_close'}, '*');" 
                      style="padding:8px 18px; background:#ef4444; color:white; border:none; border-radius:8px; cursor:pointer;">
                Đóng
              </button>
            </div>
          </div>
        </div>
        <script>
        window.addEventListener('message', (event) => {
          if (event.data.type === 'popup_close') {
            const popup = document.getElementById('center-popup');
            if (popup) popup.style.display = 'none';
            // báo cho streamlit
            window.parent.postMessage({isStreamlitMessage: true, type: 'popup_closed'}, '*');
          }
        });
        </script>
        ''')
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
        st.components.v1.html(popup_html, height=320, width=None)

        # xử lý sự kiện popup_closed từ frontend
        if st.session_state.get('popup_closed_flag', False):
            st.session_state['notice_shown'] = True


    # Hiển thị popup _một lần_ mỗi phiên nếu chưa đóng
    if not st.session_state.get('notice_shown', False):
        popup_html = textwrap.dedent('''
        <div class="popup-center" id="center-popup">
          <div style="background:white; padding:26px; border-radius:12px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); max-width:480px; text-align:center;">
            <h3 style="color:#b91c1c; margin:0 0 10px 0;">⚠️ Thông báo</h3>
            <p style="margin:0; font-size:14px; color:#374151;">Trang web đang trong quá trình hoàn thiện. Dữ liệu hiện tại là thử nghiệm.</p>
            <div style="margin-top:18px; display:flex; justify-content:center; gap:12px;">
              <button id="close-popup-btn" style="padding:8px 18px; background:#ef4444; color:white; border:none; border-radius:8px; cursor:pointer;">Đóng</button>
            </div>
          </div>
        </div>
        <script>
        const btn = window.parent.document.querySelector('#root').querySelector('#close-popup-btn');
        // Note: query into parent may not work in all Streamlit setups. We use local button handler below.
        document.getElementById('close-popup-btn').addEventListener('click', function(){
            const elm = document.getElementById('center-popup');
            if (elm) elm.style.display = 'none';
            // also set a visible flag into Streamlit via hash change (simple hack)
            location.hash = '#popup_closed';
        });
        </script>
        ''')
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
        # embed full-width so popup appears centered in iframe; width=None lets Streamlit use available width
        st.components.v1.html(popup_html, height=320, width=None)

        # detect hash change to mark closed (user may close via button)
        q = st.query_params
        if q.get('popup_closed') or q.get('popup') == ['closed']:
            st.session_state['notice_shown'] = True


# ---------------------------------
# BUILD DATAFRAMES & SAFE VIEWS
# ---------------------------------

def build_diary_df(entries):
    df = pd.DataFrame(entries)
    if df.empty:
        return df
    # ensure columns exist
    for c in ['date', 'time', 'activity']:
        if c not in df.columns:
            df[c] = ''
    # parse datetime
    df['datetime_vn'] = df.apply(lambda r: parse_datetime(r['date'], r['time']), axis=1)
    df['date_only'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    return df


def build_itin_df(itins):
    df = pd.DataFrame(itins)
    # ensure columns exist
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
    # returns two DataFrames
    to_df = pd.DataFrame(tr.get('to_nhatrang', []))
    back_df = pd.DataFrame(tr.get('to_saigon', []))
    for d in [to_df, back_df]:
        for c in ['train_no','dep_time','arr_time']:
            if c not in d.columns:
                d[c] = ''
    return to_df, back_df

# ---------------------------------
# UI SECTION: components for each part
# ---------------------------------

def show_overview(meta):
    """Hiển thị ô tổng quan đẹp mắt: destination, days, people, theme"""
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        cols = st.columns([2,1,1,2])
        with cols[0]:
            st.markdown(f"<div style='font-size:22px; font-weight:800; color:#0f172a;'>{meta.get('destination','-')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='small-muted'>Địa điểm</div>")
        with cols[1]:
            st.metric(label='Số ngày', value=meta.get('num_days','-'))
        with cols[2]:
            st.metric(label='Số người', value=meta.get('num_people','-'))
        with cols[3]:
            st.markdown(f"<div style='text-align:right;'><div class='small-muted'>Chủ đề</div><div style='font-style:italic'>{meta.get('theme','-')}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def show_diary_ui(df_diary):
    st.subheader('Nhật ký (Diary)')
    # filters row
    c1, c2, c3 = st.columns([1,2,1])
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
        st.write('')
        if st.button('Làm mới bộ lọc'):
            logger.info('User reset diary filters')

    # apply filters
    filtered = df_diary.copy() if not df_diary.empty else df_diary
    if not filtered.empty and date_range:
        try:
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                dmin, dmax = date_range
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
        # prepare display
        show_df = filtered.sort_values(['date','time']).reset_index(drop=True)
        show_df_display = show_df[['date','time','activity']].rename(columns={'date':'Ngày','time':'Thời gian','activity':'Hoạt động/Địa điểm'})
        show_df_display.index = range(1, len(show_df_display)+1)
        show_df_display.index.name = 'STT'
        st.dataframe(show_df_display)

        # detail area
        st.markdown('---')
        st.markdown('**Xem chi tiết mục nhật ký**')
        max_stt = len(show_df_display)
        sel = st.number_input('Chọn số thứ tự (STT):', min_value=1, max_value=max_stt, value=1)
        selected_row = show_df.iloc[sel-1]
        # show details with VN timezone
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
    st.subheader('Lịch trình')
    if df_itin.empty:
        st.info('Chưa có lịch trình.')
        return
    # day select
    days = sorted(df_itin['day'].unique().tolist())
    day_opt = ['Tất cả'] + [f'Ngày {d}' for d in days]
    sel_day = st.selectbox('Chọn ngày', day_opt)
    if sel_day != 'Tất cả':
        day_num = int(sel_day.split()[1])
        show = df_itin[df_itin['day'] == day_num]
    else:
        show = df_itin

    for _, r in show.sort_values('day').iterrows():
        with st.expander(f"Ngày {int(r['day'])}"):
            # always show labels and values (including '-') per user request
            st.write('Sáng:')
            st.write(r.get('morning','-'))
            st.write('Chiều:')
            st.write(r.get('afternoon','-'))
            st.write('Tối:')
            st.write(r.get('evening','-'))


def show_hotels_ui(df_hotels):
    st.subheader('Thông tin Khách sạn')
    if df_hotels.empty:
        st.info('Chưa có thông tin khách sạn.')
        return
    df = df_hotels.rename(columns={'name':'Tên khách sạn','checkin':'Ngày Check-in','checkout':'Ngày Check-out','phone':'SĐT liên hệ','notes':'Ghi chú'})
    df.index = range(1, len(df)+1)
    df.index.name = 'STT'
    st.dataframe(df[['Tên khách sạn','Ngày Check-in','Ngày Check-out','SĐT liên hệ','Ghi chú']])


def show_trains_ui(df_to, df_back):
    st.subheader('Tàu hoả')
    col1, col2 = st.columns(2)
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
# MAIN APP LAYOUT (giữ nguyên logic ban đầu nhưng UI đẹp hơn)
# ---------------------------------

def app_main():
    # top header and popup
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.write('')
    st.write('')
    # show popup in center (no background)
    show_center_popup()

    # two-column header with logo/title and quick actions
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("""
            <div style='display:flex; align-items:center; gap:12px;'>
                <div style='width:56px; height:56px; border-radius:10px; background:linear-gradient(135deg,#06b6d4,#3b82f6); display:flex; align-items:center; justify-content:center;'>
                    <span style='font-size:20px; color:white; font-weight:700;'>NT</span>
                </div>
                <div>
                    <div style='font-size:20px; font-weight:800;'>Nhật ký & Kế hoạch — Nha Trang</div>
                    <div class='small-muted'>Ứng dụng chỉ tra cứu — chỉnh dữ liệu tại phần DỮ LIỆU MẪU</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button('Tải lại trang'):
            st.rerun()

    st.markdown('---')

    # Sidebar filters and navigation
    st.sidebar.title('Điều hướng & Bộ lọc')
    st.sidebar.write('Chọn phần muốn xem:')

    nav = st.sidebar.radio('Phần', ['Tổng quan', 'Nhật ký', 'Lịch trình', 'Khách sạn', 'Tàu hỏa'], index=0)

    # Build dataframes safely
    df_diary = build_diary_df(diary_entries)
    df_itin = build_itin_df(itinerary)
    df_hotels = build_hotels_df(hotels)
    df_tr_to, df_tr_back = build_trains_df(trains)

    # Show selected section
    if nav == 'Tổng quan':
        show_overview(trip_meta)

    if nav == 'Nhật ký':
        show_diary_ui(df_diary)

    if nav == 'Lịch trình':
        show_itinerary_ui(df_itin)

    if nav == 'Khách sạn':
        show_hotels_ui(df_hotels)

    if nav == 'Tàu hỏa':
        show_trains_ui(df_tr_to, df_tr_back)

    # Footer
    st.markdown('---')
    st.markdown('<div style="font-size:13px; color:#6b7280">Phiên bản: 1.0 — Ứng dụng read-only. Dữ liệu mẫu ở đầu file.</div>', unsafe_allow_html=True)


# ---------------------------------
# RUN
# ---------------------------------
if __name__ == '__main__':
    try:
        app_main()
    except Exception as e:
        logger.exception('Ứng dụng gặp lỗi khi chạy:')
        st.error(f'Ứng dụng gặp lỗi: {e}')

# ============================
# GHI CHÚ
# - Giữ nguyên read-only: không có hàm lưu hoặc ghi file.
# - Bạn có thể mở rộng UI (chỉnh CSS) trong GLOBAL_CSS.
# - Để tắt popup mặc định, thay st.session_state['notice_shown'] = True ở đầu.
# ============================
