# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ModelExtractor_Widget.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ExtractModelWidget(object):
    def setupUi(self, ExtractModelWidget):
        ExtractModelWidget.setObjectName(_fromUtf8("ExtractModelWidget"))
        ExtractModelWidget.resize(753, 525)
        ExtractModelWidget.setStyleSheet(_fromUtf8("\n"
"QGroupBox {\n"
"    font: 75 9pt \"Arial\" bold;\n"
"    border: 1px solid rgb(85, 170, 255);\n"
"    border-radius: 5px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"QGroupBox::title { \n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
" } "))
        self.verticalLayout = QtGui.QVBoxLayout(ExtractModelWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.inputBox = QtGui.QGroupBox(ExtractModelWidget)
        self.inputBox.setObjectName(_fromUtf8("inputBox"))
        self.gridLayout = QtGui.QGridLayout(self.inputBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.inputBox)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setStyleSheet(_fromUtf8(""))
        self.label.setFrameShape(QtGui.QFrame.NoFrame)
        self.label.setFrameShadow(QtGui.QFrame.Raised)
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setScaledContents(False)
        self.label.setWordWrap(True)
        self.label.setIndent(2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.extractModelFileLabel = QtGui.QLabel(self.inputBox)
        self.extractModelFileLabel.setMinimumSize(QtCore.QSize(50, 0))
        self.extractModelFileLabel.setObjectName(_fromUtf8("extractModelFileLabel"))
        self.gridLayout.addWidget(self.extractModelFileLabel, 1, 0, 1, 1)
        self.extractModelFileTextbox = QtGui.QLineEdit(self.inputBox)
        self.extractModelFileTextbox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);\n"
"border-color: rgb(180, 180, 180);"))
        self.extractModelFileTextbox.setObjectName(_fromUtf8("extractModelFileTextbox"))
        self.gridLayout.addWidget(self.extractModelFileTextbox, 1, 1, 1, 1)
        self.extractModelFileButton = QtGui.QPushButton(self.inputBox)
        self.extractModelFileButton.setObjectName(_fromUtf8("extractModelFileButton"))
        self.gridLayout.addWidget(self.extractModelFileButton, 1, 2, 1, 1)
        self.extractOutputLabel = QtGui.QLabel(self.inputBox)
        self.extractOutputLabel.setMinimumSize(QtCore.QSize(50, 0))
        self.extractOutputLabel.setObjectName(_fromUtf8("extractOutputLabel"))
        self.gridLayout.addWidget(self.extractOutputLabel, 2, 0, 1, 1)
        self.extractOutputTextbox = QtGui.QLineEdit(self.inputBox)
        self.extractOutputTextbox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);\n"
"border-color: rgb(180, 180, 180);"))
        self.extractOutputTextbox.setObjectName(_fromUtf8("extractOutputTextbox"))
        self.gridLayout.addWidget(self.extractOutputTextbox, 2, 1, 1, 1)
        self.extractOutputButton = QtGui.QPushButton(self.inputBox)
        self.extractOutputButton.setObjectName(_fromUtf8("extractOutputButton"))
        self.gridLayout.addWidget(self.extractOutputButton, 2, 2, 1, 1)
        self.extractModelFileLabel.raise_()
        self.extractModelFileTextbox.raise_()
        self.extractModelFileButton.raise_()
        self.extractOutputLabel.raise_()
        self.extractOutputTextbox.raise_()
        self.extractOutputButton.raise_()
        self.label.raise_()
        self.label.raise_()
        self.verticalLayout.addWidget(self.inputBox)
        self.modelExtractorGroup = QtGui.QGroupBox(ExtractModelWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial 12"))
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.modelExtractorGroup.setFont(font)
        self.modelExtractorGroup.setObjectName(_fromUtf8("modelExtractorGroup"))
        self.gridLayout_2 = QtGui.QGridLayout(self.modelExtractorGroup)
        self.gridLayout_2.setContentsMargins(-1, 16, -1, -1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.extractOutputTextArea = QtGui.QTextEdit(self.modelExtractorGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.extractOutputTextArea.sizePolicy().hasHeightForWidth())
        self.extractOutputTextArea.setSizePolicy(sizePolicy)
        self.extractOutputTextArea.setMinimumSize(QtCore.QSize(0, 250))
        self.extractOutputTextArea.setMaximumSize(QtCore.QSize(16777215, 600))
        self.extractOutputTextArea.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);\n"
"border-color: rgb(180, 180, 180);"))
        self.extractOutputTextArea.setObjectName(_fromUtf8("extractOutputTextArea"))
        self.gridLayout_2.addWidget(self.extractOutputTextArea, 1, 0, 1, 2)
        self.extractModelButton = QtGui.QPushButton(self.modelExtractorGroup)
        self.extractModelButton.setMinimumSize(QtCore.QSize(100, 0))
        self.extractModelButton.setObjectName(_fromUtf8("extractModelButton"))
        self.gridLayout_2.addWidget(self.extractModelButton, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(490, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.modelExtractorGroup)
        spacerItem1 = QtGui.QSpacerItem(20, 3, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(ExtractModelWidget)
        QtCore.QMetaObject.connectSlotsByName(ExtractModelWidget)

    def retranslateUi(self, ExtractModelWidget):
        ExtractModelWidget.setWindowTitle(_translate("ExtractModelWidget", "Form", None))
        self.inputBox.setTitle(_translate("ExtractModelWidget", "Inputs", None))
        self.label.setText(_translate("ExtractModelWidget", "Extract all of the files associated with a model into another directory.\n"
"Either browse for a model file (.ief or .tcf) in the inputs group or right-click on an logged entry in the Run table and select \'Extract model\'.\n"
"Any issues with exporting the model, including missing files, or files that could not be copied, will be recorded in the text box below the extract model button.", None))
        self.extractModelFileLabel.setText(_translate("ExtractModelWidget", "Model file", None))
        self.extractModelFileButton.setText(_translate("ExtractModelWidget", "Browse...", None))
        self.extractOutputLabel.setText(_translate("ExtractModelWidget", "Output folder", None))
        self.extractOutputButton.setText(_translate("ExtractModelWidget", "Browse...", None))
        self.modelExtractorGroup.setTitle(_translate("ExtractModelWidget", "Model extractor", None))
        self.extractModelButton.setText(_translate("ExtractModelWidget", "Extract Model", None))

