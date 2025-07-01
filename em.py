from PIL import Image, ImageDraw, ImageFont

# تحميل الصورة
img = Image.open("قاعة التجليس.png")
draw = ImageDraw.Draw(img)

# تحميل الخط (تقدرين تختارين خط عربي واضح)
font = ImageFont.load_default()

# مثال: كرسي رقم 1
draw.text((220, 50), "محمد", fill="black", font=font)

# كرسي رقم 2
draw.text((180, 50), "خالد", fill="black", font=font)

# وهكذا...

# حفظ النتيجة
img.save("قاعة-مع-الأسماء.png")
