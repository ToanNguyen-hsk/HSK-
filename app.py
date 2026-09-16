# -*- coding: utf-8 -*-
import streamlit as st
import random
import pandas as pd
import requests
import base64
from io import BytesIO
from gtts import gTTS

# 1. Cấu hình trang web
st.set_page_config(page_title="App Ôn Tập Từ Vựng HSK - MSUTONG 1 & 2", layout="centered")

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbxcnKRCCcd-iIkzspRGjS4jnwdCU3A25FwAVCBWlmJHMKT2le5kYd22O3i-V-fv3c0V/exec"

st.markdown("""
    <style>
    section.main div[data-testid="stRadio"] label p {
        font-size: 28px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hàm tạo âm thanh MP3 trực tiếp từ Google TTS
def get_audio_html(text, autoplay=True):
    if not text:
        return ""
    try:
        tts = gTTS(text=text, lang='zh-CN', slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        autoplay_attr = "autoplay" if autoplay else ""
        random_id = random.randint(10000, 99999)
        audio_html = f'''
            <div style="text-align: center; margin: 10px 0;">
                <audio controls {autoplay_attr} id="aud_{random_id}" style="height: 40px; width: 280px;">
                    <source src="data:audio/mp3;base64,{b64_audio}?v={random_id}" type="audio/mp3">
                    Trình duyệt không hỗ trợ phát âm thanh.
                </audio>
            </div>
        '''
        return audio_html
    except Exception:
        return ""

# Danh mục Tên bài học chuẩn MSUTONG
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

# 2. BẢNG TỪ VỰNG TỔNG HỢP TOÀN BỘ TỪ MỚI & TỪ BỔ SUNG (补充词语)
VOCAB_DATA = [
    # --- QUYỂN 1: BÀI 1 ---
    {"char": "你好", "pinyin": "nǐ hǎo", "meaning": "xin chào", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "您", "pinyin": "nín", "meaning": "ngài, ông, bà", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "你们", "pinyin": "nǐmen", "meaning": "các bạn", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "老师", "pinyin": "lǎoshī", "meaning": "thầy/cô giáo", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "对不起", "pinyin": "duìbuqǐ", "meaning": "xin lỗi", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "没关系", "pinyin": "méi guānxi", "meaning": "không sao", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "谢谢", "pinyin": "xièxie", "meaning": "cảm ơn", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "不客气", "pinyin": "bú kèqi", "meaning": "không có gì", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "再见", "pinyin": "zàijiàn", "meaning": "tạm biệt", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "王", "pinyin": "Wáng", "meaning": "họ Vương", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "大卫", "pinyin": "Dàwèi", "meaning": "David (tên riêng)", "lesson": LESSON_NAMES["Q1_1"]},

    # --- QUYỂN 1: BÀI 2 ---
    {"char": "叫", "pinyin": "jiào", "meaning": "gọi, tên là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "什么", "pinyin": "shénme", "meaning": "gì, cái gì", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "名字", "pinyin": "míngzi", "meaning": "tên", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "我", "pinyin": "wǒ", "meaning": "tôi", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "呢", "pinyin": "ne", "meaning": "trợ từ ngữ khí (còn...thì sao)", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "是", "pinyin": "shì", "meaning": "là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "哪", "pinyin": "nǎ", "meaning": "nào", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "国", "pinyin": "guó", "meaning": "quốc gia, nước", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "人", "pinyin": "rén", "meaning": "người", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "卡玛拉", "pinyin": "Kǎmǎlā", "meaning": "Kamala (tên riêng)", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "高小明", "pinyin": "Gāo Xiǎomíng", "meaning": "Cao Tiểu Minh", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "南非", "pinyin": "Nánfēi", "meaning": "Nam Phi", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "中国", "pinyin": "Zhōngguó", "meaning": "Trung Quốc", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "英国", "pinyin": "Yīngguó", "meaning": "nước Anh", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "美国", "pinyin": "Měiguó", "meaning": "nước Mỹ", "lesson": LESSON_NAMES["Q1_2"]},

    # --- QUYỂN 1: BÀI 3 ---
    {"char": "请问", "pinyin": "qǐngwèn", "meaning": "xin hỏi", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "贵姓", "pinyin": "guìxìng", "meaning": "quý danh, quý họ", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "姓", "pinyin": "xìng", "meaning": "họ", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "这", "pinyin": "zhè", "meaning": "đây, này", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "名片", "pinyin": "míngpiàn", "meaning": "danh thiếp", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "很高兴", "pinyin": "gāoxìng", "meaning": "vui mừng, phấn khởi", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "认识", "pinyin": "rènshi", "meaning": "quen biết, quen", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "不", "pinyin": "bù", "meaning": "không", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "贵", "pinyin": "guì", "meaning": "quý", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "也", "pinyin": "yě", "meaning": "cũng", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "吗", "pinyin": "ma", "meaning": "trợ từ nghi vấn", "lesson": LESSON_NAMES["Q1_3"]},

    # --- QUYỂN 1: BÀI 4 ---
    {"char": "小姐", "pinyin": "xiǎojiě", "meaning": "cô, tiểu thư", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "师傅", "pinyin": "shīfu", "meaning": "bác tài, thợ", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "去", "pinyin": "qù", "meaning": "đi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "哪儿", "pinyin": "nǎr", "meaning": "đâu, ở đâu", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "人民", "pinyin": "rénmín", "meaning": "nhân dân", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "广场", "pinyin": "guǎngchǎng", "meaning": "quảng trường", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "知道", "pinyin": "zhīdào", "meaning": "biết", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "了", "pinyin": "le", "meaning": "rồi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "远", "pinyin": "yuǎn", "meaning": "xa", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "近", "pinyin": "jìn", "meaning": "gần", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "到", "pinyin": "dào", "meaning": "đến, tới", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "多少", "pinyin": "duōshao", "meaning": "bao nhiêu", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "钱", "pinyin": "qián", "meaning": "tiền", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "块", "pinyin": "kuài", "meaning": "đồng (lượng từ tiền)", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "客气", "pinyin": "kèqi", "meaning": "khách sáo", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "再", "pinyin": "zài", "meaning": "lại", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "坐", "pinyin": "zuò", "meaning": "ngồi, đi (xe)", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "出租车", "pinyin": "chūzūchē", "meaning": "xe taxi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "公共汽车", "pinyin": "gōnggòng qìchē", "meaning": "xe buýt", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "打车", "pinyin": "dǎ chē", "meaning": "gọi xe, bắt xe", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "地铁", "pinyin": "dìtiě", "meaning": "tàu điện ngầm", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "银行", "pinyin": "yínháng", "meaning": "ngân hàng", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "公安局", "pinyin": "gōng'ān jú", "meaning": "sở công an", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "饭店", "pinyin": "fàndiàn", "meaning": "nhà hàng, khách sạn", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "邮局", "pinyin": "yóujú", "meaning": "bưu điện", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "宾馆", "pinyin": "bīnguǎn", "meaning": "khách sạn", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "饭馆儿", "pinyin": "fànguǎnr", "meaning": "nhà hàng", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "洗手间", "pinyin": "xǐshǒujiān", "meaning": "nhà vệ sinh", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "厕所", "pinyin": "cèsuǒ", "meaning": "nhà vệ sinh", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "飞机场", "pinyin": "fēijīchǎng", "meaning": "sân bay", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "火车站", "pinyin": "huǒchēzhàn", "meaning": "ga tàu hỏa", "lesson": LESSON_NAMES["Q1_4"]},

    # --- QUYỂN 1: BÀI 5 ---
    {"char": "要", "pinyin": "yào", "meaning": "muốn, cần", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "吃", "pinyin": "chī", "meaning": "ăn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "一点儿", "pinyin": "yìdiǎnr", "meaning": "một chút, một ít", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "个", "pinyin": "gè", "meaning": "cái, chiếc", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "牛肉", "pinyin": "niúròu", "meaning": "thịt bò", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "青菜", "pinyin": "qīngcài", "meaning": "rau xanh", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "还", "pinyin": "hái", "meaning": "còn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "两", "pinyin": "liǎng", "meaning": "hai (số lượng)", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "碗", "pinyin": "wǎn", "meaning": "bát, chén", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "米饭", "pinyin": "mǐfàn", "meaning": "cơm", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "快", "pinyin": "kuài", "meaning": "nhanh", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "饿", "pinyin": "è", "meaning": "đói", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "喝", "pinyin": "hē", "meaning": "uống", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "杯", "pinyin": "bēi", "meaning": "cốc, ly", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "奶茶", "pinyin": "nǎichá", "meaning": "trà sữa", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "大", "pinyin": "dà", "meaning": "to, lớn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "还是", "pinyin": "háishi", "meaning": "hay là", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "小", "pinyin": "xiǎo", "meaning": "nhỏ, bé", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "咖啡", "pinyin": "kāfēi", "meaning": "cà phê", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "一共", "pinyin": "yígòng", "meaning": "tổng cộng", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "包子", "pinyin": "bāozi", "meaning": "bánh bao", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "饺子", "pinyin": "jiǎozi", "meaning": "bánh sủi cáo", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "面条", "pinyin": "miàntiáo", "meaning": "mì sợi", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "水", "pinyin": "shuǐ", "meaning": "nước", "lesson": LESSON_NAMES["Q1_5"]},

    # --- QUYỂN 1: BÀI 6 ---
    {"char": "在", "pinyin": "zài", "meaning": "ở, tại", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "工作", "pinyin": "gōngzuò", "meaning": "công việc, làm việc", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "苹果", "pinyin": "píngguǒ", "meaning": "quả táo / Apple", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "公司", "pinyin": "gōngsī", "meaning": "công ty", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "留学生", "pinyin": "liúxuéshēng", "meaning": "lưu học sinh", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "学生", "pinyin": "xuéshēng", "meaning": "học sinh, sinh viên", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "这儿", "pinyin": "zhèr", "meaning": "ở đây", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "学习", "pinyin": "xuéxí", "meaning": "học tập", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "汉语", "pinyin": "Hànyǔ", "meaning": "tiếng Hán", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "对", "pinyin": "duì", "meaning": "đúng", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "男朋友", "pinyin": "nánpéngyou", "meaning": "bạn trai", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "做", "pinyin": "zuò", "meaning": "làm", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "大学", "pinyin": "dàxué", "meaning": "đại học", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "教", "pinyin": "jiāo", "meaning": "dạy", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "英语", "pinyin": "Yīngyǔ", "meaning": "tiếng Anh", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "女朋友", "pinyin": "nǚpéngyou", "meaning": "bạn gái", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "医院", "pinyin": "yīyuàn", "meaning": "bệnh viện", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "医生", "pinyin": "yīshēng", "meaning": "bác sĩ", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "经理", "pinyin": "jīnglǐ", "meaning": "giám đốc", "lesson": LESSON_NAMES["Q1_6"]},

    # --- QUYỂN 1: BÀI 7 ---
    {"char": "附近", "pinyin": "fùjìn", "meaning": "gần đây, lân cận", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "银行", "pinyin": "yínháng", "meaning": "ngân hàng", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "家", "pinyin": "jiā", "meaning": "lượng từ (nhà hàng, cửa hàng)", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "从", "pinyin": "cóng", "meaning": "từ", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "往", "pinyin": "wǎng", "meaning": "hướng, đi về phía", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "前", "pinyin": "qián", "meaning": "phía trước", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "走", "pinyin": "zǒu", "meaning": "đi", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "然后", "pinyin": "ránhòu", "meaning": "sau đó", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "左", "pinyin": "zuǒ", "meaning": "trái", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "拐", "pinyin": "guǎi", "meaning": "rẽ", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "饭店", "pinyin": "fàndiàn", "meaning": "nhà hàng, khách sạn", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "就", "pinyin": "jiù", "meaning": "chính là, ngay", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "对面", "pinyin": "duìmiàn", "meaning": "đối diện", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "书店", "pinyin": "shūdiàn", "meaning": "nhà sách", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "超市", "pinyin": "chāoshì", "meaning": "siêu thị", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "右", "pinyin": "yòu", "meaning": "phải", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "旁", "pinyin": "páng", "meaning": "bên cạnh", "lesson": LESSON_NAMES["Q1_7"]},

    # --- QUYỂN 1: BÀI 8 ---
    {"char": "今天", "pinyin": "jīntiān", "meaning": "hôm nay", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "真", "pinyin": "zhēn", "meaning": "thật", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "漂亮", "pinyin": "piàoliang", "meaning": "xinh đẹp", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "事", "pinyin": "shì", "meaning": "chuyện, việc", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "生日", "pinyin": "shēngrì", "meaning": "sinh nhật", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "几", "pinyin": "jǐ", "meaning": "mấy", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "号", "pinyin": "hào", "meaning": "ngày", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "月", "pinyin": "yuè", "meaning": "tháng", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "快乐", "pinyin": "kuàilè", "meaning": "vui vẻ", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "星期", "pinyin": "xīngqī", "meaning": "tuần, thứ", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "空儿", "pinyin": "kòngr", "meaning": "thời gian rảnh", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "想", "pinyin": "xiǎng", "meaning": "muốn, nghĩ", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "请", "pinyin": "qǐng", "meaning": "mời", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "晚饭", "pinyin": "wǎnfàn", "meaning": "bữa tối", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "昨天", "pinyin": "zuótiān", "meaning": "hôm qua", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "明天", "pinyin": "míngtiān", "meaning": "ngày mai", "lesson": LESSON_NAMES["Q1_8"]},

    # --- QUYỂN 1: BÀI 9 ---
    {"char": "喜欢", "pinyin": "xǐhuan", "meaning": "thích", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "吧", "pinyin": "ba", "meaning": "trợ từ (nhé, đi)", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "平时", "pinyin": "píngshí", "meaning": "ngày thường, bình thường", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "怎么", "pinyin": "zěnme", "meaning": "thế nào, bằng cách nào", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "坐", "pinyin": "zuò", "meaning": "ngồi, đi (xe)", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "地铁", "pinyin": "dìtiě", "meaning": "tàu điện ngầm", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "走路", "pinyin": "zǒu lù", "meaning": "đi bộ", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "出租车", "pinyin": "chūzūchē", "meaning": "xe taxi", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "电影", "pinyin": "diànyǐng", "meaning": "phim", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "电影院", "pinyin": "diànyǐngyuàn", "meaning": "rạp chiếu phim", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "菜", "pinyin": "cài", "meaning": "đồ ăn, món ăn", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "都", "pinyin": "dōu", "meaning": "đều", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "非常", "pinyin": "fēicháng", "meaning": "rất, cực kỳ", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "公交车", "pinyin": "gōngjiāochē", "meaning": "xe buýt", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "好吃", "pinyin": "hǎochī", "meaning": "ngon", "lesson": LESSON_NAMES["Q1_9"]},

    # --- QUYỂN 1: BÀI 10 ---
    {"char": "口", "pinyin": "kǒu", "meaning": "lượng từ (thành viên gia đình)", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "爸爸", "pinyin": "bàba", "meaning": "bố", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "妈妈", "pinyin": "māma", "meaning": "mẹ", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "哥哥", "pinyin": "gēge", "meaning": "anh trai", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "姐姐", "pinyin": "jiějie", "meaning": "chị gái", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "弟弟", "pinyin": "dìdi", "meaning": "em trai", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "妹妹", "pinyin": "mèimei", "meaning": "em gái", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "岁", "pinyin": "suì", "meaning": "tuổi", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "可爱", "pinyin": "kě'ài", "meaning": "đáng yêu", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "狗", "pinyin": "gǒu", "meaning": "con chó", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "猫", "pinyin": "māo", "meaning": "con mèo", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "多大", "pinyin": "duō dà", "meaning": "bao nhiêu tuổi", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "和", "pinyin": "hé", "meaning": "và", "lesson": LESSON_NAMES["Q1_10"]},

    # --- QUYỂN 2: BÀI 1 -> 10 ---
    {"char": "正在", "pinyin": "zhèngzài", "meaning": "đang", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "听", "pinyin": "tīng", "meaning": "nghe", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "音乐", "pinyin": "yīnyuè", "meaning": "âm nhạc", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "起床", "pinyin": "qǐchuáng", "meaning": "thức dậy", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "睡觉", "pinyin": "shuìjiào", "meaning": "đi ngủ", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "可以", "pinyin": "kěyǐ", "meaning": "có thể", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "手机", "pinyin": "shǒujī", "meaning": "điện thoại", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "借", "pinyin": "jiè", "meaning": "mượn", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "衣服", "pinyin": "yīfu", "meaning": "quần áo", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "便宜", "pinyin": "piányi", "meaning": "rẻ", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "空儿", "pinyin": "kòngr", "meaning": "thời gian rảnh", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "博物馆", "pinyin": "bówùguǎn", "meaning": "bảo tàng", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "自行车", "pinyin": "zìxíngchē", "meaning": "xe đạp", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "做菜", "pinyin": "zuò cài", "meaning": "nấu ăn", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "熊猫", "pinyin": "xióngmāo", "meaning": "gấu trúc", "lesson": LESSON_NAMES["Q2_9"]},
    {"char": "麻烦", "pinyin": "máfan", "meaning": "làm phiền", "lesson": LESSON_NAMES["Q2_10"]}
]

# 3. KHO CÂU ĐẦY ĐỦ CHO TẤT CẢ CÁC BÀI
SENTENCE_DATA = [
    # Q1_1
    {"words": ["王", "老师", "您", "好"], "pinyin_words": ["Wáng", "lǎoshī", "nín", "hǎo"], "lesson": LESSON_NAMES["Q1_1"]},
    {"words": ["大卫", "你好", "再见"], "pinyin_words": ["Dàwèi", "nǐ hǎo", "zàijiàn"], "lesson": LESSON_NAMES["Q1_1"]},
    {"words": ["对不起", "没关系"], "pinyin_words": ["Duìbuqǐ", "méi guānxi"], "lesson": LESSON_NAMES["Q1_1"]},
    {"words": ["谢谢", "你", "不客气"], "pinyin_words": ["Xièxie", "nǐ", "bú kèqi"], "lesson": LESSON_NAMES["Q1_1"]},
    
    # Q1_2
    {"words": ["你", "叫", "什么", "名字"], "pinyin_words": ["Nǐ", "jiào", "shénme", "míngzi"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["我", "叫", "高", "小明"], "pinyin_words": ["Wǒ", "jiào", "Gāo", "Xiǎomíng"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["你", "是", "哪", "国", "人"], "pinyin_words": ["Nǐ", "shì", "nǎ", "guó", "rén"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["他", "是", "南非", "人"], "pinyin_words": ["Tā", "shì", "Nánfēi", "rén"], "lesson": LESSON_NAMES["Q1_2"]},
    {"words": ["卡玛拉", "是", "留学生", "吗"], "pinyin_words": ["Kǎmǎlā", "shì", "liúxuéshēng", "ma"], "lesson": LESSON_NAMES["Q1_2"]},
    
    # Q1_3
    {"words": ["请问", "您", "贵姓"], "pinyin_words": ["Qǐngwèn", "nín", "guìxìng"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["我", "认识", "你", "很", "高兴"], "pinyin_words": ["Wǒ", "rènshi", "nǐ", "hěn", "gāoxìng"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["这", "是", "我", "的", "名片"], "pinyin_words": ["Zhè", "shì", "wǒ", "de", "míngpiàn"], "lesson": LESSON_NAMES["Q1_3"]},
    {"words": ["你", "是", "英国人", "吗"], "pinyin_words": ["Nǐ", "shì", "Yīngguórén", "ma"], "lesson": LESSON_NAMES["Q1_3"]},
    
    # Q1_4
    {"words": ["我", "去", "人民", "广场"], "pinyin_words": ["Wǒ", "qù", "Rénmín", "Guǎngchǎng"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["请问", "这个", "多少", "钱"], "pinyin_words": ["Qǐngwèn", "zhège", "duōshao", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["师傅", "去", "飞机场", "远", "不", "远"], "pinyin_words": ["Shīfu", "qù", "fēijīchǎng", "yuǎn", "bù", "yuǎn"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["一共", "是", "五十", "块", "钱"], "pinyin_words": ["Yígòng", "shì", "wǔshí", "kuài", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["到", "火车站", "坐", "地铁"], "pinyin_words": ["Dào", "huǒchēzhàn", "zuò", "dìtiě"], "lesson": LESSON_NAMES["Q1_4"]},
    
    # Q1_5
    {"words": ["你", "要", "吃", "什么"], "pinyin_words": ["Nǐ", "yào", "chī", "shénme"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["我", "要", "一", "碗", "米饭"], "pinyin_words": ["Wǒ", "yào", "yì", "wǎn", "mǐfàn"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["我", "要", "两", "杯", "珍珠", "奶茶"], "pinyin_words": ["Wǒ", "yào", "liǎng", "bēi", "zhēnzhū", "nǎichá"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["弟弟", "不想", "吃", "牛肉"], "pinyin_words": ["Dìdi", "bù xiǎng", "chī", "niúròu"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["请", "快点儿", "我", "很", "饿"], "pinyin_words": ["Qǐng", "kuàidiǎnr", "wǒ", "hěn", "è"], "lesson": LESSON_NAMES["Q1_5"]},
    
    # Q1_6
    {"words": ["她", "的", "男朋友", "是", "中国人"], "pinyin_words": ["Tā", "de", "nánpéngyou", "shì", "Zhōngguórén"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["海伦", "在", "北京", "教", "英语"], "pinyin_words": ["Hǎilún", "zài", "Běijīng", "jiāo", "Yīngyǔ"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["马文", "在", "苹果", "公司", "工作"], "pinyin_words": ["Mǎwén", "zài", "Píngguǒ", "gōngsī", "gōngzuò"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["他", "在", "中国", "学习", "汉语"], "pinyin_words": ["Tā", "zài", "Zhōngguó", "xuéxí", "Hànyǔ"], "lesson": LESSON_NAMES["Q1_6"]},
    
    # Q1_7
    {"words": ["我", "家", "附近", "有", "超市", "和", "银行"], "pinyin_words": ["Wǒ", "jiā", "fùjìn", "yǒu", "chāoshì", "hé", "yínháng"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["从", "这儿", "往前走", "往", "右", "拐"], "pinyin_words": ["Cóng", "zhèr", "wǎng", "qián", "zǒu", "wǎng", "yòu", "guǎi"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["中国", "银行", "就在", "饭店", "对面"], "pinyin_words": ["Zhōngguó", "Yínháng", "jiù zài", "fàndiàn", "duìmiàn"], "lesson": LESSON_NAMES["Q1_7"]},
    
    # Q1_8
    {"words": ["今天", "是", "二零二零年", "二月", "二十九号"], "pinyin_words": ["Jīntiān", "shì", "èr líng èr líng nián", "èr yuè", "èrshíjiǔ hào"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["今天", "晚上", "我", "想", "请", "你", "看", "电影"], "pinyin_words": ["Jīntiān", "wǎnshang", "wǒ", "xiǎng", "qǐng", "nǐ", "kàn", "diànyǐng"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["祝", "你", "生日", "快乐"], "pinyin_words": ["Zhù", "nǐ", "shēngrì", "kuàilè"], "lesson": LESSON_NAMES["Q1_8"]},
    
    # Q1_9
    {"words": ["你", "喜欢", "喝", "咖啡", "还是", "喝", "茶"], "pinyin_words": ["Nǐ", "xǐhuan", "hē", "kāfēi", "háishi", "hē", "chá"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["坐", "地铁", "又", "快", "又", "便宜"], "pinyin_words": ["Zuò", "dìtiě", "yòu", "kuài", "yòu", "piányi"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["我们", "坐", "出租车", "去", "电影院", "吧"], "pinyin_words": ["Wǒmen", "zuò", "chūzūchē", "qù", "diànyǐngyuàn", "ba"], "lesson": LESSON_NAMES["Q1_9"]},
    
    # Q1_10
    {"words": ["你", "家", "有", "几", "口", "人"], "pinyin_words": ["Nǐ", "jiā", "yǒu", "jǐ", "kǒu", "rén"], "lesson": LESSON_NAMES["Q1_10"]},
    {"words": ["我", "家", "有", "四", "口", "人"], "pinyin_words": ["Wǒ", "jiā", "yǒu", "sì", "kǒu", "rén"], "lesson": LESSON_NAMES["Q1_10"]},
    {"words": ["我", "妹妹", "今年", "十", "岁", "很", "可爱"], "pinyin_words": ["Wǒ", "mèimei", "jīnnián", "shí", "suì", "hěn", "kě'ài"], "lesson": LESSON_NAMES["Q1_10"]},
    {"words": ["我", "爸爸", "是", "律师", "妈妈", "是", "医生"], "pinyin_words": ["Wǒ", "bàba", "shì", "lǜshī", "māma", "shì", "yīshēng"], "lesson": LESSON_NAMES["Q1_10"]},
    {"words": ["上海", "和", "北京", "都", "是", "大城市"], "pinyin_words": ["Shànghǎi", "hé", "Běijīng", "dōu", "shì", "dà chéngshì"], "lesson": LESSON_NAMES["Q1_10"]},

    # QUYỂN 2
    {"words": ["他", "常常", "一边", "吃饭", "一边", "看", "电视"], "pinyin_words": ["Tā", "chángcháng", "yìbiān", "chī fàn", "yìbiān", "kàn", "diànshì"], "lesson": LESSON_NAMES["Q2_1"]},
    {"words": ["你", "平时", "几点", "起床"], "pinyin_words": ["Nǐ", "píngshí", "jǐ diǎn", "qǐchuáng"], "lesson": LESSON_NAMES["Q2_2"]},
    {"words": ["我", "可以", "用", "一下", "你", "的", "手机", "吗"], "pinyin_words": ["Wǒ", "kěyǐ", "yòng", "yíxià", "nǐ", "de", "shǒujī", "ma"], "lesson": LESSON_NAMES["Q2_3"]},
    {"words": ["这", "件", "衣服", "太", "贵", "了"], "pinyin_words": ["Zhè", "jiàn", "yīfu", "tài", "guì", "le"], "lesson": LESSON_NAMES["Q2_4"]},
    {"words": ["你", "周末", "什么时候", "有", "空儿"], "pinyin_words": ["Nǐ", "zhōumò", "shénme shíhou", "yǒu", "kòngr"], "lesson": LESSON_NAMES["Q2_5"]},
    {"words": ["我", "参观", "了", "上海", "博物馆"], "pinyin_words": ["Wǒ", "cānguān", "le", "Shànghǎi", "bówùguǎn"], "lesson": LESSON_NAMES["Q2_6"]},
    {"words": ["我们", "是", "骑", "自行车", "去", "的"], "pinyin_words": ["Wǒmen", "shì", "qí", "zìxíngchē", "qù", "de"], "lesson": LESSON_NAMES["Q2_7"]},
    {"words": ["除了", "英语", "以外", "我", "还", "会", "说", "汉语"], "pinyin_words": ["Chúle", "Yīngyǔ", "yǐwài", "wǒ", "hái", "huì", "shuō", "Hànyǔ"], "lesson": LESSON_NAMES["Q2_8"]},
    {"words": ["如果", "你", "感兴趣", "的", "话", "可以", "去", "动物园"], "pinyin_words": ["Rúguǒ", "nǐ", "gǎn xìngqù", "de", "huà", "kěyǐ", "qù", "dòngwùyuán"], "lesson": LESSON_NAMES["Q2_9"]},
    {"words": ["今天", "真", "是", "给", "您", "添", "麻烦", "了"], "pinyin_words": ["Jīntiān", "zhēn", "shì", "gěi", "nín", "tiān", "máfan", "le"], "lesson": LESSON_NAMES["Q2_10"]}
]

# Sidebar UI
st.sidebar.title("👤 Thông Tin Người Làm")
user_name = st.sidebar.text_input("Họ và tên (không bắt buộc):", placeholder="Nhập tên của bạn...")

st.sidebar.title("⚙️ Tùy Chỉnh Bài Học")
all_lessons_options = list(LESSON_NAMES.values())
selected_lessons = st.sidebar.multiselect("Lựa chọn bài kiểm tra:", options=all_lessons_options, default=[LESSON_NAMES["Q1_4"]])

st.sidebar.title("🎯 Dạng Bài Tập")
quiz_mode = st.sidebar.radio(
    "Chọn dạng bài kiểm tra:",
    ("Tất cả (Ngẫu nhiên)", "Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa", "Dạng 4: Ghép nối câu từ Hán & Pinyin")
)

start_button = st.sidebar.button("🚀 Bắt đầu kiểm tra", use_container_width=True)

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
if "q_id" not in st.session_state:
    st.session_state.q_id = 0
if "vocab_deck" not in st.session_state:
    st.session_state.vocab_deck = []
if "sentence_deck" not in st.session_state:
    st.session_state.sentence_deck = []
if "last_selected_lessons" not in st.session_state:
    st.session_state.last_selected_lessons = []
if "speech_target" not in st.session_state:
    st.session_state.speech_target = ""

filtered_vocab = [item for item in VOCAB_DATA if item["lesson"] in selected_lessons]
filtered_sentences = [item for item in SENTENCE_DATA if item["lesson"] in selected_lessons]

def new_question():
    st.session_state.selected_sentence_words = []
    st.session_state.answered = False
    st.session_state.speech_target = ""
    st.session_state.q_id += 1
    
    if not filtered_vocab:
        st.session_state.question = None
        return
        
    current_mode = quiz_mode
    if current_mode == "Tất cả (Ngẫu nhiên)":
        available_modes = ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"]
        if filtered_sentences:
            available_modes.append("Dạng 4: Ghép nối câu từ Hán & Pinyin")
        current_mode = random.choice(available_modes)

    if current_mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin" and not filtered_sentences:
        current_mode = "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"

    if current_mode in ["Dạng 1: Chữ Hán ➡️ 4 Pinyin", "Dạng 2: Pinyin ➡️ 4 Chữ Hán", "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa"]:
        if st.session_state.last_selected_lessons != selected_lessons or not st.session_state.vocab_deck:
            st.session_state.vocab_deck = list(filtered_vocab)
            random.shuffle(st.session_state.vocab_deck)
            st.session_state.last_selected_lessons = list(selected_lessons)
            
        target = st.session_state.vocab_deck.pop()
        
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
        st.session_state.speech_target = target["char"]
        
    elif current_mode == "Dạng 4: Ghép nối câu từ Hán & Pinyin":
        if not st.session_state.sentence_deck:
            st.session_state.sentence_deck = list(filtered_sentences)
            random.shuffle(st.session_state.sentence_deck)
            
        target_sent = st.session_state.sentence_deck.pop()
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
    st.session_state.vocab_deck = list(filtered_vocab)
    random.shuffle(st.session_state.vocab_deck)
    st.session_state.sentence_deck = list(filtered_sentences)
    random.shuffle(st.session_state.sentence_deck)
    st.session_state.last_selected_lessons = list(selected_lessons)
    new_question()
    st.rerun()

def send_to_google_sheet(is_correct):
    name = user_name.strip() if user_name.strip() else "Ẩn danh"
    mode_clean = st.session_state.question["mode"].replace(":", " -")
    payload = {"name": name, "mode": mode_clean, "is_correct": 1 if is_correct else 0}
    try:
        requests.post(GOOGLE_SHEET_URL, json=payload, timeout=2.5)
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
        
        play_audio_js(q['target']['char'])
        
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

        user_choice = st.radio("Chọn Chữ Hán:", q["options"], key=current_radio_key, on_change=handle_answer, index=None, label_visibility="collapsed")
        
        if st.session_state.answered:
            play_audio_js(q['target']['char'])
            if user_choice == q["correct_ans"]:
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Chữ Hán đúng của **{q['target']['pinyin']}** là: **{q['correct_ans']}** ({q['target']['meaning']})")

    elif mode == "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa":
        st.info("📌 **Dạng 3:** Chọn nghĩa Tiếng Việt chính xác:")
        st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #2E7D32;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 24px; color: gray;'>Pinyin: <b>{q['target']['pinyin']}</b></p>", unsafe_allow_html=True)

        play_audio_js(q['target']['char'])

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
        
        if st.session_state.speech_target:
            play_audio_js(st.session_state.speech_target)

        cols = st.columns(len(q["shuffled_words"]))
        for idx, w in enumerate(q["shuffled_words"]):
            if cols[idx].button(w, key=f"btn_{st.session_state.q_id}_{idx}"):
                st.session_state.selected_sentence_words.append(w)
                st.session_state.speech_target = w
                st.rerun()

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🔄 Xóa chọn lại"):
                st.session_state.selected_sentence_words = []
                st.session_state.speech_target = ""
                st.rerun()
        with c2:
            if st.button("✔️ Nộp bài ghép câu"):
                if not st.session_state.answered:
                    st.session_state.answered = True
                    user_sentence = " ".join(st.session_state.selected_sentence_words)
                    is_correct = (user_sentence == q["correct_sent"])
                    record_answer(is_correct)
                    st.session_state.speech_target = "".join(st.session_state.selected_sentence_words)
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

# BẢNG TỶ SỐ
with st.sidebar.expander("📊 Bảng Xếp Hạng Tỷ Số", expanded=False):
    try:
        res = requests.get(GOOGLE_SHEET_URL, timeout=2.5)
        sheet_data = res.json()
        if len(sheet_data) <= 1:
            st.write("Chưa có dữ liệu làm bài nào.")
        else:
            df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
            df["is_correct"] = pd.to_numeric(df["Kết quả (1=Đúng, 0=Sai)"])
            
            summary_df = df.groupby(["Tên", "Dạng bài"]).agg(
                Tong_Cau=("is_correct", "count"),
                Cau_Dung=("is_correct", "sum")
            ).reset_index()
            
            summary_df["Ty_Le_Dung_%"] = (summary_df["Cau_Dung"] / summary_df["Tong_Cau"] * 100).round(1)
            
            st.write("**Bảng xếp hạng thi đua (%)**")
            st.dataframe(
                summary_df[["Tên", "Dạng bài", "Ty_Le_Dung_%", "Cau_Dung", "Tong_Cau"]],
                column_config={
                    "Tên": "Họ & Tên",
                    "Dạng bài": "Dạng bài",
                    "Ty_Le_Dung_%": "Tỷ lệ đúng (%)",
                    "Cau_Dung": "Đúng",
                    "Tong_Cau": "Tổng"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.write("**Biểu đồ Tỷ lệ đúng (%)**")
            chart_data = summary_df.pivot(index="Tên", columns="Dạng bài", values="Ty_Le_Dung_%").fillna(0)
            chart_data.columns = [str(col).replace("➡️", "->") for col in chart_data.columns]
            st.bar_chart(chart_data)
    except Exception:
        st.write("Đang kết nối bảng xếp hạng...")
