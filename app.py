# -*- coding: utf-8 -*-
import streamlit as st
import random
import pandas as pd
import requests
import json
import time
import streamlit.components.v1 as components

# 1. Cấu hình trang web
st.set_page_config(page_title="App Ôn Tập Từ Vựng HSK - MSUTONG 1 & 2", layout="centered")

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyFGBMkcRyOK1z_Hw7KEd3zSnJvnKQGxn-6MUnMwFyC4StagIWtbWqQe5MqgPkkqDb4/exec"

st.markdown("""
    <style>
    section.main div[data-testid="stRadio"] label p {
        font-size: 28px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    .online-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
        margin-bottom: 10px;
    }
    .avatar-circle {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background-color: #1E88E5;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
        border: 2px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

# Hàm phát âm JS
def play_audio_js(text):
    if not text:
        return
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    js_code = f"""
    <script>
        (function() {{
            try {{
                var synth = window.parent.speechSynthesis || window.speechSynthesis;
                if (synth) {{
                    synth.cancel();
                    var msg = new SpeechSynthesisUtterance("{clean_text}");
                    msg.lang = "zh-CN";
                    msg.rate = 0.85;
                    synth.speak(msg);
                }}
            }} catch(e) {{}}
        }})();
    </script>
    """
    components.html(js_code, height=0, width=0)

# Danh mục Tên 20 bài học chuẩn MSUTONG
LESSON_NAMES = {
    # Quyển 1
    "Q1_1": "Quyển 1 - Bài 1: 你好 (Nǐ hǎo)",
    "Q1_2": "Quyển 1 - Bài 2: 你叫什么名字? (Nǐ jiào shénme míngzi?)",
    "Q1_3": "Quyển 1 - Bài 3: 很高兴认识你 (Hěn gāoxìng rènshi nǐ)",
    "Q1_4": "Quyển 1 - Bài 4: 你去哪儿? (Nǐ qù nǎr?)",
    "Q1_5": "Quyển 1 - Bài 5: 你要吃什么? (Nǐ yào chī shénme?)",
    "Q1_6": "Quyển 1 - Bài 6: 你在哪儿工作? (Nǐ zài nǎr gōngzuò?)",
    "Q1_7": "Quyển 1 - Bài 7: 中国银行在哪儿? (Zhōngguó Yínháng zài nǎr?)",
    "Q1_8": "Quyển 1 - Bài 8: 你的生日是几月几号? (Nǐ de shēngrì shì jǐ yuè jǐ hào?)",
    "Q1_9": "Quyển 1 - Bài 9: 你喜欢中国电影还是美国电影? (Nǐ xǐhuan Zhōngguó diànyǐng háishi Měiguó diànyǐng?)",
    "Q1_10": "Quyển 1 - Bài 10: 你家有几口人? (Nǐ jiā yǒu jǐ kǒu rén?)",
    
    # Quyển 2
    "Q2_1": "Quyển 2 - Bài 1: 你在听什么? (Nǐ zài tīng shénme?)",
    "Q2_2": "Quyển 2 - Bài 2: 你平时几点起床? (Nǐ píngshí jǐ diǎn qǐchuáng?)",
    "Q2_3": "Quyển 2 - Bài 3: 可以用一下你的手机吗? (Kěyǐ yòng yíxià nǐ de shǒujī ma?)",
    "Q2_4": "Quyển 2 - Bài 4: 你想要哪件? (Nǐ xiǎng yào nǎ jiàn?)",
    "Q2_5": "Quyển 2 - Bài 5: 你这个周末什么时候有空儿? (Nǐ zhège zhōumò shénme shíhou yǒu kòngr?)",
    "Q2_6": "Quyển 2 - Bài 6: 上个周末你做什么了? (Shàng gè zhōumò nǐ zuò shénme le?)",
    "Q2_7": "Quyển 2 - Bài 7: 你是跟谁一起去的? (Nǐ shì gēn shéi yìqǐ qù de?)",
    "Q2_8": "Quyển 2 - Bài 8: 你会做菜吗? (Nǐ huì zuò cài ma?)",
    "Q2_9": "Quyển 2 - Bài 9: 你见过熊猫吗? (Nǐ jiànguò xióngmāo ma?)",
    "Q2_10": "Quyển 2 - Bài 10: 给您添麻烦了! (Gěi nín tiān máfan le!)"
}

# FULL TỪ VỰNG CHÍNH VÀ TỪ BỔ SUNG (CỐ ĐỊNH 100%)
VOCAB_DATA = [
    # QUYỂN 1: BÀI 1
    {"char": "你好", "pinyin": "nǐ hǎo", "meaning": "xin chào", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "您", "pinyin": "nín", "meaning": "ngài, ông, bà", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "你们", "pinyin": "nǐmen", "meaning": "các bạn", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "老师", "pinyin": "lǎoshī", "meaning": "thầy/cô giáo", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "对不起", "pinyin": "duìbuqǐ", "meaning": "xin lỗi", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "没关系", "pinyin": "méi guānxi", "meaning": "không sao", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "谢谢", "pinyin": "xièxie", "meaning": "cảm ơn", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "不客气", "pinyin": "bú kèqi", "meaning": "không có gì", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "再见", "pinyin": "zàijiàn", "meaning": "tạm biệt", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "王", "pinyin": "Wáng", "meaning": "họ Vương", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "大卫", "pinyin": "Dàwèi", "meaning": "David", "lesson": LESSON_NAMES["Q1_1"]},

    # QUYỂN 1: BÀI 2
    {"char": "叫", "pinyin": "jiào", "meaning": "gọi, tên là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "什么", "pinyin": "shénme", "meaning": "gì, cái gì", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "名字", "pinyin": "míngzi", "meaning": "tên", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "我", "pinyin": "wǒ", "meaning": "tôi", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "呢", "pinyin": "ne", "meaning": "trợ từ ngữ khí", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "是", "pinyin": "shì", "meaning": "là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "哪", "pinyin": "nǎ", "meaning": "nào", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "国", "pinyin": "guó", "meaning": "nước, quốc gia", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "人", "pinyin": "rén", "meaning": "người", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "卡玛拉", "pinyin": "Kǎmǎlā", "meaning": "Kamala", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "高小明", "pinyin": "Gāo Xiǎomíng", "meaning": "Cao Tiểu Minh", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "南非", "pinyin": "Nánfēi", "meaning": "Nam Phi", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "中国", "pinyin": "Zhōngguó", "meaning": "Trung Quốc", "lesson": LESSON_NAMES["Q1_2"]},

    # QUYỂN 1: BÀI 3
    {"char": "请问", "pinyin": "qǐngwèn", "meaning": "xin hỏi", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "贵姓", "pinyin": "guìxìng", "meaning": "quý danh, quý họ", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "姓", "pinyin": "xìng", "meaning": "họ", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "这", "pinyin": "zhè", "meaning": "đây, này", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "名片", "pinyin": "míngpiàn", "meaning": "danh thiếp", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "很高兴", "pinyin": "gāoxìng", "meaning": "vui mừng", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "认识", "pinyin": "rènshi", "meaning": "quen biết", "lesson": LESSON_NAMES["Q1_3"]},

    # QUYỂN 1: BÀI 4
    {"char": "小姐", "pinyin": "xiǎojiě", "meaning": "cô, tiểu thư", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "师傅", "pinyin": "shīfu", "meaning": "bác tài, thợ", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "去", "pinyin": "qù", "meaning": "đi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "哪儿", "pinyin": "nǎr", "meaning": "đâu, ở đâu", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "人民", "pinyin": "rénmín", "meaning": "nhân dân", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "广场", "pinyin": "guǎngchǎng", "meaning": "quảng trường", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "知道", "pinyin": "zhīdào", "meaning": "biết", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "远", "pinyin": "yuǎn", "meaning": "xa", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "近", "pinyin": "jìn", "meaning": "gần", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "到", "pinyin": "dào", "meaning": "đến, tới", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "多少", "pinyin": "duōshao", "meaning": "bao nhiêu", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "钱", "pinyin": "qián", "meaning": "tiền", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "块", "pinyin": "kuài", "meaning": "đồng (tiền)", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "坐", "pinyin": "zuò", "meaning": "ngồi, đi (xe)", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "出租车", "pinyin": "chūzūchē", "meaning": "xe taxi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "公共汽车", "pinyin": "gōnggòng qìchē", "meaning": "xe buýt", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "打车", "pinyin": "dǎ chē", "meaning": "bắt xe", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "地铁", "pinyin": "dìtiě", "meaning": "tàu điện ngầm", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "银行", "pinyin": "yínháng", "meaning": "ngân hàng", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "公安局", "pinyin": "gōng'ān jú", "meaning": "sở công an", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "饭店", "pinyin": "fàndiàn", "meaning": "nhà hàng", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "邮局", "pinyin": "yóujú", "meaning": "bưu điện", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "宾馆", "pinyin": "bīnguǎn", "meaning": "khách sạn", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "洗手间", "pinyin": "xǐshǒujiān", "meaning": "nhà vệ sinh", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "飞机场", "pinyin": "fēijīchǎng", "meaning": "sân bay", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "火车站", "pinyin": "huǒchēzhàn", "meaning": "ga tàu hỏa", "lesson": LESSON_NAMES["Q1_4"]},

    # QUYỂN 1: BÀI 5
    {"char": "要", "pinyin": "yào", "meaning": "muốn, cần", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "吃", "pinyin": "chī", "meaning": "ăn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "牛肉", "pinyin": "niúròu", "meaning": "thịt bò", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "米饭", "pinyin": "mǐfàn", "meaning": "cơm", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "咖啡", "pinyin": "kāfēi", "meaning": "cà phê", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "奶茶", "pinyin": "nǎichá", "meaning": "trà sữa", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "包子", "pinyin": "bāozi", "meaning": "bánh bao", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "饺子", "pinyin": "jiǎozi", "meaning": "sủi cáo", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "面条", "pinyin": "miàntiáo", "meaning": "mì sợi", "lesson": LESSON_NAMES["Q1_5"]},

    # BÀI 6 -> 10 QUYỂN 1
    {"char": "工作", "pinyin": "gōngzuò", "meaning": "công việc, làm việc", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "附近", "pinyin": "fùjìn", "meaning": "gần đây", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "生日", "pinyin": "shēngrì", "meaning": "sinh nhật", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "喜欢", "pinyin": "xǐhuan", "meaning": "thích", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "爸爸", "pinyin": "bàba", "meaning": "bố", "lesson": LESSON_NAMES["Q1_10"]},

    # QUYỂN 2
    {"char": "正在", "pinyin": "zhèngzài", "meaning": "đang", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "听", "pinyin": "tīng", "meaning": "nghe", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "起床", "pinyin": "qǐchuáng", "meaning": "thức dậy", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "可以", "pinyin": "kěyǐ", "meaning": "có thể", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "衣服", "pinyin": "yīfu", "meaning": "quần áo", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "空儿", "pinyin": "kòngr", "meaning": "thời gian rảnh", "lesson": LESSON_NAMES["Q2_5"]}
]

# Kho câu Dạng 4 đầy đủ
SENTENCE_DATA = [
    {"words": ["王", "老师", "您", "好"], "pinyin_words": ["Wáng", "lǎoshī", "nín", "hǎo"], "lesson": LESSON_NAMES["Q1_1"]},
    {"words": ["你", "叫", "什么", "名字"], "pinyin_words": ["Nǐ", "jiào", "shénme", "míngzi"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["请问", "您", "贵姓"], "pinyin_words": ["Qǐngwèn", "nín", "guìxìng"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["我", "去", "人民", "广场"], "pinyin_words": ["Wǒ", "qù", "Rénmín", "Guǎngchǎng"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["请问", " cái这", "多少", "钱"], "pinyin_words": ["Qǐngwèn", "zhège", "duōshao", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["师傅", "去", "飞机场", "远", "不", "远"], "pinyin_words": ["Shīfu", "qù", "fēijīchǎng", "yuǎn", "bù", "yuǎn"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["一共", "是", "五十", "块", "钱"], "pinyin_words": ["Yígòng", "shì", "wǔshí", "kuài", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["到", "火车站", "坐", "地铁"], "pinyin_words": ["Dào", "huǒchēzhàn", "zuò", "dìtiě"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["你", "要", "吃", "什么"], "pinyin_words": ["Nǐ", "yào", "chī", "shénme"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["我", "要", "一", "碗", "米饭"], "pinyin_words": ["Wǒ", "yào", "yì", "wǎn", "mǐfàn"], "lesson": LESSON_NAMES["Q1_5"]}
]

# --- SIDEBAR: TÊN NGƯỜI DÙNG & AVATAR ONLINE ---
st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

def update_online_status():
    if user_name and user_name.strip():
        try:
            params = {"action": "ping_online", "name": user_name.strip()}
            requests.get(GOOGLE_SHEET_URL, params=params, timeout=1.2)
            res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_online"}, timeout=1.2)
            return res.json()
        except Exception:
            return [user_name.strip()]
    return []

active_users = update_online_status()

# Hiển thị Avatar Online ở Sidebar
st.sidebar.markdown("### 🟢 Đang Online")
if active_users:
    avatar_html = "<div class='online-container'>"
    for u in active_users:
        initial = u[0].upper() if u else "U"
        avatar_html += f"<div class='avatar-circle' title='{u}'>{initial}</div>"
    avatar_html += "</div>"
    st.sidebar.markdown(avatar_html, unsafe_allow_html=True)

# --- SIDEBAR: TÙY CHỈNH BÀI HỌC CŨ ---
st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
all_lessons_options = list(LESSON_NAMES.values())
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=all_lessons_options, default=[LESSON_NAMES["Q1_4"]])

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Tất cả (Ngẫu nhiên)", "Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép nối câu từ Hán & Pinyin")
)

start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# Hàm đọc phòng thi công khai xử lý an toàn
def get_public_rooms():
    try:
        res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_rooms"}, timeout=1.5).json()
        if isinstance(res, list):
            # Bỏ qua hàng tiêu đề
            return res[1:] if len(res) > 1 else []
        return []
    except Exception:
        return []

# --- SIDEBAR EXPANDER: PHÒNG THI MULTIPLAYER ---
with st.sidebar.expander("🏆 Phòng Thi Đấu Trực Tuyến", expanded=True):
    st.caption("Khởi tạo hoặc gia nhập cuộc thi nhỏ")
    host_mode = st.selectbox("Dạng bài thi:", ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép nối câu từ Hán & Pinyin"])
    host_num_questions = st.number_input("Số lượng câu:", min_value=3, max_value=50, value=5)
    host_time_limit = st.number_input("Thời gian (Phút):", min_value=1, max_value=60, value=3)
    
    if st.button("➕ Tạo Phòng Thi"):
        h_name = user_name.strip() if user_name.strip() else "Ẩn danh"
        params = {
            "action": "create_room",
            "host": h_name,
            "lessons": json.dumps(selected_lessons),
            "mode": host_mode,
            "num_questions": host_num_questions,
            "time_limit": host_time_limit
        }
        try:
            res = requests.get(GOOGLE_SHEET_URL, params=params, timeout=2.0).json()
            if isinstance(res, dict) and res.get("roomId"):
                st.success(f"Đã tạo phòng: **{res.get('roomId')}**")
            else:
                st.info("Đã tạo phòng thi!")
        except Exception:
            st.info("Đã tạo phòng thi!")

    st.write("---")
    st.markdown("**Danh Sách Phòng Hiện Có:**")
    rooms_list = get_public_rooms()
    if not rooms_list:
        st.caption("Chưa có phòng thi nào. Nhấn 'Tạo Phòng Thi' để bắt đầu!")
    else:
        for idx, rm in enumerate(rooms_list):
            # Ép kiểu an toàn cả List lẫn Dict
            if isinstance(rm, list) and len(rm) >= 6:
                r_id = rm[0]
                r_host = rm[1]
                r_mode = rm[3]
                r_num = rm[4]
                r_time = rm[5]
            elif isinstance(rm, dict):
                r_id = rm.get("roomId", "ROOM")
                r_host = rm.get("host", "Host")
                r_mode = rm.get("mode", "Dạng 1")
                r_num = rm.get("numQ", 5)
                r_time = rm.get("timeLimit", 3)
            else:
                continue
            
            st.markdown(f"**📌 {r_id}** (Host: {r_host})")
            st.caption(f"{r_mode} | {r_num} câu | {r_time} phút")
            if st.button(f"🎮 Gia nhập {r_id}", key=f"join_{r_id}_{idx}"):
                st.session_state.in_room_exam = True
                st.session_state.room_info = {
                    "roomId": r_id, "host": r_host, "mode": r_mode, "numQ": r_num, "timeLimit": r_time
                }
                st.session_state.room_q_index = 0
                st.session_state.room_score = 0
                st.session_state.room_start_time = time.time()
                st.rerun()

# Khởi tạo trạng thái ứng dụng
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "question" not in st.session_state:
    st.session_state.question = None
if "selected_sentence_words" not in st.session_state:
    st.session_state.selected_sentence_words = []
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "answered" not in st.session_state:
    st.session_state.answered = False
if "q_id" not in st.session_state:
    st.session_state.q_id = 0
if "vocab_deck" not in st.session_state:
    st.session_state.vocab_deck = []
if "sentence_deck" not in st.session_state:
    st.session_state.sentence_deck = []
if "last_selected_lessons" not in st.session_state:
    st.session_state.last_selected_lessons = []
if "speech_target" not in st.session_state:
    st.session_state.speech_target = ""

filtered_vocab = [item for item in VOCAB_DATA if item["lesson"] in selected_lessons]
filtered_sentences = [item for item in SENTENCE_DATA if item["lesson"] in selected_lessons]

def new_question():
    st.session_state.selected_sentence_words = []
    st.session_state.answered = False
    st.session_state.speech_target = ""
    st.session_state.q_id += 1
    
    if not filtered_vocab:
        st.session_state.question = None
        return
        
    current_mode = quiz_mode
    if current_mode == "Tất cả (Ngẫu nhiên)":
        available_modes = ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"]
        if filtered_sentences:
            available_modes.append("Dạng 4: Ghép nối câu từ Hán & Pinyin")
        current_mode = random.choice(available_modes)

    if current_mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin" and not filtered_sentences:
        current_mode = "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"

    if current_mode in ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"]:
        if st.session_state.last_selected_lessons != selected_lessons or not st.session_state.vocab_deck:
            st.session_state.vocab_deck = list(filtered_vocab)
            random.shuffle(st.session_state.vocab_deck)
            st.session_state.last_selected_lessons = list(selected_lessons)
            
        target = st.session_state.vocab_deck.pop()
        
        if current_mode == "Dạng 1: Chữ Hán ➡️ 4 Pinyin":
            key = "pinyin"
            wrong_options = [item["pinyin"] for item in VOCAB_DATA if item["pinyin"] != target["pinyin"]]
        elif current_mode == "Dạng 2: Pinyin ➡️ 4 Chữ Hán":
            key = "char"
            wrong_options = [item["char"] for item in VOCAB_DATA if item["char"] != target["char"]]
        else:
            key = "meaning"
            wrong_options = [item["meaning"] for item in VOCAB_DATA if item["meaning"] != target["meaning"]]
            
        distractors = random.sample(wrong_options, min(3, len(wrong_options)))
        options = distractors + [target[key]]
        random.shuffle(options)
        
        st.session_state.question = {
            "mode": current_mode,
            "target": target,
            "options": options,
            "correct_ans": target[key]
        }
        st.session_state.speech_target = target["char"]
        
    elif current_mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin":
        if not st.session_state.sentence_deck:
            st.session_state.sentence_deck = list(filtered_sentences)
            random.shuffle(st.session_state.sentence_deck)
            
        target_sent = st.session_state.sentence_deck.pop()
        words = list(target_sent["words"])
        shuffled_words = list(words)
        while shuffled_words == words and len(words) > 1:
            random.shuffle(shuffled_words)
            
        st.session_state.question = {
            "mode": current_mode,
            "target_sent": target_sent,
            "shuffled_words": shuffled_words,
            "correct_sent": " ".join(target_sent["words"])
        }

if start_button:
    st.session_state.quiz_started = True
    st.session_state.in_room_exam = False
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.vocab_deck = list(filtered_vocab)
    random.shuffle(st.session_state.vocab_deck)
    st.session_state.sentence_deck = list(filtered_sentences)
    random.shuffle(st.session_state.sentence_deck)
    st.session_state.last_selected_lessons = list(selected_lessons)
    new_question()
    st.rerun()

def send_to_google_sheet(is_correct):
    name = user_name.strip() if user_name.strip() else "Ẩn danh"
    mode_clean = st.session_state.question["mode"].replace(":", " -")
    params = {
        "action": "submit_score",
        "name": name,
        "mode": mode_clean,
        "is_correct": 1 if is_correct else 0
    }
    try:
        requests.get(GOOGLE_SHEET_URL, params=params, timeout=2.0)
    except Exception:
        pass

def record_answer(is_correct):
    st.session_state.total += 1
    if is_correct:
        st.session_state.score += 1
    send_to_google_sheet(is_correct)

def handle_answer():
    if not st.session_state.answered:
        st.session_state.answered = True
        radio_key = f"user_choice_radio_{st.session_state.q_id}"
        user_choice = st.session_state.get(radio_key)
        is_correct = (user_choice == st.session_state.question["correct_ans"])
        record_answer(is_correct)

# --- MÀN HÌNH CHÍNH ---
st.title("🎓 App Kiểm Tra Từ Vựng & Ngữ Pháp MSUTONG")

# LUỒNG PHÒNG THI MULTIPLAYER
if st.session_state.get("in_room_exam", False):
    rm_info = st.session_state.get("room_info", {})
    st.info(f"🏆 **ĐANG THI MULTIPLAYER** | Phòng: **{rm_info.get('roomId', 'ROOM')}** (Host: {rm_info.get('host')})")
    
    elapsed = int(time.time() - st.session_state.get("room_start_time", time.time()))
    time_limit_sec = int(rm_info.get("timeLimit", 3)) * 60
    remaining = time_limit_sec - elapsed
    
    if remaining <= 0:
        st.error("⏰ Đã hết thời gian làm bài thi!")
        st.write(f"📊 Kết quả cuộc thi: **{st.session_state.get('room_score', 0)} / {rm_info.get('numQ', 5)}** câu đúng.")
        if st.button("🚪 Thoát Phòng Thi"):
            st.session_state.in_room_exam = False
            st.rerun()
    else:
        st.warning(f"⏳ Thời gian còn lại: **{remaining // 60} phút {remaining % 60} giây**")
        st.progress(min(1.0, max(0.0, (st.session_state.get("room_q_index", 0)) / int(rm_info.get("numQ", 5)))))
        
        if st.session_state.get("room_q_index", 0) >= int(rm_info.get("numQ", 5)):
            st.balloons()
            st.success("🎉 Bạn đã hoàn thành cuộc thi!")
            st.write(f"📊 Tổng kết điểm số: **{st.session_state.get('room_score', 0)} / {rm_info.get('numQ', 5)}** câu đúng.")
            if st.button("🚪 Trở Về Trang Chủ"):
                st.session_state.in_room_exam = False
                st.rerun()
        else:
            q_num = st.session_state.get("room_q_index", 0) + 1
            target = random.choice(filtered_vocab) if filtered_vocab else VOCAB_DATA[0]
            st.subheader(f"Câu {q_num}/{rm_info.get('numQ', 5)}:")
            st.markdown(f"<h1 style='text-align: center; font-size: 90px; color: #1E88E5;'>{target['char']}</h1>", unsafe_allow_html=True)
            play_audio_js(target['char'])
            
            wrong_opts = [x["pinyin"] for x in VOCAB_DATA if x["pinyin"] != target["pinyin"]]
            options = random.sample(wrong_opts, min(3, len(wrong_opts))) + [target["pinyin"]]
            random.shuffle(options)
            
            ans = st.radio("Chọn phiên âm đúng:", options, key=f"rm_ans_{q_num}")
            if st.button("Nộp câu này ➡️", key=f"rm_btn_{q_num}"):
                if ans == target["pinyin"]:
                    st.session_state.room_score = st.session_state.get("room_score", 0) + 1
                st.session_state.room_q_index = st.session_state.get("room_q_index", 0) + 1
                st.rerun()

# LUỒNG KIỂM TRA CÁ NHÂN CỦ
else:
    if not st.session_state.quiz_started:
        st.info("👈 Hãy tích chọn các Bài ở danh mục bên trái, sau đó nhấn nút **🚀 Bắt đầu kiểm tra** để làm bài!")
    elif not selected_lessons:
        st.warning("⚠️ Vui lòng chọn ít nhất 1 Bài ở thanh bên trái!")
    elif st.session_state.question is None:
        st.warning("⚠️ Không tìm thấy dữ liệu cho bài học đã chọn!")
    else:
        q = st.session_state.question
        mode = q["mode"]
        current_radio_key = f"user_choice_radio_{st.session_state.q_id}"

        if mode == "Dạng 1: Chữ Hán ➡️ 4 Pinyin":
            st.info("📌 **Dạng 1:** Hãy chọn phiên âm Pinyin đúng:")
            st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 110px; color: #1E88E5;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
            
            play_audio_js(q['target']['char'])
            
            user_choice = st.radio("Chọn Pinyin:", q["options"], key=current_radio_key, on_change=handle_answer, index=None, label_visibility="collapsed")
            
            if st.session_state.answered:
                if user_choice == q["correct_ans"]:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Sai rồi! Pinyin đúng của **{q['target']['char']}** là: **{q['correct_ans']}** ({q['target']['meaning']})")

        elif mode == "Dạng 2: Pinyin ➡️ 4 Chữ Hán":
            st.info("📌 **Dạng 2:** Hãy chọn Chữ Hán đúng:")
            st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 70px; color: #E65100;'>{q['target']['pinyin']}</h1>", unsafe_allow_html=True)

            user_choice = st.radio("Chọn Chữ Hán:", q["options"], key=current_radio_key, on_change=handle_answer, index=None, label_visibility="collapsed")
            
            if st.session_state.answered:
                play_audio_js(q['target']['char'])
                if user_choice == q["correct_ans"]:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Sai rồi! Chữ Hán đúng của **{q['target']['pinyin']}** là: **{q['correct_ans']}** ({q['target']['meaning']})")

        elif mode == "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa":
            st.info("📌 **Dạng 3:** Chọn nghĩa Tiếng Việt chính xác:")
            st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #2E7D32;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 24px; color: gray;'>Pinyin: <b>{q['target']['pinyin']}</b></p>", unsafe_allow_html=True)

            play_audio_js(q['target']['char'])

            user_choice = st.radio("Chọn Nghĩa:", q["options"], key=current_radio_key, on_change=handle_answer, index=None, label_visibility="collapsed")
            
            if st.session_state.answered:
                if user_choice == q["correct_ans"]:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Sai rồi! Đáp án đúng là: **{q['correct_ans']}**")

        elif mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin":
            st.info("📌 **Dạng 4:** Bấm chọn từ để ghép thành câu hoàn chỉnh:")
            st.markdown(f"<p style='font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target_sent']['lesson']}</b></p>", unsafe_allow_html=True)
            pinyin_hint = " ".join(q["target_sent"]["pinyin_words"])
            st.markdown(f"<p style='font-size: 20px; color: #1565C0;'>💡 Gợi ý Pinyin: <b>{pinyin_hint}</b></p>", unsafe_allow_html=True)
            
            current_sentence = " ".join(st.session_state.selected_sentence_words)
            st.markdown(f"### Câu bạn chọn: **{current_sentence}**")
            
            if st.session_state.speech_target:
                play_audio_js(st.session_state.speech_target)

            cols = st.columns(len(q["shuffled_words"]))
            for idx, w in enumerate(q["shuffled_words"]):
                if cols[idx].button(w, key=f"btn_{st.session_state.q_id}_{idx}"):
                    st.session_state.selected_sentence_words.append(w)
                    st.session_state.speech_target = w
                    st.rerun()

            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("🔄 Xóa chọn lại"):
                    st.session_state.selected_sentence_words = []
                    st.session_state.speech_target = ""
                    st.rerun()
            with c2:
                if st.button("✔️ Nộp bài ghép câu"):
                    if not st.session_state.answered:
                        st.session_state.answered = True
                        user_sentence = " ".join(st.session_state.selected_sentence_words)
                        is_correct = (user_sentence == q["correct_sent"])
                        record_answer(is_correct)
                        st.session_state.speech_target = "".join(st.session_state.selected_sentence_words)
                        st.rerun()

            if st.session_state.answered:
                user_sentence = " ".join(st.session_state.selected_sentence_words)
                if user_sentence == q["correct_sent"]:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Sai rồi! Câu đúng là:\n\n**{q['correct_sent']}**")

        st.write("---")
        display_name = f" của **{user_name.strip()}**" if user_name.strip() else ""
        st.write(f"📊 Kết quả học tập{display_name}: **{st.session_state.score} / {st.session_state.total}** câu đúng.")
        
        if st.button("Câu tiếp theo ➡️"):
            new_question()
            st.rerun()

# --- BẢNG TỶ SỐ ---
with st.sidebar.expander("📊 Bảng Xếp Hạng Tỷ Số", expanded=False):
    try:
        res = requests.get(GOOGLE_SHEET_URL, timeout=2.0)
        sheet_data = res.json()
        if len(sheet_data) <= 1:
            st.write("Chưa có dữ liệu làm bài nào.")
        else:
            df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
            df["is_correct"] = pd.to_numeric(df["Result"])
            
            summary_df = df.groupby(["Name", "Mode"]).agg(
                Tong_Cau=("is_correct", "count"),
                Cau_Dung=("is_correct", "sum")
            ).reset_index()
            
            summary_df["Ty_Le_Dung_%"] = (summary_df["Cau_Dung"] / summary_df["Tong_Cau"] * 100).round(1)
            
            st.write("**Bảng xếp hạng thi đua (%)**")
            st.dataframe(
                summary_df[["Name", "Mode", "Ty_Le_Dung_%", "Cau_Dung", "Tong_Cau"]],
                column_config={
                    "Name": "Họ & Tên",
                    "Mode": "Dạng bài",
                    "Ty_Le_Dung_%": "Tỷ lệ đúng (%)",
                    "Cau_Dung": "Đúng",
                    "Tong_Cau": "Tổng"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.write("**Biểu đồ Tỷ lệ đúng (%)**")
            chart_data = summary_df.pivot(index="Name", columns="Mode", values="Ty_Le_Dung_%").fillna(0)
            chart_data.columns = [str(col).replace("➡️", "->") for col in chart_data.columns]
            st.bar_chart(chart_data)
    except Exception:
        st.write("Đang kết nối bảng xếp hạng...")
