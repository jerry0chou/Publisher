from PyQt5.QtWidgets import QMessageBox

from windows import Ui_MainWindow
from PyQt5 import QtWidgets
from util import *
import sys, shutil


class Mywindow(QtWidgets.QMainWindow, Ui_MainWindow):
    # 建立的是Main Window项目，故此处导入的是QMainWindow
    # 参考博客中建立的是Widget项目，因此哪里导入的是QWidget
    def __init__(self):
        super(Mywindow, self).__init__()
        self.setupUi(self)
        self.setFixedSize(670, 520)
        self.setPythonInfo()
        self.loadToolAndSettingData()
        self.save_setting_button.clicked.connect(self.saveSetting)
        self.move_directory_button.clicked.connect(self.moveDirectory)
        self.switch_button.clicked.connect(self.switch)
        self.java_radioButton.clicked.connect(self.setJavaInfo)
        self.python_radioButton.clicked.connect(self.setPythonInfo)
        self.deploy_button.clicked.connect(self.deploy)
        self.setStyleSheet(readQss())

    def deploy(self):
        try:
            obj = {
                "app_name": self.app_name_lineEdit.text().replace("\\", "/"),
                "local_app_path": self.local_app_path_lineEdit.text().replace("\\", "/"),
                "server_app_path": self.server_app_path_lineEdit.text().replace("\\", "/"),
            }
            self.textEdit.setText("")
            self.textEdit.append("save app info successfully")
            if self.java_radioButton.isChecked():
                write_json('java.json', obj)
                self.textEdit.append("uploading java war file to server...")
                self.thread = UploadThread()
                self.thread.type = "java"
                self.thread.localFile = obj['local_app_path']
                self.thread.remoteFile = f"{obj['server_app_path']}/{obj['app_name']}.war"
                self.thread.signal.connect(self.handleUploadResult)
                self.thread.start()
            else:
                write_json('python.json', obj)
                self.textEdit.append("uploading python project zip file to server...")
                self.thread = UploadThread()
                self.thread.type = "python"
                self.thread.localFile = obj['local_app_path']
                self.thread.remoteFile = f"{obj['server_app_path']}"
                self.thread.signal.connect(self.handleUploadResult)
                self.thread.start()

        except Exception as e:
            self.textEdit.append(f"{str(e)}\n")

    def handleUploadResult(self, msg):
        self.textEdit.append(msg)
        info = ""
        if self.java_radioButton.isChecked():
            dic = read_json("java.json")
            info = executeCmd(f"ls -l {dic['server_app_path']}")
        elif self.python_radioButton.isCheckable():
            info = executePythonCode()
        self.textEdit.append(info)

    def loadInfo(self, filename):
        try:
            dic = read_json(filename)
            for k, v in dic.items():
                eval(f"self.{k}_lineEdit.setText('{v}')")
        except Exception as e:
            self.textEdit.append(f"load {filename} error: " + str(e))

    def setJavaInfo(self):
        self.loadInfo("java.json")

    def setPythonInfo(self):
        self.loadInfo("python.json")

    def switch(self):
        tmp = self.source_path_lineEdit.text()
        self.source_path_lineEdit.setText(self.destination_path_lineEdit.text())
        self.destination_path_lineEdit.setText(tmp)

    def loadToolAndSettingData(self):
        self.loadInfo("setting.json")
        self.loadInfo("tool.json")

    def saveSetting(self):
        try:
            obj = {
                "server_address": self.server_address_lineEdit.text(),
                "server_port": self.server_port_lineEdit.text(),
                "username": self.username_lineEdit.text(),
                "password": self.password_lineEdit.text()
            }
            write_json('setting.json', obj)
            QMessageBox.about(self, "Title", "save setting successfully")
        except Exception as e:
            QMessageBox.about(self, "Title", str(e))

    def moveDirectory(self):
        try:
            obj = {
                "source_path": self.source_path_lineEdit.text().replace("\\", "/"),
                "destination_path": self.destination_path_lineEdit.text().replace("\\", "/"),
            }
            write_json('tool.json', obj)
            if (os.path.isdir(obj['source_path']) and float(getdirsize(obj['source_path'])) < int(
                    self.spinBox.value())) or (
                    os.path.isfile(obj['source_path']) and float(getFileSize(obj['source_path'])) < int(
                self.spinBox.value())):
                shutil.copy(obj['source_path'], obj['destination_path'])
                QMessageBox.about(self, "Title", "save tool successfully")
            else:
                QMessageBox.about(self, "Title", "size is not proper or path input wrong")

        except Exception as e:
            QMessageBox.about(self, "Title", str(e))


app = QtWidgets.QApplication(sys.argv)
window = Mywindow()
window.show()
sys.exit(app.exec_())
