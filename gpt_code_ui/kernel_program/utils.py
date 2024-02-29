import os
import pathlib
import re
import subprocess
import sys
import venv


def escape_ansi(line):
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


def create_venv(venv_dir: pathlib.Path, install_default_packages: bool) -> pathlib.Path:
    venv_bindir = venv_dir / "bin"
    venv_python_executable = venv_bindir / os.path.basename(sys.executable)

    if not os.path.isdir(venv_dir):
        # create virtual env inside venv_dir directory
        venv.create(venv_dir, system_site_packages=True, with_pip=True, upgrade_deps=True)

        if install_default_packages:
            # install wheel because some packages do not like being installed without
            subprocess.run([venv_python_executable, "-m", "pip", "install", "wheel>=0.41,<1.0"])
            # install all default packages into the venv
            default_packages = [
                "ipykernel>=6,<7",
                "numpy>=1.24,<1.25",
                "dateparser>=1.1,<1.2",
                "pandas>=1.5,<1.6",
                "geopandas>=0.13,<0.14",
                "tabulate>=0.9.0<1.0",
                "PyPDF2>=3.0,<3.1",
                "pdfminer>=20191125,<20191200",
                "pdfplumber>=0.9,<0.10",
                "matplotlib>=3.7,<3.8",
                "openpyxl>=3.1.2,<4",
                "rdkit>=2023.3.3",
                "bio>=1.6.2",
                "scipy==1.11.1",
                "scikit-learn==1.3.0",
                "wordcloud>=1.9.3",
                "XlsxWriter>=3.1.9",
                "docx>=0.2.4",
            ]
            subprocess.run([str(venv_python_executable), "-m", "pip", "install"] + default_packages)

    # get base env library path as we need this to refer to this form a derived venv
    site_packages = subprocess.check_output(
        [
            venv_python_executable,
            "-c",
            'import sysconfig; print(sysconfig.get_paths()["purelib"])',
        ]
    )
    site_packages_decoded = site_packages.decode("utf-8").split("\n")[0]

    return pathlib.Path(site_packages_decoded)


def create_derived_venv(base_venv: pathlib.Path, venv_dir: pathlib.Path):
    site_packages_base = create_venv(base_venv, install_default_packages=True)
    site_packages_derived = create_venv(venv_dir, install_default_packages=False)

    # create a link from derived venv into the base venv, see https://stackoverflow.com/a/75545634
    with open(site_packages_derived / "_base_packages.pth", "w") as pth:
        pth.write(f"{site_packages_base}\n")

    venv_bindir = venv_dir / "bin"
    venv_python_executable = venv_bindir / os.path.basename(sys.executable)

    return venv_bindir, venv_python_executable
