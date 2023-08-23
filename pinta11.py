import sys
import os
import psutil
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QSplitter, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QShortcut
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
import json
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLabel, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl, Qt, QTimer, QObject

QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

class BookmarksManager(QObject):
    def __init__(self, tree_widget):
        super(BookmarksManager, self).__init__()
        self.tree_widget = tree_widget
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setColumnWidth(0, 150)  # Szerokość kolumny dla tytułu zakładki
        self.tree_widget.setColumnWidth(1, 20)   # Szerokość kolumny dla przycisku "x"
        self.tree_widget.setHeaderLabels(["Bookmarks", "Options"])
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDragDropMode(QTreeWidget.DragDrop)
        self.load_bookmarks()
        self.tree_widget.viewport().installEventFilter(self)
        self.tree_widget.setEditTriggers(QTreeWidget.DoubleClicked)
        self.tree_widget.installEventFilter(self)
        self.tree_widget.itemClicked.connect(self.handle_delete_click)
        self.tree_widget.itemChanged.connect(self.on_item_changed)
        self.tree_widget.itemChanged.connect(self.save_bookmarks)

    def load_bookmarks(self):
        try:
            with open("bookmarks.json", "r") as file:
                bookmarks = json.load(file)

                def add_items(parent, items):
                    for item_data in items:
                        item = QTreeWidgetItem(parent)
                        item.setText(0, item_data["title"])
                        item.setData(0, Qt.UserRole, item_data["url"])
                        item.setFlags(item.flags() | Qt.ItemIsEditable)
                        item.setText(1, "x")
                        if "children" in item_data:
                            add_items(item, item_data["children"])

                add_items(self.tree_widget, bookmarks)

        except FileNotFoundError:
            pass

    def handle_delete_click(self, item, column):
        if column == 1:
            self.remove_bookmark(item)

    def on_item_changed(self, item):
        self.save_bookmarks()

    def save_bookmarks(self):
        bookmarks = []

        def traverse_tree(item):
            children = []
            for index in range(item.childCount()):
                child = item.child(index)
                child_data = {
                    "title": child.text(0),
                    "url": child.data(0, Qt.UserRole),
                    "children": traverse_tree(child)
                }
                children.append(child_data)
            return children

        for index in range(self.tree_widget.topLevelItemCount()):
            top_level_item = self.tree_widget.topLevelItem(index)
            top_level_data = {
                "title": top_level_item.text(0),
                "url": top_level_item.data(0, Qt.UserRole),
                "children": traverse_tree(top_level_item)
            }
            bookmarks.append(top_level_data)

        with open("bookmarks.json", "w") as file:
            json.dump(bookmarks, file)

    def add_bookmark(self, title, url):
        print('--- ADD BOOKMARK ---')
        self.tree_widget.itemChanged.disconnect(self.save_bookmarks)  # tymczasowo odłącz sygnał

        item = QTreeWidgetItem(self.tree_widget)
        item.setText(0, title)
        item.setData(0, Qt.UserRole, url)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setText(1, "x")
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            parent = selected_items[0]
            parent.addChild(item)
        else:
            self.tree_widget.addTopLevelItem(item)

        self.save_bookmarks()

        self.tree_widget.itemChanged.connect(self.save_bookmarks)  # ponownie podłącz sygnał

    def remove_bookmark(self, item):
        def delayed_remove():
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.tree_widget.indexOfTopLevelItem(item)
                self.tree_widget.takeTopLevelItem(index)
            self.save_bookmarks()

        QTimer.singleShot(0, delayed_remove)

    def eventFilter(self, source, event):
        if (source == self.tree_widget and event.type() == QtCore.QEvent.KeyPress):
            key = event.key()
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                current_item = self.tree_widget.currentItem()
                if current_item:
                    self.tree_widget.editItem(current_item)
                return True
        if (event.type() == QtCore.QEvent.Drop and
                source == self.tree_widget.viewport()):
            mime_data = event.mimeData()
            if event.mimeData().hasUrls():
                url = mime_data.urls()[0].toString()
                self.add_bookmark(url, url)
                self.save_bookmarks()
        return super().eventFilter(source, event)


class BrowserTab(QWidget):
    def __init__(self, bookmarks_manager, parent=None):
        super().__init__(parent)
        self.bookmarks_manager = bookmarks_manager
        self.initial_load = True
        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        self.browser.setUrl(QUrl("http://www.google.com"))
        self.browser.setAcceptDrops(False)
        self.browser.loadFinished.connect(self.on_load_finished)

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

    def on_load_finished(self, success):
        if success and not self.initial_load:
            title = self.browser.page().title()
            url = self.browser.url().toString()
            self.bookmarks_manager.add_bookmark(title, url)
        self.initial_load = False

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
        self.shortcut_new_tab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_new_tab.activated.connect(self.add_new_tab)
        self.add_new_tab()

        # Timer do regularnego aktualizowania tytułu okna z obciążeniem procesora i zużyciem pamięci
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_window_title)
        self.status_timer.start(1000)  # Aktualizuj co sekundę

        self.navbar = QToolBar()
        new_tab_btn = QAction("New Split", self)
        # new_tab_btn.triggered.connect(self.add_new_tab)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        self.navbar.addAction(new_tab_btn)
        self.addToolBar(self.navbar)

        # self.add_bookmark_btn = QPushButton("+")
        # self.add_bookmark_btn.clicked.connect(self.add_bookmark_prompt)
        # self.layout.addWidget(self.add_bookmark_btn)
        self.load_last_session()

    def add_bookmark_prompt(self):
        title, ok1 = QInputDialog.getText(self, "Add Bookmark", "Title:")
        url, ok2 = QInputDialog.getText(self, "Add Bookmark", "URL:")
        if ok1 and ok2:
            self.bookmarks_manager.add_bookmark(title, url)

    def open_bookmark(self, item):
        url = item.data(0, Qt.UserRole)
        current_tab = self.splitter.currentWidget()
        if hasattr(current_tab, 'browser'):
            current_tab.browser.setUrl(QUrl(url))

    def add_new_tab(self, url=QUrl("http://www.google.com")):
        browser_tab = BrowserTab(self.bookmarks_manager, self.splitter)
        browser_tab.browser.setUrl(url)
        self.splitter.addWidget(browser_tab)

    def update_window_title(self):
        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        memory_percent = memory_info.rss / psutil.virtual_memory().total * 100
        self.setWindowTitle(f"Pinta Browser || Usage: CPU: {cpu_percent:.1f}% RAM: {memory_percent:.1f}%")

    def closeEvent(self, event):
        self.save_current_session()
        event.accept()
        super().closeEvent(event)

    def load_last_session(self):
        # Wczytaj zakładki z ostatniej sesji
        try:
            with open("session.json", "r") as file:
                open_tabs = json.load(file)
                for url in open_tabs:
                    self.add_new_tab(QUrl(url))
        except FileNotFoundError:
            pass

    def save_current_session(self):
        urls = []
        for index in range(self.splitter.count()):
            tab = self.splitter.widget(index)
            if hasattr(tab, 'browser'):  # Sprawdź, czy obiekt tab ma atrybut 'browser'
                urls.append(tab.browser.url().toString())
        with open("session.json", "w") as file:
            json.dump(urls, file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Pinta Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
