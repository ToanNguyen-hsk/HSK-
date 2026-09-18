# -*- coding: utf-8 -*-
import streamlit as st
import random
import requests
import json
import time
import re
import datetime
import pandas as pd
import streamlit.components.v1 as components

# Tải dữ liệu trực tiếp từ file data.py cùng thư mục
from data import FULL_VOCAB, FULL_SENTENCES

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
    div[data-testid="stRadio"] > div { gap: 15px; }
    .leaderboard-title {
        color: #1E88E5; font-size: 22px; font-weight: bold; margin-top: 15px; margin-bottom: 10px;
    }
    div[data-testid="column"] button p {
        font-size: 32px !important;
        font-weight: bold !important;
    }
    div[data-testid="column"] button {
        height: 72px !important;
        border-radius: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

def play_audio_js(text):
    if not text: return
    clean_text = str(text).replace("'", "\\'").replace('"', '\\"').replace("\n", " ").strip()
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

# Đồng hồ đếm ngược JS tự phát âm thanh khi về 0s
def render_js_timer(seconds, key_id, correct_ans_display, tts_text=""):
    clean_ans = str(correct_ans_display).replace("'", "\\'").replace('"', '\\"').replace("\n", " ").strip()
    clean_tts = str(tts_text).replace("'", "\\'").replace('"', '\\"').replace("\n", " ").strip()
    js_timer_code = f"""
    <div id="timer-box-{key_id}" style="
        font-size: 20px; 
        font-weight: bold; 
        color: #D32F2F; 
        text-align: center;
        background-color: #FFEBEE; 
        padding: 10px 14px; 
        border-radius: 8px; 
        border: 1px solid #FFCDD2;
        font-family: sans-serif;
        margin-bottom: 12px;">
        ⏱️ Thời gian còn lại: <span id="count-{key_id}">{seconds}</span> giây
    </div>
    <script>
        (function() {{
            var timeLeft = {seconds};
            var elem = document.getElementById('count-{key_id}');
            var box = document.getElementById('timer-box-{key_id}');
            if (!elem || !box) return;
            var timerId = setInterval(function() {{
                timeLeft--;
                if (timeLeft <= 0) {{
                    clearInterval(timerId);
                    box.style.backgroundColor = "#FFF3E0";
                    box.style.borderColor = "#FFE0B2";
                    box.style.color = "#E65100";
                    box.innerHTML = "⏰ <b>Đã hết thời gian làm câu này!</b><br><span style='font-size: 17px; color: #2E7D32;'>💡 Đáp án đúng: <b>{clean_ans}</b></span>";
                    if ("{clean_tts}" !== "") {{
                        try {{
                            var synth = window.parent.speechSynthesis || window.speechSynthesis;
                            if (synth) {{
                                synth.cancel();
                                var msg = new SpeechSynthesisUtterance("{clean_tts}");
                                msg.lang = "zh-CN"; msg.rate = 0.85; synth.speak(msg);
                            }}
                        }} catch(e) {{}}
                    }}
                }} else {{
                    elem.innerHTML = timeLeft;
                }}
            }}, 1000);
        }})();
    </script>
    """
    components.html(js_timer_code, height=68)

def parse_book_and_lesson(text):
    if not text: return ("", "")
    s = str(text).strip()
    b_match = re.search(r'Quyển\s*(\d+)', s, re.IGNORECASE)
    l_match = re.search(r'Bài\s*(\d+)', s, re.IGNORECASE)
    book = b_match.group(1) if b_match else ""
    lesson = l_match.group(1) if l_match else ""
    return (book, lesson)

def is_lesson_selected(item_lesson, selected_lessons):
    if not selected_lessons:
        return True
    item_bk, item_ls = parse_book_and_lesson(item_lesson)
    for sel in selected_lessons:
        if item_lesson and (item_lesson.strip() in sel.strip() or sel.strip() in item_lesson.strip()):
            return True
        sel_bk, sel_ls = parse_book_and_lesson(sel)
        if item_bk and item_ls and sel_bk and sel_ls:
            if item_bk == sel_bk and item_ls == sel_ls:
                return True
    return False

@st.cache_data(ttl=15)
def fetch_rooms_from_sheet():
    try:
        remote_response = requests.get(GOOGLE_SHEET_URL, params={"action": "get_rooms"}, timeout=1.5).json()
        if isinstance(remote_response, list):
            return [r for r in remote_response if isinstance(r, dict) and r.get("roomId")]
    except Exception:
        pass
    return []

DYNAMIC_LESSONS = [
    "Quyển 1 - Bài 1: 你好", "Quyển 1 - Bài 2: 你叫什么名字?", "Quyển 1 - Bài 3: 很高兴认识你",
    "Quyển 1 - Bài 4: 你去哪儿?", "Quyển 1 - Bài 5: 你要吃什么?", "Quyển 1 - Bài 6: 你在哪儿工作?",
    "Quyển 1 - Bài 7: 中国银行在哪儿?", "Quyển 1 - Bài 8: 你的生日是几月几号?", "Quyển 1 - Bài 9: 你喜欢中国电影还是美国电影?",
    "Quyển 1 - Bài 10: 你家有几口人?", "Quyển 2 - Bài 1: 你在听什么?", "Quyển 2 - Bài 2: 你平时几点起床?",
    "Quyển 2 - Bài 3: 可以用一下你的手机吗?", "Quyển 2 - Bài 4: 你想要哪件?", "Quyển 2 - Bài 5: 你 cái周末什么时候有空儿?",
    "Quyển 2 - Bài 6: 上个周末你做什么了?", "Quyển 2 - Bài 7: 你是跟谁 festival一起去的?", "Quyển 2 - Bài 8: 你会做菜吗?",
    "Quyển 2 - Bài 9: 你见过熊猫吗?", "Quyển 2 - Bài 10: 给您添麻烦了!"
]

for k in ["score", "total", "q_id"]:
    if k not in st.session_state: st.session_state[k] = 0
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "quiz_finished" not in st.session_state: st.session_state.quiz_finished = False
if "start_time" not in st.session_state: st.session_state.start_time = time.time()
if "local_leaderboard" not in st.session_state:
    st.session_state.local_leaderboard = [
        {"name": "Giáo viên tập sự", "score": 10, "total": 10, "mode": "Dạng 1", "date": "17/09/2026 14:30"},
        {"name": "Thành viên HSK", "score": 8, "total": 10, "mode": "Dạng 4", "date": "17/09/2026 12:15"}
    ]

# --- 1. THANH BÊN CẤU HÌNH CÁ NHÂN ---
st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", value=st.session_state.get("user_name", ""), placeholder="Nhập tên của bạn...")
st.session_state.user_name = user_name

st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=DYNAMIC_LESSONS, default=DYNAMIC_LESSONS[:5])

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép câu hội thoại chuẩn")
)

time_per_question = st.sidebar.slider("⏱️ Thời gian mỗi câu (giây):", min_value=5, max_value=60, value=15)
start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# --- 2. KHU VỰC PHÒNG THI NHÓM ---
with st.sidebar.expander("🏆 Phòng Thi Đấu Trực Tuyến", expanded=False):
    st.caption("Khởi tạo hoặc gia nhập cuộc thi nhóm")
    host_mode = st.selectbox("Dạng bài thi:", ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"])
    host_num_questions = st.number_input("Số lượng câu:", min_value=3, max_value=20, value=5)
    
    if st.button("➕ Tạo Phòng Thi"):
        h_name = user_name.strip() if user_name.strip() else "Ẩn danh"
        try:
            params = {"action": "create_room", "host": h_name, "lessons": json.dumps(selected_lessons), "mode": host_mode, "num_questions": host_num_questions}
            requests.get(GOOGLE_SHEET_URL, params=params, timeout=1.5)
            st.success("🎉 Đã yêu cầu tạo phòng thành công!")
        except Exception:
            st.warning("⚠️ Lỗi mạng: Gửi yêu cầu thất bại.")
            
    st.write("---")
    st.markdown("**Danh Sách Phòng:**")
    valid_rooms = fetch_rooms_from_sheet()
        
    if not valid_rooms:
        st.caption("Chưa có phòng nào. Hãy nhấn 'Tạo Phòng Thi'!")
    else:
        for idx, rm in enumerate(valid_rooms):
            r_id = rm.get("roomId", "")
            r_host = rm.get("host", "Ẩn danh")
            r_mode = rm.get("mode", "Dạng 1")
            r_num = rm.get("numQ", 5)
            if st.button(f"🎮 Gia nhập {r_id} ({r_host})", key=f"btn_join_{r_id}_{idx}"):
                st.session_state.in_room_exam = True
                st.session_state.room_info = rm
                st.session_state.room_q_index = 0
                st.session_state.room_score = 0
                
                pool = FULL_VOCAB
                questions_deck = []
                for _ in range(int(r_num)):
                    tgt = random.choice(pool)
                    if "Dạng 1" in r_mode:
                        wrong_opts = [str(x.get("pinyin", "")).strip() for x in pool if str(x.get("pinyin", "")).strip() != str(tgt.get("pinyin", "")).strip()]
                        opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [str(tgt.get("pinyin", "")).strip()]
                    elif "Dạng 2" in r_mode:
                        wrong_opts = [str(x.get("char", "")).strip() for x in pool if str(x.get("char", "")).strip() != str(tgt.get("char", "")).strip()]
                        opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [str(tgt.get("char", "")).strip()]
                    else:
                        wrong_opts = [str(x.get("meaning", "")).strip() for x in pool if str(x.get("meaning", "")).strip() != str(tgt.get("meaning", "")).strip()]
                        opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [str(tgt.get("meaning", "")).strip()]
                        
                    random.shuffle(opts)
                    questions_deck.append({"target": tgt, "options": opts, "mode": r_mode})
                    
                st.session_state.room_questions = questions_deck
                st.rerun()

def new_question(mode_choice, lessons_choice):
    st.session_state.q_id += 1
    st.session_state.start_time = time.time()
    
    vocab_pool = [i for i in FULL_VOCAB if is_lesson_selected(i.get("lesson"), lessons_choice)]
    sent_pool = [i for i in FULL_SENTENCES if is_lesson_selected(i.get("lesson"), lessons_choice)]
    
    if not vocab_pool: vocab_pool = FULL_VOCAB
    if not sent_pool: sent_pool = FULL_SENTENCES

    if "Dạng 4" in mode_choice:
        target = random.choice(sent_pool)
        raw_sentence = re.sub(r'[？！。，、“”]', '', str(target.get("sentence", ""))).strip()
        words = list(raw_sentence)
        shuffled_words = list(words)
        random.shuffle(shuffled_words)
        st.session_state.question = {
            "mode": 4, "meaning": str(target.get("meaning", "")).strip(), "correct_sentence": raw_sentence,
            "shuffled_words": shuffled_words, "full_target": str(target.get("sentence", "")).strip()
        }
    else:
        target = random.choice(vocab_pool)
        
        if "Dạng 1" in mode_choice:
            target_ans = str(target.get("pinyin", "")).strip()
            wrong_opts = [str(item.get("pinyin", "")).strip() for item in FULL_VOCAB if str(item.get("pinyin", "")).strip() != target_ans]
            opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [target_ans]
            random.shuffle(opts)
            st.session_state.question = {"mode": 1, "target": target, "options": opts, "correct_ans": target_ans}
            
        elif "Dạng 2" in mode_choice:
            target_ans = str(target.get("char", "")).strip()
            wrong_opts = [str(item.get("char", "")).strip() for item in FULL_VOCAB if str(item.get("char", "")).strip() != target_ans]
            opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [target_ans]
            random.shuffle(opts)
            st.session_state.question = {"mode": 2, "target": target, "options": opts, "correct_ans": target_ans}
            
        elif "Dạng 3" in mode_choice:
            target_ans = str(target.get("meaning", "")).strip()
            wrong_opts = [str(item.get("meaning", "")).strip() for item in FULL_VOCAB if str(item.get("meaning", "")).strip() != target_ans]
            opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [target_ans]
            random.shuffle(opts)
            st.session_state.question = {"mode": 3, "target": target, "options": opts, "correct_ans": target_ans}

if start_button:
    st.session_state.quiz_started = True
    st.session_state.quiz_finished = False
    st.session_state.in_room_exam = False
    st.session_state.active_mode = quiz_mode
    st.session_state.active_lessons = selected_lessons
    st.session_state.active_timer = time_per_question
    st.session_state.score = 0
    st.session_state.total = 0
    new_question(quiz_mode, selected_lessons)
    st.rerun()

st.title("🎓 App Kiểm Tra Từ Vựng & Ngữ Pháp MSUTONG")

# ==========================================
# 📊 GIAO DIỆN TỔNG KẾT BÀI THI & BẢNG TỶ SỐ
# ==========================================
if st.session_state.get("quiz_finished", False):
    st.balloons()
    st.success("🎉 BẠN ĐÃ HOÀN THÀNH BÀI KIỂM TRA!")
    
    total_q = st.session_state.get('total', 0)
    score_q = st.session_state.get('score', 0)
    ratio = round((score_q / total_q) * 100, 1) if total_q > 0 else 0
    
    st.metric(label="📊 Điểm số chung cuộc", value=f"{score_q} / {total_q} câu đúng", delta=f"{ratio}% Tỷ lệ chính xác")
    
    st.write("---")
    st.markdown("<div class='leaderboard-title'>📝 Cập nhật tên & Lưu điểm vào Bảng Tỷ Số</div>", unsafe_allow_html=True)
    
    col_name, col_save = st.columns([3, 1])
    with col_name:
        update_name = st.text_input("👤 Họ và tên người làm (không bắt buộc):", value=st.session_state.get("user_name", ""), key="end_user_name_input")
    with col_save:
        st.write(" ")
        st.write(" ")
        save_score_btn = st.button("💾 Lưu Bảng Tỷ Số", use_container_width=True)
        
    if save_score_btn:
        final_name = update_name.strip() if update_name.strip() else "Ẩn danh"
        st.session_state.user_name = final_name
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        new_entry = {
            "name": final_name,
            "score": score_q,
            "total": total_q,
            "mode": st.session_state.get("active_mode", "Dạng 1"),
            "date": now_str
        }
        st.session_state.local_leaderboard.insert(0, new_entry)
        
        try:
            params = {
                "action": "save_score",
                "name": final_name,
                "score": score_q,
                "total": total_q,
                "mode": st.session_state.get("active_mode", "Dạng 1")
            }
            requests.get(GOOGLE_SHEET_URL, params=params, timeout=1.5)
        except Exception:
            pass
            
        st.success(f"✅ Đã ghi nhận kết quả của **{final_name}** vào Bảng Tỷ Số!")

    st.write("---")
    st.markdown("<div class='leaderboard-title'>🏆 BẢNG TỶ SỐ CÁC THÀNH VIÊN</div>", unsafe_allow_html=True)
    if st.session_state.local_leaderboard:
        df_lb = pd.DataFrame(st.session_state.local_leaderboard)
        df_lb.columns = ["Họ và tên", "Điểm", "Tổng câu", "Dạng bài", "Thời gian"]
        st.dataframe(df_lb, use_container_width=True, hide_index=True)

    st.write(" ")
    if st.button("🔄 Làm bài kiểm tra mới", use_container_width=True):
        st.session_state.quiz_started = False
        st.session_state.quiz_finished = False
        st.rerun()

# --- GIAO DIỆN LÀM BÀI PHÒNG THI NHÓM ---
elif st.session_state.get("in_room_exam", False):
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
        target, options, r_mode = q_item["target"], q_item["options"], q_item["mode"]
        
        if "Dạng 1" in r_mode:
            st.markdown(f"<h1 style='text-align: center; font-size: 90px; color: #1E88E5;'>{target.get('char')}</h1>", unsafe_allow_html=True)
            play_audio_js(target.get('char'))
            correct_ans = f"{target.get('pinyin')} ({target.get('meaning', '')})"
        elif "Dạng 2" in r_mode:
            st.markdown(f"<h1 style='text-align: center; font-size: 70px; color: #1E88E5;'>{target.get('pinyin')}</h1>", unsafe_allow_html=True)
            play_audio_js(target.get('char'))
            correct_ans = f"{target.get('char')} ({target.get('meaning', '')})"
        else:
            st.markdown(f"<h1 style='text-align: center; font-size: 80px; color: #1E88E5;'>{target.get('char')}</h1>", unsafe_allow_html=True)
            play_audio_js(target.get('char'))
            st.markdown(f"<h3 style='text-align: center; color: #666;'>{target.get('pinyin')}</h3>", unsafe_allow_html=True)
            correct_ans = f"{target.get('meaning')} ({target.get('pinyin', '')})"
        
        ans = st.radio("Chọn đáp án:", options, index=None, key=f"rm_ans_{curr_idx}")
        if ans is not None:
            ans_clean = str(ans).strip()
            if ans_clean in correct_ans or correct_ans.startswith(ans_clean): 
                st.session_state.room_score += 1
                st.success(f"🎉 Chính xác! **{correct_ans}**")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng: **{correct_ans}**")
                
            if st.button("Câu tiếp theo ➡️"):
                st.session_state.room_q_index += 1
                st.rerun()

# --- GIAO DIỆN LÀM BÀI CÁ NHÂN ---
elif not st.session_state.quiz_started:
    st.info("👈 Chọn bài kiểm tra ở thanh bên trái và bấm **🚀 Bắt đầu kiểm tra**!")

elif st.session_state.get("question"):
    q = st.session_state.question
    score_flag_key = f"scored_{st.session_state.q_id}"
    word_state_key = f"word_indices_{st.session_state.q_id}"
    if word_state_key not in st.session_state:
        st.session_state[word_state_key] = []
        
    has_answered = score_flag_key in st.session_state
    
    elapsed = time.time() - st.session_state.start_time
    timer_limit = st.session_state.get("active_timer", 15)
    remaining = max(0, int(timer_limit - elapsed))

    # TÍNH CHUỖI HIỂN THỊ ĐÁP ÁN CHUẨN
    if q.get("mode") == 4:
        correct_ans_display = f"{q['full_target']} ({q['meaning']})"
        tts_target_text = q["full_target"]
    elif q["mode"] == 1:
        correct_ans_display = f"{q['target']['pinyin']} ({q['target']['meaning']})"
        tts_target_text = q["target"]["char"]
    elif q["mode"] == 2:
        correct_ans_display = f"{q['target']['char']} ({q['target']['meaning']})"
        tts_target_text = q["target"]["char"]
    elif q["mode"] == 3:
        correct_ans_display = f"{q['target']['meaning']} ({q['target']['pinyin']})"
        tts_target_text = q["target"]["char"]

    # --- DẠNG 4: GHÉP CÂU HỘI THOẠI ---
    if q.get("mode") == 4:
        st.subheader("🧩 Bài Tập Ghép Câu Hội Thoại")
        st.markdown(f"### 💡 **Ý nghĩa:** `{q['meaning']}`")
        
        last_word_key = f"last_word_{st.session_state.q_id}"
        if last_word_key in st.session_state:
            play_audio_js(st.session_state[last_word_key])
            del st.session_state[last_word_key]

        selected_indices = st.session_state[word_state_key]
        user_sentence_str = "".join([q["shuffled_words"][i] for i in selected_indices])
        
        display_str = user_sentence_str if user_sentence_str else "..."
        st.markdown(f"<div style='background-color: #F1F8E9; padding: 12px 16px; border-radius: 10px; border: 2px solid #C8E6C9; margin-bottom: 12px;'><span style='font-size: 18px; color: #555;'>Thứ tự câu bạn ghép:</span> <br><span style='font-size: 28px; font-weight: bold; color: #2E7D32;'>{display_str}</span></div>", unsafe_allow_html=True)
        
        st.markdown("**Click trực tiếp vào các từ/chữ dưới đây theo thứ tự:**")
        num_words = len(q["shuffled_words"])
        cols = st.columns(min(num_words, 8))
        
        for idx, word in enumerate(q["shuffled_words"]):
            col = cols[idx % min(num_words, 8)]
            is_used = idx in selected_indices
            if col.button(word, key=f"w_btn_{st.session_state.q_id}_{idx}", disabled=is_used or has_answered, use_container_width=True):
                st.session_state[word_state_key].append(idx)
                st.session_state[last_word_key] = word
                st.rerun()

        if selected_indices and not has_answered:
            c_undo, c_reset = st.columns(2)
            with c_undo:
                if st.button("⌫ Xóa chữ vừa chọn", key=f"undo_w_{st.session_state.q_id}", use_container_width=True):
                    st.session_state[word_state_key].pop()
                    st.rerun()
            with c_reset:
                if st.button("🔄 Chọn lại từ đầu", key=f"reset_w_{st.session_state.q_id}", use_container_width=True):
                    st.session_state[word_state_key] = []
                    st.rerun()

        if len(selected_indices) == num_words and not has_answered:
            st.session_state.total += 1
            is_correct = (user_sentence_str.strip() == q["correct_sentence"].strip())
            st.session_state.score += (1 if is_correct else 0)
            st.session_state[score_flag_key] = is_correct
            st.rerun()

        if has_answered:
            if st.session_state[score_flag_key]:
                st.success(f"🎉 Rất xuất sắc! Câu chuẩn: **{q['full_target']}** ({q['meaning']})")
                play_audio_js(q["full_target"])
            else:
                st.error(f"❌ Chưa đúng rồi! Đáp án chuẩn: **{q['full_target']}** ({q['meaning']})")
                play_audio_js(q["full_target"])
            
            if st.button("Câu tiếp theo ➡️", key=f"sent_next_{st.session_state.q_id}", use_container_width=True):
                new_question(st.session_state.active_mode, st.session_state.active_lessons)
                st.rerun()

        else:
            if remaining <= 0:
                play_audio_js(q["full_target"])
            render_js_timer(remaining, st.session_state.q_id, correct_ans_display, tts_text=q["full_target"])
            if st.button("Sang câu tiếp theo ➡️", key=f"timeout_sent_next_{st.session_state.q_id}", use_container_width=True):
                new_question(st.session_state.active_mode, st.session_state.active_lessons)
                st.rerun()

    # --- DẠNG 1, 2, 3: TRẮC NGHIỆM ---
    else:
        if q["mode"] == 1:
            st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #1E88E5;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
            play_audio_js(q['target']['char'])
        elif q["mode"] == 2:
            st.markdown(f"<h1 style='text-align: center; font-size: 80px; color: #1E88E5;'>{q['target']['pinyin']}</h1>", unsafe_allow_html=True)
            play_audio_js(q['target']['char'])
        elif q["mode"] == 3:
            st.markdown(f"<h1 style='text-align: center; font-size: 70px; color: #1E88E5;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: #666;'>{q['target']['pinyin']}</h3>", unsafe_allow_html=True)
            play_audio_js(q['target']['char'])

        if has_answered:
            if st.session_state[score_flag_key]:
                st.success(f"🎉 Chính xác! **{correct_ans_display}**")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng: **{correct_ans_display}**")

            if st.button("Câu tiếp theo ➡️", key=f"ans_next_{st.session_state.q_id}", use_container_width=True):
                new_question(st.session_state.active_mode, st.session_state.active_lessons)
                st.rerun()

        else:
            if remaining <= 0:
                play_audio_js(tts_target_text)
            render_js_timer(remaining, st.session_state.q_id, correct_ans_display, tts_text=tts_target_text)
            user_choice = st.radio("Chọn đáp án:", q["options"], index=None, key=f"radio_{st.session_state.q_id}")
            
            if user_choice is not None:
                st.session_state.total += 1
                is_correct = (str(user_choice).strip() == str(q["correct_ans"]).strip())
                st.session_state.score += (1 if is_correct else 0)
                st.session_state[score_flag_key] = is_correct
                st.rerun()

            if st.button("Sang câu tiếp theo ➡️", key=f"timeout_next_{st.session_state.q_id}", use_container_width=True):
                new_question(st.session_state.active_mode, st.session_state.active_lessons)
                st.rerun()

    # --- NÚT KẾT THÚC BÀI KIỂM TRA ĐẶT BIỆT LẬP Ở DƯỚI CÙNG TRANG ---
    st.divider()
    st.caption("Nếu muốn dừng bài kiểm tra tại đây, nhấn nút bên dưới:")
    if st.button("🏁 Kết thúc bài kiểm tra", key=f"global_finish_{st.session_state.q_id}"):
        st.session_state.quiz_finished = True
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"🏆 **Điểm số hiện tại:** {st.session_state.get('score', 0)} / {st.session_state.get('total', 0)}")
