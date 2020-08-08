import setuptools

setuptools.setup(
    name="turing-envs",
    version="0.1.0",
    author="Grupo Turing",
    author_email="turing.usp@gmail.com",
    description="Ambientes do gym desenvolvidos pelo Grupo Turing",
    url="https://github.com/GrupoTuring/turing-envs",
    project_urls={
        'Source': 'https://github.com/GrupoTuring/turing-envs',
        'Tracker': 'https://github.com/GrupoTuring/turing-envs/issues',
    },
    license="MIT",
    packages=['turing_envs'],
    install_requires=['pygame', 'gym'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
