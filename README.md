# Ulagich

Rozilik bilan kamera va mikrofonni vaqtincha ulash uchun Flask/WebRTC namuna. Telefon raqami kiritilganda SMS orqali bir martalik rozilik havolasi yuboriladi. Telefon egasi havolani o‘zi ochib, ekrandagi so‘rovni qabul qilishi va brauzerda kamera/mikrofonga ruxsat berishi kerak.

## Ishga tushirish

1. Python 3.10 yoki undan yangisini o‘rnating.
2. `C:\Ulagich` ichida terminal oching.
3. `python -m venv .venv`
4. PowerShell’da `.venv\Scripts\Activate.ps1`
5. `pip install -r requirements.txt`
6. Twilio hisobidan muhit o‘zgaruvchilarini sozlang: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `PUBLIC_BASE_URL` (saytning ommaviy HTTPS manzili).
7. `python app.py`

Sayt HTTPS manzilda joylashtirilishi kerak. `127.0.0.1` faqat server ishlayotgan kompyuterda ochiladi. Kalitlarni kod ichiga yozmang.

## Rozilik va cheklovlar

Ko‘ruvchi telefon raqamini xalqaro formatda kiritadi. SMS havolasi 10 daqiqada eskiradi. Namuna soatiga bir IP’dan 5, bir raqamga 3 SMS bilan cheklaydi. Telefon egasi havolani ochishi, rozilikni bosishi va brauzer ruxsatini berishi shart. Havola kamera/mikrofonni o‘zi yoqmaydi. Istalgan tomon sessiyani to‘xtata oladi.

Takliflar va limitlar hozir xotirada saqlanadi; server qayta ishga tushsa takliflar bekor bo‘ladi. Ochiq internetga chiqarishdan oldin HTTPS reverse proxy, doimiy saqlash va abuse himoyasini qo‘shing. SMS provayderida to‘lov va mamlakat bo‘yicha cheklovlar bo‘lishi mumkin.
