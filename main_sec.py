import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math


# ——————————————————————————————————————————————————————————————
# تهيئة حالة الجلسة
# ——————————————————————————————————————————————————————————————

st.markdown(
    """
    <style>
      /* يستهدف كل زر يُنشئه st.button */
      div.stButton > button {
        width: 200px;
        height: 60px;
        font-size: 24px;
      }
    </style>
    """,
    unsafe_allow_html=True
)

if "guests_df" not in st.session_state:
    guests = pd.read_csv('data/guest-list.csv', encoding='utf-8')
    guests.columns = guests.columns.str.strip()
    st.session_state.guests_df = guests

if "classes_df" not in st.session_state:
    classes = pd.read_csv('data/class-priority.csv', encoding='utf-8')
    classes.columns = classes.columns.str.strip()
    st.session_state.classes_df = classes


if "page" not in st.session_state:
    st.session_state.page = 1

# تأكيد الصفوف والمتغيّرات للصفحات التالية
if "rows_confirmed" not in st.session_state:# اذا الرو كونفيرمد مو موجود حطها بفولس
    st.session_state.rows_confirmed = False
if "guests_confirmed" not in st.session_state:
    st.session_state.guests_confirmed = False

def next_page():
    st.session_state.page += 1
    # عند الانتقال للصفحة التالية نعيد ضبط تأكيدات ما عدا الصفحة الرابعة
    if st.session_state.page == 2:
        st.session_state.rows_confirmed = False
    if st.session_state.page == 3:
        st.session_state.guests_confirmed = False

# =======================================================================
# الصفحة 1: المقدمة (مع تنسيق HTML لجعل العنوان والنص في المنتصف وبخط أكبر، وزر "التالي" في المنتصف)
# =======================================================================
if st.session_state.page == 1:
    st.markdown(
        "<h1 style='text-align: center; font-size: 48px;'>نظام التجليس</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="
            text-align: center;
            font-size: 22px;
            margin-top: 20px;
            margin-bottom: 20px;
        ">   
            مرحبًا بكم في نظام التجليس<br>
            هذا النظام مصمم لتسهيل عملية توزيع الضيوف في القاعة
        </div>
        """,
        unsafe_allow_html=True
    )
        # ثم تحط زر التالي وسط الأعمدة 
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("التالي"):
         next_page()

# =======================================================================
# الصفحة 2: تحديد عدد الصفوف (عن طريق اختيار من متعدد)
# =======================================================================
elif st.session_state.page == 2:

    st.markdown(
        "<h2 style='text-align: center; font-size: 32px;'>تحديد عدد الصفوف</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='
            margin-top: 22px;
            background-color: #d9edf7;
            border: 1px solid #bce8f1;
            border-radius: 4px;
            padding: 7px;
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
        '>
            <strong>ملاحظة:</strong><br>كل صف يحتوي على 31 كرسي
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        selected_option = st.radio(
            "اختر عدد الصفوف:",
            options=[1, 2, 3, 4, 5],
            index=st.session_state.get("num_rows", 1) - 1,
            horizontal=True
        )


    # تأكيد أو التالي
    if not st.session_state.rows_confirmed:
        st.markdown("<p style='text-align:center;'>اضغط تأكيد عدد الصفوف للاستمرار</p>", unsafe_allow_html=True)
        if st.button("تأكيد عدد الصفوف", key="confirm_rows"):
            st.session_state.num_rows = selected_option
            st.session_state.rows_confirmed = True
    else:
        total = st.session_state.num_rows * 31
        st.markdown(
            f"<p style='text-align: center; color: green;'>تم تأكيد الصفوف: {st.session_state.num_rows} — الكراسي: {total}</p>",
            unsafe_allow_html=True
        )
        if st.button("التالي", key="go_to_next"):
            next_page()


# ——————————————————————————————————————————————————————————————
# الصفحة 3: اختيار أسماء الضيوف + زر "تأكيد"
# ——————————————————————————————————————————————————————————————
elif st.session_state.page == 3:

    # ——— عدد المقاعد الكلي حسب الصفوف ———
    num_rows = st.session_state.get("num_rows", 1)
    seats_per_row = 31  # ← عدّلي هذا الرقم إذا تغيّر تصميم الكراسي
    num_seats = num_rows * seats_per_row

    # ——— تكبير خط Tabs ———
    st.markdown(
        """
        <style>
        button[role="tab"] {
            font-size: 24px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ——— عنوان وتوضيح ———
    st.markdown(
        "<h2 style='text-align:center; font-size:32px;'>اختيار أسماء الضيوف</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='text-align:center; font-size:20px;'>"
        f"الحد الأقصى للمقاعد: <strong>{num_seats}</strong> ضيفًا<br>"
        f"لن تستطيع اختيار أكثر من العدد المحدد. التوزيع يتم عبر التبويبات حسب الفئة."
        f"</p>",
        unsafe_allow_html=True
    )

    # ——— تحميل البيانات ودمجها ———
    guests  = st.session_state.guests_df.copy()
    classes = st.session_state.classes_df.copy()
    df      = guests.merge(classes, left_on="رقم الفئة", right_on="الرتبة")
    categories = classes.sort_values("الرتبة")["الفئة"].tolist()

    # ——— حساب عدد المختارين ———
    def get_selected_count():
        return sum(len(st.session_state.get(cat, [])) for cat in categories)

    # ——— عداد المقاعد المتبقية ———
    counter = st.empty()
    def update_counter():
        rem = num_seats - get_selected_count()
        color = "green" if rem > 10 else ("orange" if rem > 0 else "red")
        counter.markdown(
            f"<h3 style='text-align:center; font-size:24px; color:{color};'>"
            f"عدد المقاعد المتبقية: <strong>{rem}</strong>"
            f"</h3>",
            unsafe_allow_html=True
        )
    update_counter()

    # ——— Tabs للفئات ———
    tabs = st.tabs(categories)
    for tab, cname in zip(tabs, categories):
        with tab:
            update_counter()

            # استبعاد المختارين من الفئات الأخرى
            others = []
            for other in categories:
                if other != cname:
                    others.extend(st.session_state.get(other, []))

            # قائمة الأسماء المتاحة
            avail = df[df["الفئة"] == cname]["الاسم"].drop_duplicates().tolist()
            avail = [n for n in avail if n not in others]
            if not avail:
                st.info("لا يوجد أسماء متاحة في هذه الفئة.")
                continue

            # checkboxes منظمة في 3 أعمدة
            cols = st.columns(3)
            picks = []
            for i, name in enumerate(avail):
                col = cols[i % 3]
                key = f"{cname}__{name}"
                checked = st.session_state.get(key, False)
                next_count = get_selected_count() + (0 if checked else 1)
                disabled = next_count > num_seats
                val = col.checkbox(name, value=checked, key=key, disabled=disabled)
                if val:
                    picks.append(name)

            st.session_state[cname] = picks
            update_counter()

    # ——— أزرار تأكيد/التالي ———
    st.markdown("---")
    selected_total = get_selected_count()
    guests_confirmed = st.session_state.get("guests_confirmed", False)

    if not guests_confirmed:
        if st.button("تأكيد الضيوف", key="confirm_guests", disabled=(selected_total == 0 or selected_total > num_seats)):
            final = []
            for cat in categories:
                final.extend(st.session_state.get(cat, []))
            st.session_state.selected_names = list(dict.fromkeys(final))
            st.session_state.guests_confirmed = True
            st.session_state.guests_merged = df
            st.rerun()
    else:
        st.success(f"تم اختيار {selected_total} ضيفًا بنجاح")
        if st.button("التالي", key="go_next"):
            next_page()



# ——————————————————————————————————————————————————————————————
# الصفحة 4: عرض رسم القاعة
# ——————————————————————————————————————————————————————————————
elif st.session_state.page == 4:

    import matplotlib.pyplot as plt

    # ——— العنوان ———
    st.markdown(
        "<h2 style='text-align: center; font-size: 32px;'>عرض رسم القاعة</h2>",
        unsafe_allow_html=True
    )

    # ——— البيانات ———
    num_rows = st.session_state.num_rows
    selected_names = st.session_state.selected_names

    guests  = st.session_state.guests_df.copy()
    classes = st.session_state.classes_df.copy()
    df = st.session_state.guests_merged.copy()
    df = df[df['الاسم'].isin(selected_names)].drop_duplicates('الاسم')
    df['order'] = df.index
    df = df.sort_values(['الرتبة', 'order']).reset_index(drop=True)

    # ——— توزيع الكراسي من المنتصف ———
    def middle_out_from_center(seat_list, center=16):
        left = sorted([s for s in seat_list if s < center], reverse=True)
        right = sorted([s for s in seat_list if s > center])
        result = [center]
        for l, r in zip(left, right):
            result.extend([l, r])
        result.extend(left[len(right):])
        result.extend(right[len(left):])
        return result

    # ——— المواقع الثابتة للكراسي الفيزيائيًا ———
    positions = {
        1:(1140,670),2:(1140,620),3:(1140,570),4:(1140,520),5:(1140,470),
        6:(1140,420),7:(1140,370),8:(1140,320),9:(1140,270),10:(1140,220),
        11:(1050,130),12:(970,130),13:(890,130),14:(810,130),15:(730,130),
        16:(650,130),17:(570,130),18:(490,130),19:(410,130),20:(330,130),
        21:(250,130),22:(160,220),23:(160,270),24:(160,320),25:(160,370),
        26:(160,420),27:(160,470),28:(160,520),29:(160,570),30:(160,620),31:(160,670)
    }

    chairs_per_row = 31
    full_seq = middle_out_from_center(list(range(1, 32)), center=16)

    for r in range(num_rows):
        st.markdown(f"<h3 style='text-align: center;'>الصف {r+1}</h3>", unsafe_allow_html=True)

        sub = df.iloc[r * chairs_per_row : (r+1) * chairs_per_row].reset_index(drop=True)
        if sub.empty:
            st.markdown(
                """
                <div style="
                    margin-top: 22px;
                    background-color: #f2f2f2;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 15px;
                    text-align: center;
                    font-size: 18px;
                    color: #555;
                    margin-bottom: 20px;
                ">
                    لا يوجد ضيوف في هذا الصف
                </div>
                """,
                unsafe_allow_html=True
            )
            continue

        assigned = {}
        used = []
        names = sub['الاسم'].tolist()
        for i, name in enumerate(names):
            for ch in full_seq:
                if ch not in used:
                    assigned[name] = ch
                    used.append(ch)
                    break

        sub['رقم الكرسي']   = list(range(1, len(sub)+1))
        sub['الموقع_الفعلي'] = sub['الاسم'].map(assigned)

        # ——— رسم الصف ———
        fig, ax = plt.subplots(figsize=(12, 6))
        info = []

        for _, row_ in sub.iterrows():
            ch = row_["الموقع_الفعلي"]
            name = row_["الاسم"]
            cat  = row_["الفئة"]
            x, y = positions.get(ch, (0, 0))
            clr  = "#d8de60" if ch == 16 else 'lightgray'

            ax.plot(x, y, 'o', ms=20, color=clr)
            ax.text(x, y, str(row_["رقم الكرسي"]), fontsize=16, ha='center', va='center', color='black')

            info.append({
                "رقم الكرسي": row_["رقم الكرسي"],
                "الاسم": name,
                "الفئة": cat
            })

        ax.set_xlim(0, 1300)
        ax.set_ylim(100, 800)
        ax.axis("off")
        st.pyplot(fig)

        # ——— جدول التوزيع مع الفئة ———
        st.dataframe(
            pd.DataFrame(info).sort_values("رقم الكرسي").reset_index(drop=True),
            use_container_width=True
        )

