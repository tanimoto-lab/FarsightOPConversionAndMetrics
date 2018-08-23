# FarsightOPConversionAndMetrics
A small QT based application to convert output of farsight into 32bit label image and measure label sizes

Compilation command using PyInstaller 3.3.1

`pyinstaller --hidden-import=PyQt5.sip --hidden-import=pandas._libs.tslibs.np_datetime --hidden-import=pandas._libs.tslibs.nattype --hidden-import=pandas._libs.skiplist --hidden-import=scipy._lib.messagestream --path D:\Windows\Installations\Anaconda3\envs\farsightOPConv\Lib\site-packages\scipy\extra-dll --windowed FarsightOPConvMetricsQT.py`

IMPORTANT:
There could be trouble with compilation when pacakges are installed using conda. The last successful
build was with packages installed from pip.