import os
from setuptools import setup,find_packages



from setuptools import Extension
from setuptools.command.build_ext import build_ext
class DummyExtension(Extension):
    def __init__(self):
        super().__init__("dummy.extension", sources=[])
class DummyExtensionBuild(build_ext):
    def run(self) -> None:
        return
cmdclass = {
    "build_ext": DummyExtensionBuild,
}
# 定义扩展模块
ext_modules = [
    # DummyExtension()
    ]



classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3 :: Only
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Unix
"""

curr_path = os.path.abspath(os.path.dirname(__file__))
setup(
    name='asyncllm',
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    version='0.0.0.1',
    packages=find_packages(),
    package_data={'asyncllm': ['py.typed']},
    python_requires='>=3.8',
    install_requires=['httpx >= 0.27.0', 'pydantic >= 2.7.3',"aiohttp == 3.11.11","openai >= 1.43.0","requests >= 2.32.3","ollama >= 0.4.4"],
    classifiers=filter(None, classifiers.split('\n')),
    zip_safe=True,
    author='YaqiangSun',
    long_description=open(os.path.join(curr_path, 'README.md'), 'r').read(),
    long_description_content_type='text/x-rst',
    description='asyncllm framework',
    license='GPL v3',
    keywords='asyncllm framework',
    url='https://github.com/xxxxxx/asyncllm',
    include_package_data=True,
)