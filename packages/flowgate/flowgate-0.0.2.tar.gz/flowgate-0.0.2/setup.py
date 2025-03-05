from setuptools import find_packages, setup

setup(
    name="flowgate",
    version="0.0.2",
    description="The kafka client we all want",
    url="https://github.com/nf1s/flowgate",
    author="nf1s",
    author_email="ahmed.nafies@gmail.com",
    license="MIT",
    packages=find_packages(),
    setup_requires=['wheel'],
    install_requires=[
        'structlog>=17.2.0',
        'confluent-kafka[avro]==2.*',
        'opentelemetry-api==1.27.0',
        'opentelemetry-semantic-conventions==0.48b0',  # 1.27.0
    ],
    zip_safe=False,
)
