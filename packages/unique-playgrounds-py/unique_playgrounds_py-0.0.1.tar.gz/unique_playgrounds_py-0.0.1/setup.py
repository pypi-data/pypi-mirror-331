import re
import setuptools


def read_requirements(path):
    with open(path, "r") as f:
        requirements = f.read().splitlines()
        processed_requirements = []

        for req in requirements:
            # For git or other VCS links
            if req.startswith("git+") or "@" in req:
                pkg_name = re.search(r"(#egg=)([\w\-_]+)", req)
                if pkg_name:
                    processed_requirements.append(pkg_name.group(2))
                else:
                    # You may decide to raise an exception here,
                    # if you want to ensure every VCS link has an #egg=<package_name> at the end
                    continue
            else:
                processed_requirements.append(req)
        return processed_requirements


with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = read_requirements("requirements.txt")


setuptools.setup(
    name="unique-playgrounds-py",
    version="0.0.1",
    author="UniqueNetwork",
    author_email="pypi@unique.network",
    description="A helper class for working with the Unique Network blockchain.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UniqueNetwork/unique-playgrounds-py",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="Apache-2.0",
    python_requires=">=3.11",
)
