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
@st.cache_data(ttl=30)
def load_vocab_from_sheet():
    try:
        res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_vocab"}, timeout=3.0)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            valid_items = []
            for item in data:
                if isinstance(item, dict) and "char" in item and "pinyin" in item and "meaning" in item:
                    valid_items.append(item)
            return valid_items
    except Exception:
        pass
    return [
        {"char": "你好", "pinyin": "nǐ hǎo", "meaning": "xin chào", "lesson": "Quyển 1 - Bài 1: 你好 (Nǐ hǎo)"},
        {"char": "谢谢", "pinyin": "xièxie", "meaning": "cảm ơn", "lesson": "Quyển 1 - Bài 1: 你好 (Nǐ hǎo)"}
    ]

VOCAB_DATA = load_vocab_from_sheet()
LESSON_LIST = sorted(list(set(item.get("lesson", "") for item in VOCAB_DATA if isinstance(item, dict) and item.get("lesson"))))

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
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=LESSON_LIST, default=LESSON_LIST if LESSON_LIST else [])

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép từ tạo cụm/câu")
)

start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# Trạng thái Session
for k in ["score", "total", "q_id", "room_score"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "answered" not in st.session_state: st.session_state.answered = False
if "vocab_deck" not in st.session_state: st.session_state.vocab_deck = []

filtered_vocab = [item for item in VOCAB_DATA if isinstance(item, dict) and isinstance(selected_lessons, list) and item.get("lesson") in selected_lessons]

def new_question():
    st.session_state.answered = False
    st.session_state.q_id += 1
    if not filtered_vocab:
        st.session_state.question = None
        return

    if "Dạng 4" in quiz_mode:
        # Tự động tạo câu/cụm từ ghép từ 3-4 từ vựng trong các bài được chọn
        sample_size = min(random.randint(3, 4), len(filtered_vocab))
        selected_words = random.sample(filtered_vocab, sample_size)
        
        target_chars = [w["char"] for w in selected_words]
        target_meanings = [w["meaning"] for w in selected_words]
        
        shuffled_chars = list(target_chars)
        random.shuffle(shuffled_chars)
        
        st.session_state.question = {
            "mode": 4,
            "target_chars": target_chars,
            "shuffled_chars": shuffled_chars,
            "meanings": " / ".join(target_meanings),
            "correct_ans": "".join(target_chars)
        }
    else:
        target = random.choice(filtered_vocab)
        wrong_options = [item["pinyin"] for item in VOCAB_DATA if isinstance(item, dict) and item.get("pinyin") != target["pinyin"]]
        options = random.sample(wrong_options, min(3, len(wrong_options))) + [target["pinyin"]]
        random.shuffle(options)
        st.session_state.question = {
            "mode": 1,
            "target": target,
            "options": options,
            "correct_ans": target["pinyin"]
        }

if start_button:
    st.session_state.quiz_started = True
    st.session_state.score = 0
    st.session_state.total = 0
    new_question()
    st.rerun()

st.title("🎓 App Kiểm Tra Từ Vựng & Ngữ Pháp MSUTONG")

if not st.session_state.quiz_started:
    st.info("👈 Chọn bài học bên trái và bấm nút **🚀 Bắt đầu kiểm tra**!")
elif st.session_state.question:
    q = st.session_state.question
    
    if q.get("mode") == 4:
        st.subheader("🧩 Bài Tập Ghép Cụm Từ / Câu")
        st.write(f"**Gợi ý nghĩa các từ:** {q['meanings']}")
        st.caption("Hãy chọn thứ tự các từ để tạo thành dãy từ chuẩn:")
        
        user_sentence = st.multiselect("Ghép câu tại đây:", options=q["shuffled_chars"], key=f"sentence_{st.session_state.q_id}")
        
        if st.button("Nộp bài ghép câu ➡️"):
            st.session_state.total += 1
            ans_str = "".join(user_sentence)
            if ans_str == q["correct_ans"]:
                st.session_state.score += 1
                st.success("🎉 Ghép chính xác tuyệt đối!")
                play_audio_js(q["correct_ans"])
            else:
                st.error(f"❌ Chưa chính xác! Thứ tự chuẩn đúng là: **{q['correct_ans']}**")
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
