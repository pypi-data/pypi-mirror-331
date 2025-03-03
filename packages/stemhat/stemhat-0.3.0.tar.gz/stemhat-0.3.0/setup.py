from setuptools import setup, find_packages

setup(
    name="stemhat",
    version="0.3.0",
    author="Cytron(Divyessh)",
    author_email="divyesshev3@gmail.com",
    description="A library to control Cytron Pi StemHat",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Teakzieas/StemhatPython",
    packages=find_packages(),
     install_requires=["smbus2==0.5.0","gpiozero==2.0.1","adafruit-circuitpython-ssd1306==2.12.19","adafruit-blinka==8.52.0","pillow==11.1.0","lgpio==0.2.2.0","adafruit-circuitpython-apds9960==3.1.14"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
 
    ],
    python_requires=">=3.6",
    package_data={
        "stemhat": ["Arial.ttf"],  # Include font file
    },
    include_package_data=True,
)
