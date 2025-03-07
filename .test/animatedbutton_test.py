from customwidgets import *
from PyQt5.QtWidgets import *

class MainWindow(DraggableMixin, QMainWindow):
# class MainWindow(DraggableWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 300, 200)
        self.button = AnimatedPushButton('Button', self)
        # self.button = PenetrateAnimatedButton('Button', self)
        self.edit = PenetrateLineEdit(self)
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.edit)
        container = PenetrateWidget(self)
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        
if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()