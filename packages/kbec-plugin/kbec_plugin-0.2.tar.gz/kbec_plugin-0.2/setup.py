from distutils.core import setup

setup(
    name="kbec_plugin",
    packages=["kbec_plugin"],
    version="0.2",
    license="GPL-3.0",
    description="Plugin framework for interacting with Battleye RCON",
    author="Katsi",
    author_email="katistix@gmail.com",
    url="https://github.com/Katistic/kbec-plugin/",
    download_url="https://github.com/Katistic/kbec-plugin/archive/refs/tags/v0.1.tar.gz",
    keywords=["Battleye", "RCON", "Battleye RCON"],
    install_requires=[
        "berconpy",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
    ],
)