from setuptools import setup, find_packages

setup(
    name='SST_v_2',
    version='0.1',
    author='Kushagra Upadhyay',
    author_email='kushagrathecoder@gmail.com',
    description='Speech-To-Text module for a virtual assistant',
    packages=find_packages(),
    install_requires=[
        'selenium',
    ],
    python_requires=">=3.6",
     include_package_data=True,  # ✅ Include non-Python files
    package_data={
        "": ["*.html", "*.css", "*.js"],  # ✅ Include these file types
        "static": ["*"],  # ✅ Include everything in 'static/' folder
        "templates": ["*"],  # ✅ Include everything in 'templates/' folder
        "data": ["*.txt"],  # ✅ Includes all .txt files in 'data/' folder
    },
)
