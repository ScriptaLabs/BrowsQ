import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QLabel, QPushButton, QVBoxLayout, QWidget, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon
import re
import json
import os

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.open_new_tab)
        self.tabs.currentChanged.connect(self.update_url)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)
        self.showMaximized()

        self.bookmarks_file = 'bookmarks.json'
        self.bookmarks = self.load_bookmarks()

        # Navigation bar
        nav_bar = QToolBar("Navigation")
        self.addToolBar(nav_bar)

        # Back button
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        nav_bar.addAction(back_btn)

        # Forward button
        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        nav_bar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        nav_bar.addAction(reload_btn)

        # Home button
        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.navigate_home)
        nav_bar.addAction(home_btn)

        # Padlock icon
        self.padlock_icon = QLabel()
        self.padlock_icon.setPixmap(QIcon("padlock.png").pixmap(QSize(16, 16)))
        self.padlock_icon.setVisible(False)
        nav_bar.addWidget(self.padlock_icon)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        # Bookmark button
        bookmark_btn = QAction("Bookmark", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        nav_bar.addAction(bookmark_btn)

        # Bookmark bar
        self.bookmark_bar = QToolBar("Bookmarks")
        self.addToolBar(self.bookmark_bar)
        self.load_bookmarks_into_bar()

        # New Tab button
        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.triggered.connect(lambda _: self.add_new_tab())
        nav_bar.addAction(new_tab_btn)

        # Add initial tab
        self.add_new_tab(QUrl('http://www.google.com'), 'Home')

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl('https://google.com')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not re.match(r'^(?:http|https)://', url):
            if '.' not in url.split('/')[-1]:
                # URL doesn't have a TLD, perform a Google search
                url = "https://www.google.com/search?q=" + url.replace(' ', '%20')
            else:
                url = "https://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - BrowsQ" % title)

    def update_urlbar(self, qurl, browser=None):
        if browser != self.tabs.currentWidget():
            return

        self.url_bar.setText(qurl.toString())
        if qurl.scheme() == 'https':
            self.padlock_icon.setVisible(True)
        else:
            self.padlock_icon.setVisible(False)

    def add_bookmark(self):
        url = self.tabs.currentWidget().url().toString()
        title = self.tabs.currentWidget().page().title()
        self.bookmarks[url] = title
        self.save_bookmarks()
        self.load_bookmarks_into_bar()

    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, 'r') as f:
                return json.load(f)
        return {}

    def save_bookmarks(self):
        with open(self.bookmarks_file, 'w') as f:
            json.dump(self.bookmarks, f)

    def load_bookmarks_into_bar(self):
        self.bookmark_bar.clear()
        for url, title in self.bookmarks.items():
            btn = QPushButton(title)
            btn.clicked.connect(lambda checked, url=url: self.tabs.currentWidget().setUrl(QUrl(url)))
            self.bookmark_bar.addWidget(btn)

    def open_new_tab(self, i):
        if i == -1:
            self.add_new_tab()

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

app = QApplication(sys.argv)
QApplication.setApplicationName("BrowsQ")
window = Browser()
app.exec_()
