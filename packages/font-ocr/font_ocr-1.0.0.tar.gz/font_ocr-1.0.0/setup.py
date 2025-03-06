from setuptools import setup, find_packages

setup(
    name='font_ocr',
    version='1.0.0',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'fonttools >= 4.44.0',
        'lxml >= 4.9.2',
        'loguru >= 0.7.0',
        'ddddocr >= 1.4.9',
        'matplotlib >= 3.7.1'
    ],
    author='明廷盛',
    author_email='[email protected]',
    description='使用OCR解决文字反爬',
    include_package_data=True,
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Tlyer233/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    keywords='font anti-crawler ocr web-scraping',
)
