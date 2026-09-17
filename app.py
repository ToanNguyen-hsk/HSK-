# -*- coding: utf-8 -*-
import streamlit as st
import random
import requests
import json
import time
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="App Ôn Tập Từ Vựng HSK - MSUTONG 1 & 2", layout="centered")

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyFGBMkcRyOK1z_Hw7KEd3zSnJvnKQGxn-6MUnMwFyC4StagIWtbWqQe5MqgPkkqDb4/exec"

st.markdown("""
    <style>
    section.main div[data-testid="stRadio"] label p {
        font-size: 26px !important; font-weight: 500 !important;
    }
    .online-container {
        display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 10px;
    }
    .avatar-circle {
        width: 32px; height: 32px; border-radius: 50%; background-color: #1E88E5; color: white;
        display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px;
        border: 2px solid #4CAF50;
    }
    .timer-box {
        font-size: 20px; font-weight: bold; color: #D32F2F; text-align: center;
        background-color: #FFEBEE; padding: 8px; border-radius: 8px; margin-bottom: 15px;
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

FALLBACK_LESSONS = [
    "Quyển 1 - Bài 1: 你好", "Quyển 1 - Bài 2: 你叫什么名字?", "Quyển 1 - Bài 3: 很高兴认识你",
    "Quyển 1 - Bài 4: 你去哪儿?", "Quyển 1 - Bài 5: 你要吃什么?", "Quyển 1 - Bài 6: 你在哪儿工作?",
    "Quyển 1 - Bài 7: 中国银行在哪儿?", "Quyển 1 - Bài 8: 你的生日是几月几号?", "Quyển 1 - Bài 9: 你喜欢中国电影还是美国电影?",
    "Quyển 1 - Bài 10: 你家有几口人?", "Quyển 2 - Bài 1: 你在听什么?", "Quyển 2 - Bài 2: 你平时几点起床?",
    "Quyển 2 - Bài 3: 可以用一下你的手机吗?", "Quyển 2 - Bài 4: 你想要哪件?", "Quyển 2 - Bài 5: 你这个周末什么时候有空儿?",
    "Quyển 2 - Bài 6: 上个周末你做什么了?", "Quyển 2 - Bài 7: 你是跟谁 festival一起去的?", "Quyển 2 - Bài 8: 你会做菜吗?",
    "Quyển 2 - Bài 9: 你见过熊猫吗?", "Quyển 2 - Bài 10: 给您添麻烦了!"
]

def fetch_data_from_google(action_name):
    try:
        # Bắt buộc cho phép theo Redirect 302 của Google Apps Script
        response = requests.get(
            GOOGLE_SHEET_URL,
            params={"action": action_name},
            allow_redirects=True,
            timeout=5.0
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=20)
def get_vocab_data():
    data = fetch_data_from_google("get_vocab")
    if isinstance(data, list) and len(data) > 0:
        return [i for i in data if isinstance(i, dict) and "char" in i]
    return []

@st.cache_data(ttl=20)
def get_sentences_data():
    data = fetch_data_from_google("get_sentences")
    if isinstance(data, list) and len(data) > 0:
        return [i for i in data if isinstance(i, dict) and "sentence" in i]
    return []

VOCAB_DATA = get_vocab_data()
SENTENCE_DATA = get_sentences_data()

extracted_lessons = sorted(list(set(
    [i.get("lesson", "").strip() for i in VOCAB_DATA if i.get("lesson")] + 
    [i.get("lesson", "").strip() for i in SENTENCE_DATA if i.get("lesson")]
)))

LESSON_LIST = extracted_lessons if extracted_lessons else FALLBACK_LESSONS

# --- SIDEBAR ---
st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

def update_online_status():
    if user_name and user_name.strip():
        try:
            requests.get(GOOGLE_SHEET_URL, params={"action": "ping_online", "name": user_name.strip()}, timeout=1.5)
            res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_online"}, timeout=1.5)
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
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=LESSON_LIST, default=LESSON_LIST)

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép câu hội thoại chuẩn")
)

time_per_question = st.sidebar.slider("⏱️ Thời gian mỗi câu (giây):", min_value=5, max_value=60, value=15)
start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# --- PHÒNG THI NHÓM ---
def get_public_rooms():
    try:
        res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_rooms"}, timeout=1.5).json()
        return res if isinstance(res, list) else []
    except Exception:
        return []

with st.sidebar.expander("🏆 Phòng Thi Đấu Trực Tuyến", expanded=True):
    st.caption("Khởi tạo hoặc gia nhập cuộc thi nhóm")
    host_mode = st.selectbox("Dạng bài thi:", ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 4: Ghép câu hội thoại chuẩn"])
    host_num_questions = st.number_input("Số lượng câu:", min_value=3, max_value=20, value=5)
    
    if st.button("➕ Tạo Phòng Thi"):
        h_name = user_name.strip() if user_name.strip() else "Ẩn danh"
        params = {
            "action": "create_room", "host": h_name, "lessons": json.dumps(selected_lessons),
            "mode": host_mode, "num_questions": host_num_questions
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
        st.caption("Chưa có phòng nào. Hãy nhấn nút 'Tạo Phòng Thi'!")
    else:
        for idx, rm in enumerate(rooms_list):
            if isinstance(rm, dict):
                r_id, r_host, r_mode, r_num = rm.get("roomId"), rm.get("host"), rm.get("mode"), rm.get("numQ")
                st.markdown(f"**📌 {r_id}** (Host: {r_host})")
                st.caption(f"{r_mode} | {r_num} câu")
                if st.button(f"🎮 Gia nhập {r_id}", key=f"join_{r_id}_{idx}"):
                    st.session_state.in_room_exam = True
                    st.session_state.room_info = rm
                    st.session_state.room_q_index = 0
                    st.session_state.room_score = 0
                    
                    pool = [x for x in VOCAB_DATA if x.get("lesson") in selected_lessons] if selected_lessons else VOCAB_DATA
                    questions_deck = []
                    selected_targets = random.sample(pool, min(int(r_num), len(pool))) if pool else []
                    for tgt in selected_targets:
                        wrong_opts = [x["pinyin"] for x in VOCAB_DATA if x.get("pinyin") != tgt["pinyin"]]
                        opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [tgt["pinyin"]]
                        random.shuffle(opts)
                        questions_deck.append({"target": tgt, "options": opts})
                    st.session_state.room_questions = questions_deck
                    st.rerun()

# --- XỬ LÝ LÀM BÀI ---
for k in ["score", "total", "q_id"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "start_time" not in st.session_state: st.session_state.start_time = time.time()

filtered_vocab = [i for i in VOCAB_DATA if i.get("lesson") in selected_lessons]
filtered_sentences = [i for i in SENTENCE_DATA if i.get("lesson") in selected_lessons]

def new_question():
    st.session_state.q_id += 1
    st.session_state.start_time = time.time()
    
    if "Dạng 4" in quiz_mode:
        pool = filtered_sentences if filtered_sentences else SENTENCE_DATA
        if not pool:
            st.session_state.question = None
            return
        target = random.choice(pool)
        raw_sentence = re.sub(r'[？！。，、“”]', '', target["sentence"])
        words = list(raw_sentence)
        shuffled_words = list(words)
        random.shuffle(shuffled_words)
        st.session_state.question = {
            "mode": 4, "meaning": target["meaning"], "correct_sentence": raw_sentence,
            "shuffled_words": shuffled_words, "full_target": target["sentence"]
        }
    else:
        pool = filtered_vocab if filtered_vocab else VOCAB_DATA
        if not pool:
            st.session_state.question = None
            return
        target = random.choice(pool)
        wrong_options = [item["pinyin"] for item in VOCAB_DATA if item.get("pinyin") != target["pinyin"]]
        options = random.sample(wrong_options, min(3, len(wrong_options))) + [target["pinyin"]]
        random.shuffle(options)
        st.session_state.question = {
            "mode": 1, "target": target, "options": options, "correct_ans": target["pinyin"]
        }

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
    st.info(f"🏆 **ĐANG THI NHÓM MULTIPLAYER** | Phòng: **{rm_info.get('roomId')}**")
    curr_idx = st.session_state.get("room_q_index", 0)
    total_q = int(rm_info.get("numQ", 5))
    questions = st.session_state.get("room_questions", [])
    
    if curr_idx >= total_q or not questions:
        st.balloons()
        st.success("🎉 CẢM ƠN BẠN ĐÃ HOÀN THÀNH CUỘC THI NHÓM!")
        st.write(f"📊 Điểm số: **{st.session_state.get('room_score', 0)} / {total_q}** câu đúng.")
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
            if ans == target["pinyin"]: st.session_state.room_score += 1
            st.session_state.room_q_index += 1
            st.rerun()
else:
    if not st.session_state.quiz_started:
        st.info("👈 Chọn bài học bên trái và bấm nút **🚀 Bắt đầu kiểm tra**!")
    elif st.session_state.get("question"):
        q = st.session_state.question
        
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, int(time_per_question - elapsed))
        
        st.markdown(f"<div class='timer-box'>⏱️ Thời gian còn lại: {remaining} giây</div>", unsafe_allow_html=True)
        
        if remaining <= 0:
            st.error("⏰ Hết thời gian làm câu này!")
            if st.button("Sang câu tiếp theo ➡️"):
                new_question()
                st.rerun()
        else:
            if q.get("mode") == 4:
                st.subheader("🧩 Bài Tập Ghép Câu Hội Thoại")
                st.markdown(f"### 💡 **Ý nghĩa:** `{q['meaning']}`")
                st.caption("Chọn lần lượt từng từ để xếp thành câu đúng:")
                user_selection = st.multiselect("Thứ tự câu ghép:", options=q["shuffled_words"], key=f"sent_{st.session_state.q_id}")
                
                if st.button("Nộp câu ghép ➡️"):
                    st.session_state.total += 1
                    user_ans = "".join(user_selection)
                    if user_ans == q["correct_sentence"]:
                        st.session_state.score += 1
                        st.success(f"🎉 Rất xuất sắc! Câu chuẩn: **{q['full_target']}**")
                        play_audio_js(q["full_target"])
                    else:
                        st.error(f"❌ Chưa đúng rồi! Đáp án chuẩn: **{q['full_target']}**")
            else:
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
