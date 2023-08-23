import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QSplitter, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt

QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

class BrowserTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)

        self.browser = QWebEngineView(self)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        self.browser.setUrl(QUrl("http://www.google.com"))
        self.browser.urlChanged.connect(self.update_url)

        self.navbar = QToolBar(self)
        self.layout.addWidget(self.navbar)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.browser.back)
        self.navbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.browser.forward)
        self.navbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.browser.reload)
        self.navbar.addAction(reload_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.triggered.connect(self.main_window.add_new_tab)
        self.navbar.addAction(new_tab_btn)

        close_tab_btn = QAction("X", self)
        close_tab_btn.triggered.connect(self.close_tab)
        self.navbar.addAction(close_tab_btn)

        self.url_bar = QLineEdit(self)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        self.layout.addWidget(self.browser)

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def close_tab(self):
        index = self.main_window.splitter.indexOf(self)
        if index != -1:
            self.main_window.splitter.widget(index).deleteLater()

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.splitter = QSplitter(self.central_widget)
        self.layout.addWidget(self.splitter)

        self.add_new_tab()

    def add_new_tab(self):
        browser_tab = BrowserTab(self)
        self.splitter.addWidget(browser_tab)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Oculus Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
