import setuptools

setuptools.setup(
    name="turing_envs",
    version="0.0.1",
    author="Grupo Turing",
    author_email="turing.usp@gmail.com",
    description="Ambientes do gym desenvolvidos pelo Grupo Turing",
    url="https://github.com/GrupoTuring/turing_envs",
    project_urls={
        'Source': 'https://github.com/GrupoTuring/turing_envs',
        'Tracker': 'https://github.com/GrupoTuring/turing_envs/issues',
    },
    license="MIT",
    packages=['turing_envs'],
    install_requires=['pygame', 'gym'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
