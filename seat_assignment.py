import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# تحميل ملف الضيوف المختارين (احفظيه من Streamlit مسبقًا)
selected_df = pd.read_csv('selected_guests.csv')
sorted_df = selected_df.sort_values(by='الرتبة').reset_index(drop=True)

# ترتيب الكراسي حسب المنطق الملكي
front_chairs = [26, 27, 28, 29, 30, 31, 25, 24, 23, 22, 21]  # الملك في المنتصف
right_wing = list(range(11, 21))  # يمين القاعة (من وجهة الملك)
left_wing = list(range(1, 11))    # يسار القاعة
chair_sequence = front_chairs + right_wing + left_wing

# إحداثيات الكراسي
positions = {
    1: (1120, 700), 2: (1120, 640), 3: (1120, 580), 4: (1120, 520), 5: (1120, 460),
    6: (1120, 400), 7: (1120, 340), 8: (1120, 280), 9: (1120, 220), 10: (1120, 160),
    11: (80, 160), 12: (80, 220), 13: (80, 280), 14: (80, 340), 15: (80, 400),
    16: (80, 460), 17: (80, 520), 18: (80, 580), 19: (80, 640), 20: (80, 700),
    21: (180, 80), 22: (280, 80), 23: (380, 80), 24: (480, 80), 25: (580, 80),
    26: (680, 80), 27: (780, 80), 28: (880, 80), 29: (980, 80), 30: (1080, 80), 31: (1180, 80)
}

# ربط الكراسي بالأشخاص
assigned = []
used_chairs = []

for _, row in sorted_df.iterrows():
    name = row['الاسم']
    for chair in chair_sequence:
        if chair not in used_chairs:
            assigned.append((name, chair))
            used_chairs.append(chair)
            break

# تحميل الصورة
img = Image.open('قاعة-الأساسية.png')
draw = ImageDraw.Draw(img)

# إعداد الخط
try:
    font = ImageFont.truetype("Cairo-Regular.ttf", 22)
except:
    font = ImageFont.load_default()

# كتابة الأسماء على الصورة
for name, chair in assigned:
    if chair in positions:
        x, y = positions[chair]
        draw.text((x, y), name, fill="black", font=font, anchor="mm")

# حفظ وعرض الصورة
output_path = "قاعة-التوزيع-النهائي.png"
img.save(output_path)
img.show()

print(f"✅ تم حفظ الصورة: {output_path}")
