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

# Danh sách bài học tiêu chuẩn phục vụ chọn tĩnh mượt mà
DEFAULT_LESSONS = [
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
        response = requests.get(
            GOOGLE_SHEET_URL,
            params={"action": action_name},
            allow_redirects=True,
            timeout=4.0
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

# --- FORM CẤU HÌNH TẠI THANH BEN TRÁI (KHÔNG RELOAD TRANG KHI CHỌN) ---
with st.sidebar.form("config_form"):
    st.title("👤 Thông Tin Người Làm")
    user_name = st.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

    st.title("⚙️ Tùy Chỉnh Bài Học")
    selected_lessons = st.multiselect("Lựa chọn bài kiểm tra:", options=DEFAULT_LESSONS, default=DEFAULT_LESSONS)

    st.title("🎯 Dạng Bài Tập")
    quiz_mode = st.radio(
        "Chọn dạng bài kiểm tra:",
        ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép câu hội thoại chuẩn")
    )

    time_per_question = st.slider("⏱️ Thời gian mỗi câu (giây):", min_value=5, max_value=60, value=15)
    
    # Nút submit Form duy nhất
    start_button = st.form_submit_button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# Khởi tạo session state
for k in ["score", "total", "q_id"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "start_time" not in st.session_state: st.session_state.start_time = time.time()
if "vocab_data" not in st.session_state: st.session_state.vocab_data = []
if "sentence_data" not in st.session_state: st.session_state.sentence_data = []

def clean_lesson_title(t):
    return str(t).strip() if t else ""

def new_question(mode_choice, lessons_choice):
    st.session_state.q_id += 1
    st.session_state.start_time = time.time()
    
    vocab_pool = [i for i in st.session_state.vocab_data if clean_lesson_title(i.get("lesson")) in lessons_choice]
    sent_pool = [i for i in st.session_state.sentence_data if clean_lesson_title(i.get("lesson")) in lessons_choice]
    
    if "Dạng 4" in mode_choice:
        pool = sent_pool if sent_pool else st.session_state.sentence_data
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
        pool = vocab_pool if vocab_pool else st.session_state.vocab_data
        if not pool:
            st.session_state.question = None
            return
        target = random.choice(pool)
        wrong_options = [item["pinyin"] for item in st.session_state.vocab_data if item.get("pinyin") != target["pinyin"]]
        options = random.sample(wrong_options, min(3, len(wrong_options))) + [target["pinyin"]]
        random.shuffle(options)
        st.session_state.question = {
            "mode": 1, "target": target, "options": options, "correct_ans": target["pinyin"]
        }

# BẮT ĐẦU KIỂM TRA: CHỈ KHI BẤM NÚT MỚI TẢI DỮ LIỆU
if start_button:
    with st.spinner("⏳ Đang tải cơ sở dữ liệu từ Google Sheet..."):
        st.session_state.vocab_data = fetch_data_from_google("get_vocab")
        st.session_state.sentence_data = fetch_data_from_google("get_sentences")
        
        # Cập nhật Online status
        if user_name and user_name.strip():
            try:
                requests.get(GOOGLE_SHEET_URL, params={"action": "ping_online", "name": user_name.strip()}, timeout=1.0)
            except Exception:
                pass
                
    st.session_state.quiz_started = True
    st.session_state.active_mode = quiz_mode
    st.session_state.active_lessons = selected_lessons
    st.session_state.active_timer = time_per_question
    st.session_state.score = 0
    st.session_state.total = 0
    
    new_question(quiz_mode, selected_lessons)
    st.rerun()

st.title("🎓 App Kiểm Tra Từ Vựng & Ngữ Pháp MSUTONG")

# GIAO DIỆN HIỂN THỊ CÂU HỎI
if not st.session_state.quiz_started:
    st.info("👈 Điền thông tin, tùy chỉnh tùy chọn bên thanh bên trái và bấm nút **🚀 Bắt đầu kiểm tra**!")
elif st.session_state.get("question"):
    q = st.session_state.question
    
    # Tính thời gian đếm ngược
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
elif st.session_state.quiz_started:
    st.warning("⚠️ Không tìm thấy từ vựng hay câu hội thoại thuộc bài học đã chọn trên Google Sheet!")
    if st.button("Quay lại chọn lại"):
        st.session_state.quiz_started = False
        st.rerun()
