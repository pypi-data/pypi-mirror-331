from setuptools import setup, find_packages

setup(
    name="my-secure-test-package",
    version="0.0.2",
    description="A sample package to request",
    author="hyeonwoo",
    author_email="sonhw1611@gmail.com",
    packages=find_packages(),
    install_requires=["requests==2.25.1"],  # 공인 IP 예제 사용 시 필요
    python_requires=">=3.10",
)
