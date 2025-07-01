import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- تحميل البيانات ---
guests = pd.read_csv('data/guest-list.csv', encoding='utf-8')
classes = pd.read_csv('data/class-priority.csv', encoding='utf-8')
rooms = pd.read_csv('data/rooms.csv', encoding='utf-8')

# --- تنظيف الأعمدة ---
guests.columns = guests.columns.str.strip()
classes.columns = classes.columns.str.strip()
rooms.columns = rooms.columns.str.strip()

# --- دمج الرتب مع الضيوف ---
guests = guests.merge(classes, left_on='رقم الفئة', right_on='الرتبة')

# --- إعداد الواجهة ---
st.set_page_config(page_title="توزيع الجلوس الملكي", layout="centered", page_icon="👑")
st.title("📌 توزيع الجلوس حسب الرتب")
st.markdown("---")

# --- اختيار القاعة ---
selected_room = st.selectbox("اختر القاعة:", rooms['اسم القاعة'])
room_data = rooms[rooms['اسم القاعة'] == selected_room].iloc[0]
num_seats = int(room_data['عدد الكراسي'])

# --- اختيار حجم الخط ---
font_size = st.slider("✍️ اختر حجم الرقم على الكرسي:", 12, 48, 24, step=2)

# --- اختيار الضيوف ---
guests['محدد'] = False
selected_names_global = []

for _, row in classes.sort_values('الرتبة').iterrows():
    class_name = row['الفئة']
    available_names = guests[
        (guests['الفئة'] == class_name) &
        (~guests['الاسم'].isin(selected_names_global))
    ]['الاسم'].tolist()

    remaining = max(0, num_seats - len(selected_names_global))
    if remaining == 0:
        st.info("تم حجز جميع الكراسي.")
        break

    with st.expander(f"{class_name} (باقي {remaining} كرسي):"):
        selected = st.multiselect(
            f"اختر من {class_name}:",
            available_names,
            default=[],
            key=class_name,
            max_selections=remaining
        )
        selected_names_global.extend(selected)

# --- تحقق من الحد الأعلى وعد التكرار ---
selected_names_global = list(dict.fromkeys(selected_names_global))  # إزالة التكرارات

if len(selected_names_global) > num_seats:
    st.error(f"❌ تم اختيار {len(selected_names_global)} ضيفًا، ويتجاوز عدد الكراسي ({num_seats})!")
    st.stop()

guests['محدد'] = guests['الاسم'].isin(selected_names_global)
selected_guests = guests[guests['محدد'] == True].copy()
selected_guests = selected_guests.drop_duplicates(subset='الاسم').reset_index(drop=True)

st.markdown("---")
st.subheader(f"✅ الضيوف المختارين: {len(selected_guests)} / {num_seats}")
if not selected_guests.empty:
    st.dataframe(selected_guests[['الاسم', 'الفئة', 'الرتبة']])
    selected_guests.to_csv('data/selected_guests.csv', index=False, encoding='utf-8-sig')
    st.success("✅ تم حفظ الضيوف المختارين.")
else:
    st.warning("⚠️ لم يتم اختيار أي ضيف بعد.")

# --- الرسم ---
if not selected_guests.empty and st.button("🎨 رسم القاعة"):

    # --- ترتيب الكراسي من 16 → 15 → 1 → 17 → 31
    chair_sequence = [16] + list(range(15, 0, -1)) + list(range(17, 32))

    # --- إحداثيات الكراسي
    positions = {
        1: (1140, 670), 2: (1140, 620), 3: (1140, 570), 4: (1140, 520), 5: (1140, 470),
        6: (1140, 420), 7: (1140, 370), 8: (1140, 320), 9: (1140, 270), 10: (1140, 220),
        11: (1050, 130), 12: (970, 130), 13: (890, 130), 14: (810, 130), 15: (730, 130),
        16: (650, 130), 17: (570, 130), 18: (490, 130), 19: (410, 130), 20: (330, 130),
        21: (250, 130), 22: (160, 220), 23: (160, 270), 24: (160, 320), 25: (160, 370),
        26: (160, 420), 27: (160, 470), 28: (160, 520), 29: (160, 570), 30: (160, 620), 31: (160, 670)
    }

    # --- ترتيب الضيوف
    selected_guests['ترتيب_الظهور'] = selected_guests.index
    sorted_df = selected_guests.sort_values(by=['الرتبة', 'ترتيب_الظهور']).reset_index(drop=True)

    # --- توزيع الكراسي مع الحفاظ على تلاصق الرتب
    chair_assignment = {}
    used_chairs = []

    for _, group in sorted_df.groupby('الرتبة', sort=True):
        members = group['الاسم'].tolist()
        for i in range(len(chair_sequence)):
            sub_seq = chair_sequence[i:i+len(members)]
            if len(sub_seq) < len(members):
                break
            if all(ch not in used_chairs for ch in sub_seq):
                for ch, name in zip(sub_seq, members):
                    chair_assignment[ch] = name
                    used_chairs.append(ch)
                break

    # --- الرسم
    fig, ax = plt.subplots(figsize=(12, 6))
    chair_info = []

    for ch, name in chair_assignment.items():
        if ch in positions:
            x, y = positions[ch]
            color = '#d4af37' if ch == 16 else 'lightgray'
            ax.plot(x, y, 'o', markersize=20, color=color)
            ax.text(x, y, str(ch), fontsize=font_size, ha='center', va='center', color='black')
            chair_info.append({'رقم الكرسي': ch, 'الاسم': name})

    ax.set_xlim(0, 1300)
    ax.set_ylim(100, 800)
    ax.axis('off')

    st.pyplot(fig)
    st.markdown("### 📋 توزيع الكراسي:")
    st.dataframe(pd.DataFrame(sorted(chair_info, key=lambda x: x["رقم الكرسي"])))
