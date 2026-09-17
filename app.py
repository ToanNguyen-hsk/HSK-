# -*- coding: utf-8 -*-
import streamlit as st
import random
import requests
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="App Ôn Tập Từ Vựng HSK - MSUTONG 1 & 2", layout="centered")

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyFGBMkcRyOK1z_Hw7KEd3zSnJvnKQGxn-6MUnMwFyC4StagIWtbWqQe5MqgPkkqDb4/exec"

st.markdown("""
    <style>
    section.main div[data-testid="stRadio"] label p {
        font-size: 26px !important; font-weight: 500 !important;
    }
    .stMultiSelect [data-baseweb="select"] {
        border-radius: 8px;
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

# Chuẩn hóa tên bài học để không bị lệch dấu/khoảng trắng
def clean_lesson_title(title):
    if not title: return ""
    return str(title).strip()

@st.cache_data(ttl=15)
def load_vocab_from_sheet():
    try:
        res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_vocab"}, timeout=4.0)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            return [{"char": i.get("char"), "pinyin": i.get("pinyin"), "meaning": i.get("meaning"), "lesson": clean_lesson_title(i.get("lesson"))} 
                    for i in data if isinstance(i, dict) and i.get("char")]
    except Exception:
        pass
    return []

@st.cache_data(ttl=15)
def load_sentences_from_sheet():
    try:
        res = requests.get(GOOGLE_SHEET_URL, params={"action": "get_sentences"}, timeout=4.0)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            return [{"sentence": i.get("sentence"), "meaning": i.get("meaning"), "lesson": clean_lesson_title(i.get("lesson"))} 
                    for i in data if isinstance(i, dict) and i.get("sentence")]
    except Exception:
        pass
    return []

VOCAB_DATA = load_vocab_from_sheet()
SENTENCE_DATA = load_sentences_from_sheet()

# Lấy danh sách bài học duy nhất từ cả 2 nguồn
raw_lessons = list(set(
    [i["lesson"] for i in VOCAB_DATA if i.get("lesson")] + 
    [i["lesson"] for i in SENTENCE_DATA if i.get("lesson")]
))

LESSON_LIST = sorted(raw_lessons)

st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
if LESSON_LIST:
    selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=LESSON_LIST, default=LESSON_LIST)
else:
    st.sidebar.warning("⚠️ Đang kết nối Google Sheet...")
    selected_lessons = []

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép câu hội thoại chuẩn")
)

start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

for k in ["score", "total", "q_id"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False

filtered_vocab = [i for i in VOCAB_DATA if i.get("lesson") in selected_lessons]
filtered_sentences = [i for i in SENTENCE_DATA if i.get("lesson") in selected_lessons]

def new_question():
    st.session_state.q_id += 1
    
    if "Dạng 4" in quiz_mode:
        pool = filtered_sentences if filtered_sentences else SENTENCE_DATA
        if not pool:
            st.session_state.question = None
            return
        target = random.choice(pool)
        
        # Làm sạch các dấu câu tiếng Trung để cắt chữ
        raw_sentence = re.sub(r'[？！。，、“”]', '', target["sentence"])
        words = list(raw_sentence)
        shuffled_words = list(words)
        random.shuffle(shuffled_words)
        
        st.session_state.question = {
            "mode": 4,
            "meaning": target["meaning"],
            "correct_sentence": raw_sentence,
            "shuffled_words": shuffled_words,
            "full_target": target["sentence"]
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
elif st.session_state.get("question"):
    q = st.session_state.question
    
    if q.get("mode") == 4:
        st.subheader("🧩 Bài Tập Ghép Câu Hội Thoại Thực Tế")
        st.markdown(f"### 💡 **Ý nghĩa:** `{q['meaning']}`")
        st.caption("Chọn lần lượt từng từ/chữ dưới đây để xếp thành câu đúng:")
        
        user_selection = st.multiselect("Thứ tự câu ghép của bạn:", options=q["shuffled_words"], key=f"sentence_select_{st.session_state.q_id}")
        
        if st.button("Nộp câu ghép ➡️"):
            st.session_state.total += 1
            user_ans = "".join(user_selection)
            if user_ans == q["correct_sentence"]:
                st.session_state.score += 1
                st.success(f"🎉 Xuất sắc! Câu hoàn chỉnh: **{q['full_target']}**")
                play_audio_js(q["full_target"])
            else:
                st.error(f"❌ Chưa chính xác! Đáp án đúng: **{q['full_target']}**")
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
