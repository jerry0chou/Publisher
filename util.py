import json, os, re
import zipfile, tarfile

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from conn import uploadFile, execute
from os.path import join, getsize


def write_json(filename, obj):
    with open(f"data/{filename}", 'w') as f:
        f.write(json.dumps(obj, sort_keys=True, indent=4, separators=(',', ':')))


def read_json(filename):
    path = f"data/{filename}"
    if not os.path.exists(path):
        open(path, "w").close()
    strings = ""
    with open(f"data/{filename}", 'r') as f:
        for line in f:
            strings += line
    return json.loads(strings)


def getdirsize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])

    # MB
    return '%.4f' % float(size / 1000000)


def getFileSize(filename):
    size = getsize(filename)
    return '%.4f' % float(size / 1000000)


def uploadFileToServer(localFile, remoteFile):
    dic = read_json("setting.json")
    info = uploadFile(dic["server_address"], dic["server_port"], dic["username"], dic["password"], localFile,
                      remoteFile)
    return info


def executeCmd(cmd):
    dic = read_json("setting.json")
    msg = execute(dic["server_address"], dic["server_port"], dic["username"], dic["password"], cmd)
    return msg


# "/root/economy/scheduling.py"
def killPythonProcess(lauchFilePath):
    info = executeCmd(f"ps -ef |grep {lauchFilePath};")
    for line in info.split("\n"):
        if "python3" in line and lauchFilePath in line:
            pid = re.findall("\d+", line)[0]
            executeCmd(f"kill -9 {pid};")
            break


def executePythonCode():
    dic = read_json("python.json")
    projectName = os.path.basename(dic['local_app_path'])
    projectPath = f"{dic['server_app_path']}/{projectName}"
    killPythonProcess(f"{projectPath}/{dic['app_name']}")
    cmd1 = f'''
        mkdir {projectPath}
        tar -zxvf {projectPath}.tar.gz -C {projectPath}
        nohup python3 -u  {projectPath}/{dic['app_name']} > {projectPath}/out.log 2>&1 &
        '''
    executeCmd(cmd1)
    cmd2 = f'''
        ps -ef |grep {dic['app_name']}
        ls -l {projectPath}
    '''
    info = executeCmd(cmd2)
    return info


def readQss():
    strings = ""
    with open("./data/style.qss", 'r') as f:
        for line in f:
            strings += line
    return strings


def zipDir(dirpath, outFullName):
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')
        for filename in filenames:
            # print(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


def tarDir(dirname, tarfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, file in os.walk(dirname):
            for name in file:
                filelist.append(os.path.join(root, name))
    # 'w:bz2'是指写bz2压缩包，如果是gz包的话就用'w:gz'
    tf = tarfile.open(tarfilename, 'w:gz')
    for tar in filelist:
        arcname = tar[len(dirname):]
        tf.add(tar, arcname)
    tf.close()


class UploadThread(QtCore.QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super(UploadThread, self).__init__()
        self.type = "python"
        self.localFile = ""
        self.remoteFile = ""

    def run(self):
        msg = ''
        if self.type == "java":
            msg = uploadFileToServer(self.localFile, self.remoteFile)
        elif self.type == "python":
            tarDir(self.localFile, self.localFile + ".tar.gz")
            msg = uploadFileToServer(self.localFile + ".tar.gz",
                                     self.remoteFile + "/" + os.path.basename(self.localFile) + ".tar.gz")
        self.signal.emit(msg)

    def __del__(self):
        self.wait()

    # def callback(self, msg):
    #     print('callback')
