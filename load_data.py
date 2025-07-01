import pandas as pd

# قراءة ملف الضيوف
guests_df = pd.read_csv('data/guest-list.csv', encoding='utf-8')

# قراءة ملف الرتب (عشان نعرضها في الواجهة لاحقًا)
priority_df = pd.read_csv('data/class-priority.csv', encoding='utf-8')

# قراءة ملف القاعات
rooms_df = pd.read_csv('data/rooms.csv', encoding='utf-8')

# عرض أول صفوف من كل ملف للتأكد
print("📋 الضيوف:")
print(guests_df.head())

print("\n🏷️ الفئات وترتيبها:")
print(priority_df.head())

print("\n🏛️ القاعات:")
print(rooms_df.head())
