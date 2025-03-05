from setuptools import setup, find_packages

setup(
    name="my-secure-test-package2",
    version="0.0.1",
    description="보안상 취약점이 있는 소스 코드 포함",
    author="hyeonwoo",
    author_email="sonhw1611@gmail.com",
    packages=find_packages(),
    install_requires=[],  # 공인 IP 예제 사용 시 필요
    python_requires=">=3.10",
)
