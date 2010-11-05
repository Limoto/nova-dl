#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
import sys, os

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
        self.save_lineedit = QtGui.QLineEdit()
        save_browsebutton = QtGui.QPushButton(u"Najít")
        self.connect(save_browsebutton, QtCore.SIGNAL('clicked()'), self.showDialog )
        grid.addWidget(save_label, 1, 0)
        grid.addWidget(self.save_lineedit, 1, 1)
        grid.addWidget(save_browsebutton, 1, 2)
        
        quality_label = QtGui.QLabel(u"Kvalita:")
        self.quality_combobox = QtGui.QComboBox()
        self.quality_combobox.addItem(u"Vysoká kvalita")
        self.quality_combobox.addItem(u"Nízká kvalita")
        
        down_button = QtGui.QPushButton(u"STÁHNI")
        down_button.setStyleSheet( "background-color: green; color: white")
        self.connect(down_button, QtCore.SIGNAL('clicked()'), self.run )
        
        stop_button = QtGui.QPushButton(u"STOP")
        stop_button.setStyleSheet("background-color: red; color: white")
        self.connect(stop_button, QtCore.SIGNAL('clicked()'), self.stop)
        
        self.button = QtGui.QStackedWidget()
        self.button.addWidget(down_button)
        self.button.addWidget(stop_button)
        self.button.setFixedWidth(80)
        
        grid.addWidget(quality_label, 2, 0)
        grid.addWidget(self.quality_combobox, 2, 1)
        grid.addWidget(self.button, 2, 2)
        
        self.textArea = QtGui.QTextEdit()
        self.textArea.setReadOnly(True)
        self.textArea.setOverwriteMode(False)
        
        grid.addWidget(self.textArea, 3, 0, 5, 3)
        
        about_label = QtGui.QLabel(u'<a href="about">O programu</a>')
        about_label.linkActivated.connect(self.about)
        grid.addWidget(about_label, 8,0)
        
        self.setLayout(grid)
        self.exe = self.findExe()
        
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
        
        q = 'high' if self.quality_combobox.currentIndex() == 0 else "low"

        self.p = QtCore.QProcess()
        self.p.setReadChannel(QtCore.QProcess.StandardError)
        arg = ["-q", q,
               '-o', '"%s"' %self.save_lineedit.text(),
               str(self.url_lineedit.text() ) ]
        
        self.connect(self.p, QtCore.SIGNAL('readyRead()'), self.readyRead)
        self.connect(self.p, QtCore.SIGNAL('finished(int, QProcess::ExitStatus)'), self.finished)
        self.p.start(self.exe, arg )
        
    def stop(self):
        self.p.terminate()
    
    def readyRead(self):
        self.textArea.append( QtCore.QString( self.p.readAll() ) )
        
    def finished(self, exitCode, exitStatus):
        if exitCode == 0 and exitStatus == QtCore.QProcess.NormalExit:
            QtGui.QMessageBox.information(self, u"Hotovo", u"Stahování úspěšně dokončeno")
        
        else:
            QtGui.QMessageBox.critical(self, u"Selhání", u"Stahování selhalo")
        
        self.p.close()
        self.button.setCurrentIndex(0)

    def about(self, url):
      QtGui.QMessageBox.about(self, "O nova-dl", QtCore.QString.fromUtf8('''Autor: Jakub Lužný
Ikona: Roman Šmakal''') )

        
app = QtGui.QApplication(sys.argv)

mw = MainWindow()
mw.show()

sys.exit(app.exec_())
