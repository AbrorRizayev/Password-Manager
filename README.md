TeamVault — Secure Password Manager
TeamVault bu parollarni shifrlangan holatda saqlash va boshqarish uchun mo'ljallangan backend tizimi. Loyiha xavfsizlik va foydalanish qulayligiga qaratilgan bo'lib, Django frameworkida ishlab chiqilgan.

Asosiy funksiyalar
Xavfsiz Hashing: Master parollar Argon2 algoritmi yordamida himoyalangan.

Ma'lumotlar Shifrlash: Saqlangan parollar AES-256 simmetrik shifrlash asosida saqlanadi.

Password Strength: Har bir parol uchun murakkablik darajasi (Weak, Fair, Strong) indikatori mavjud.

Reuse Alert: Bir xil parollar bir necha xizmatlarda ishlatilganda ogohlantirish tizimi ishlaydi.

Eksport: Saqlangan ma'lumotlarni Pandas yordamida Excel formatida yuklab olish mumkin.

Qidiruv va Filtr: Xizmat nomi bo'yicha qidirish va kategoriyalar bo'yicha saralash funksiyalari mavjud.

Texnologiyalar
Backend: Python / Django

Database: PostgreSQL (Supabase) / Redis

Xavfsizlik: Argon2, Cryptography

Frontend: Tailwind CSS

O'rnatish tartibi
Loyihani yuklab oling va virtual muhitni yoqing:

Bash
git clone https://github.com/SizningUsername/reponame.git
python -m venv .venv
source .venv/bin/activate  # Windows uchun: .venv\Scripts\activate
Zarur kutubxonalarni o'rnating:

Bash
pip install -r requirements.txt
Ma'lumotlar bazasini sozlang:

Bash
python manage.py migrate
Admin akkauntini yarating:

Bash
python manage.py createsuperuser
Loyihani ishga tushiring:

Bash
python manage.py runserver
