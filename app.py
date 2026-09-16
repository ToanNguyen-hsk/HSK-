import streamlit as st
import random
import pandas as pd

# 1. Cấu hình trang web
st.set_page_config(page_title="App Ôn Tập Từ Vựng HSK - MSUTONG 1 & 2", layout="centered")

# CSS Tùy chỉnh: Làm to font chữ ở khu vực đáp án chính
st.markdown("""
    <style>
    section.main div[data-testid="stRadio"] label p {
        font-size: 28px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    </style>
""", unsafe_allow_html=True)

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

# 2. ĐẦY ĐỦ KHO TỪ VỰNG MSUTONG QUYỂN 1 & 2 (Đã chuẩn hóa & không lặp lại)
VOCAB_DATA = [
    # --- QUYỂN 1: BÀI 1 ---
    {"char": "你", "pinyin": "nǐ", "meaning": "Bạn, anh, chị", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "好", "pinyin": "hǎo", "meaning": "Tốt, đẹp, hay", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "老师", "pinyin": "lǎoshī", "meaning": "Thầy/cô giáo", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "您", "pinyin": "nín", "meaning": "Ngài, ông, bà (kính trọng)", "lesson": LESSON_NAMES["Q1_1"]},
    {"char": "你们", "pinyin": "nǐmen", "meaning": "Các bạn", "lesson": LESSON_NAMES["Q1_1"]},

    # --- QUYỂN 1: BÀI 2 ---
    {"char": "叫", "pinyin": "jiào", "meaning": "Gọi, tên là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "什么", "pinyin": "shénme", "meaning": "Cái gì", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "名字", "pinyin": "míngzi", "meaning": "Tên", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "我", "pinyin": "wǒ", "meaning": "Tôi, tớ", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "呢", "pinyin": "ne", "meaning": "Thế, còn... thì sao", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "是", "pinyin": "shì", "meaning": "Là", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "哪", "pinyin": "nǎ", "meaning": "Nào", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "国", "pinyin": "guó", "meaning": "Nước, quốc gia", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "人", "pinyin": "rén", "meaning": "Người", "lesson": LESSON_NAMES["Q1_2"]},
    {"char": "他", "pinyin": "tā", "meaning": "Anh ấy, cậu ấy", "lesson": LESSON_NAMES["Q1_2"]},

    # --- QUYỂN 1: BÀI 3 ---
    {"char": "请问", "pinyin": "qǐngwèn", "meaning": "Xin hỏi", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "问", "pinyin": "wèn", "meaning": "Hỏi", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "贵姓", "pinyin": "guìxìng", "meaning": "Quý danh, họ (lịch sự)", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "姓", "pinyin": "xìng", "meaning": "Họ, mang họ", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "这", "pinyin": "zhè", "meaning": "Đây, này", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "名片", "pinyin": "míngpiàn", "meaning": "Danh thiếp", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "没有", "pinyin": "méiyǒu", "meaning": "Không có", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "很", "pinyin": "hěn", "meaning": "Rất", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "高兴", "pinyin": "gāoxìng", "meaning": "Vui vẻ", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "认识", "pinyin": "rènshi", "meaning": "Quen biết", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "先生", "pinyin": "xiānsheng", "meaning": "Ngài, ông", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "也", "pinyin": "yě", "meaning": "Cũng", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "吗", "pinyin": "ma", "meaning": "Không (trợ từ nghi vấn)", "lesson": LESSON_NAMES["Q1_3"]},
    {"char": "不", "pinyin": "bù", "meaning": "Không", "lesson": LESSON_NAMES["Q1_3"]},

    # --- QUYỂN 1: BÀI 4 ---
    {"char": "小姐", "pinyin": "xiǎojiě", "meaning": "Cô, tiểu thư", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "师傅", "pinyin": "shīfu", "meaning": "Bác tài, bác thợ", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "去", "pinyin": "qù", "meaning": "Đi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "哪儿", "pinyin": "nǎr", "meaning": "Đâu, ở đâu", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "人民", "pinyin": "rénmín", "meaning": "Nhân dân", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "广场", "pinyin": "guǎngchǎng", "meaning": "Quảng trường", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "知道", "pinyin": "zhīdào", "meaning": "Biết", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "了", "pinyin": "le", "meaning": "Rồi", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "远", "pinyin": "yuǎn", "meaning": "Xa", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "近", "pinyin": "jìn", "meaning": "Gần", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "到", "pinyin": "dào", "meaning": "Đến, tới", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "多少", "pinyin": "duōshao", "meaning": "Bao nhiêu", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "钱", "pinyin": "qián", "meaning": "Tiền", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "块", "pinyin": "kuài", "meaning": "Đồng (đơn vị tiền)", "lesson": LESSON_NAMES["Q1_4"]},
    {"char": "再见", "pinyin": "zàijiàn", "meaning": "Tạm biệt", "lesson": LESSON_NAMES["Q1_4"]},

    # --- QUYỂN 1: BÀI 5 ---
    {"char": "要", "pinyin": "yào", "meaning": "Muốn, cần", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "吃", "pinyin": "chī", "meaning": "Ăn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "一点儿", "pinyin": "yìdiǎnr", "meaning": "Một chút, một ít", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "个", "pinyin": "gè", "meaning": "Cái, chiếc (lượng từ)", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "牛肉", "pinyin": "niúròu", "meaning": "Thịt bò", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "青菜", "pinyin": "qīngcài", "meaning": "Rau xanh", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "还", "pinyin": "hái", "meaning": "Còn, nữa", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "两", "pinyin": "liǎng", "meaning": "Hai (số lượng)", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "碗", "pinyin": "wǎn", "meaning": "Bát, chén", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "米饭", "pinyin": "mǐfàn", "meaning": "Cơm", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "快", "pinyin": "kuài", "meaning": "Nhanh", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "饿", "pinyin": "è", "meaning": "Đói", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "喝", "pinyin": "hē", "meaning": "Uống", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "杯", "pinyin": "bēi", "meaning": "Cốc, ly", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "奶茶", "pinyin": "nǎichá", "meaning": "Trà sữa", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "大", "pinyin": "dà", "meaning": "To, lớn", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "还是", "pinyin": "háishi", "meaning": "Hay là (câu hỏi)", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "小", "pinyin": "xiǎo", "meaning": "Nhỏ, bé", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "咖啡", "pinyin": "kāfēi", "meaning": "Cà phê", "lesson": LESSON_NAMES["Q1_5"]},
    {"char": "一共", "pinyin": "yígòng", "meaning": "Tổng cộng", "lesson": LESSON_NAMES["Q1_5"]},

    # --- QUYỂN 1: BÀI 6 ---
    {"char": "在", "pinyin": "zài", "meaning": "Ở, tại", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "工作", "pinyin": "gōngzuò", "meaning": "Làm việc, công việc", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "苹果", "pinyin": "píngguǒ", "meaning": "Quả táo", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "公司", "pinyin": "gōngsī", "meaning": "Công ty", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "留学生", "pinyin": "liúxuéshēng", "meaning": "Lưu học sinh", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "学生", "pinyin": "xuéshēng", "meaning": "Học sinh, sinh viên", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "这儿", "pinyin": "zhèr", "meaning": "Ở đây", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "学习", "pinyin": "xuéxí", "meaning": "Học tập", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "汉语", "pinyin": "Hànyǔ", "meaning": "Tiếng Hán", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "对", "pinyin": "duì", "meaning": "Đúng", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "男朋友", "pinyin": "nánpéngyou", "meaning": "Bạn trai", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "朋友", "pinyin": "péngyou", "meaning": "Bạn bè", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "做", "pinyin": "zuò", "meaning": "Làm", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "大学", "pinyin": "dàxué", "meaning": "Đại học", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "教", "pinyin": "jiāo", "meaning": "Dạy học", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "英语", "pinyin": "Yīngyǔ", "meaning": "Tiếng Anh", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "女朋友", "pinyin": "nǚpéngyou", "meaning": "Bạn gái", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "她", "pinyin": "tā", "meaning": "Cô ấy, bà ấy", "lesson": LESSON_NAMES["Q1_6"]},
    {"char": "中学", "pinyin": "zhōngxué", "meaning": "Trường trung học", "lesson": LESSON_NAMES["Q1_6"]},

    # --- QUYỂN 1: BÀI 7 ---
    {"char": "附近", "pinyin": "fùjìn", "meaning": "Gần đây, lân cận", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "银行", "pinyin": "yínháng", "meaning": "Ngân hàng", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "家", "pinyin": "jiā", "meaning": "Lượng từ (cửa hàng/nhà)", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "从", "pinyin": "cóng", "meaning": "Từ", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "往", "pinyin": "wǎng", "meaning": "Đi về phía, hướng", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "前", "pinyin": "qián", "meaning": "Phía trước", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "走", "pinyin": "zǒu", "meaning": "Đi", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "然后", "pinyin": "ránhòu", "meaning": "Sau đó", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "左", "pinyin": "zuǒ", "meaning": "Bên trái", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "拐", "pinyin": "guǎi", "meaning": "Rẽ, ngoặt", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "饭店", "pinyin": "fàndiàn", "meaning": "Nhà hàng, quán ăn", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "就", "pinyin": "jiù", "meaning": "Ngay, chính là", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "对面", "pinyin": "duìmiàn", "meaning": "Đối diện", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "书店", "pinyin": "shūdiàn", "meaning": "Nhà sách", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "超市", "pinyin": "chāoshì", "meaning": "Siêu thị", "lesson": LESSON_NAMES["Q1_7"]},
    {"char": "右", "pinyin": "yòu", "meaning": "Bên phải", "lesson": LESSON_NAMES["Q1_7"]},

    # --- QUYỂN 1: BÀI 8 ---
    {"char": "今天", "pinyin": "jīntiān", "meaning": "Hôm nay", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "真", "pinyin": "zhēn", "meaning": "Thật, thật là", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "漂亮", "pinyin": "piàoliang", "meaning": "Đẹp, xinh đẹp", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "事", "pinyin": "shì", "meaning": "Việc, chuyện", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "生日", "pinyin": "shēngrì", "meaning": "Sinh nhật", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "几", "pinyin": "jǐ", "meaning": "Mấy", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "号", "pinyin": "hào", "meaning": "Ngày (ngôn ngữ nói)", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "月", "pinyin": "yuè", "meaning": "Tháng", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "快乐", "pinyin": "kuàilè", "meaning": "Vui vẻ, hạnh phúc", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "星期", "pinyin": "xīngqī", "meaning": "Tuần, thứ", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "空儿", "pinyin": "kòngr", "meaning": "Thời gian rảnh", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "想", "pinyin": "xiǎng", "meaning": "Muốn, suy nghĩ", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "请", "pinyin": "qǐng", "meaning": "Mời", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "晚饭", "pinyin": "wǎnfàn", "meaning": "Bữa tối", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "为什么", "pinyin": "wèi shénme", "meaning": "Tại sao", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "太...了", "pinyin": "tài...le", "meaning": "Quá... rồi", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "那", "pinyin": "nà", "meaning": "Thế thì, vậy thì", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "晚上", "pinyin": "wǎnshang", "meaning": "Buổi tối", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "看", "pinyin": "kàn", "meaning": "Xem, nhìn", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "电影", "pinyin": "diànyǐng", "meaning": "Phim điện ảnh", "lesson": LESSON_NAMES["Q1_8"]},
    {"char": "学校", "pinyin": "xuéxiào", "meaning": "Trường học", "lesson": LESSON_NAMES["Q1_8"]},

    # --- QUYỂN 1: BÀI 9 ---
    {"char": "喜欢", "pinyin": "xǐhuan", "meaning": "Thích", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "还是", "pinyin": "háishi", "meaning": "Hay là", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "吧", "pinyin": "ba", "meaning": "Nhé, đi (trợ từ)", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "平时", "pinyin": "píngshí", "meaning": "Bình thường, ngày thường", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "怎么", "pinyin": "zěnme", "meaning": "Bằng cách nào, thế nào", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "坐", "pinyin": "zuò", "meaning": "Ngồi, đi (xe)", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "地铁", "pinyin": "dìtiě", "meaning": "Tàu điện ngầm", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "走路", "pinyin": "zǒu lù", "meaning": "Đi bộ", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "出租车", "pinyin": "chūzūchē", "meaning": "Xe taxi", "lesson": LESSON_NAMES["Q1_9"]},
    {"char": "又...又...", "pinyin": "yòu...yòu...", "meaning": "Vừa... lại vừa...", "lesson": LESSON_NAMES["Q1_9"]},

    # --- QUYỂN 1: BÀI 10 ---
    {"char": "口", "pinyin": "kǒu", "meaning": "Lượng từ (thành viên gia đình)", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "爸爸", "pinyin": "bàba", "meaning": "Bố", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "妈妈", "pinyin": "māma", "meaning": "Mẹ", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "哥哥", "pinyin": "gēge", "meaning": "Anh trai", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "姐姐", "pinyin": "jiějie", "meaning": "Chị gái", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "弟弟", "pinyin": "dìdi", "meaning": "Em trai", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "妹妹", "pinyin": "mèimei", "meaning": "Em gái", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "岁", "pinyin": "suì", "meaning": "Tuổi", "lesson": LESSON_NAMES["Q1_10"]},
    {"char": "可爱", "pinyin": "kě'ài", "meaning": "Đáng yêu", "lesson": LESSON_NAMES["Q1_10"]},

    # --- QUYỂN 2: BÀI 1 ---
    {"char": "正在", "pinyin": "zhèngzài", "meaning": "Đang (tiếp diễn)", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "听", "pinyin": "tīng", "meaning": "Nghe", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "音乐", "pinyin": "yīnyuè", "meaning": "Âm nhạc", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "好听", "pinyin": "hǎotīng", "meaning": "Hay (âm thanh)", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "一边...一边...", "pinyin": "yìbiān...yìbiān...", "meaning": "Vừa... vừa...", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "唱歌", "pinyin": "chàng gē", "meaning": "Hát bài hát", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "只", "pinyin": "zhǐ", "meaning": "Chỉ (phó từ)", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "常常", "pinyin": "chángcháng", "meaning": "Thường xuyên", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "行", "pinyin": "xíng", "meaning": "Được, đồng ý", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "下次", "pinyin": "xià cì", "meaning": "Lần sau", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "打球", "pinyin": "dǎ qiú", "meaning": "Đánh bóng, chơi bóng", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "电视", "pinyin": "diànshì", "meaning": "Tivi", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "跳舞", "pinyin": "tiào wǔ", "meaning": "Nhảy múa, khiêu vũ", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "别人", "pinyin": "biérén", "meaning": "Người khác", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "篮球", "pinyin": "lánqiú", "meaning": "Bóng rổ", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "周末", "pinyin": "zhōumò", "meaning": "Cuối tuần", "lesson": LESSON_NAMES["Q2_1"]},
    {"char": "一起", "pinyin": "yìqǐ", "meaning": "Cùng nhau", "lesson": LESSON_NAMES["Q2_1"]},

    # --- QUYỂN 2: BÀI 2 ---
    {"char": "现在", "pinyin": "xiànzài", "meaning": "Bây giờ, hiện tại", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "点", "pinyin": "diǎn", "meaning": "Giờ", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "半", "pinyin": "bàn", "meaning": "Rưỡi, nửa", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "刻", "pinyin": "kè", "meaning": "15 phút", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "分", "pinyin": "fēn", "meaning": "Phút", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "上课", "pinyin": "shàng kè", "meaning": "Lên lớp, vào học", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "下课", "pinyin": "xià kè", "meaning": "Tan học", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "中午", "pinyin": "zhōngwǔ", "meaning": "Buổi trưa", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "或者", "pinyin": "huòzhě", "meaning": "Hoặc là", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "门口", "pinyin": "ménkǒu", "meaning": "Cổng, cửa", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "起床", "pinyin": "qǐchuáng", "meaning": "Thức dậy", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "有时候", "pinyin": "yǒushíhou", "meaning": "Có lúc, thỉnh thoảng", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "左右", "pinyin": "zuǒyòu", "meaning": "Khoảng, xấp xỉ", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "每天", "pinyin": "měitiān", "meaning": "Hàng ngày", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "这么", "pinyin": "zhème", "meaning": "Thế này, như vậy", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "早", "pinyin": "zǎo", "meaning": "Sớm", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "睡觉", "pinyin": "shuìjiào", "meaning": "Đi ngủ", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "因为", "pinyin": "yīnwèi", "meaning": "Bởi vì", "lesson": LESSON_NAMES["Q2_2"]},
    {"char": "晚", "pinyin": "wǎn", "meaning": "Muộn", "lesson": LESSON_NAMES["Q2_2"]},

    # --- QUYỂN 2: BÀI 3 ---
    {"char": "可以", "pinyin": "kěyǐ", "meaning": "Có thể", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "给", "pinyin": "gěi", "meaning": "Cho, cho ai", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "打电话", "pinyin": "dǎ diànhuà", "meaning": "Gọi điện thoại", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "可是", "pinyin": "kěshì", "meaning": "Nhưng", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "号码", "pinyin": "hàomǎ", "meaning": "Số, mã số", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "手机", "pinyin": "shǒujī", "meaning": "Điện thoại di động", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "等", "pinyin": "děng", "meaning": "Chờ, đợi", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "一下", "pinyin": "yíxià", "meaning": "Một chút, một lát", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "笔", "pinyin": "bǐ", "meaning": "Bút", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "写", "pinyin": "xiě", "meaning": "Viết", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "慢", "pinyin": "màn", "meaning": "Chậm", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "说", "pinyin": "shuō", "meaning": "Nói", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "遍", "pinyin": "biàn", "meaning": "Lần (lượng từ hành động)", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "用", "pinyin": "yòng", "meaning": "Dùng, sử dụng", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "电脑", "pinyin": "diànnǎo", "meaning": "Máy tính", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "对了", "pinyin": "duìle", "meaning": "Đúng rồi", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "借", "pinyin": "jiè", "meaning": "Mượn", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "没电了", "pinyin": "méi diàn le", "meaning": "Hết pin, hết điện", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "没问题", "pinyin": "méi wèntí", "meaning": "Không vấn đề", "lesson": LESSON_NAMES["Q2_3"]},
    {"char": "找", "pinyin": "zhǎo", "meaning": "Tìm kiếm", "lesson": LESSON_NAMES["Q2_3"]},

    # --- QUYỂN 2: BÀI 4 ---
    {"char": "买", "pinyin": "mǎi", "meaning": "Mua", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "衣服", "pinyin": "yīfu", "meaning": "Quần áo", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "件", "pinyin": "jiàn", "meaning": "Chiếc, cái (lượng từ áo)", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "衬衫", "pinyin": "chènshān", "meaning": "Áo sơ mi", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "颜色", "pinyin": "yánsè", "meaning": "Màu sắc", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "黑", "pinyin": "hēi", "meaning": "Đen", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "红", "pinyin": "hóng", "meaning": "Đỏ", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "蓝", "pinyin": "lán", "meaning": "Xanh da trời", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "试", "pinyin": "shì", "meaning": "Thử", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "穿", "pinyin": "chuān", "meaning": "Mặc", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "觉得", "pinyin": "juéde", "meaning": "Cảm thấy", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "合适", "pinyin": "héshì", "meaning": "Vừa vặn, phù hợp", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "双", "pinyin": "shuāng", "meaning": "Đôi (lượng từ giày)", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "鞋", "pinyin": "xié", "meaning": "Giày", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "贵", "pinyin": "guì", "meaning": "Đắt", "lesson": LESSON_NAMES["Q2_4"]},
    {"char": "便宜", "pinyin": "piányi", "meaning": "Rẻ", "lesson": LESSON_NAMES["Q2_4"]},

    # --- QUYỂN 2: BÀI 5 ---
    {"char": "忙", "pinyin": "máng", "meaning": "Bận rộn", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "有点儿", "pinyin": "yǒudiǎnr", "meaning": "Hơi... một chút", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "考试", "pinyin": "kǎoshì", "meaning": "Thi, kiểm tra", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "帮", "pinyin": "bāng", "meaning": "Giúp đỡ", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "准备", "pinyin": "zhǔnbèi", "meaning": "Chuẩn bị", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "时候", "pinyin": "shíhou", "meaning": "Lúc, khi", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "跟", "pinyin": "gēn", "meaning": "Cùng, với", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "参加", "pinyin": "cānjiā", "meaning": "Tham gia", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "比赛", "pinyin": "bǐsài", "meaning": "Trận đấu, cuộc thi", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "图书馆", "pinyin": "túshūguǎn", "meaning": "Thư viện", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "难", "pinyin": "nán", "meaning": "Khó", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "旅行", "pinyin": "lǚxíng", "meaning": "Du lịch", "lesson": LESSON_NAMES["Q2_5"]},
    {"char": "不好意思", "pinyin": "bù hǎoyìsi", "meaning": "Ngại quá, xin lỗi", "lesson": LESSON_NAMES["Q2_5"]},

    # --- QUYỂN 2: BÀI 6 ---
    {"char": "上个", "pinyin": "shàng gè", "meaning": "Trước (tuần/tháng)", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "一些", "pinyin": "yìxiē", "meaning": "Một vài, một số", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "参观", "pinyin": "cānguān", "meaning": "Tham quan", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "博物馆", "pinyin": "bówùguǎn", "meaning": "Viện bảo tàng", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "公园", "pinyin": "gōngyuán", "meaning": "Công viên", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "非常", "pinyin": "fēicháng", "meaning": "Rất, vô cùng", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "门票", "pinyin": "ménpiào", "meaning": "Vé vào cổng", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "累", "pinyin": "lèi", "meaning": "Mệt mỏi", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "好玩儿", "pinyin": "hǎowánr", "meaning": "Vui, thú vị", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "风景", "pinyin": "fēngjǐng", "meaning": "Phong cảnh", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "美", "pinyin": "měi", "meaning": "Đẹp", "lesson": LESSON_NAMES["Q2_6"]},
    {"char": "拍照片", "pinyin": "pāi zhàopiàn", "meaning": "Chụp ảnh", "lesson": LESSON_NAMES["Q2_6"]},

    # --- QUYỂN 2: BÀI 7 ---
    {"char": "听说", "pinyin": "tīngshuō", "meaning": "Nghe nói", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "玩儿", "pinyin": "wánr", "meaning": "Chơi", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "告诉", "pinyin": "gàosu", "meaning": "Nói cho biết, bảo", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "微信", "pinyin": "wēixìn", "meaning": "WeChat", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "忘", "pinyin": "wàng", "meaning": "Quên", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "当然", "pinyin": "dāngrán", "meaning": "Đương nhiên", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "有意思", "pinyin": "yǒu yìsi", "meaning": "Thú vị, hay", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "骑", "pinyin": "qí", "meaning": "Đi, cưỡi (xe)", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "自行车", "pinyin": "zìxíngchē", "meaning": "Xe đạp", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "多长", "pinyin": "duō cháng", "meaning": "Bao lâu", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "小时", "pinyin": "xiǎoshí", "meaning": "Giờ, tiếng đồng hồ", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "好看", "pinyin": "hǎokàn", "meaning": "Đẹp mắt", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "自己", "pinyin": "zìjǐ", "meaning": "Bản thân, tự mình", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "最近", "pinyin": "zuìjìn", "meaning": "Gần đây", "lesson": LESSON_NAMES["Q2_7"]},
    {"char": "去年", "pinyin": "qùnián", "meaning": "Năm ngoái", "lesson": LESSON_NAMES["Q2_7"]},

    # --- QUYỂN 2: BÀI 8 ---
    {"char": "会", "pinyin": "huì", "meaning": "Biết (kỹ năng)", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "做菜", "pinyin": "zuò cài", "meaning": "Nấu ăn", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "水果", "pinyin": "shuǐguǒ", "meaning": "Hoa quả", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "沙拉", "pinyin": "shālā", "meaning": "Sa-lát", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "酒", "pinyin": "jiǔ", "meaning": "Rượu", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "尝", "pinyin": "cháng", "meaning": "Nếm thử", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "聪明", "pinyin": "cōngming", "meaning": "Thông minh", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "外语", "pinyin": "wàiyǔ", "meaning": "Ngoại ngữ", "lesson": LESSON_NAMES["Q2_8"]},
    {"char": "除了...以外", "pinyin": "chúle...yǐwài", "meaning": "Ngoài... ra", "lesson": LESSON_NAMES["Q2_8"]},

    # --- QUYỂN 2: BÀI 9 ---
    {"char": "建议", "pinyin": "jiànyì", "meaning": "Gợi ý, đề xuất", "lesson": LESSON_NAMES["Q2_9"]},
    {"char": "计划", "pinyin": "jìhuà", "meaning": "Kế hoạch", "lesson": LESSON_NAMES["Q2_9"]},
    {"char": "熊猫", "pinyin": "xióngmāo", "meaning": "Gấu trúc", "lesson": LESSON_NAMES["Q2_9"]},
    {"char": "动物园", "pinyin": "dòngwùyuán", "meaning": "Sở thú", "lesson": LESSON_NAMES["Q2_9"]},
    {"char": "感兴趣", "pinyin": "gǎn xìngqù", "meaning": "Hứng thú", "lesson": LESSON_NAMES["Q2_9"]},

    # --- QUYỂN 2: BÀI 10 ---
    {"char": "客气", "pinyin": "kèqi", "meaning": "Khách khí, lịch sự", "lesson": LESSON_NAMES["Q2_10"]},
    {"char": "麻烦", "pinyin": "máfan", "meaning": "Làm phiền", "lesson": LESSON_NAMES["Q2_10"]},
    {"char": "做客", "pinyin": "zuòkè", "meaning": "Làm khách", "lesson": LESSON_NAMES["Q2_10"]}
]

# 3. KHO DỮ LIỆU MẪU CÂU TỪ SÁCH BÀI TẬP BỔ TRỢ MSUTONG (Có mặt đầy đủ ở 20 bài)
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
    {"words": ["他", "有", "中国", "名字", "没有"], "pinyin_words": ["Tā", "yǒu", "Zhōngguó", "míngzi", "méiyǒu"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["我", "去", "人民", "广场"], "pinyin_words": ["Wǒ", "qù", "Rénmín", "Guǎngchǎng"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["你", "是不是", "中国", "人"], "pinyin_words": ["Nǐ", "shì bu shì", "Zhōngguó", "rén"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["请问", "这个", "多少", "钱"], "pinyin_words": ["Qǐngwèn", "zhège", "duōshao", "qián"], "lesson": LESSON_NAMES["Q1_4"]},
    {"words": ["你", "要", "吃", "什么"], "pinyin_words": ["Nǐ", "yào", "chī", "shénme"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["我", "要", "一", "碗", "米饭", "和", "两", "杯", "茶"], "pinyin_words": ["Wǒ", "yào", "yì", "wǎn", "mǐfàn", "hé", "liǎng", "bēi", "chá"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["弟弟", "不想", "吃", "牛肉"], "pinyin_words": ["Dìdi", "bù xiǎng", "chī", "niúròu"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["请", "快点儿", "我", "很", "饿"], "pinyin_words": ["Qǐng", "kuàidiǎnr", "wǒ", "hěn", "è"], "lesson": LESSON_NAMES["Q1_5"]},
    {"words": ["她", "的", "男朋友", "是", "中国人"], "pinyin_words": ["Tā", "de", "nánpéngyou", "shì", "Zhōngguórén"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["海伦", "在", "北京", "教", "英语"], "pinyin_words": ["Hǎilún", "zài", "Běijīng", "jiāo", "Yīngyǔ"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["马文", "的", "女朋友", "是", "留学生"], "pinyin_words": ["Mǎwén", "de", "nǚpéngyou", "shì", "liúxuéshēng"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["他", "在", "中国", "学习", "汉语"], "pinyin_words": ["Tā", "zài", "Zhōngguó", "xuéxí", "Hànyǔ"], "lesson": LESSON_NAMES["Q1_6"]},
    {"words": ["我", "家", "附近", "有", "书店", "超市", "和", "银行"], "pinyin_words": ["Wǒ", "jiā", "fùjìn", "yǒu", "shūdiàn", "chāoshì", "hé", "yínháng"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["请问", "这儿", "附近", "有", "没有", "中国银行"], "pinyin_words": ["Qǐngwèn", "zhèr", "fùjìn", "yǒu", "méiyǒu", "Zhōngguó Yínháng"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["全家", "超市", "在", "哪儿"], "pinyin_words": ["Quánjiā", "chāoshì", "zài", "nǎr"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["往", "右", "拐", "就是", "四川", "饭店"], "pinyin_words": ["Wǎng", "yòu", "guǎi", "jiù shì", "Sìchuān", "Fàndiàn"], "lesson": LESSON_NAMES["Q1_7"]},
    {"words": ["今天", "是", "二零二零年", "二月", "二十九号"], "pinyin_words": ["Jīntiān", "shì", "èr líng èr líng nián", "èr yuè", "èrshíjiǔ hào"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["今天", "晚上", "我", "想", "请", "你", "看", "电影"], "pinyin_words": ["Jīntiān", "wǎnshang", "wǒ", "xiǎng", "qǐng", "nǐ", "kàn", "diànyǐng"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["中国", "银行", "就在", "中华", "饭店", "对面"], "pinyin_words": ["Zhōngguó", "Yínháng", "jiù zài", "Zhōnghuá", "Fàndiàn", "duìmiàn"], "lesson": LESSON_NAMES["Q1_8"]},
    {"words": ["中国", "菜", "和", "韩国", "菜", "都", "好", "吃"], "pinyin_words": ["Zhōngguó", "cài", "hé", "Hánguó", "cài", "dōu", "hǎo", "chī"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["你", "喜欢", "喝", "咖啡", "还是", "喝", "茶"], "pinyin_words": ["Nǐ", "xǐhuan", "hē", "kāfēi", "háishi", "hē", "chá"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["坐", "地铁", "又", "快", "又", "便宜"], "pinyin_words": ["Zuò", "dìtiě", "yòu", "kuài", "yòu", "piányi"], "lesson": LESSON_NAMES["Q1_9"]},
    {"words": ["我", "姐姐", "的", "爱好", "都", "是", "看", "电影"], "pinyin_words": ["Wǒ", "jiějie", "de", "àihào", "dōu", "shì", "kàn", "diànyǐng"], "lesson": LESSON_NAMES["Q1_10"]},
    {"words": ["我", "家", "有", "四", "口", "人"], "pinyin_words": ["Wǒ", "jiā", "yǒu", "sì", "kǒu", "rén"], "lesson": LESSON_NAMES["Q1_10"]},

    # QUYỂN 2
    {"words": ["他", "常常", "一边", "吃饭", "一边", "看", "电视"], "pinyin_words": ["Tā", "chángcháng", "yìbiān", "chī fàn", "yìbiān", "kàn", "diànshì"], "lesson": LESSON_NAMES["Q2_1"]},
    {"words": ["我", "只", "喜欢", "看", "别人", "打球"], "pinyin_words": ["Wǒ", "zhǐ", "xǐhuan", "kàn", "biérén", "dǎqiú"], "lesson": LESSON_NAMES["Q2_1"]},
    {"words": ["星期天", "上午", "九点", "在", "学校", "门口", "见"], "pinyin_words": ["Xīngqītiān", "shàngwǔ", "jiǔ diǎn", "zài", "xuéxiào", "ménkǒu", "jiàn"], "lesson": LESSON_NAMES["Q2_2"]},
    {"words": ["我", "早上", "有时候", "六点", "起床"], "pinyin_words": ["Wǒ", "zǎoshang", "yǒushíhou", "liù diǎn", "qǐchuáng"], "lesson": LESSON_NAMES["Q2_2"]},
    {"words": ["我", "可不可以", "借", "用", "一下", "你", "的", "笔"], "pinyin_words": ["Wǒ", "kě bu kěyǐ", "jiè", "yòng", "yíxià", "nǐ", "de", "bǐ"], "lesson": LESSON_NAMES["Q2_3"]},
    {"words": ["你", "的", "电话", "号码", "是", "多少"], "pinyin_words": ["Nǐ", "de", "diànhuà", "hàomǎ", "shì", "duōshao"], "lesson": LESSON_NAMES["Q2_3"]},
    {"words": ["你", "觉得", "这", "件", "衣服", "不太", "贵"], "pinyin_words": ["Nǐ", "juéde", "zhè", "jiàn", "yīfu", "bú tài", "guì"], "lesson": LESSON_NAMES["Q2_4"]},
    {"words": ["姐姐", "买", "了", "两", "双", "鞋"], "pinyin_words": ["Jiějie", "mǎi", "le", "liǎng", "shuāng", "xié"], "lesson": LESSON_NAMES["Q2_4"]},
    {"words": ["明天", "晚上", "我", "要", "跟", "妈妈", "一起", "去", "买", "东西"], "pinyin_words": ["Míngtiān", "wǎnshang", "wǒ", "yào", "gēn", "māma", "yìqǐ", "qù", "mǎi", "dōngxi"], "lesson": LESSON_NAMES["Q2_5"]},
    {"words": ["他", "周末", "和", "朋友", "去", "参观", "博物馆", "了"], "pinyin_words": ["Tā", "zhōumò", "hé", "péngyou", "qù", "cānguān", "bówùguǎn", "le"], "lesson": LESSON_NAMES["Q2_6"]},
    {"words": ["你", "是", "跟", "谁", "一起", "去", "的"], "pinyin_words": ["Nǐ", "shì", "gēn", "shéi", "yìqǐ", "qù", "de"], "lesson": LESSON_NAMES["Q2_7"]},
    {"words": ["我们", "是", "骑", "自行车", "去", "的"], "pinyin_words": ["Wǒmen", "shì", "qí", "zìxíngchē", "qù", "de"], "lesson": LESSON_NAMES["Q2_7"]},
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

def record_answer(is_correct):
    st.session_state.total += 1
    if is_correct:
        st.session_state.score += 1
    
    name = user_name.strip() if user_name.strip() else "Ẩn danh"
    mode_clean = st.session_state.question["mode"].replace(":", " -")
    
    st.session_state.history.append({
        "name": name,
        "mode": mode_clean,
        "is_correct": 1 if is_correct else 0
    })

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
            if user_choice == q["correct_ans"]:
                st.success("🎉 Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Chữ Hán đúng của **{q['target']['pinyin']}** là: **{q['correct_ans']}** ({q['target']['meaning']})")

    elif mode == "Dạng 3: Hán + Pinyin ➡️ 4 Nghĩa":
        st.info("📌 **Dạng 3:** Chọn nghĩa Tiếng Việt chính xác:")
        st.markdown(f"<p style='text-align: center; font-size: 18px; color: #888;'>📚 Bài học: <b>{q['target']['lesson']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #2E7D32;'>{q['target']['char']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 24px; color: gray;'>Pinyin: <b>{q['target']['pinyin']}</b></p>", unsafe_allow_html=True)
        
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
    if not st.session_state.history:
        st.write("Chưa có dữ liệu làm bài nào.")
    else:
        df = pd.DataFrame(st.session_state.history)
        
        summary_df = df.groupby(["name", "mode"]).agg(
            Tong_Cau=("is_correct", "count"),
            Cau_Dung=("is_correct", "sum")
        ).reset_index()
        
        summary_df["Ty_Le_Dung_%"] = (summary_df["Cau_Dung"] / summary_df["Tong_Cau"] * 100).round(1)
        
        st.write("**Bảng tỷ lệ làm đúng (%)**")
        st.dataframe(
            summary_df[["name", "mode", "Ty_Le_Dung_%", "Cau_Dung", "Tong_Cau"]],
            column_config={
                "name": "Tên",
                "mode": "Dạng bài",
                "Ty_Le_Dung_%": "Tỷ lệ đúng (%)",
                "Cau_Dung": "Đúng",
                "Tong_Cau": "Tổng câu"
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.write("**Biểu đồ Tỷ lệ đúng (%)**")
        chart_data = summary_df.pivot(index="name", columns="mode", values="Ty_Le_Dung_%").fillna(0)
        chart_data.columns = [str(col).replace("➡️", "->") for col in chart_data.columns]
        st.bar_chart(chart_data)