#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
import sys, os, re
from os.path import basename

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.resize(450, 310)
        self.setWindowTitle(u"Nova stahovač")
        self.setWindowIcon( QtGui.QIcon('nova-dl.svg') )
        grid = QtGui.QGridLayout()
        
        self.url_lineedit = QtGui.QLineEdit()
        url_label = QtGui.QLabel(u"Adresa pořadu:")
        grid.addWidget( url_label, 0, 0)
        grid.addWidget( self.url_lineedit, 0, 1, 1, 2)
        
        save_label = QtGui.QLabel(u"Uložit do:")
        self.save_lineedit = QtGui.QLineEdit( QtCore.QDir.homePath() )
        save_browsebutton = QtGui.QPushButton(u"Najít")
        save_browsebutton.clicked.connect(self.showDialog)
        grid.addWidget(save_label, 1, 0)
        grid.addWidget(self.save_lineedit, 1, 1)
        grid.addWidget(save_browsebutton, 1, 2)
        
        quality_label = QtGui.QLabel(u"Kvalita:")
        self.quality_combobox = QtGui.QComboBox()
        self.quality_combobox.addItem(u"Vysoká kvalita")
        self.quality_combobox.addItem(u"Nízká kvalita")
        
        down_button = QtGui.QPushButton(u"STÁHNI")
        down_button.setStyleSheet( "background-color: green; color: white")
        down_button.clicked.connect(self.run)
        
        stop_button = QtGui.QPushButton(u"STOP")
        stop_button.setStyleSheet("background-color: red; color: white")
        stop_button.clicked.connect(self.stop)
        
        self.button = QtGui.QStackedWidget()
        self.button.addWidget(down_button)
        self.button.addWidget(stop_button)
        self.button.setFixedWidth(80)
        
        grid.addWidget(quality_label, 2, 0)
        grid.addWidget(self.quality_combobox, 2, 1)
        grid.addWidget(self.button, 2, 2)
        
        self.progress = QtGui.QProgressBar()
        self.progress.setRange(0, 1000)
        
        grid.addWidget(self.progress, 3, 0, 1, 3)
        
        self.textArea = QtGui.QTextEdit()
        self.textArea.setReadOnly(True)
        self.textArea.setOverwriteMode(False)
        
        grid.addWidget(self.textArea, 4, 0, 5, 3)
        
        about_label = QtGui.QLabel(u'<a href="about">O programu</a>')
        about_label.linkActivated.connect(self.about)
        grid.addWidget(about_label, 9,0)
        
        self.setLayout(grid)
        self.exe = self.findExe()
        
        self.fg = FilenameGetter(self.exe, QtCore.QDir.homePath() )
        self.url_lineedit.textChanged.connect(self.fg.getFilename)
        self.fg.gotFilename.connect(self.save_lineedit.setText)
        self.save_lineedit.cursorPositionChanged.connect(self.fg.abort)
                
    def showDialog(self):
        self.save_lineedit.setText( QtGui.QFileDialog.getSaveFileName(self, u"Uložit do", self.save_lineedit.text(), u"Flash video (*.flv)" ) )

    def findExe(self):
        if os.name == 'nt':
            return "nova-dl.exe"
        else:
            if os.path.isfile('./nova-dl.py'):
                return './nova-dl.py'
            else:
                return 'nova-dl'

    def run(self):
        self.textArea.clear()
        self.button.setCurrentIndex(1)
        self.progress.setValue(0)
        
        q = 'high' if self.quality_combobox.currentIndex() == 0 else "low"

        self.p = QtCore.QProcess()
        self.p.setReadChannel(QtCore.QProcess.StandardError)
        arg = ["-q", q,
               '-o', '"%s"' %self.save_lineedit.text(),
               str(self.url_lineedit.text() ) ]
        
        self.p.start(self.exe, arg )
        self.p.readyRead.connect(self.readyRead)
        self.p.finished.connect(self.finished)
        
    def stop(self):
        self.p.terminate()
    
    def readyRead(self):
        s = self.p.readAll()
        self.textArea.append( QtCore.QString( s ) )
        
        r = re.findall(r"\((.+)?%\)", s)
        if r:
            self.progress.setValue( int( float(r[-1])*10 ) )
        
    def finished(self, exitCode, exitStatus):
        if exitCode == 0 and exitStatus == QtCore.QProcess.NormalExit:
            QtGui.QMessageBox.information(self, u"Hotovo", u"Stahování úspěšně dokončeno")
        
        else:
            QtGui.QMessageBox.critical(self, u"Selhání", u"Stahování selhalo")
        
        self.p.close()
        self.button.setCurrentIndex(0)
        self.progress.setValue(100*10)

    def about(self, url):
      QtGui.QMessageBox.about(self, "O nova-dl", u'''Autor: Jakub Lužný
Ikona: Roman Šmakal''' )

class FilenameGetter(QtCore.QObject):
    p = QtCore.QProcess()
    gotFilename = QtCore.pyqtSignal(QtCore.QString)
    
    def __init__(self, exe, dest):
        QtCore.QObject.__init__(self)
        self.exe = exe
        self.dest = dest
        self.p.finished.connect(self.processFinished)
        self.p.setReadChannel(QtCore.QProcess.StandardOutput)
        
    def getFilename(self, url):
        self.p.kill()
        self.p.start(self.exe, ['-g', url])
        
    def processFinished(self):
        url = str( self.p.readAll() ).strip()
        if url:
            url = QtCore.QString( self.dest + QtCore.QDir.separator() + basename(url) + '.flv' )
            self.gotFilename.emit(url)
    
    def abort(self):
        self.p.kill()
        self.p.readAll()
             
app = QtGui.QApplication(sys.argv)

mw = MainWindow()
mw.show()

sys.exit(app.exec_())
