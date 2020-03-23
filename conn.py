import paramiko
from util import *

def execute(ip, port, username, passwd, cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, int(port), username, passwd, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        string = ""
        for x in stdout.readlines():
            string += x
        string += '%s OK\n' % (ip)
        return string
    except:
        return f"{ip} error"
    finally:
        ssh.close()


def uploadFile(ip, port, username, password, localFileorDir, remoteFileorDir):
    try:
        ssh = paramiko.Transport((ip, int(port)))
        ssh.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(ssh)
        sftp.put(localFileorDir, remoteFileorDir)
        return f"uploadFile {localFileorDir} success"
    except Exception as e:
        return f"uploadFile {localFileorDir} error\n {e}"
    finally:
        ssh.close()

# def initSSHInfo(localFile,remoteFile):
#     dic=read_json("setting.json")
#     val = uploadFile(dic["server_address"],dic["server_port"], dic["username"], dic["password"],localFile ,remoteFile)

# val = ssh2("47.104.246.188", "22", "root", "Aliyun123456.", "ls -al ~/")
# print(val)

# val = uploadFile("47.104.246.188", "22", "root", "Aliyun123456.", "D:/CodeSpace/ScalaSpace/ApiDoc/target/scala-2.12/apidoc_2.12-0.1.war","/root/apidoc.war")
# val = uploadFile("47.104.246.188", "22", "root", "Aliyun123456.", "D:/CodeSpace/PySpace/economy","/root/economy2")
# print(val)
#
# val = executeCmd("47.104.246.188", "22", "root", "Aliyun123456.", "ls -al ~/")
# print(val)