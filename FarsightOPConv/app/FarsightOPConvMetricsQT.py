import inspect
import os
import platform
import sys

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, \
    QMessageBox, QDesktopWidget, QTextEdit, \
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QGroupBox

from FarsightOPConv.app.customWidgets import FileSelect, raiseInfo
from FarsightOPConv.app.coreFunction import farsightOPConvAndMetricsGen


class FarsightOPConvMetricsThread(QThread):

    def __init__(self, farsightOutputLabelImageFile: str, farsightOutputSeedsFile: str):
        self.labelFile = farsightOutputLabelImageFile
        self.seedsFile = farsightOutputSeedsFile
        self.terminated = False

        super().__init__()

    def run(self):
        yields = []

        for ret in farsightOPConvAndMetricsGen(self.labelFile, self.seedsFile):

            if self.isInterruptionRequested():
                return
            else:
                yields.append(ret)

        self.outputFiles = yields[-1]


class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.initui()
        self.calcThread = FarsightOPConvMetricsThread('', '')

    def initui(self):
        mainVBox = QVBoxLayout()

        self.labelImageSelect = FileSelect(title='Farsight Output Label Image',
                                             dialogDefaultPath=None,
                                             dialogFileTypeFilter='Label Image(*.tif *.tiff)',
                                             dialogTitle='Choose Farsight Output Label Image'
                                             )
        self.seedFileSelect = FileSelect(title='Farsight Output Seed Points File',
                                             dialogDefaultPath=None,
                                             dialogFileTypeFilter='Seed Points File(*.txt)',
                                             dialogTitle='Choose Farsight Output Seed Points file'
                                             )

        mainVBox.addWidget(self.labelImageSelect)
        mainVBox.addWidget(self.seedFileSelect)

        runGroupBox = QGroupBox(self)
        runBox = QHBoxLayout()

        runControlBox = QVBoxLayout()
        startButton = QPushButton('Run')
        startButton.clicked.connect(self.runFarsightOPConvMetrics)

        self.interruptButton = QPushButton('Interrupt')

        runControlBox.addWidget(startButton)
        runControlBox.addWidget(self.interruptButton)

        self.outputDisplay = QTextEdit()
        self.outputDisplay.setReadOnly(True)

        runBox.addWidget(self.outputDisplay)
        runBox.addLayout(runControlBox)
        runGroupBox.setLayout(runBox)

        mainVBox.addWidget(runGroupBox)

        self.setLayout(mainVBox)

    def runFarsightOPConvMetrics(self):

        labelFile = self.labelImageSelect.getText()

        seedsFile = self.seedFileSelect.getText()

        if labelFile == '':
            raiseInfo("Label File not initialized! Please initialize and try again.", self)
            return

        if seedsFile == '':
            raiseInfo("Seed Points File not initialized! Please initialize and try again", self)
            return

        self.calcThread.__init__(labelFile, seedsFile)
        self.calcThread.start()
        self.outputDisplay.append(f'Working on:\n{labelFile} and {seedsFile}\nPlease Wait. The program may take '
                                  f'a upto an hour to finish depending on the input files......')
        self.interruptButton.clicked.connect(self.handleInterruption)
        self.calcThread.finished.connect(self.handleFinished)

    def handleInterruption(self):

        self.calcThread.terminated = True
        self.calcThread.requestInterruption()
        self.calcThread.wait()

    def handleFinished(self):

        if self.calcThread.terminated:
            self.outputDisplay.append('Calculation Terminated. No Output generated.')
        else:
            self.outputDisplay.append(f'Finished Succesfully. The following output files were generated\n'
                                      f'{self.calcThread.outputFiles[0]}\nf{self.calcThread.outputFiles[1]}')



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):


        exitAction = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)


        centralWidget = CentralWidget(self)
        self.setCentralWidget(centralWidget)


        self.setWindowTitle('Farsight Output Conversion and Metrics')
        self.setGeometry(300, 300, 500, 700)
        self.center()
        # self.setWindowIcon(QIcon('web.png'))
        self.show()



    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):

        message = ""
        centralWidget = self.centralWidget()
        if centralWidget.calcThread.isRunning():
            message += "A conversion process is running. If you quit, all progress will be lost. "
        reply = QMessageBox.question(self, 'Message',
                                     f"{message}Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            centralWidget.handleInterruption()
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())