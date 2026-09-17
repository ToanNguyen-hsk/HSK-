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

def fetch_data_from_google(action_name):
    try:
        response = requests.get(
            GOOGLE_SHEET_URL,
            params={"action": action_name},
            allow_redirects=True,
            timeout=5.0
        )
        if response.status_code == 200:
            res = response.json()
            if isinstance(res, list):
                return [item for item in res if isinstance(item, dict)]
    except Exception:
        pass
    return []

# Thuật toán trích xuất số quyển và số bài để so sánh lỏng thông minh
def extract_book_and_lesson(text):
    if not text: return ("", "")
    s = str(text).lower()
    
    # Xác định Quyển 1 hay Quyển 2
    book = "q1" if ("1" in s or "quyển 1" in s or "quyen 1" in s) else ("q2" if ("2" in s or "quyển 2" in s or "quyen 2" in s) else "")
    
    # Tìm số bài (ví dụ: Bài 5 -> 5)
    match = re.search(r'(?:bài|lesson|b|l)\s*(\d+)', s)
    lesson_num = match.group(1) if match else ""
    
    if not lesson_num:
        digits = re.findall(r'\d+', s)
        if digits:
            lesson_num = digits[-1]
            
    return (book, lesson_num)

# Tải dữ liệu ban đầu
if "vocab_data" not in st.session_state or not st.session_state.vocab_data:
    st.session_state.vocab_data = fetch_data_from_google("get_vocab")
if "sentence_data" not in st.session_state or not st.session_state.sentence_data:
    st.session_state.sentence_data = fetch_data_from_google("get_sentences")

# Tạo danh sách bài học động
raw_lessons = set()
for item in st.session_state.vocab_data:
    if item.get("lesson"): raw_lessons.add(str(item.get("lesson")).strip())
for item in st.session_state.sentence_data:
    if item.get("lesson"): raw_lessons.add(str(item.get("lesson")).strip())

DYNAMIC_LESSONS = sorted(list(raw_lessons)) if raw_lessons else [
    "Quyển 1 - Bài 1: 你好", "Quyển 1 - Bài 2: 你叫什么名字?", "Quyển 1 - Bài 3: 很高兴认识你",
    "Quyển 1 - Bài 4: 你去哪儿?", "Quyển 1 - Bài 5: 你要吃什么?", "Quyển 1 - Bài 6: 你在哪儿工作?",
    "Quyển 1 - Bài 7: 中国银行在哪儿?", "Quyển 1 - Bài 8: 你的生日是几月几号?", "Quyển 1 - Bài 9: 你喜欢中国电影还是美国电影?",
    "Quyển 1 - Bài 10: 你家有几口人?", "Quyển 2 - Bài 1: 你在听什么?", "Quyển 2 - Bài 2: 你平时几点起床?",
    "Quyển 2 - Bài 3: 可以用一下你的手机吗?", "Quyển 2 - Bài 4: 你想要哪件?", "Quyển 2 - Bài 5: 你这个周末什么时候有空儿?",
    "Quyển 2 - Bài 6: 上个周末你做什么了?", "Quyển 2 - Bài 7: 你是跟谁 festival一起去的?", "Quyển 2 - Bài 8: 你会做菜吗?",
    "Quyển 2 - Bài 9: 你见过熊猫吗?", "Quyển 2 - Bài 10: 给您添麻烦了!"
]

# Khởi tạo state
for k in ["score", "total", "q_id"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "start_time" not in st.session_state: st.session_state.start_time = time.time()

# --- 1. THANH BÊN CẤU HÌNH CÁ NHÂN ---
st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=DYNAMIC_LESSONS, default=DYNAMIC_LESSONS)

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép câu hội thoại chuẩn")
)

time_per_question = st.sidebar.slider("⏱️ Thời gian mỗi câu (giây):", min_value=5, max_value=60, value=15)
start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# --- 2. KHU VỰC PHÒNG THI NHÓM (TRỰC TUYẾN) ---
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
                    
                    pool = st.session_state.vocab_data
                    questions_deck = []
                    selected_targets = random.sample(pool, min(int(r_num), len(pool))) if pool else []
                    for tgt in selected_targets:
                        wrong_opts = [x.get("pinyin") for x in pool if x.get("pinyin") != tgt.get("pinyin")]
                        opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [tgt.get("pinyin")]
                        random.shuffle(opts)
                        questions_deck.append({"target": tgt, "options": opts})
                    st.session_state.room_questions = questions_deck
                    st.rerun()

# Hàm kiểm tra trùng khớp bài học thông minh
def is_lesson_match(item_lesson, selected_lessons_list):
    item_bk, item_ls = extract_book_and_lesson(item_lesson)
    for sel in selected_lessons_list:
        sel_bk, sel_ls = extract_book_and_lesson(sel)
        # Nếu trùng cả số quyển và số bài
        if item_ls and sel_ls and item_ls == sel_ls:
            if not item_bk or not sel_bk or item_bk == sel_bk:
                return True
        # Hoặc trùng chuỗi gốc
        if str(item_lesson).strip() in str(sel).strip() or str(sel).strip() in str(item_lesson).strip():
            return True
    return False

def new_question(mode_choice, lessons_choice):
    st.session_state.q_id += 1
    st.session_state.start_time = time.time()
    
    vocab_pool = [i for i in st.session_state.vocab_data if is_lesson_match(i.get("lesson"), lessons_choice)]
    sent_pool = [i for i in st.session_state.sentence_data if is_lesson_match(i.get("lesson"), lessons_choice)]
    
    # Fallback nếu không lọc được bài cụ thể
    if not vocab_pool: vocab_pool = st.session_state.vocab_data
    if not sent_pool: sent_pool = st.session_state.sentence_data

    if "Dạng 4" in mode_choice:
        pool = sent_pool if sent_pool else st.session_state.sentence_data
        if not pool:
            st.session_state.question = None
            return
        target = random.choice(pool)
        raw_sentence = re.sub(r'[？！。，、“”]', '', str(target.get("sentence", "")))
        words = list(raw_sentence)
        shuffled_words = list(words)
        random.shuffle(shuffled_words)
        st.session_state.question = {
            "mode": 4, "meaning": target.get("meaning", ""), "correct_sentence": raw_sentence,
            "shuffled_words": shuffled_words, "full_target": target.get("sentence", "")
        }
    else:
        pool = vocab_pool if vocab_pool else st.session_state.vocab_data
        if not pool:
            st.session_state.question = None
            return
        target = random.choice(pool)
        wrong_options = [item.get("pinyin") for item in st.session_state.vocab_data if item.get("pinyin") != target.get("pinyin")]
        options = random.sample(wrong_options, min(3, len(wrong_options))) + [target.get("pinyin")]
        random.shuffle(options)
        st.session_state.question = {
            "mode": 1, "target": target, "options": options, "correct_ans": target.get("pinyin")
        }

if start_button:
    st.session_state.vocab_data = fetch_data_from_google("get_vocab")
    st.session_state.sentence_data = fetch_data_from_google("get_sentences")
    
    st.session_state.quiz_started = True
    st.session_state.in_room_exam = False
    st.session_state.active_mode = quiz_mode
    st.session_state.active_lessons = selected_lessons
    st.session_state.active_timer = time_per_question
    st.session_state.score = 0
    st.session_state.total = 0
    
    new_question(quiz_mode, selected_lessons)
    st.rerun()

st.title("🎓 App Kiểm Tra Từ Vựng & Ngữ Pháp MSUTONG")

# --- GIAO DIỆN LÀM BÀI ---
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
        st.markdown(f"<h1 style='text-align: center; font-size: 90px; color: #1E88E5;'>{target.get('char')}</h1>", unsafe_allow_html=True)
        play_audio_js(target.get('char'))
        ans = st.radio("Chọn phiên âm đúng:", options, key=f"rm_ans_{curr_idx}")
        if st.button("Nộp câu này ➡️", key=f"rm_sub_{curr_idx}"):
            if ans == target.get("pinyin"): st.session_state.room_score += 1
            st.session_state.room_q_index += 1
            st.rerun()
else:
    if not st.session_state.quiz_started:
        st.info("👈 Điền thông tin, chọn bài kiểm tra ở thanh bên trái và bấm **🚀 Bắt đầu kiểm tra**!")
    elif st.session_state.get("question"):
        q = st.session_state.question
        
        elapsed = time.time() - st.session_state.start_time
        timer_limit = st.session_state.get("active_timer", 15)
        remaining = max(0, int(timer_limit - elapsed))
        
        st.markdown(f"<div class='timer-box'>⏱️ Thời gian còn lại: {remaining} giây</div>", unsafe_allow_html=True)
        
        if remaining <= 0:
            st.error("⏰ Hết thời gian làm câu này!")
            if st.button("Sang câu tiếp theo ➡️"):
                new_question(st.session_state.active_mode, st.session_state.active_lessons)
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
                new_question(st.session_state.active_mode, st.session_state.active_lessons)
                st.rerun()
