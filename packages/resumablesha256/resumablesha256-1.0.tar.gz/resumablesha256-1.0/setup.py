from setuptools import setup, find_packages, Extension


# Note that for Python 3.6, which only supports setuptools<=59.6.0, we need
# to specify the name and version, pyproject.toml is only supported in >=61.0.
setup(
    name="resumablesha256",
    version="1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=False,
    ext_modules=[Extension(
        "resumablesha256._sha256_ext",
        [
            "src_ext/_sha256_ext.c",
            "src_ext/bcon_sha256.c"
        ],
        include_dirs=["src_ext"],
        py_limited_api=True)
    ]
)
