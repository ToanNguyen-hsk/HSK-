import streamlit as st
import random
import pandas as pd
import requests
import io
from gtts import gTTS

# 1. Cấu hình trang web
st.set_page_config(page_title="App Ôn Tập Từ Vựng HSK - MSUTONG 1 & 2", layout="centered")

# 🔗 ĐÃ TÍCH HỢP LINK GOOGLE APP SCRIPT CỦA BẠN
GOOGLE_SHEET_URL = "https://script.google.com/a/macros/pecc1.com.vn/s/AKfycbxToDszqQ08QKayKbbTouG7wzQIqDOgFtTyvJAqYcGYi3f26RYzNkLnglaoZnIigvIiyw/exec"

# CSS Tùy chỉnh làm to font chữ ở khu vực đáp án chính (main content)
st.markdown("""
    <style>
    section.main div[data-testid="stRadio"] label p {
        font-size: 28px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hàm phát âm tiếng Trung
def speak_chinese(text):
    try:
        tts = gTTS(text=text, lang='zh-CN')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3', autoplay=True)
    except Exception:
        pass

# Danh mục Tên bài học
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

# 2. Kho dữ liệu Từ vựng MSUTONG Quyển 1 & Quyển 2
VOCAB_DATA = [
    # --- QUYỂN 1 ---
    {"char": "你好", "pinyin": "nǐ hǎo", "meaning": "Xin chào", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "老师", "pinyin": "lǎoshī", "meaning": "Thầy/cô giáo", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "谢谢", "pinyin": "xièxie", "meaning": "Cảm ơn", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "再见", "pinyin": "zàijiàn", "meaning": "Tạm biệt", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "叫", "pinyin": "jiào", "meaning": "Tên là, gọi là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "名字", "pinyin": "míngzi", "meaning": "Tên", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "中国", "pinyin": "Zhōngguó", "meaning": "Trung Quốc", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "请问", "pinyin": "qǐngwèn", "meaning": "Xin hỏi", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "认识", "pinyin": "rènshi", "meaning": "Quen biết", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "去", "pinyin": "qù", "meaning": "Đi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "多少", "pinyin": "duōshao", "meaning": "Bao nhiêu", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "要", "pinyin": "yào", "meaning": "Muốn, cần", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "吃", "pinyin": "chī", "meaning": "Ăn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "工作", "pinyin": "gōngzuò", "meaning": "Làm việc, công việc", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "学习", "pinyin": "xuéxí", "meaning": "Học tập", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "银行", "pinyin": "yínháng", "meaning": "Ngân hàng", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "超市", "pinyin": "chāoshì", "meaning": "Siêu thị", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "生日", "pinyin": "shēngrì", "meaning": "Sinh nhật", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "快乐", "pinyin": "kuàilè", "meaning": "Vui vẻ", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "喜欢", "pinyin": "xǐhuan", "meaning": "Thích", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "电影", "pinyin": "diànyǐng", "meaning": "Phim", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "家", "pinyin": "jiā", "meaning": "Gia đình, nhà", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "爸爸", "pinyin": "bàba", "meaning": "Bố", "lesson": LESSON_NAMES["Q1_10"]},

    # --- QUYỂN 2 ---
    {"char": "正在", "pinyin": "zhèngzài", "meaning": "Đang (tiếp diễn)", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "听", "pinyin": "tīng", "meaning": "Nghe", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "音乐", "pinyin": "yīnyuè", "meaning": "Âm nhạc", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "起床", "pinyin": "qǐchuáng", "meaning": "Thức dậy", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "睡觉", "pinyin": "shuìjiào", "meaning": "Đi ngủ", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "可以", "pinyin": "kěyǐ", "meaning": "Có thể", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "手机", "pinyin": "shǒujī", "meaning": "Điện thoại di động", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "借", "pinyin": "jiè", "meaning": "Mượn", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "衣服", "pinyin": "yīfu", "meaning": "Quần áo", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "颜色", "pinyin": "yánsè", "meaning": "Màu sắc", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "便宜", "pinyin": "piányi", "meaning": "Rẻ", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "空儿", "pinyin": "kòngr", "meaning": "Thời gian rảnh", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "帮助", "pinyin": "bāngzhù", "meaning": "Giúp đỡ", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "参观", "pinyin": "cānguān", "meaning": "Tham quan", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "博物馆", "pinyin": "bówùguǎn", "meaning": "Bảo tàng", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "听说", "pinyin": "tīngshuō", "meaning": "Nghe nói", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "自行车", "pinyin": "zìxíngchē", "meaning": "Xe đạp", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "会", "pinyin": "huì", "meaning": "Biết (kỹ năng)", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "做菜", "pinyin": "zuò cài", "meaning": "Nấu ăn", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "建议", "pinyin": "jiànyì", "meaning": "Gợi ý", "lesson": LESSON_NAMES["Q2_9"]},
    {"char": "熊猫", "pinyin": "xióngmāo", "meaning": "Gấu trúc", "lesson": LESSON_NAMES["Q2_9"]},
    {"char": "客气", "pinyin": "kèqi", "meaning": "Khách khí", "lesson": LESSON_NAMES["Q2_10"]},
    {"char": "麻烦", "pinyin": "máfan", "meaning": "Làm phiền", "lesson": LESSON_NAMES["Q2_10"]}
]

# 3. Kho dữ liệu Mẫu câu ghép chuẩn từ sách Bài Tập Bổ Trợ
SENTENCE_DATA = [
    # QUYỂN 1
    {"words": ["王", "老师", "您", "好"], "pinyin_words": ["Wáng", "lǎoshī", "nín", "hǎo"], "lesson": LESSON_NAMES["Q1_1"]},
    {"words": ["你", "叫", "什么", "名字"], "pinyin_words": ["Nǐ", "jiào", "shénme", "míngzi"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["我", "叫", "高", "小明"], "pinyin_words": ["Wǒ", "jiào", "Gāo", "Xiǎomíng"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["你", "是", "哪", "国", "人"], "pinyin_words": ["Nǐ", "shì", "nǎ", "guó", "rén"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["他", "是", "南非", "人"], "pinyin_words": ["Tā", "shì", "Nánfēi", "rén"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["你", "的", "名字", "是", "什么"], "pinyin_words": ["Nǐ", "de", "míngzi", "shì", "shénme"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["我", "认识", "你", "很", "高兴"], "pinyin_words": ["Wǒ", "rènshi", "nǐ", "hěn", "gāoxìng"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["这", "是", "我", "的", "名片"], "pinyin_words": ["Zhè", "shì", "wǒ", "de", "míngpiàn"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["你", "是", "英国人", "吗"], "pinyin_words": ["Nǐ", "shì", "Yīngguórén", "ma"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["我", "去", "人民", "广场"], "pinyin_words": ["Wǒ", "qù", "Rénmín", "Guǎngchǎng"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["你", "是不是", "中国", "人"], "pinyin_words": ["Nǐ", "shì bu shì", "Zhōngguó", "rén"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["请问", "这个", "多少", "钱"], "pinyin_words": ["Qǐngwèn", "zhège", "duōshao", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["你", "要", "吃", "什么"], "pinyin_words": ["Nǐ", "yào", "chī", "shénme"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["我", "要", "一", "碗", "米饭", "和", "两", "杯", "茶"], "pinyin_words": ["Wǒ", "yào", "yì", "wǎn", "mǐfàn", "hé", "liǎng", "bēi", "chá"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["弟弟", "不想", "吃", "牛肉"], "pinyin_words": ["Dìdi", "bù xiǎng", "chī", "niúròu"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["她", "的", "男朋友", "是", "中国人"], "pinyin_words": ["Tā", "de", "nánpéngyou", "shì", "Zhōngguórén"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["海伦", "在", "北京", "教", "英语"], "pinyin_words": ["Hǎilún", "zài", "Běijīng", "jiāo", "Yīngyǔ"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["他", "在", "中国", "学习", "汉语"], "pinyin_words": ["Tā", "zài", "Zhōngguó", "xuéxí", "Hànyǔ"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["我", "家", "附近", "有", "书店", "超市", "和", "银行"], "pinyin_words": ["Wǒ", "jiā", "fùjìn", "yǒu", "shūdiàn", "chāoshì", "hé", "yínháng"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["往", "右", "拐", "就是", "四川", "饭店"], "pinyin_words": ["Wǎng", "yòu", "guǎi", "jiù shì", "Sìchuān", "Fàndiàn"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["今天", "是", "二零二零年", "二月", "二十九号"], "pinyin_words": ["Jīntiān", "shì", "èr líng èr líng nián", "èr yuè", "èrshíjiǔ hào"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["今天", "晚上", "我", "想", "请", "你", "看", "电影"], "pinyin_words": ["Jīntiān", "wǎnshang", "wǒ", "xiǎng", "qǐng", "nǐ", "kàn", "diànyǐng"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["你", "喜欢", "喝", "咖啡", "还是", "喝", "茶"], "pinyin_words": ["Nǐ", "xǐhuan", "hē", "kāfēi", "háishi", "hē", "chá"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["坐", "地铁", "又", "快", "又", "便宜"], "pinyin_words": ["Zuò", "dìtiě", "yòu", "kuài", "yòu", "piányi"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["我", "家", "有", "四", "口", "人"], "pinyin_words": ["Wǒ", "jiā", "yǒu", "sì", "kǒu", "rén"], "lesson": LESSON_NAMES["Q1_10"]},

    # QUYỂN 2
    {"words": ["他", "常常", "一边", "吃饭", "一边", "看", "电视"], "pinyin_words": ["Tā", "chángcháng", "yìbiān", "chī fàn", "yìbiān", "kàn", "diànshì"], "lesson": LESSON_NAMES["Q2_1"]},
    {"words": ["星期天", "上午", "九点", "在", "学校", "门口", "见"], "pinyin_words": ["Xīngqītiān", "shàngwǔ", "jiǔ diǎn", "zài", "xuéxiào", "ménkǒu", "jiàn"], "lesson": LESSON_NAMES["Q2_2"]},
    {"words": ["我", "可不可以", "借", "用", "一下", "你", "的", "笔"], "pinyin_words": ["Wǒ", "kě bu kěyǐ", "jiè", "yòng", "yíxià", "nǐ", "de", "bǐ"], "lesson": LESSON_NAMES["Q2_3"]},
    {"words": ["姐姐", "买", "了", "两", "双", "鞋"], "pinyin_words": ["Jiějie", "mǎi", "le", "liǎng", "shuāng", "xié"], "lesson": LESSON_NAMES["Q2_4"]},
    {"words": ["明天", "晚上", "我", "要", "跟", "妈妈", "一起", "去", "买", "东西"], "pinyin_words": ["Míngtiān", "wǎnshang", "wǒ", "yào", "gēn", "māma", "yìqǐ", "qù", "mǎi", "dōngxi"], "lesson": LESSON_NAMES["Q2_5"]},
    {"words": ["他", "周末", "和", "朋友", "去", "参观", "博物馆", "了"], "pinyin_words": ["Tā", "zhōumò", "hé", "péngyou", "qù", "cānguān", "bówùguǎn", "le"], "lesson": LESSON_NAMES["Q2_6"]},
    {"words": ["你", "是", "跟", "谁", "一起", "去", "的"], "pinyin_words": ["Nǐ", "shì", "gēn", "shéi", "yìqǐ", "qù", "de"], "lesson": LESSON_NAMES["Q2_7"]},
    {"words": ["除了", "英语", "以外", "我", "还", "会", "说", "汉语"], "pinyin_words": ["Chúle", "Yīngyǔ", "yǐwài", "wǒ", "hái", "huì", "shuō", "Hànyǔ"], "lesson": LESSON_NAMES["Q2_8"]},
    {"words": ["如果", "你", "感兴趣", "的", "话", "可以", "去", "动物园"], "pinyin_words": ["Rúguǒ", "nǐ", "gǎn xìngqù", "de", "huà", "kěyǐ", "qù", "dòngwùyuán"], "lesson": LESSON_NAMES["Q2_9"]},
    {"words": ["明天", "我", "去", "黄", "老师", "家", "做客"], "pinyin_words": ["Míngtiān", "wǒ", "qù", "Huáng", "lǎoshī", "jiā", "zuòkè"], "lesson": LESSON_NAMES["Q2_10"]}
]

# 4. Sidebar Tùy chỉnh
st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
all_lessons_options = list(LESSON_NAMES.values())

selected_lessons = st.sidebar.multiselect(
    "Lựa chọn bài kiểm tra:",
    options=all_lessons_options,
    default=[LESSON_NAMES["Q1_1"]]
)

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    (
        "Tất cả (Ngẫu nhiên)",
        "Dạng 1: Chữ Hán ➡️ 4 Pinyin",
        "Dạng 2: Pinyin ➡️ 4 Chữ Hán",
        "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa",
        "Dạng 4: Ghép nối câu từ Hán & Pinyin"
    )
)

start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

# 5. Quản lý trạng thái Session State & Lưu Lịch sử Điểm
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "question" not in st.session_state:
    st.session_state.question = None
if "selected_sentence_words" not in st.session_state:
    st.session_state.selected_sentence_words = []
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "answered" not in st.session_state:
    st.session_state.answered = False
if "history" not in st.session_state:
    st.session_state.history = []
if "q_id" not in st.session_state:
    st.session_state.q_id = 0

filtered_vocab = [item for item in VOCAB_DATA if item["lesson"] in selected_lessons]
filtered_sentences = [item for item in SENTENCE_DATA if item["lesson"] in selected_lessons]

def new_question():
    st.session_state.selected_sentence_words = []
    st.session_state.answered = False
    st.session_state.q_id += 1
    
    if not filtered_vocab:
        st.session_state.question = None
        return
        
    current_mode = quiz_mode
    if current_mode == "Tất cả (Ngẫu nhiên)":
        available_modes = [
            "Dạng 1: Chữ Hán ➡️ 4 Pinyin",
            "Dạng 2: Pinyin ➡️ 4 Chữ Hán",
            "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"
        ]
        if filtered_sentences:
            available_modes.append("Dạng 4: Ghép nối câu từ Hán & Pinyin")
        current_mode = random.choice(available_modes)

    if current_mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin" and not filtered_sentences:
        current_mode = "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"

    if current_mode in ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"]:
        target = random.choice(filtered_vocab)
        
        if current_mode == "Dạng 1: Chữ Hán ➡️ 4 Pinyin":
            key = "pinyin"
            wrong_options = [item["pinyin"] for item in VOCAB_DATA if item["pinyin"] != target["pinyin"]]
        elif current_mode == "Dạng 2: Pinyin ➡️ 4 Chữ Hán":
            key = "char"
            wrong_options = [item["char"] for item in VOCAB_DATA if item["char"] != target["char"]]
        else:
            key = "meaning"
            wrong_options = [item["meaning"] for item in VOCAB_DATA if item["meaning"] != target["meaning"]]
            
        distractors = random.sample(wrong_options, min(3, len(wrong_options)))
        options = distractors + [target[key]]
        random.shuffle(options)
        
        st.session_state.question = {
            "mode": current_mode,
            "target": target,
            "options": options,
            "correct_ans": target[key]
        }
        
    elif current_mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin":
        target_sent = random.choice(filtered_sentences)
        words = list(target_sent["words"])
        shuffled_words = list(words)
        while shuffled_words == words and len(words) > 1:
            random.shuffle(shuffled_words)
            
        st.session_state.question = {
            "mode": current_mode,
            "target_sent": target_sent,
            "shuffled_words": shuffled_words,
            "correct_sent": " ".join(target_sent["words"])
        }

if start_button:
    st.session_state.quiz_started = True
    st.session_state.score = 0
    st.session_state.total = 0
    new_question()
    st.rerun()

def send_to_google_sheet(is_correct):
    name = user_name.strip() if user_name.strip() else "Ẩn danh"
    mode_clean = st.session_state.question["mode"].replace(":", " -")
    payload = {"name": name, "mode": mode_clean, "is_correct": 1 if is_correct else 0}
    try:
        requests.post(GOOGLE_SHEET_URL, json=payload)
    except Exception:
        pass

def record_answer(is_correct):
    st.session_state.total += 1
    if is_correct:
        st.session_state.score += 1
    send_to_google_sheet(is_correct)

def handle_answer():
    if not st.session_state.answered:
        st.session_state.answered = True
        radio_key = f"user_choice_radio_{st.session_state.q_id}"
        user_choice = st.session_state.get(radio_key)
        is_correct = (user_choice == st.session_state.question["correct_ans"])
        record_answer(is_correct)

# --- GIAO DIỆN CHÍNH ---
st.title("🎓 App Kiểm Tra Từ Vựng & Ngữ Pháp MSUTONG")

if not st.session_state.quiz_started:
    st.info("👈 Hãy tích chọn các Bài ở danh mục bên trái, sau đó nhấn nút **🚀 Bắt đầu kiểm tra** để làm bài!")
elif not selected_lessons:
    st.warning("⚠️ Vui lòng chọn ít nhất 1 Bài ở thanh bên trái!")
elif st.session_state.question is None:
    st.warning("⚠️ Không tìm thấy dữ liệu cho bài học đã chọn!")
else:
    q = st.session_state.question
    mode = q["mode"]
    current_radio_key = f"user_choice_radio_{st.session_state.q_id}"

    if mode == "Dạng 1: Chữ Hán ➡️ 4 Pinyin":
        st.info("📌 **Dạng 1:** Hãy chọn phiên âm Pinyin đúng:")
        st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 110px; color: #1E88E5;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
        
        # 🔊 Tự động phát âm từ mới
        speak_chinese(q['target']['char'])
        
        user_choice = st.radio("Chọn Pinyin:", q["options"], key=current_radio_key, on_change=handle_answer, index=None, label_visibility="collapsed")
        
        if st.session_state.answered:
            if user_choice == q["correct_ans"]:
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Pinyin đúng của **{q['target']['char']}** là: **{q['correct_ans']}** ({q['target']['meaning']})")

    elif mode == "Dạng 2: Pinyin ➡️ 4 Chữ Hán":
        st.info("📌 **Dạng 2:** Hãy chọn Chữ Hán đúng:")
        st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 70px; color: #E65100;'>{q['target']['pinyin']}</h1>", unsafe_allow_html=True)
        
        # 🔊 Phát âm từ
        speak_chinese(q['target']['char'])

        user_choice = st.radio("Chọn Chữ Hán:", q["options"], key=current_radio_key, on_change=handle_answer, index=None, label_visibility="collapsed")
        
        if st.session_state.answered:
            if user_choice == q["correct_ans"]:
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Chữ Hán đúng của **{q['target']['pinyin']}** là: **{q['correct_ans']}** ({q['target']['meaning']})")

    elif mode == "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa":
        st.info("📌 **Dạng 3:** Chọn nghĩa Tiếng Việt chính xác:")
        st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #2E7D32;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 24px; color: gray;'>Pinyin: <b>{q['target']['pinyin']}</b></p>", unsafe_allow_html=True)
        
        # 🔊 Phát âm từ
        speak_chinese(q['target']['char'])

        user_choice = st.radio("Chọn Nghĩa:", q["options"], key=current_radio_key, on_change=handle_answer, index=None, label_visibility="collapsed")
        
        if st.session_state.answered:
            if user_choice == q["correct_ans"]:
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng là: **{q['correct_ans']}**")

    elif mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin":
        st.info("📌 **Dạng 4:** Bấm chọn từ để ghép thành câu hoàn chỉnh:")
        st.markdown(f"<p style='font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target_sent']['lesson']}</b></p>", unsafe_allow_html=True)
        pinyin_hint = " ".join(q["target_sent"]["pinyin_words"])
        st.markdown(f"<p style='font-size: 20px; color: #1565C0;'>💡 Gợi ý Pinyin: <b>{pinyin_hint}</b></p>", unsafe_allow_html=True)
        
        current_sentence = " ".join(st.session_state.selected_sentence_words)
        st.markdown(f"### Câu bạn chọn: **{current_sentence}**")
        
        cols = st.columns(len(q["shuffled_words"]))
        for idx, w in enumerate(q["shuffled_words"]):
            if cols[idx].button(w, key=f"btn_{st.session_state.q_id}_{idx}"):
                st.session_state.selected_sentence_words.append(w)
                # 🔊 Phát âm từ khi bấm vào
                speak_chinese(w)
                st.rerun()

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🔄 Xóa chọn lại"):
                st.session_state.selected_sentence_words = []
                st.rerun()
        with c2:
            if st.button("✔️ Nộp bài ghép câu"):
                if not st.session_state.answered:
                    st.session_state.answered = True
                    user_sentence = " ".join(st.session_state.selected_sentence_words)
                    is_correct = (user_sentence == q["correct_sent"])
                    record_answer(is_correct)
                    # 🔊 Phát âm toàn câu khi nộp bài
                    speak_chinese("".join(st.session_state.selected_sentence_words))
                    st.rerun()

        if st.session_state.answered:
            user_sentence = " ".join(st.session_state.selected_sentence_words)
            if user_sentence == q["correct_sent"]:
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Câu đúng là:\n\n**{q['correct_sent']}**")

    st.write("---")
    display_name = f" của **{user_name.strip()}**" if user_name.strip() else ""
    st.write(f"📊 Kết quả học tập{display_name}: **{st.session_state.score} / {st.session_state.total}** câu đúng.")
    
    if st.button("Câu tiếp theo ➡️"):
        new_question()
        st.rerun()

# 6. MỤC MỞ RỘNG "TỶ SỐ"
with st.sidebar.expander("📊 Tỷ số", expanded=False):
    try:
        res = requests.get(GOOGLE_SHEET_URL)
        sheet_data = res.json()
        
        if len(sheet_data) <= 1:
            st.write("Chưa có dữ liệu làm bài nào.")
        else:
            df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
            df["Kết quả (1=Đúng, 0=Sai)"] = pd.to_numeric(df["Kết quả (1=Đúng, 0=Sai)"])
            
            summary_df = df.groupby(["Tên", "Dạng bài"]).agg(
                Tong_Cau=("Kết quả (1=Đúng, 0=Sai)", "count"),
                Cau_Dung=("Kết quả (1=Đúng, 0=Sai)", "sum")
            ).reset_index()
            
            summary_df["Ty_Le_Dung_%"] = (summary_df["Cau_Dung"] / summary_df["Tong_Cau"] * 100).round(1)
            
            st.write("**Bảng xếp hạng toàn bộ người làm (%)**")
            st.dataframe(
                summary_df[["Tên", "Dạng bài", "Ty_Le_Dung_%", "Cau_Dung", "Tong_Cau"]],
                column_config={
                    "Tên": "Tên",
                    "Dạng bài": "Dạng bài",
                    "Ty_Le_Dung_%": "Tỷ lệ đúng (%)",
                    "Cau_Dung": "Đúng",
                    "Tong_Cau": "Tổng câu"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.write("**Biểu đồ so sánh Tỷ lệ đúng (%)**")
            chart_data = summary_df.pivot(index="Tên", columns="Dạng bài", values="Ty_Le_Dung_%").fillna(0)
            chart_data.columns = [str(col).replace("➡️", "->") for col in chart_data.columns]
            st.bar_chart(chart_data)
    except Exception:
        st.write("Đang kết nối tới máy chủ...")
