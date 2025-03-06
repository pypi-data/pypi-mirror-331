# Django Project Generator

🚀 **Django Project Generator** - bu interaktiv CLI vositasi bo‘lib, u yangi Django loyihalarini tez va soddalashtirilgan
tarzda yaratishga yordam beradi. Bu vosita turli konfiguratsiya variantlarini taklif qiladi va foydalanuvchining
tanloviga qarab kerakli kutubxonalarni avtomatik o‘rnatadi.

---

## ⚙️ O‘rnatish

```bash
pip install django-gen
```

---

## 🚀 Ishga tushirish

Yangi Django loyihasini yaratish uchun quyidagi buyruqni bajaring:

```bash
django-gen <project_name>
```

So‘ng, terminalda bir nechta interaktiv savollarga javob berishingiz kerak bo‘ladi:

```bash
❓ Django REST Framework ishlatiladimi? (y/n)
❓ JWT Authentication kerakmi? (y/n)
❓ Docker orqali ishga tushirasizmi? (y/n)
❓ Django Debug Toolbar o‘rnatilsinmi? (y/n)
❓ Black formatter o‘rnatilsinmi? (y/n)
❓ Flake8 linter o‘rnatilsinmi? (y/n)

🔹 Qaysi database-ni ishlatmoqchisiz?
   1. PostgreSQL
   2. MySQL
   3. SQLite (default)
```

Tanlangan variantlarga qarab loyiha avtomatik yaratiladi va kerakli konfiguratsiyalar bajariladi.

---

## 🔧 Konfiguratsiya

Agar barchasiga Ha deb javob bergan bo'lsangi loyihangiz shu korinishda generatsya boladi.

```
project_name
├── config
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings
│   │   ├── base.py
│   │   ├── deployment.py
│   │   └── __init__.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── setup.cfg
├── src
│   ├── api
│   │   ├── include_routers.py
│   │   └── __init__.py
│   ├── apps
│   │   ├── __init__.py
│   │   ├── serializers
│   │   │   ├── base.py
│   │   │   └── __init__.py
│   │   ├── urls
│   │   │   └── __init__.py
│   │   └── views
│   │       └── __init__.py
│   ├── core
│   │   ├── admin
│   │   │   └── __init__.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   └── models
│   │       ├── base.py
│   │       └── __init__.py
│   └── shared
│       ├── drf_yasg.py
│       └── __init__.py
└── templates
    └── base.html
```

---

## 🛠 Hissa qo‘shish

Hissa qo‘shmoqchi bo‘lsangiz ([Github]):

1. **Fork qiling** – [GitHub repo](https://github.com/zohidillo/django-project-generator) sahifasiga kiring va `Fork` tugmasini bosing.
2. O‘zingizning branch-ni qo'shing (`feature/new-feature`).
3. O‘zgarishlaringizni push qiling.
4. Pull request yuboring.

---

## 📄 Litsenziya

Ushbu loyiha MIT License ostida tarqatiladi. Siz koddan erkin foydalanishingiz, uni o‘zgartirishingiz va tarqatishingiz
mumkin. Agar loyihaga o‘z hissangizni qo‘shmoqchi bo‘lsangiz, pull request yoki issue oching! 🎉
