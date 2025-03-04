from setuptools import setup, find_packages

# Paket bilgileri
setup(
    name="kriptex",  # Paket ismi
    version="0.1.0",  # Versiyon numarası 
    author="Zaman Huseyinli",  # Yazar adı
    author_email="zamanhuseynli23@gmail.com",  # Yazar emaili
    description="Kriptex symbol encryption library",  # Paket açıklaması
    long_description=open('README.md').read(),  # README dosyasını oku
    long_description_content_type='text/markdown',  # README dosyasının türü
    url="https://github.com/Azccriminal/kriptex",  # GitHub URL'niz (ya da proje linkiniz)
    packages=find_packages(),  # Projedeki tüm paketleri bul
    classifiers=[  # PyPI sınıflandırmaları   
        "Programming Language :: Python :: 3", 
        "License :: OSI Approved :: BSD License",  # BSD 3-Clause lisansı belirtildi
        "Operating System :: OS Independent",  
    ],
    install_requires=[  # Gerekli bağımlılıklar
        'pycryptodome',  # Kriptografi kütüphanesi
        'requests',  # Web isteği için
        'PyQt6',  # GUI için
    ],
    python_requires='>=3.6',  # Python sürümü gereksinimi
    entry_points={  # Komut satırından çalıştırılacak komutlar (opsiyonel)
        'console_scripts': [
            'kriptex=kriptex.main:main',  # Komut satırı giriş noktası
        ],
    },
    include_package_data=True,  # Paket içerisindeki veri dosyalarını dahil et
    package_data={  # Paket dosyaları
        'kriptex': ['encryption.py'],  # encryption.py dosyasını ekleyin
    },
    zip_safe=False,  # .egg dosyalarını kullanma
)
