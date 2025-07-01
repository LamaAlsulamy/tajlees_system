import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# =======================================================================
# تحميل بيانات الضيوف والرتب
# =======================================================================
guests = pd.read_csv('data/guest-list.csv', encoding='utf-8')
classes = pd.read_csv('data/class-priority.csv', encoding='utf-8')

# تنظيف أسماء الأعمدة
guests.columns = guests.columns.str.strip()
classes.columns = classes.columns.str.strip()

# دمج الرتب مع بيانات الضيوف
guests = guests.merge(classes, left_on='رقم الفئة', right_on='الرتبة')

# =======================================================================
# إعداد واجهة Streamlit
# =======================================================================
st.set_page_config(page_title="توزيع الجلوس الملكي", layout="centered", page_icon="👑")
st.title("📌 توزيع الجلوس حسب الرتب")
st.markdown("---")

# -----------------------------------------------------------------------
# اختيار عدد الصفوف (كل صف يحتوي على 31 كرسي فقط)
# -----------------------------------------------------------------------
num_rows = st.slider("اختر عدد الصفوف:", min_value=1, max_value=5, value=1, step=1)
chairs_per_row = 31  # ثابت دائمًا
num_seats = num_rows * chairs_per_row
st.success(f"الغرفة تحتوي على {num_rows} صفوف، كل صف به {chairs_per_row} كرسي (الإجمالي: {num_seats} كرسي).")
st.markdown("---")


# =======================================================================
# اختيار الضيوف (باستخدام ملف الضيوف والرتب)
# =======================================================================
guests['محدد'] = False
selected_names_global = []

for _, row in classes.sort_values('الرتبة').iterrows():
    class_name = row['الفئة']
    available_names = guests[
        (guests['الفئة'] == class_name) & (~guests['الاسم'].isin(selected_names_global))
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

# إزالة التكرارات إن وُجدت والتحقق من عدم تجاوز العدد الإجمالي للكراسي
selected_names_global = list(dict.fromkeys(selected_names_global))
if len(selected_names_global) > num_seats:
    st.error(f"❌ تم اختيار {len(selected_names_global)} ضيفًا، ويتجاوز ذلك عدد الكراسي ({num_seats})!")
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

# =======================================================================
# رسم القاعة: لكل صف رسمته الخاصة كما في النسخة الأصلية (31 كرسي)
# =======================================================================
if not selected_guests.empty and st.button("🎨 رسم القاعة"):

    # --- ترتيب الكراسي في صف واحد وفق البروتوكول:
    # الكرسي 16 هو للمقام الأعلى، ثم من 15 إلى 1 (يمين) ومن 17 إلى 31 (يسار)
    row_chair_sequence = [16] + list(range(15, 0, -1)) + list(range(17, 32))
    
    # ===================================================================
    # نقوم بتقسيم الضيوف وفق ترتيب ظهورهم إلى أجزاء (شريحة من 31 ضيف لكل صف)
    # ===================================================================
    selected_guests['ترتيب_الظهور'] = selected_guests.index
    sorted_df = selected_guests.sort_values(by=['الرتبة', 'ترتيب_الظهور']).reset_index(drop=True)
    
    total_assigned = 0  # لتعقب عدد الضيوف المعينين
    # لكل صف (من 1 إلى num_rows)
    for r in range(num_rows):
        st.markdown(f"### الصف {r+1}")
        
        # استخراج شريحة الضيوف المخصصة لهذا الصف:
        start_idx = r * chairs_per_row
        end_idx = (r + 1) * chairs_per_row
        sub_df = sorted_df.iloc[start_idx:end_idx].copy()
        
        # إذا كانت الشريحة فارغة فلا داعي للرسم
        if sub_df.empty:
            st.info("لا توجد ضيوف لهذا الصف.")
            continue
        
        # توزيع الكراسي داخل هذا الصف مع الحفاظ على تلاصق أصحاب الرتبة
        row_assignment = {}
        used_chairs = []  # تُستخدم لتتبع الكراسي التي تم استخدامها في هذا الصف
        
        # استخدام طريقة التجميع حسب الرتبة داخل الشريحة
        for _, group in sub_df.groupby('الرتبة', sort=True):
            members = group['الاسم'].tolist()
            # البحث عن كتلة متتالية في row_chair_sequence تناسب عدد الأعضاء
            for i in range(len(row_chair_sequence)):
                sub_seq = row_chair_sequence[i:i + len(members)]
                if len(sub_seq) < len(members):
                    break
                if all(ch not in used_chairs for ch in sub_seq):
                    for ch, name in zip(sub_seq, members):
                        row_assignment[ch] = name
                        used_chairs.append(ch)
                    break
        
        # ===================================================================
        # إحداثيات الكراسي (كما في النسخة الأصلية)
        positions = {
            1: (1140, 670), 2: (1140, 620), 3: (1140, 570), 4: (1140, 520), 5: (1140, 470),
            6: (1140, 420), 7: (1140, 370), 8: (1140, 320), 9: (1140, 270), 10: (1140, 220),
            11: (1050, 130), 12: (970, 130), 13: (890, 130), 14: (810, 130), 15: (730, 130),
            16: (650, 130), 17: (570, 130), 18: (490, 130), 19: (410, 130), 20: (330, 130),
            21: (250, 130), 22: (160, 220), 23: (160, 270), 24: (160, 320), 25: (160, 370),
            26: (160, 420), 27: (160, 470), 28: (160, 520), 29: (160, 570), 30: (160, 620), 31: (160, 670)
        }
        
        # ===================================================================
        # رسم الصف باستخدام matplotlib
        fig, ax = plt.subplots(figsize=(12, 6))
        chair_info = []
        for ch, name in row_assignment.items():
            if ch in positions:
                x, y = positions[ch]
                # نميز الكرسي 16 بلون ذهبي، والبقية بلون رمادي
                color = '#d4af37' if ch == 16 else 'lightgray'
                ax.plot(x, y, 'o', markersize=20, color=color)
                ax.text(x, y, str(ch), fontsize=font_size, ha='center', va='center', color='black')
                chair_info.append({'رقم الكرسي': ch, 'الاسم': name})
        
        # ضبط النطاق والمحاور
        ax.set_xlim(0, 1300)
        ax.set_ylim(100, 800)
        ax.axis('off')
        
        st.pyplot(fig)
        st.markdown("#### توزيع الكراسي في هذا الصف:")
        st.dataframe(pd.DataFrame(sorted(chair_info, key=lambda x: x["رقم الكرسي"])))
