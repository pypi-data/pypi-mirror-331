from setuptools import setup, find_packages

setup(
    name="django-gen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "django",
        "click",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "django-gen=django_gen.cli:main",
        ],
    },
    author="Zohidillo Turgunov",
    description="""🚀 **Django Project Generator** - bu interaktiv CLI vositasi bo‘lib, u yangi Django loyihalarini tez va soddalashtirilgan
tarzda yaratishga yordam beradi. Bu vosita turli konfiguratsiya variantlarini taklif qiladi va foydalanuvchining
tanloviga qarab kerakli kutubxonalarni avtomatik o‘rnatadi.
""",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zohidillo/django-project-generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
    ],
)
