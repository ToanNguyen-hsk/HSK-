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
    div[data-testid="stRadio"] > div { gap: 15px; }
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

# Hàm lấy dữ liệu trực tiếp từ Google Sheet (Có bộ nhớ đệm cache 10 phút để cực nhanh sau lần tải đầu)
@st.cache_data(ttl=600)
def fetch_data_from_google(action_name):
    try:
        response = requests.get(
            GOOGLE_SHEET_URL,
            params={"action": action_name},
            allow_redirects=True,
            timeout=10.0 # Nới lỏng thời gian chờ Google Sheet phản hồi
        )
        if response.status_code == 200:
            res = response.json()
            if isinstance(res, list) and len(res) > 0:
                return [item for item in res if isinstance(item, dict)]
    except Exception as e:
        print(f"Fetch error ({action_name}): {e}")
    return []

# Tải trước dữ liệu ngay khi mở app
if "vocab_data" not in st.session_state:
    st.session_state.vocab_data = fetch_data_from_google("get_vocab")
if "sentence_data" not in st.session_state:
    st.session_state.sentence_data = fetch_data_from_google("get_sentences")

# Làm sạch chuỗi bài học để so sánh chính xác 100%
def clean_key(s):
    if not s: return ""
    return re.sub(r'[^\w\s]', '', str(s)).replace(" ", "").lower()

# Khởi tạo danh sách bài học động từ Google Sheet
raw_lessons = set()
for item in st.session_state.vocab_data:
    if item.get("lesson"): raw_lessons.add(str(item.get("lesson")).strip())
for item in st.session_state.sentence_data:
    if item.get("lesson"): raw_lessons.add(str(item.get("lesson")).strip())

DYNAMIC_LESSONS = sorted(list(raw_lessons)) if raw_lessons else [
    "Quyển 1 - Bài 1: 你好", "Quyển 1 - Bài 2: 你叫什么名字?", "Quyển 1 - Bài 3: 很高兴认识你",
    "Quyển 1 - Bài 4: 你去哪儿?", "Quyển 1 - Bài 5: 你要吃什么?"
]

# State Khởi tạo
for k in ["score", "total", "q_id"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "start_time" not in st.session_state: st.session_state.start_time = time.time()
if "local_rooms" not in st.session_state: st.session_state.local_rooms = []

# --- 1. THANH BÊN CẤU HÌNH CÁ NHÂN ---
st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=DYNAMIC_LESSONS, default=DYNAMIC_LESSONS[:5] if DYNAMIC_LESSONS else [])

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép câu hội thoại chuẩn")
)

time_per_question = st.sidebar.slider("⏱️ Thời gian mỗi câu (giây):", min_value=5, max_value=60, value=15)
start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# --- 2. PHÒNG THI NHÓM MULTIPLAYER ---
with st.sidebar.expander("🏆 Phòng Thi Đấu Trực Tuyến", expanded=False):
    st.caption("Khởi tạo hoặc gia nhập cuộc thi nhóm")
    host_mode = st.selectbox("Dạng bài thi:", ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 4: Ghép câu hội thoại chuẩn"])
    host_num_questions = st.number_input("Số lượng câu:", min_value=3, max_value=20, value=5)
    
    if st.button("➕ Tạo Phòng Thi"):
        h_name = user_name.strip() if user_name.strip() else "Ẩn danh"
        new_room_id = f"ROOM_{random.randint(1000, 9999)}"
        new_rm = {
            "roomId": new_room_id,
            "host": h_name,
            "mode": host_mode,
            "numQ": host_num_questions
        }
        st.session_state.local_rooms.insert(0, new_rm)
        try:
            params = {"action": "create_room", "host": h_name, "lessons": json.dumps(selected_lessons), "mode": host_mode, "num_questions": host_num_questions}
            requests.get(GOOGLE_SHEET_URL, params=params, timeout=1.0)
        except Exception:
            pass
        st.success(f"🎉 Đã tạo {new_room_id} thành công!")
        time.sleep(0.5)
        st.rerun()

    st.write("---")
    st.markdown("**Danh Sách Phòng Hiện Có:**")
    try:
        remote_rooms = requests.get(GOOGLE_SHEET_URL, params={"action": "get_rooms"}, timeout=2.0).json()
    except:
        remote_rooms = []
        
    all_rooms = st.session_state.local_rooms + [r for r in remote_rooms if r.get("roomId") not in [x.get("roomId") for x in st.session_state.local_rooms]]
    
    if not all_rooms:
        st.caption("Chưa có phòng nào. Hãy nhấn nút 'Tạo Phòng Thi'!")
    else:
        for idx, rm in enumerate(all_rooms):
            r_id = rm.get("roomId", f"ROOM_{idx}")
            st.markdown(f"**📌 {r_id}** (Host: {rm.get('host', 'Ẩn danh')})")
            st.caption(f"{rm.get('mode', 'Dạng 1')} | {rm.get('numQ', 5)} câu")
            
            if st.button(f"🎮 Gia nhập {r_id}", key=f"btn_join_{r_id}_{idx}"):
                st.session_state.in_room_exam = True
                st.session_state.room_info = rm
                st.session_state.room_q_index = 0
                st.session_state.room_score = 0
                
                # Tải lại dữ liệu nếu trống
                if not st.session_state.vocab_data:
                    st.session_state.vocab_data = fetch_data_from_google("get_vocab")
                
                pool = st.session_state.vocab_data
                questions_deck = []
                num_q = int(rm.get("numQ", 5))
                selected_targets = random.sample(pool, min(num_q, len(pool))) if pool else []
                for tgt in selected_targets:
                    wrong_opts = [x.get("pinyin") for x in pool if x.get("pinyin") != tgt.get("pinyin")]
                    opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [tgt.get("pinyin")]
                    random.shuffle(opts)
                    questions_deck.append({"target": tgt, "options": opts})
                st.session_state.room_questions = questions_deck
                st.rerun()

# HÀM TẠO CÂU HỎI MỚI TỪ GOOGLE SHEET
def new_question(mode_choice, lessons_choice):
    st.session_state.q_id += 1
    st.session_state.start_time = time.time()
    
    normalized_selected = [clean_key(x) for x in lessons_choice]
    
    vocab_pool = [i for i in st.session_state.vocab_data if clean_key(i.get("lesson")) in normalized_selected]
    sent_pool = [i for i in st.session_state.sentence_data if clean_key(i.get("lesson")) in normalized_selected]
    
    # Fallback nếu lọc bị rỗng (do lỗi đặt tên)
    if not vocab_pool: vocab_pool = st.session_state.vocab_data
    if not sent_pool: sent_pool = st.session_state.sentence_data

    if "Dạng 4" in mode_choice:
        if not sent_pool:
            st.session_state.question = None
            return
        target = random.choice(sent_pool)
        raw_sentence = re.sub(r'[？！。，、“”]', '', str(target.get("sentence", "")))
        words = list(raw_sentence)
        shuffled_words = list(words)
        random.shuffle(shuffled_words)
        st.session_state.question = {
            "mode": 4, "meaning": target.get("meaning", ""), "correct_sentence": raw_sentence,
            "shuffled_words": shuffled_words, "full_target": target.get("sentence", "")
        }
    else:
        if not vocab_pool:
            st.session_state.question = None
            return
        target = random.choice(vocab_pool)
        
        if "Dạng 1" in mode_choice:
            wrong_opts = [item.get("pinyin") for item in st.session_state.vocab_data if item.get("pinyin") != target.get("pinyin")]
            opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [target.get("pinyin")]
            random.shuffle(opts)
            st.session_state.question = {"mode": 1, "target": target, "options": opts, "correct_ans": target.get("pinyin")}
            
        elif "Dạng 2" in mode_choice:
            wrong_opts = [item.get("char") for item in st.session_state.vocab_data if item.get("char") != target.get("char")]
            opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [target.get("char")]
            random.shuffle(opts)
            st.session_state.question = {"mode": 2, "target": target, "options": opts, "correct_ans": target.get("char")}
            
        elif "Dạng 3" in mode_choice:
            wrong_opts = [item.get("meaning") for item in st.session_state.vocab_data if item.get("meaning") != target.get("meaning")]
            opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [target.get("meaning")]
            random.shuffle(opts)
            st.session_state.question = {"mode": 3, "target": target, "options": opts, "correct_ans": target.get("meaning")}

if start_button:
    with st.spinner("⏳ Đang tải cơ sở dữ liệu từ Google Sheet..."):
        st.session_state.vocab_data = fetch_data_from_google("get_vocab")
        st.session_state.sentence_data = fetch_data_from_google("get_sentences")
        
    if not st.session_state.vocab_data:
        st.error("⚠️ Không thể tải dữ liệu từ Google Sheet. Vui lòng kiểm tra lại link Google Apps Script hoặc thử lại sau.")
    else:
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

# --- GIAO DIỆN LÀM BÀI PHÒNG THI NHÓM ---
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
        
        # CHẤM ĐIỂM TỰ ĐỘNG THI NHÓM
        ans = st.radio("Chọn phiên âm đúng:", options, index=None, key=f"rm_ans_{curr_idx}")
        if ans is not None:
            if ans == target.get("pinyin"): 
                st.session_state.room_score += 1
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng: **{target.get('pinyin')}**")
                
            if st.button("Câu tiếp theo ➡️"):
                st.session_state.room_q_index += 1
                st.rerun()

# --- GIAO DIỆN LÀM BÀI CÁ NHÂN ---
elif not st.session_state.quiz_started:
    st.info("👈 Chọn bài kiểm tra ở thanh bên trái và bấm **🚀 Bắt đầu kiểm tra**!")

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
        # DẠNG 4: GHÉP CÂU
        if q.get("mode") == 4:
            st.subheader("🧩 Bài Tập Ghép Câu Hội Thoại")
            st.markdown(f"### 💡 **Ý nghĩa:** `{q['meaning']}`")
            st.caption("Chọn lần lượt từng từ để xếp thành câu đúng:")
            
            user_selection = st.multiselect("Thứ tự câu ghép:", options=q["shuffled_words"], key=f"sent_{st.session_state.q_id}")
            
            # TỰ ĐỘNG CHẤM KHI CHỌN ĐỦ KÝ TỰ (Không cần nút Nộp)
            if len(user_selection) == len(q["correct_sentence"]):
                score_flag_key = f"scored_{st.session_state.q_id}"
                if score_flag_key not in st.session_state:
                    st.session_state.total += 1
                    user_ans = "".join(user_selection)
                    if user_ans == q["correct_sentence"]:
                        st.session_state.score += 1
                        st.session_state[score_flag_key] = True
                    else:
                        st.session_state[score_flag_key] = False

                if st.session_state[score_flag_key]:
                    st.success(f"🎉 Rất xuất sắc! Câu chuẩn: **{q['full_target']}**")
                    play_audio_js(q["full_target"])
                else:
                    st.error(f"❌ Chưa đúng rồi! Đáp án chuẩn: **{q['full_target']}**")
                
                if st.button("Câu tiếp theo ➡️"):
                    new_question(st.session_state.active_mode, st.session_state.active_lessons)
                    st.rerun()

        # DẠNG 1, 2, 3: TRẮC NGHIỆM TỰ ĐỘNG CHẤM KHI CHỌN RADIO
        else:
            if q["mode"] == 1:
                st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #1E88E5;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
                play_audio_js(q['target']['char'])
            elif q["mode"] == 2:
                st.markdown(f"<h1 style='text-align: center; font-size: 80px; color: #1E88E5;'>{q['target']['pinyin']}</h1>", unsafe_allow_html=True)
            elif q["mode"] == 3:
                st.markdown(f"<h1 style='text-align: center; font-size: 70px; color: #1E88E5;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center; color: #666;'>{q['target']['pinyin']}</h3>", unsafe_allow_html=True)
                play_audio_js(q['target']['char'])

            user_choice = st.radio("Chọn đáp án:", q["options"], index=None, key=f"radio_{st.session_state.q_id}")
            
            # TỰ ĐỘNG CHẤM NGAY KHI NGƯỜI DÙNG BẤM CHỌN (Không cần nút nộp bài)
            if user_choice is not None:
                score_flag_key = f"scored_{st.session_state.q_id}"
                if score_flag_key not in st.session_state:
                    st.session_state.total += 1
                    if user_choice == q["correct_ans"]:
                        st.session_state.score += 1
                        st.session_state[score_flag_key] = True
                    else:
                        st.session_state[score_flag_key] = False

                if st.session_state[score_flag_key]:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Sai rồi! Đáp án đúng: **{q['correct_ans']}** ({q['target'].get('meaning', '')})")

                if st.button("Câu tiếp theo ➡️"):
                    new_question(st.session_state.active_mode, st.session_state.active_lessons)
                    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"🏆 **Điểm số của bạn:** {st.session_state.get('score', 0)} / {st.session_state.get('total', 0)}")
