from setuptools import setup
from io import open

setup(
    name="scireadability",
    packages=["scireadability"],
    version="1.0.0",
    description="Calculate statistical features from text, mainly scientific literature",
    author="Shivam Bansal, Chaitanya Aggarwal, Robert Roth",
    author_email="rwroth5@gmail.com",
    url="https://github.com/robert-roth/scireadability",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_data={"": ["resources/en/easy_word_list.txt", "resources/en/custom_dict.json"]},
    include_package_data=True,
    install_requires=["cmudict", "setuptools", "appdirs"],
    license="MIT",
    python_requires=">=3.10",
    project_urls={
        'Documentation': 'https://scireadability-rwroth5.pythonanywhere.com/about/',
        'Demo': 'https://scireadability-rwroth5.pythonanywhere.com/analyze/',
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing",
    ],
)
