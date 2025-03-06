from setuptools import setup, find_packages

setup(
    name='ocr_onnx',  # 包的名称
    version='0.',     # 版本号
    packages=find_packages(),  # 自动查找包目录
    install_requires=[
        # 列出你的包依赖的其他包
    ],
    package_data={
        'ocr_onnx': ['models/*'],  # 指定包含的数据文件
    },
    include_package_data=True,  # 确保数据文件被包含
    description='ocr_onnx',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='你的名字',
    author_email='你的邮箱',
    url='你的项目主页URL',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
