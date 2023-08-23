import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QSplitter, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt

QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.splitter = QSplitter(self.central_widget)
        self.layout.addWidget(self.splitter)
        self.browsers = []
        self.add_new_tab()
        self.active_browser = self.browsers[0]

        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.navigate_back)
        navbar.addAction(back_btn)
        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.navigate_forward)
        navbar.addAction(forward_btn)
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        navbar.addAction(reload_btn)
        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        self.current_browser().urlChanged.connect(self.update_url)

    def add_new_tab(self):
        browser = QWebEngineView()
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        browser.setUrl(QUrl("http://www.google.com"))
        browser.urlChanged.connect(self.set_active_browser)
        self.splitter.addWidget(browser)
        self.browsers.append(browser)

    def current_browser(self):
        return self.active_browser

    def set_active_browser(self, q):
        clicked_browser = self.sender()
        if isinstance(clicked_browser, QWebEngineView):
            self.active_browser = clicked_browser

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def navigate_back(self):
        self.current_browser().back()

    def navigate_forward(self):
        self.current_browser().forward()

    def reload_page(self):
        self.current_browser().reload()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Oculus Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
