# -*- coding: utf-8 -*-
import streamlit as st
import random
import pandas as pd
import requests
import base64
from io import BytesIO
from gtts import gTTS
import streamlit.components.v1 as components

# 1. Cấu hình trang web
st.set_page_config(page_title="App Ôn Tập & Thi Đấu HSK MSUTONG", layout="wide")

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbxcnKRCCcd-iIkzspRGjS4jnwdCU3A25FwAVCBWlmJHMKT2le5kYd22O3i-V-fv3c0V/exec"

# CSS Tùy chỉnh Avatar Online & Giao diện
st.markdown("""
    <style>
    section.main div[data-testid="stRadio"] label p {
        font-size: 24px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    .online-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-bottom: 15px;
    }
    .avatar-circle {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background-color: #1E88E5;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 15px;
        border: 2px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Hàm phát âm MP3 Base64
def play_audio_js(text):
    if not text:
        return
    try:
        tts = gTTS(text=text, lang='zh-CN', slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        random_id = random.randint(10000, 99999)
        
        audio_html = f'''
            <div style="text-align: center; margin: 5px 0;">
                <audio autoplay id="aud_{random_id}" style="height: 35px; width: 260px;">
                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                </audio>
            </div>
            <script>
                (function() {{
                    try {{
                        var aud = document.getElementById("aud_{random_id}");
                        if (aud) {{ aud.play(); }}
                    }} catch(e) {{}}
                }})();
            </script>
        '''
        components.html(audio_html, height=45)
    except Exception:
        pass

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

# Kho từ vựng đầy đủ (Từ chính + Từ bổ sung)
VOCAB_DATA = [
    # --- QUYỂN 1 ---
    {"char": "你好", "pinyin": "nǐ hǎo", "meaning": "xin chào", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "您", "pinyin": "nín", "meaning": "ngài, ông, bà", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "你们", "pinyin": "nǐmen", "meaning": "các bạn", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "老师", "pinyin": "lǎoshī", "meaning": "thầy/cô giáo", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "对不起", "pinyin": "duìbuqǐ", "meaning": "xin lỗi", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "没关系", "pinyin": "méi guānxi", "meaning": "không sao", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "谢谢", "pinyin": "xièxie", "meaning": "cảm ơn", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "不客气", "pinyin": "bú kèqi", "meaning": "không có gì", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "再见", "pinyin": "zàijiàn", "meaning": "tạm biệt", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "叫", "pinyin": "jiào", "meaning": "gọi, tên là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "什么", "pinyin": "shénme", "meaning": "gì, cái gì", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "名字", "pinyin": "míngzi", "meaning": "tên", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "我", "pinyin": "wǒ", "meaning": "tôi", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "呢", "pinyin": "ne", "meaning": "trợ từ ngữ khí", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "是", "pinyin": "shì", "meaning": "là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "哪", "pinyin": "nǎ", "meaning": "nào", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "国", "pinyin": "guó", "meaning": "nước, quốc gia", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "人", "pinyin": "rén", "meaning": "người", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "中国", "pinyin": "Zhōngguó", "meaning": "Trung Quốc", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "请问", "pinyin": "qǐngwèn", "meaning": "xin hỏi", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "贵姓", "pinyin": "guìxìng", "meaning": "quý danh, quý họ", "lesson": LESSON_NAMES["Q1_3"]},
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
    {"char": "要", "pinyin": "yào", "meaning": "muốn, cần", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "吃", "pinyin": "chī", "meaning": "ăn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "牛肉", "pinyin": "niúròu", "meaning": "thịt bò", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "米饭", "pinyin": "mǐfàn", "meaning": "cơm", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "咖啡", "pinyin": "kāfēi", "meaning": "cà phê", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "工作", "pinyin": "gōngzuò", "meaning": "công việc, làm việc", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "附近", "pinyin": "fùjìn", "meaning": "gần đây", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "生日", "pinyin": "shēngrì", "meaning": "sinh nhật", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "喜欢", "pinyin": "xǐhuan", "meaning": "thích", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "爸爸", "pinyin": "bàba", "meaning": "bố", "lesson": LESSON_NAMES["Q1_10"]},

    # --- QUYỂN 2 ---
    {"char": "正在", "pinyin": "zhèngzài", "meaning": "đang", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "听", "pinyin": "tīng", "meaning": "nghe", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "起床", "pinyin": "qǐchuáng", "meaning": "thức dậy", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "可以", "pinyin": "kěyǐ", "meaning": "có thể", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "衣服", "pinyin": "yīfu", "meaning": "quần áo", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "空儿", "pinyin": "kòngr", "meaning": "thời gian rảnh", "lesson": LESSON_NAMES["Q2_5"]}
]

# Kho câu Dạng 4 đầy đủ
SENTENCE_DATA = [
    # Q1_1 -> Q1_5
    {"words": ["王", "老师", "您", "好"], "pinyin_words": ["Wáng", "lǎoshī", "nín", "hǎo"], "lesson": LESSON_NAMES["Q1_1"]},
    {"words": ["你", "叫", "什么", "名字"], "pinyin_words": ["Nǐ", "jiào", "shénme", "míngzi"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["请问", "您", "贵姓"], "pinyin_words": ["Qǐngwèn", "nín", "guìxìng"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["我", "去", "人民", "广场"], "pinyin_words": ["Wǒ", "qù", "Rénmín", "Guǎngchǎng"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["请问", "这个", "多少", "钱"], "pinyin_words": ["Qǐngwèn", "zhège", "duōshao", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["师傅", "去", "飞机场", "远", "不", "远"], "pinyin_words": ["Shīfu", "qù", "fēijīchǎng", "yuǎn", "bù", "yuǎn"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["一共", "是", "五十", "块", "钱"], "pinyin_words": ["Yígòng", "shì", "wǔshí", "kuài", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["到", "火车站", "坐", "地铁"], "pinyin_words": ["Dào", "huǒchēzhàn", "zuò", "dìtiě"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["你", "要", "吃", "什么"], "pinyin_words": ["Nǐ", "yào", "chī", "shénme"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["我", "要", "一", "碗", "米饭"], "pinyin_words": ["Wǒ", "yào", "yì", "wǎn", "mǐfàn"], "lesson": LESSON_NAMES["Q1_5"]},
    
    # Q1_6 -> Q2_10
    {"words": ["他", "在", "北京", "大学", "学习", "汉语"], "pinyin_words": ["Tā", "zài", "Běijīng", "dàxué", "xuéxí", "Hànyǔ"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["从", "这儿", "往前走", "往", "右", "拐"], "pinyin_words": ["Cóng", "zhèr", "wǎng", "qián", "zǒu", "wǎng", "yòu", "guǎi"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["今天", "晚上", "我", "想", "请", "你", "看", "电影"], "pinyin_words": ["Jīntiān", "wǎnshang", "wǒ", "xiǎng", "qǐng", "nǐ", "kàn", "diànyǐng"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["你", "喜欢", "中国", "菜", "还是", "韩国", "菜"], "pinyin_words": ["Nǐ", "xǐhuan", "Zhōngguó", "cài", "háishi", "Hánguó", "cài"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["你", "家", "有", "几", "口", "人"], "pinyin_words": ["Nǐ", "jiā", "yǒu", "jǐ", "kǒu", "rén"], "lesson": LESSON_NAMES["Q1_10"]},
    {"words": ["他", "常常", "一边", "吃饭", "一边", "看", "电视"], "pinyin_words": ["Tā", "chángcháng", "yìbiān", "chī fàn", "yìbiān", "kàn", "diànshì"], "lesson": LESSON_NAMES["Q2_1"]}
]

# --- SIDEBAR: QUẢN LÝ TÀI KHOẢN & DANH SÁCH ONLINE ---
st.sidebar.title("👤 Tài Khoản Người Dùng")
user_name = st.sidebar.text_input("Nhập tên của bạn:", value="Học viên", key="user_name_input")

def update_online_status():
    if user_name:
        try:
            requests.post(GOOGLE_SHEET_URL, json={"action": "ping_online", "name": user_name}, timeout=1.5)
            res = requests.get(f"{GOOGLE_SHEET_URL}?action=get_online", timeout=1.5)
            return res.json()
        except:
            return [user_name]
    return []

active_users = update_online_status()

# Hiển thị Avatar Online góc Sidebar (kiểu Google Sheet)
st.sidebar.markdown("### 🟢 Đang Online")
if active_users:
    avatar_html = "<div class='online-container'>"
    for u in active_users:
        initial = u[0].upper() if u else "U"
        avatar_html += f"<div class='avatar-circle' title='{u}'>{initial}</div>"
    avatar_html += "</div>"
    st.sidebar.markdown(avatar_html, unsafe_allow_html=True)
    st.sidebar.caption(f"Có **{len(active_users)}** người đang truy cập.")

# --- KHU VỰC TABS CHÍNH ---
tab_practice, tab_competition = st.tabs(["📚 Luyện Tập Cá Nhân", "🏆 Phòng Thi Đấu (Multiplayer)"])

# ================= TAB 1: LUYỆN TẬP CÁ NHÂN =================
with tab_practice:
    st.header("🎯 Ôn Tập Tự Do")
    
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        selected_lessons = st.multiselect("Chọn bài ôn tập:", options=list(LESSON_NAMES.values()), default=[LESSON_NAMES["Q1_4"]])
    with col_sel2:
        quiz_mode = st.radio("Chọn dạng bài:", ("Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép nối câu từ Hán & Pinyin"))

    if st.button("🚀 Bắt Đầu Luyện Tập"):
        st.session_state.practice_started = True
        st.session_state.q_id = random.randint(100, 999)
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.selected_words = []
        st.session_state.speech_target = ""
        st.rerun()

    filtered_vocab = [item for item in VOCAB_DATA if item["lesson"] in selected_lessons]
    filtered_sentences = [item for item in SENTENCE_DATA if item["lesson"] in selected_lessons]

    if st.session_state.get("practice_started", False):
        st.write("---")
        
        if quiz_mode in ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"]:
            if filtered_vocab:
                target = random.choice(filtered_vocab)
                play_audio_js(target["char"])
                
                st.markdown(f"<p style='color: #888;'>📚 Bài học: <b>{target['lesson']}</b></p>", unsafe_allow_html=True)
                
                if quiz_mode == "Dạng 1: Chữ Hán ➡️ 4 Pinyin":
                    st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #1E88E5;'>{target['char']}</h1>", unsafe_allow_html=True)
                    correct_ans = target["pinyin"]
                    wrong_opts = [x["pinyin"] for x in VOCAB_DATA if x["pinyin"] != correct_ans]
                elif quiz_mode == "Dạng 2: Pinyin ➡️ 4 Chữ Hán":
                    st.markdown(f"<h1 style='text-align: center; font-size: 60px; color: #E65100;'>{target['pinyin']}</h1>", unsafe_allow_html=True)
                    correct_ans = target["char"]
                    wrong_opts = [x["char"] for x in VOCAB_DATA if x["char"] != correct_ans]
                else:
                    st.markdown(f"<h1 style='text-align: center; font-size: 90px; color: #2E7D32;'>{target['char']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 22px; color: gray;'>Pinyin: <b>{target['pinyin']}</b></p>", unsafe_allow_html=True)
                    correct_ans = target["meaning"]
                    wrong_opts = [x["meaning"] for x in VOCAB_DATA if x["meaning"] != correct_ans]

                options = random.sample(wrong_opts, min(3, len(wrong_opts))) + [correct_ans]
                random.shuffle(options)
                
                ans = st.radio("Chọn đáp án đúng:", options, key=f"ans_{st.session_state.q_id}")
                if st.button("Nộp bài"):
                    if ans == correct_ans:
                        st.success("🎉 Chính xác!")
                    else:
                        st.error(f"❌ Sai rồi! Đáp án đúng là: **{correct_ans}**")

        elif quiz_mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin":
            if filtered_sentences:
                target_sent = random.choice(filtered_sentences)
                st.markdown(f"<p style='color: #888;'>📚 Bài học: <b>{target_sent['lesson']}</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 20px; color: #1565C0;'>💡 Gợi ý Pinyin: <b>{' '.join(target_sent['pinyin_words'])}</b></p>", unsafe_allow_html=True)
                
                curr_sent = " ".join(st.session_state.get("selected_words", []))
                st.markdown(f"### Câu bạn chọn: **{curr_sent}**")
                
                if st.session_state.get("speech_target", ""):
                    play_audio_js(st.session_state.speech_target)
                
                shuffled_words = list(target_sent["words"])
                random.shuffle(shuffled_words)
                
                cols = st.columns(len(shuffled_words))
                for idx, w in enumerate(shuffled_words):
                    if cols[idx].button(w, key=f"btn_{st.session_state.q_id}_{idx}"):
                        st.session_state.selected_words.append(w)
                        st.session_state.speech_target = w
                        st.rerun()

                if st.button("✔️ Kiểm Tra Câu"):
                    user_str = " ".join(st.session_state.selected_words)
                    correct_str = " ".join(target_sent["words"])
                    play_audio_js("".join(target_sent["words"]))
                    if user_str == correct_str:
                        st.success("🎉 Chính xác!")
                    else:
                        st.error(f"❌ Sai rồi! Câu đúng là: **{correct_str}**")

# ================= TAB 2: PHÒNG THI ĐẤU MULTIPLAYER =================
with tab_competition:
    st.header("🏆 Phòng Thi Đấu Trực Tuyến")
    
    col_host, col_join = st.columns([1, 1])
    
    # KHU VỰC HOST TẠO PHÒNG
    with col_host:
        st.subheader("🛠️ Tạo Cuộc Thi Mới (Host)")
        host_lessons = st.multiselect("Chọn nội dung thi:", options=list(LESSON_NAMES.values()), default=[LESSON_NAMES["Q1_4"]])
        host_mode = st.selectbox("Dạng bài thi:", ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép nối câu từ Hán & Pinyin"])
        host_num_questions = st.number_input("Số lượng câu hỏi:", min_value=3, max_value=50, value=5)
        host_time_limit = st.number_input("Thời gian làm bài (Phút):", min_value=1, max_value=60, value=3)
        
        if st.button("➕ Khởi Tạo Phòng Thi"):
            payload = {
                "action": "create_room",
                "host": user_name,
                "lessons": host_lessons,
                "mode": host_mode,
                "num_questions": host_num_questions,
                "time_limit": host_time_limit
            }
            try:
                res = requests.post(GOOGLE_SHEET_URL, json=payload, timeout=3.0).json()
                st.success(f"🎉 Đã tạo phòng thành công! Mã phòng: **{res['roomId']}**")
            except Exception:
                st.error("Không thể kết nối máy chủ tạo phòng!")

    # KHU VỰC DANH SÁCH PHÒNG THI
    with col_join:
        st.subheader("🚪 Danh Sách Phòng Thi Hiện Có")
        try:
            rooms_res = requests.get(f"{GOOGLE_SHEET_URL}?action=get_rooms", timeout=2.5).json()
        except:
            rooms_res = []

        if not rooms_res:
            st.info("Chưa có cuộc thi nào được tạo. Hãy là người đầu tiên tạo phòng!")
        else:
            for r in rooms_res:
                with st.expander(f"📌 {r['roomId']} - Host: {r['host']} ({r['status']})"):
                    st.write(f"• **Dạng thi:** {r['mode']}")
                    st.write(f"• **Số câu:** {r['num_questions']} câu")
                    st.write(f"• **Thời gian:** {r['time_limit']} phút")
                    
                    if r['status'] == "WAITING":
                        if r['host'] == user_name:
                            if st.button(f"▶️ Bắt Đầu Thi (Host)", key=f"start_{r['roomId']}"):
                                requests.post(GOOGLE_SHEET_URL, json={"action": "start_room", "roomId": r['roomId']})
                                st.rerun()
                        else:
                            if st.button(f"🎮 Gia Nhập Phòng {r['roomId']}", key=f"join_{r['roomId']}"):
                                st.session_state.current_room = r
                                st.session_state.room_exam_started = True
                                st.rerun()
                    elif r['status'] == "STARTED":
                        st.warning("⚡ Cuộc thi đang diễn ra!")
