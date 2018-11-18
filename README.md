# Description


A small QT based application to convert the 16-bit output of farsight into 32-bit and calculate the following features of labelld objects: centroid, surface area, sphericity, volume and principal moments

# Installation

see install.md

# Compilation

The application can be compiled into a standalone QT application using the following steps. Note: Only PyInstaller v3.3.1 was tested. The application may not compile successfully with other versions.

1. Activate the conda environment created in 'install.md'
2. Navigate into the directory containing FarsighOPConvMetricsQT.py
3. Execute the following:


`pyinstaller --hidden-import=PyQt5.sip --hidden-import=pandas._libs.tslibs.np_datetime --hidden-import=pandas._libs.tslibs.nattype --hidden-import=pandas._libs.skiplist --hidden-import=scipy._lib.messagestream --path D:\Windows\Installations\Anaconda3\envs\farsightOPConv\Lib\site-packages\scipy\extra-dll --windowed FarsightOPConvMetricsQT.py`

Notes:

1. The path of the folder extra-dll above needs to be changed depending the anaconda environment created in 'install.md'
2. There could be trouble with compilation when packages are installed using conda. The last successful
build was with packages installed from pip.

# Usage
The application can be run using the executable "FarsightOPConvMetricsQT" in the folder dist/FarsightOPConvMetricsQT.

Alternatively, the application can also be started directly using the following steps:

1. Activate the conda environment created in 'install.md'
2. Navigate into the directory containing FarsightOPConvMetricsQT.py
3. Execute `python FarsightOPConvMetricsQT.py`
