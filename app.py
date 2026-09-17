# -*- coding: utf-8 -*-
import streamlit as st
import random
import pandas as pd
import requests
import json
import time
import streamlit.components.v1 as components

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
        display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 10px;
    }
    .avatar-circle {
        width: 34px; height: 34px; border-radius: 50%; background-color: #1E88E5; color: white;
        display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px;
        border: 2px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

def play_audio_js(text):
    if not text: return
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    js_code = f"""
    <script>
        (function() {{
            try {{
                var synth = window.parent.speechSynthesis || window.speechSynthesis;
                if (synth) {{
                    synth.cancel();
                    var msg = new SpeechSynthesisUtterance("{clean_text}");
                    msg.lang = "zh-CN"; msg.rate = 0.85; synth.speak(msg);
                }}
            }} catch(e) {{}}
        }})();
    </script>
    """
    components.html(js_code, height=0, width=0)

# Load toàn bộ dữ liệu từ vựng từ Google Sheet
@st.cache_data(ttl=60)
def load_vocab_from_sheet():
    try:
        res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_vocab"}, timeout=3.0)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            return data
    except Exception:
        pass
    return []

VOCAB_DATA = load_vocab_from_sheet()

# Lấy danh sách tên bài học từ dữ liệu
LESSON_LIST = sorted(list(set(item["lesson"] for item in VOCAB_DATA if "lesson" in item))) if VOCAB_DATA else []

# Kho câu ghép
SENTENCE_DATA = [
    {"words": ["王", "老师", "您", "好"], "pinyin_words": ["Wáng", "lǎoshī", "nín", "hǎo"], "lesson": "Quyển 1 - Bài 1: 你好 (Nǐ hǎo)"},
    {"words": ["你", "叫", "什么", "名字"], "pinyin_words": ["Nǐ", "jiào", "shénme", "míngzi"], "lesson": "Quyển 1 - Bài 2: 你叫什么名字? (Nǐ jiào shénme míngzi?)"},
    {"words": ["请问", "您", "贵姓"], "pinyin_words": ["Qǐngwèn", "nín", "guìxìng"], "lesson": "Quyển 1 - Bài 3: 很高兴认识你 (Hěn gāoxìng rènshi nǐ)"},
    {"words": ["我", "去", "人民", "广场"], "pinyin_words": ["Wǒ", "qù", "Rénmín", "Guǎngchǎng"], "lesson": "Quyển 1 - Bài 4: 你去哪儿? (Nǐ qù nǎr?)"}
]

st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

def update_online_status():
    if user_name and user_name.strip():
        try:
            requests.get(GOOGLE_SHEET_URL, params={"action": "ping_online", "name": user_name.strip()}, timeout=1.0)
            res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_online"}, timeout=1.0)
            return res.json()
        except Exception:
            return [user_name.strip()]
    return []

active_users = update_online_status()

st.sidebar.markdown("### 🟢 Đang Online")
if active_users:
    avatar_html = "<div class='online-container'>"
    for u in active_users:
        initial = u[0].upper() if u else "U"
        avatar_html += f"<div class='avatar-circle' title='{u}'>{initial}</div>"
    avatar_html += "</div>"
    st.sidebar.markdown(avatar_html, unsafe_allow_html=True)

st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=LESSON_LIST, default=LESSON_LIST[:1] if LESSON_LIST else [])

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Tất cả (Ngẫu nhiên)", "Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép nối câu từ Hán & Pinyin")
)

start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

def get_public_rooms():
    try:
        res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_rooms"}, timeout=1.5).json()
        return res if isinstance(res, list) else []
    except Exception:
        return []

with st.sidebar.expander("🏆 Phòng Thi Đấu Trực Tuyến", expanded=True):
    st.caption("Khởi tạo hoặc gia nhập cuộc thi nhỏ")
    host_mode = st.selectbox("Dạng bài thi:", ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"])
    host_num_questions = st.number_input("Số lượng câu:", min_value=3, max_value=50, value=5)
    host_time_limit = st.number_input("Thời gian (Phút):", min_value=1, max_value=60, value=3)
    
    if st.button("➕ Tạo Phòng Thi"):
        h_name = user_name.strip() if user_name.strip() else "Ẩn danh"
        params = {
            "action": "create_room", "host": h_name, "lessons": json.dumps(selected_lessons),
            "mode": host_mode, "num_questions": host_num_questions, "time_limit": host_time_limit
        }
        try:
            requests.get(GOOGLE_SHEET_URL, params=params, timeout=1.5)
            st.success("🎉 Tạo phòng thành công!")
            time.sleep(0.3)
            st.rerun()
        except Exception:
            st.info("Đã gửi yêu cầu tạo phòng!")

    st.write("---")
    st.markdown("**Danh Sách Phòng Hiện Có:**")
    rooms_list = get_public_rooms()
    if not rooms_list:
        st.caption("Chưa có phòng nào. Nhấn 'Tạo Phòng Thi' ở trên!")
    else:
        for idx, rm in enumerate(rooms_list):
            if isinstance(rm, dict):
                r_id, r_host, r_mode, r_num, r_time = rm.get("roomId"), rm.get("host"), rm.get("mode"), rm.get("numQ"), rm.get("timeLimit")
                st.markdown(f"**📌 {r_id}** (Host: {r_host})")
                st.caption(f"{r_mode} | {r_num} câu | {r_time} phút")
                if st.button(f"🎮 Gia nhập {r_id}", key=f"join_{r_id}_{idx}"):
                    st.session_state.in_room_exam = True
                    st.session_state.room_info = rm
                    st.session_state.room_q_index = 0
                    st.session_state.room_score = 0
                    st.session_state.room_history = []
                    st.session_state.room_start_time = time.time()
                    
                    pool = [x for x in VOCAB_DATA if x["lesson"] in selected_lessons] if selected_lessons else VOCAB_DATA
                    questions_deck = []
                    selected_targets = random.sample(pool, min(int(r_num), len(pool))) if pool else []
                    for tgt in selected_targets:
                        wrong_opts = [x["pinyin"] for x in VOCAB_DATA if x["pinyin"] != tgt["pinyin"]]
                        opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [tgt["pinyin"]]
                        random.shuffle(opts)
                        questions_deck.append({"target": tgt, "options": opts})
                    st.session_state.room_questions = questions_deck
                    st.rerun()

# Trạng thái Session
for k in ["score", "total", "q_id", "room_score"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "answered" not in st.session_state: st.session_state.answered = False
if "vocab_deck" not in st.session_state: st.session_state.vocab_deck = []

filtered_vocab = [item for item in VOCAB_DATA if item["lesson"] in selected_lessons]

def new_question():
    st.session_state.answered = False
    st.session_state.q_id += 1
    if not filtered_vocab:
        st.session_state.question = None
        return
    if not st.session_state.vocab_deck:
        st.session_state.vocab_deck = list(filtered_vocab)
        random.shuffle(st.session_state.vocab_deck)
    target = st.session_state.vocab_deck.pop()
    wrong_options = [item["pinyin"] for item in VOCAB_DATA if item["pinyin"] != target["pinyin"]]
    options = random.sample(wrong_options, min(3, len(wrong_options))) + [target["pinyin"]]
    random.shuffle(options)
    st.session_state.question = {"target": target, "options": options, "correct_ans": target["pinyin"]}

if start_button:
    st.session_state.quiz_started = True
    st.session_state.in_room_exam = False
    st.session_state.score = 0
    st.session_state.total = 0
    new_question()
    st.rerun()

st.title("🎓 App Kiểm Tra Từ Vựng & Ngữ Pháp MSUTONG")

if st.session_state.get("in_room_exam", False):
    rm_info = st.session_state.get("room_info", {})
    st.info(f"🏆 **ĐANG THI MULTIPLAYER** | Phòng: **{rm_info.get('roomId')}**")
    curr_idx = st.session_state.get("room_q_index", 0)
    total_q = int(rm_info.get("numQ", 5))
    questions = st.session_state.get("room_questions", [])
    
    if curr_idx >= total_q or not questions:
        st.balloons()
        st.success("🎉 CẢM ƠN BẠN ĐÃ HOÀN THÀNH CUỘC THI!")
        st.write(f"📊 Điểm số: **{st.session_state.get('room_score', 0)} / {total_q}** câu đúng.")
        st.markdown("### 📝 Bảng Review Đáp Án")
        for i, item in enumerate(st.session_state.get("room_history", [])):
            icon = "✅ Đúng" if item["is_correct"] else "❌ Sai"
            st.markdown(f"**Câu {i+1}:** **{item['char']}** ({item['meaning']}) | Chọn: `{item['user_ans']}` | Đúng: **`{item['correct_ans']}`** ➡️ {icon}")
        if st.button("🚪 Trở Về Trang Chủ"):
            st.session_state.in_room_exam = False
            st.rerun()
    else:
        st.subheader(f"Câu {curr_idx + 1}/{total_q}:")
        q_item = questions[curr_idx]
        target, options = q_item["target"], q_item["options"]
        st.markdown(f"<h1 style='text-align: center; font-size: 90px; color: #1E88E5;'>{target['char']}</h1>", unsafe_allow_html=True)
        play_audio_js(target['char'])
        ans = st.radio("Chọn phiên âm đúng:", options, key=f"rm_ans_{curr_idx}")
        if st.button("Nộp câu này ➡️", key=f"rm_sub_{curr_idx}"):
            is_corr = (ans == target["pinyin"])
            if is_corr: st.session_state.room_score += 1
            st.session_state.room_history.append({"char": target["char"], "meaning": target["meaning"], "correct_ans": target["pinyin"], "user_ans": ans, "is_correct": is_corr})
            st.session_state.room_q_index += 1
            st.rerun()
else:
    if not st.session_state.quiz_started:
        st.info("👈 Chọn bài học bên trái và bấm nút **🚀 Bắt đầu kiểm tra**!")
    elif st.session_state.question:
        q = st.session_state.question
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #1E88E5;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
        play_audio_js(q['target']['char'])
        user_choice = st.radio("Chọn Pinyin:", q["options"], key=f"radio_{st.session_state.q_id}")
        if st.button("Nộp bài ➡️"):
            st.session_state.total += 1
            if user_choice == q["correct_ans"]:
                st.session_state.score += 1
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng: **{q['correct_ans']}** ({q['target']['meaning']})")
        if st.button("Câu tiếp theo ➡️"):
            new_question()
            st.rerun()
