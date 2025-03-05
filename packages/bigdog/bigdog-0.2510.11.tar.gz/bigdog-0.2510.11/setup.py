from setuptools import setup, find_packages

setup(
    name='bigdog',
    version='0.2510.11',
    author='Donghyeok Koh',
    author_email='donghyeok.koh.code@gmail.com',
    description='Test field for pre-release package evaluation',
    long_description=open('README.md').read(),  # README 파일 내용
    long_description_content_type='text/markdown',
    url='https://kohdh.com/',  # 패키지 저장소 URL
    packages=find_packages(),  # 패키지 디렉토리 자동 검색
    classifiers=[  # 패키지 분류 정보
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
    python_requires='>=3.6',  # 필요 파이썬 버전
    install_requires=[  # 의존성 패키지 목록
        'numpy>=1.23.2',
        'scipy>=1.9.2',
        'astropy',
    ],
    entry_points={  # 콘솔 스크립트 등록
        'console_scripts': [
            'your_script_name=your_package_name.your_module:main',
        ],
    },
)