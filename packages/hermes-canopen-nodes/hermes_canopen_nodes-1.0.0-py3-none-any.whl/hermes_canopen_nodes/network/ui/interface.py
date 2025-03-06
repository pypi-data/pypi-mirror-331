# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(309, 330)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.groupBox)
        self.tabWidget.setObjectName(u"tabWidget")
        self.Kvaeser = QWidget()
        self.Kvaeser.setObjectName(u"Kvaeser")
        self.formLayout = QFormLayout(self.Kvaeser)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.Kvaeser)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.kvaeser_channel = QComboBox(self.Kvaeser)
        self.kvaeser_channel.addItem("")
        self.kvaeser_channel.addItem("")
        self.kvaeser_channel.addItem("")
        self.kvaeser_channel.setObjectName(u"kvaeser_channel")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.kvaeser_channel)

        self.label_2 = QLabel(self.Kvaeser)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.kvaeser_bitrate = QComboBox(self.Kvaeser)
        self.kvaeser_bitrate.addItem("")
        self.kvaeser_bitrate.addItem("")
        self.kvaeser_bitrate.setObjectName(u"kvaeser_bitrate")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.kvaeser_bitrate)

        self.tabWidget.addTab(self.Kvaeser, "")
        self.Can2Usb = QWidget()
        self.Can2Usb.setObjectName(u"Can2Usb")
        self.formLayout_3 = QFormLayout(self.Can2Usb)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_5 = QLabel(self.Can2Usb)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_5)

        self.can2usb_bitrate = QComboBox(self.Can2Usb)
        self.can2usb_bitrate.addItem("")
        self.can2usb_bitrate.addItem("")
        self.can2usb_bitrate.setObjectName(u"can2usb_bitrate")

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.can2usb_bitrate)

        self.can2usb_serial = QLineEdit(self.Can2Usb)
        self.can2usb_serial.setObjectName(u"can2usb_serial")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.can2usb_serial)

        self.label_12 = QLabel(self.Can2Usb)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_12)

        self.tabWidget.addTab(self.Can2Usb, "")
        self.Linux = QWidget()
        self.Linux.setObjectName(u"Linux")
        self.formLayout_2 = QFormLayout(self.Linux)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.socketcan_serial_2 = QLabel(self.Linux)
        self.socketcan_serial_2.setObjectName(u"socketcan_serial_2")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.socketcan_serial_2)

        self.linuxcan_bitrate = QComboBox(self.Linux)
        self.linuxcan_bitrate.setObjectName(u"linuxcan_bitrate")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.linuxcan_bitrate)

        self.linuxcan_interface = QLineEdit(self.Linux)
        self.linuxcan_interface.setObjectName(u"linuxcan_interface")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.linuxcan_interface)

        self.label_4 = QLabel(self.Linux)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.tabWidget.addTab(self.Linux, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.enable_sync = QCheckBox(self.groupBox)
        self.enable_sync.setObjectName(u"enable_sync")

        self.verticalLayout.addWidget(self.enable_sync)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout.addWidget(self.label_7)

        self.sync_frequency = QDoubleSpinBox(self.groupBox)
        self.sync_frequency.setObjectName(u"sync_frequency")
        self.sync_frequency.setDecimals(1)
        self.sync_frequency.setMinimum(0.100000000000000)
        self.sync_frequency.setMaximum(100.000000000000000)
        self.sync_frequency.setValue(10.000000000000000)

        self.horizontalLayout.addWidget(self.sync_frequency)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addWidget(self.groupBox)


        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"Config", None))
        self.label.setText(QCoreApplication.translate("Form", u"Channel", None))
        self.kvaeser_channel.setItemText(0, QCoreApplication.translate("Form", u"0", None))
        self.kvaeser_channel.setItemText(1, QCoreApplication.translate("Form", u"1", None))
        self.kvaeser_channel.setItemText(2, QCoreApplication.translate("Form", u"2", None))

        self.label_2.setText(QCoreApplication.translate("Form", u"Bitrate", None))
        self.kvaeser_bitrate.setItemText(0, QCoreApplication.translate("Form", u"1000000", None))
        self.kvaeser_bitrate.setItemText(1, QCoreApplication.translate("Form", u"500000", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Kvaeser), QCoreApplication.translate("Form", u" Kvaeser", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Bitrate", None))
        self.can2usb_bitrate.setItemText(0, QCoreApplication.translate("Form", u"1000000", None))
        self.can2usb_bitrate.setItemText(1, QCoreApplication.translate("Form", u"500000", None))

        self.label_12.setText(QCoreApplication.translate("Form", u"Serial", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Can2Usb), QCoreApplication.translate("Form", u"Can2Usb", None))
        self.socketcan_serial_2.setText(QCoreApplication.translate("Form", u"Bitrate", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Interface", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Linux), QCoreApplication.translate("Form", u"LinuxCan", None))
        self.enable_sync.setText(QCoreApplication.translate("Form", u"Enable Sync", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Sync Rate", None))
        self.sync_frequency.setSuffix(QCoreApplication.translate("Form", u"Hz", None))
    # retranslateUi

