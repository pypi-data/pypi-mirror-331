from setuptools import setup, Extension
import sys
import platform
import os

# Read the content of README.md
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Platforma göre uygun derleyici ayarlarını belirleyin
extra_compile_args = []
extra_link_args = []
sources = []
include_dirs = []

# Linux/Unix platformu için ayarlar
if platform.system() == 'Linux' or platform.system() == 'Darwin':
    extra_compile_args = ['-O2', '-Wall']
    extra_link_args = []  # Sodium bağımlılığı kaldırıldı
    sources = [
        'src/Unix-posix/adam.c',     # Linux/Unix kaynak dosyası
        'src/Unix-posix/datasetname.c' # Linux/Unix kaynak dosyası
    ]
    include_dirs = [
        '/usr/local/include',    # Diğer header dosyaları
        '/usr/include/python3.x',  # Python header dosyası
    ]

extensions = [
    Extension(
        'adamlibrary.adam',  # Modül adı
        sources=[sources[0]],  # Platforma göre kaynak dosyası
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        include_dirs=include_dirs,  # Header dosya yolu
    ),
    Extension(
        'adamlibrary.datasetname',  # Modül adı
        sources=[sources[1]],  # Platforma göre kaynak dosyası
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        include_dirs=include_dirs,  # Header dosya yolu
    ),
]

# Setup fonksiyonu ile paketi oluştur
setup(
    name='adamlibrary',
    version='1.5',
    description='Improved library for Python to support C library extensions',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Specify the format of the description
    ext_modules=extensions,  # Derleme için gerekli extensionlar
    packages=['adamlibrary'],  # Paket ismi
    include_package_data=True,
    install_requires=[  # Gerekli Python kütüphaneleri
        'cython',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: C',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python versiyonu
)
