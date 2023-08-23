import sys
import os
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QSplitter, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
import json
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLabel, QHBoxLayout

QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

class BookmarksManager:
    def __init__(self, tree_widget):
        self.tree_widget = tree_widget
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderLabels(["Bookmarks"])
        self.load_bookmarks()

    def load_bookmarks(self):
        try:
            with open("bookmarks.json", "r") as file:
                bookmarks = json.load(file)
                for bookmark in bookmarks:
                    item = QTreeWidgetItem(self.tree_widget)
                    item.setText(0, bookmark["title"])
                    item.setData(0, Qt.UserRole, bookmark["url"])
        except FileNotFoundError:
            pass

    def save_bookmarks(self):
        bookmarks = []
        for index in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(index)
            bookmarks.append({
                "title": item.text(0),
                "url": item.data(0, Qt.UserRole)
            })
        with open("bookmarks.json", "w") as file:
            json.dump(bookmarks, file)

    def add_bookmark(self, title, url):
        item = QTreeWidgetItem()
        item.setText(0, title)
        item.setData(0, Qt.UserRole, url)
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            parent = selected_items[0]
            parent.addChild(item)
        else:
            self.tree_widget.addTopLevelItem(item)
        self.save_bookmarks()

    def remove_bookmark(self, item):
        index = self.tree_widget.indexOfTopLevelItem(item)
        self.tree_widget.takeTopLevelItem(index)
        self.save_bookmarks()

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
        url = self.url_bar.text().strip()
        if not url:
            return
        if "." not in url:
            url = f"https://www.google.com/search?q={url}"
        elif not url.startswith(("http://", "https://")):
            url = "http://" + url
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
        self.splitter = QSplitter(Qt.Horizontal, self.central_widget)  # Ustaw orientację na poziomą
        self.layout.addWidget(self.splitter)
        # Dodaj pasek boczny z zakładkami
        self.bookmarks_layout = QVBoxLayout()
        self.bookmarks_header_layout = QHBoxLayout()

        self.bookmarks_label = QLabel("Bookmarks")
        self.add_bookmark_btn = QPushButton("+")
        self.add_bookmark_btn.clicked.connect(self.add_bookmark_prompt)
        self.bookmarks_header_layout.addWidget(self.bookmarks_label)
        self.bookmarks_header_layout.addWidget(self.add_bookmark_btn)

        self.bookmarks_tree = QTreeWidget(self.splitter)
        self.bookmarks_layout.addLayout(self.bookmarks_header_layout, 1)
        self.bookmarks_layout.addWidget(self.bookmarks_tree)
        self.bookmarks_widget = QWidget()
        self.bookmarks_widget.setLayout(self.bookmarks_layout)
        self.splitter.insertWidget(0, self.bookmarks_widget)

        self.bookmarks_manager = BookmarksManager(self.bookmarks_tree)
        self.bookmarks_tree.itemClicked.connect(self.open_bookmark)

        self.add_new_tab()

        # Timer do regularnego aktualizowania tytułu okna z obciążeniem procesora i zużyciem pamięci
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_window_title)
        self.status_timer.start(1000)  # Aktualizuj co sekundę

        self.navbar = QToolBar()
        new_tab_btn = QAction("New Split", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_btn)
        self.addToolBar(self.navbar)

        self.add_bookmark_btn = QPushButton("+")
        self.add_bookmark_btn.clicked.connect(self.add_bookmark_prompt)
        self.layout.addWidget(self.add_bookmark_btn)

    def add_bookmark_prompt(self):
        title, ok1 = QInputDialog.getText(self, "Add Bookmark", "Title:")
        url, ok2 = QInputDialog.getText(self, "Add Bookmark", "URL:")
        if ok1 and ok2:
            self.bookmarks_manager.add_bookmark(title, url)

    def open_bookmark(self, item):
        url = item.data(0, Qt.UserRole)
        current_tab = self.splitter.widget(self.splitter.count() - 1)
        current_tab.browser.setUrl(QUrl(url))


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
    QApplication.setApplicationName("Pinta Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
