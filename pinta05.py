import sys
import os
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QSplitter, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QTimer

QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        self.browser.setUrl(QUrl("http://www.google.com"))

        self.navbar = QToolBar()
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.browser.back)
        self.navbar.addAction(back_btn)
        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.browser.forward)
        self.navbar.addAction(forward_btn)
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.browser.reload)
        self.navbar.addAction(reload_btn)
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)

        close_btn = QPushButton("x")
        close_btn.clicked.connect(self.close_tab)
        self.navbar.addWidget(close_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.navbar)
        layout.addWidget(self.browser)
        self.setLayout(layout)

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def close_tab(self):
        index = self.parent().indexOf(self)
        if index != -1:
            self.parent().widget(index).deleteLater()

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.splitter = QSplitter(self.central_widget)
        self.layout.addWidget(self.splitter)

        self.add_new_tab()

        # Timer do regularnego aktualizowania tytułu okna z obciążeniem procesora i zużyciem pamięci
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_window_title)
        self.status_timer.start(1000)  # Aktualizuj co sekundę

        self.navbar = QToolBar()
        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_btn)
        self.addToolBar(self.navbar)

    def add_new_tab(self):
        browser_tab = BrowserTab(self.splitter)
        self.splitter.addWidget(browser_tab)

    def update_window_title(self):
        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_percent = memory_info.rss / psutil.virtual_memory().total * 100
        self.setWindowTitle(f"Oculus Browser - CPU: {cpu_percent:.1f}% RAM: {memory_percent:.1f}%")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Oculus Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
