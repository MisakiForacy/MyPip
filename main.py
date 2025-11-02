import sys, os, subprocess
import queue, threading
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit
from PyQt5.QtCore import QObject, pyqtSignal
import time

class LogEmitter(QObject):
    log = pyqtSignal(str)

class Main(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MyPip")
        self.resize(540, 720)
        
        layout = QGridLayout()
        
        
        self.name = time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))
        self.WirteLog = open(f".\\log\\{self.name}", "w", encoding="utf-8")
        
        # 文本组件
        Text = {
            "lable" : QLabel("Pip Packages Install Manager"), 
            "version" : QLabel("Version"),
            "package" : QLabel("Package"),
            "log" : QLabel("LOG")
        }   
        
        # 按钮组件
        Button = {
            "install" : QPushButton("Install"),
            "remove" : QPushButton("Remove"),
            "list" : QPushButton("List"),
            "upgrade" : QPushButton("Upgrade"),
            "show" : QPushButton("Show"),
            "test" : QPushButton("Test")
        }
        Button["install"].clicked.connect(self.Install_clicked)
        Button["remove"].clicked.connect(self.Remove_clicked)
        Button["list"].clicked.connect(self.List_clicked)
        Button["upgrade"].clicked.connect(self.Upgrade_clicked)
        Button["show"].clicked.connect(self.Show_clicked)
        Button["test"].clicked.connect(self.test)
        
        # 拉列表控件
        self.Combobox = QComboBox(self)
        self.Combobox.addItems([""] + self.Get_ComboBox())
        self.Combobox.currentIndexChanged.connect(self.Combobox_changed)
        
        # 文本框控件
        self.Line = QLineEdit(self)
        self.LOG = QTextEdit(self)
        self.LOG.setReadOnly(True)
        
        # 合并控件
        layout.addWidget(Text["lable"], 0, 0, 1, 5)
        layout.addWidget(Text["version"], 3, 0, 1, 1)
        layout.addWidget(Text["package"], 6, 0, 1, 1)
        layout.addWidget(Text["log"], 12, 0, 1, 1)
        
        layout.addWidget(Button["install"], 9, 2, 1, 5)
        layout.addWidget(Button["remove"], 9, 7, 1, 5)
        layout.addWidget(Button["list"], 9, 12, 1, 5)
        layout.addWidget(Button["upgrade"], 9, 17, 1, 5)
        layout.addWidget(Button["show"], 9, 22, 1, 5)
        layout.addWidget(Button["test"], 9, 27, 1, 5)
        
        layout.addWidget(self.Combobox, 3, 2, 1, 30)
        layout.addWidget(self.Line, 6, 2, 1, 30)
        layout.addWidget(self.LOG, 15, 0, 20, 35)
        
        self.setLayout(layout)
    
    def WriteInLOG(self, text):
        self.WirteLog.write(text)
        # pass
    
    def Install_clicked(self):
        version = self.Combobox.currentText().split('\n')[0]
        package = self.Line.text()
        self.cmd = f"\"{version}\" -m pip install {package}"
        self.result = f"[COMMAND] : {self.cmd}\n"
        self.Get_LOG()
        self.Run()
    
    def Remove_clicked(self):
        version = self.Combobox.currentText().split('\n')[0]
        package = self.Line.text()
        self.cmd = f"\"{version}\" -m pip uninstall -y {package}"
        self.result = f"[COMMAND] : {self.cmd}\n"
        self.Get_LOG()
        self.Run()
    
    def List_clicked(self):
        # print("Listed")
        version = self.Combobox.currentText().split('\n')[0]
        self.cmd = f"\"{version}\" -m pip list"
        self.result = f"[COMMAND] : {self.cmd}\n"
        self.Get_LOG()
        self.Run()
        
    def Upgrade_clicked(self):
        version = self.Combobox.currentText().split('\n')[0]
        package = self.Line.text()
        self.cmd = f"\"{version}\" -m pip install --upgrade {package}"
        self.result = f"[COMMAND] : {self.cmd}\n"
        self.Get_LOG()
        self.Run()
    
    def Show_clicked(self):
        version = self.Combobox.currentText().split('\n')[0]
        package = self.Line.text()
        self.cmd = f"\"{version}\" -m pip show {package}"
        self.result = f"[COMMAND] : {self.cmd}\n"
        self.Get_LOG()
        self.Run()
    
    def test(self):
        self.cmd = f"ping bing.com"
        self.result = f"[COMMAND] : {self.cmd}\n"
        self.Get_LOG()
        self.Run()
    
    def Get_ComboBox(self):
        cmd = "where python"
        text = os.popen(cmd)
        return text.readlines()
    
    def Combobox_changed(self):
        text = self.Combobox.currentText()
        print(text)
        
    def Get_LOG(self):
        self.WriteInLOG(self.result)
        self.LOG.insertPlainText(self.result)
        # self.LOG.insertPlainText('\n')

    def Run(self):
        self.emitter = LogEmitter()
        self.emitter.log.connect(self.AppendLog)
        threading.Thread(target=self.RunCommand, daemon=True).start()

    def AppendLog(self, text):
        self.WriteInLOG(text)
        self.LOG.insertPlainText(text)
        self.LOG.ensureCursorVisible()

    def RunCommand(self):
        self.successful = "Successful !!!"
        q = queue.Queue()

        def _reader(stream):
            while True:
                chunk = stream.read(1)
                if not chunk:
                    q.put(None)
                    break
                q.put(chunk)

        with subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            universal_newlines=False,
            shell=True
        ) as proc:
            threading.Thread(target=_reader, args=(proc.stdout,), daemon=True).start()

            line_bytes = b''
            while True:
                ch = q.get()
                if ch is None:
                    break
                line_bytes += ch
                if ch == b'\n':
                    line = line_bytes.decode(errors='ignore')
                    self.emitter.log.emit(line)
                    if "ERROR" in line:
                        self.successful = "Failed QAQ"
                    line_bytes = b''
            proc.wait()

        self.emitter.log.emit(f"[End] : {self.successful}\n")
        
app = QApplication(sys.argv)

window = Main()
window.show()

sys.exit(app.exec_())