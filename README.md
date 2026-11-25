# Ulagich

Rozilik bilan kamera va mikrofonni vaqtincha ulash uchun Flask/WebRTC namuna. Qabul qiluvchining emailiga Supabase Auth taklif havolasi yuboriladi. U havolani o‘zi ochib, so‘rovni qabul qilishi va brauzerda kamera/mikrofonga ruxsat berishi kerak.

## Supabase sozlash

1. Supabase’da loyiha yarating. Project URL va anon/publishable key’ni oling.
2. Auth > URL Configuration bo‘limida saytning Site URL’ini va Redirect URLs ro‘yxatiga `https://saytingiz-manzili/**` qo‘shing.
3. Auth > Email Templates > Invite user shablonini ochib, xat matnida kamera va mikrofon faqat qabul qiluvchi tasdiqlagach ulanadi deb aniq yozing. `{{ .ConfirmationURL }}` havolasini saqlang.
4. Supabase’ning standart email jo‘natgichi faqat loyihangiz jamoasidagi oldindan ruxsat etilgan manzillarga yuboradi va hozir 2 ta email/soat bilan cheklangan. Tashqi foydalanuvchilarga yuborish uchun Auth SMTP Settings’da custom SMTP sozlang.
5. Project URL, public anon key va server uchun secret/service_role key’ni sozlang. **Secret key’ni hech qachon HTML, brauzer yoki GitHub’ga joylamang.**

## Ishga tushirish

1. `C:\Ulagich` ichida terminal oching.
2. `python -m venv .venv`
3. PowerShell’da `.venv\Scripts\Activate.ps1`
4. `pip install -r requirements.txt`
5. Quyidagi muhit o‘zgaruvchilarini terminalda belgilang:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY` (yoki publishable key)
   - `SUPABASE_SECRET_KEY` (faqat Flask serverda)
   - `APP_PUBLIC_URL` (ommaviy HTTPS sayt manzili)
6. `python app.py`

Email taklif havolasi Supabase sozlamasidagi Email OTP Expiration muddatiga bog‘liq (standartida 1 soat). Bu muddat davomidagi rozilik linkiga taalluqli; ulanish boshlangach, sessiya tomonlardan biri **Uzatishni to‘xtatish** tugmasini bosmaguncha davom etadi. Kamera va mikrofon uchun rozilik talab qilinadi.

## Xavfsizlik eslatmasi

Namuna email yuborishni soatiga bir IP’dan 5, bir manzilga 3 taklif bilan cheklaydi; bu xotirada saqlanadi va server qayta ishga tushsa tozalanadi. Ochiq internetga chiqarishdan oldin doimiy rate-limit, HTTPS reverse proxy, abuse himoyasi va production sozlamalarini qo‘shing. Supabase secret kaliti RLS’ni chetlab o‘tadi va faqat ishonchli serverda turishi kerak.

