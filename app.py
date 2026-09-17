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

# DỮ LIỆU DỰ PHÒNG CHUẨN ĐẢM BẢO LUÔN CÓ CÂU HỎI & BÀI HỌC TỨC THÌ
BUILTIN_VOCAB = [
    {"char": "你好", "pinyin": "nǐ hǎo", "meaning": "xin chào", "lesson": "Quyển 1 - Bài 1: 你好"},
    {"char": "谢谢", "pinyin": "xièxie", "meaning": "cảm ơn", "lesson": "Quyển 1 - Bài 1: 你好"},
    {"char": "名字", "pinyin": "míngzi", "meaning": "tên", "lesson": "Quyển 1 - Bài 2: 你叫什么名字?"},
    {"char": "中国", "pinyin": "Zhōngguó", "meaning": "Trung Quốc", "lesson": "Quyển 1 - Bài 2: 你叫什么名字?"},
    {"char": "高兴", "pinyin": "gāoxìng", "meaning": "vui mừng", "lesson": "Quyển 1 - Bài 3: 很高兴认识你"},
    {"char": "认识", "pinyin": "rènshi", "meaning": "quen biết", "lesson": "Quyển 1 - Bài 3: 很高兴认识你"},
    {"char": "出租车", "pinyin": "chūzūchē", "meaning": "xe taxi", "lesson": "Quyển 1 - Bài 4: 你去哪儿?"},
    {"char": "要", "pinyin": "yào", "meaning": "muốn, cần", "lesson": "Quyển 1 - Bài 5: 你要吃什么?"},
    {"char": "牛肉", "pinyin": "niúròu", "meaning": "thịt bò", "lesson": "Quyển 1 - Bài 5: 你要吃什么?"},
    {"char": "米饭", "pinyin": "mǐfàn", "meaning": "cơm", "lesson": "Quyển 1 - Bài 5: 你要吃什么?"},
    {"char": "工作", "pinyin": "gōngzuò", "meaning": "làm việc", "lesson": "Quyển 1 - Bài 6: 你在哪儿工作?"},
    {"char": "银行", "pinyin": "yínháng", "meaning": "ngân hàng", "lesson": "Quyển 1 - Bài 7: 中国银行在哪儿?"},
    {"char": "生日", "pinyin": "shēngrì", "meaning": "sinh nhật", "lesson": "Quyển 1 - Bài 8: 你的生日是几月几号?"},
    {"char": "电影", "pinyin": "diànyǐng", "meaning": "phim", "lesson": "Quyển 1 - Bài 9: 你喜欢中国电影还是美国电影?"},
    {"char": "爸爸", "pinyin": "bàba", "meaning": "bố", "lesson": "Quyển 1 - Bài 10: 你家有几口人?"},
    {"char": "音乐", "pinyin": "yīnyuè", "meaning": "âm nhạc", "lesson": "Quyển 2 - Bài 1: 你在听什么?"},
    {"char": "起床", "pinyin": "qǐchuáng", "meaning": "thức dậy", "lesson": "Quyển 2 - Bài 2: 你平时几点起床?"},
    {"char": "手机", "pinyin": "shǒujī", "meaning": "điện thoại", "lesson": "Quyển 2 - Bài 3: 可以用一下你的手机吗?"},
    {"char": "衬衫", "pinyin": "chènshān", "meaning": "áo sơ mi", "lesson": "Quyển 2 - Bài 4: 你想要哪件?"},
    {"char": "周末", "pinyin": "zhōumò", "meaning": "cuối tuần", "lesson": "Quyển 2 - Bài 5: 你这个周末什么时候有空儿?"}
]

BUILTIN_SENTENCES = [
    {"sentence": "你好！", "meaning": "Xin chào!", "lesson": "Quyển 1 - Bài 1: 你好"},
    {"sentence": "你叫什么名字？", "meaning": "Bạn tên là gì?", "lesson": "Quyển 1 - Bài 2: 你叫什么名字?"},
    {"sentence": "很高兴认识你！", "meaning": "Rất vui được quen biết bạn!", "lesson": "Quyển 1 - Bài 3: 很高兴认识你"},
    {"sentence": "我去人民广场。", "meaning": "Tôi đi quảng trường Nhân dân.", "lesson": "Quyển 1 - Bài 4: 你去哪儿?"},
    {"sentence": "我要一份牛肉和一碗米饭。", "meaning": "Tôi muốn một suất thịt bò và một bát cơm.", "lesson": "Quyển 1 - Bài 5: 你要吃什么?"},
    {"sentence": "你在 headquarters在哪儿工作？", "meaning": "Bạn làm việc ở đâu?", "lesson": "Quyển 1 - Bài 6: 你在哪儿工作?"},
    {"sentence": "中国银行在哪儿？", "meaning": "Ngân hàng Trung Quốc ở đâu?", "lesson": "Quyển 1 - Bài 7: 中国银行在哪儿?"},
    {"sentence": "祝你生日快乐！", "meaning": "Chúc bạn sinh nhật vui vẻ!", "lesson": "Quyển 1 - Bài 8: 你的生日是几月几号?"},
    {"sentence": "坐地铁又快又便宜。", "meaning": "Đi tàu điện ngầm vừa nhanh vừa rẻ.", "lesson": "Quyển 1 - Bài 9: 你喜欢中国电影还是美国电影?"},
    {"sentence": "我家有四口人。", "meaning": "Nhà tôi có 4 người.", "lesson": "Quyển 1 - Bài 10: 你家有几口人?"}
]

DYNAMIC_LESSONS = [
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
            timeout=2.0
        )
        if response.status_code == 200:
            res = response.json()
            if isinstance(res, list) and len(res) > 0:
                return [item for item in res if isinstance(item, dict)]
    except Exception:
        pass
    return []

# Tách số bài học
def get_lesson_num(text):
    if not text: return ""
    m = re.search(r'\d+', str(text))
    return m.group(0) if m else ""

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
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=DYNAMIC_LESSONS, default=DYNAMIC_LESSONS[:5])

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép câu hội thoại chuẩn")
)

time_per_question = st.sidebar.slider("⏱️ Thời gian mỗi câu (giây):", min_value=5, max_value=60, value=15)
start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# --- 2. PHÒNG THI NHÓM MULTIPLAYER ---
with st.sidebar.expander("🏆 Phòng Thi Đấu Trực Tuyến", expanded=True):
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
        # Lưu trực tiếp phòng mới vào Local State
        st.session_state.local_rooms.insert(0, new_rm)
        
        # Gửi async lên Google
        try:
            params = {"action": "create_room", "host": h_name, "lessons": json.dumps(selected_lessons), "mode": host_mode, "num_questions": host_num_questions}
            requests.get(GOOGLE_SHEET_URL, params=params, timeout=0.8)
        except Exception:
            pass
            
        st.success(f"🎉 Đã tạo {new_room_id} thành công!")
        time.sleep(0.3)
        st.rerun()

    st.write("---")
    st.markdown("**Danh Sách Phòng Hiện Có:**")
    
    # Kéo danh sách phòng online
    remote_rooms = fetch_data_from_google("get_rooms")
    all_rooms = st.session_state.local_rooms + [r for r in remote_rooms if r.get("roomId") not in [x.get("roomId") for x in st.session_state.local_rooms]]
    
    if not all_rooms:
        st.caption("Chưa có phòng nào. Hãy nhấn nút 'Tạo Phòng Thi'!")
    else:
        for idx, rm in enumerate(all_rooms):
            r_id = rm.get("roomId", f"ROOM_{idx}")
            r_host = rm.get("host", "Ẩn danh")
            r_mode = rm.get("mode", "Dạng 1")
            r_num = rm.get("numQ", 5)
            
            st.markdown(f"**📌 {r_id}** (Host: {r_host})")
            st.caption(f"{r_mode} | {r_num} câu")
            
            if st.button(f"🎮 Gia nhập {r_id}", key=f"btn_join_{r_id}_{idx}"):
                st.session_state.in_room_exam = True
                st.session_state.room_info = rm
                st.session_state.room_q_index = 0
                st.session_state.room_score = 0
                
                v_data = fetch_data_from_google("get_vocab")
                pool = v_data if v_data else BUILTIN_VOCAB
                
                questions_deck = []
                selected_targets = random.sample(pool, min(int(r_num), len(pool))) if pool else []
                for tgt in selected_targets:
                    wrong_opts = [x.get("pinyin") for x in pool if x.get("pinyin") != tgt.get("pinyin")]
                    opts = random.sample(wrong_opts, min(3, len(wrong_opts))) + [tgt.get("pinyin")]
                    random.shuffle(opts)
                    questions_deck.append({"target": tgt, "options": opts})
                st.session_state.room_questions = questions_deck
                st.rerun()

# HÀM TẠO CÂU HỎI MỚI
def new_question(mode_choice, lessons_choice):
    st.session_state.q_id += 1
    st.session_state.start_time = time.time()
    
    # Lấy dữ liệu từ Google hoặc dữ liệu built-in
    vocab_remote = fetch_data_from_google("get_vocab")
    sent_remote = fetch_data_from_google("get_sentences")
    
    vocab_source = vocab_remote if vocab_remote else BUILTIN_VOCAB
    sent_source = sent_remote if sent_remote else BUILTIN_SENTENCES
    
    selected_nums = set([get_lesson_num(x) for x in lessons_choice if get_lesson_num(x)])
    
    vocab_pool = [i for i in vocab_source if get_lesson_num(i.get("lesson")) in selected_nums]
    sent_pool = [i for i in sent_source if get_lesson_num(i.get("lesson")) in selected_nums]
    
    if not vocab_pool: vocab_pool = vocab_source
    if not sent_pool: sent_pool = sent_source

    if "Dạng 4" in mode_choice:
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
        target = random.choice(vocab_pool)
        wrong_options = [item.get("pinyin") for item in vocab_source if item.get("pinyin") != target.get("pinyin")]
        options = random.sample(wrong_options, min(3, len(wrong_options))) + [target.get("pinyin")]
        random.shuffle(options)
        st.session_state.question = {
            "mode": 1, "target": target, "options": options, "correct_ans": target.get("pinyin")
        }

if start_button:
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

# GIAO DIỆN LÀM BÀI PHÒNG THI NHÓM
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

# GIAO DIỆN LÀM BÀI CÁ NHÂN
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
