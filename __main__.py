import sys, os, platform

from pytube import YouTube, Stream, request
from pytube.exceptions import MembersOnly, RecordingUnavailable, VideoUnavailable, VideoRegionBlocked, VideoPrivate

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QMessageBox, QAction, qApp, QFileDialog, QLabel,
                             QLineEdit, QProgressDialog)
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

from downloadpopup import DownloadPopup


#globals
downloadSetting = 'first()'
videoFilesize = 0
videoFileExtension = '.mp4'
video: YouTube = None
isCancelled = False
isDownloading = False


class App(QMainWindow):
    """
    QMainWindow > QWidget
    """

    def __init__(self):
        super().__init__()

        self.statusBar().showMessage('')
        self.menubar = self.menuBar()
        self.setAnimated(True)

        self.setGeometry(400, 100, 570, 400) # sets window width, height, and position on screen. The first two args are where it appears on the screen (x, y), and the other two args are width and height of the window (x, y). all in pixels ofc
        self.setWindowTitle('Youtube Video Downloader') # sets window title. pretty straightforward
        self.setWindowIcon(QIcon('C:/Users/pmpig/Downloads/Dakirby309-Simply-Styled-YouTube.ico')) # sets window icon with the QIcon object. QIcon needs the path to the image.

        #actions

        exitWindow = QAction('&Exit', self)
        exitWindow.setShortcut('Ctrl+W') # sets action shortcut. when shortcut is pressed or something, it'll send a triggered signal to the action
        exitWindow.setStatusTip('Exit Application') # sets action status tip.
        exitWindow.triggered.connect(qApp.quit) # connects function to when 'e' is triggered.

        minimizeApp = QAction('&Minimize', self)
        minimizeApp.setShortcut('Ctrl+M')
        minimizeApp.setStatusTip('Minimize Application')
        minimizeApp.triggered.connect(self.showMinimized)

        home = QAction('&Home', self)
        home.setShortcut('Ctrl+H')
        home.setStatusTip('Reset Window Dimensions')
        home.triggered.connect(lambda: self.resize(570, 400))

        #----------------------------

        self.ohhey = QAction('Download highest resolution', self, checkable=True)
        self.ohhey.setStatusTip('Select to download video in highest resolution.')
        #self.ohhey.setChecked(False)
        self.ohhey.triggered.connect(self.downloadHighestVideoRes)

        self.ohnay = QAction('Download lowest resolution', self, checkable=True)
        self.ohnay.setStatusTip('Select to download video in lowest resolution.')
        #self.ohnay.setChecked(False)
        self.ohnay.triggered.connect(self.downloadLowestVideoRes)

        self.ohgay = QAction('Download audio only', self, checkable=True)
        self.ohgay.setStatusTip('Select to only download video audio (if available).')
        # self.ohnay.setChecked(False)
        self.ohgay.triggered.connect(self.downloadAudioOnly)

        #menus
        windowMenu = self.menubar.addMenu('Window') # adds menu to menubar. first arg is the menu title and returns said menu.
        windowMenu.addAction(exitWindow)
        windowMenu.addAction(minimizeApp)
        windowMenu.addSeparator()
        windowMenu.addAction(home)

        g = self.menubar.addMenu('Video Download')
        g.addAction(self.ohhey)
        g.addAction(self.ohnay)
        g.addSeparator()
        g.addAction(self.ohgay)

        #otherMenu = self.menubar.addMenu('Other...')

        #vm = self.menubar.addMenu()

        l1 = QLabel('Download Folder:', self, font=QFont('Arial', 14))
        l1.resize(l1.sizeHint())
        l1.move(170, 65)

        self.e1 = QLineEdit(self, font=QFont('Arial', 13))
        self.e1.setToolTip("Path to the folder where the Youtube video will be downloaded. If field is left blank,\nvideo will be downloaded to the downloads folder.")
        self.e1.setPlaceholderText('Folder path here')
        self.e1.setGeometry(170, 100, 155, 30)

        b1 = QPushButton('Browse...', self, font=QFont('Arial', 11))
        b1.move(345, 100)
        b1.setStatusTip("Browse folders")
        b1.clicked.connect(self.browse)

        l2 = QLabel('Video Link:', self, font=QFont('Arial', 14))
        l2.resize(l2.sizeHint())
        l2.move(200, 185)

        self.e2 = QLineEdit(self, font=QFont('Arial', 13))
        self.e2.setToolTip("Youtube video link to download")
        self.e2.setGeometry(170, 220, 155, 30)
        self.e2.setPlaceholderText('Video link here')

        b2 = QPushButton('Download', self, font=QFont('Arial', 13))
        b2.setStatusTip("Download Youtube video")
        b2.setGeometry(185, 330, 130, 35)
        b2.clicked.connect(self.download)

        self.show() # shows the window onscreen

        return None;

    def downloadAudioOnly(self, state):
        global downloadSetting, videoFileExtension

        if state:
            self.ohnay.setChecked(False)
            self.ohhey.setChecked(False)
            downloadSetting = 'get_audio_only()'

        elif downloadSetting == 'get_audio_only()':
            downloadSetting = 'first()'

        print(downloadSetting)


    def downloadHighestVideoRes(self, state):
        global downloadSetting

        if state:
            self.ohnay.setChecked(False)
            downloadSetting = 'get_highest_resolution()'

        elif downloadSetting == 'get_highest_resolution()':
            downloadSetting = 'first()'

    def downloadLowestVideoRes(self, state):
        global downloadSetting

        if state:
            self.ohhey.setChecked(False)
            downloadSetting = 'get_lowest_resolution()'
        else:
            if downloadSetting == 'get_lowest_resolution()':
                downloadSetting = 'first()'

    def closeEvent(self, event):
        """
        Defines what will happen on closure of the window
        """

        reply = QMessageBox.question(self, 'Exit', "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No) # The first string appears on the titlebar. The second string is the message text displayed by the dialog. The third argument specifies the combination of buttons appearing in the dialog. The last parameter is the default button. It is the button which has initially the keyboard focus. The return value is stored in the reply variable.

        if reply == QMessageBox.Yes:
            event.accept() # accepts the event
        else:
            event.ignore() # ignores the event

    def browse(self) -> None:
        #self.file = QFileDialog.getSaveFileName(self, caption="Save Project", directory=os.getcwd())
        self.viddir = QFileDialog.getExistingDirectory(self, 'Select Directory/Folder', self.getDownloadPath(), QFileDialog.ShowDirsOnly)
        self.e1.setText(self.viddir)

    @staticmethod
    def setIsCancelledToFalse():
        global isCancelled; isCancelled = False

    def idk(self, progress: int):
        self.progressDialog.setValue(progress)

    def download(self) -> str:
        """
        Downloads Youtube video.
        """
        global videoFilesize

        self.setCursor(QCursor(Qt.BusyCursor)) #changes cursor when hovering over the window and all children to busy cursor

        if bool(self.e1.text()) == False:
            print(self.getDownloadPath())
            self.e1.setText(self.getDownloadPath())
            downloadPopup = DownloadPopup(self.getDownloadPath(), self)
        else:
            downloadPopup = DownloadPopup(self.e1.text(), self)

        if not bool(self.e2.text()):
            self.createErrorPopup('Can\'t download a Youtube video with no link.')
            return

        if '&' in self.e2.text():
            link = self.e2.text().split('&')[0]
        else:
            link = self.e2.text()

        try:
            yt = YouTube(link)
            yt.check_availability()
        except MembersOnly as err:
            self.createErrorPopup('Sorry, we couldn\'t download the video. As for why, the video is not accessible to non-channel members of the video creator.')
            return
        except VideoRegionBlocked as err:
            self.createErrorPopup('Sorry, we couldn\'t download the video, it\'s region blocked.')
            return
        except VideoPrivate as err:
            self.createErrorPopup('Sorry, we couldn\'t download the video, it\'s private.')
            return
        except RecordingUnavailable as err:
            self.createErrorPopup('Sorry, we couldn\'t download the video.')
            return
        except VideoUnavailable as err:
            self.createErrorPopup('Sorry, we couldn\'t download the video.')
            return
        except Exception as err:
            self.createErrorPopup(f'An unexpected error occured. Error:{err}')
            return
        finally:
            self.setCursor(QCursor(Qt.ArrowCursor))


        if downloadSetting == 'get_highest_resolution()':
            straem = yt.streams.get_highest_resolution()

        elif downloadSetting == 'get_lowest_resolution()':
            straem = yt.streams.get_lowest_resolution()

        elif downloadSetting == 'get_audio_only()':
            straem = yt.streams.get_audio_only()

        else:
            straem = yt.streams[0]


        exec(f'yt.streams.otf().{downloadSetting}.download(output_path=self.e1.text())')
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.e1.setText('')

        self.setCursor(QCursor(Qt.ArrowCursor))
        downloadPopup.exec_()

        return self.e1.text()

    #@Video.register_on_progress_callback
    #def onProgress(self, stream: pytube.Stream, chunk, bytes_remaining: int) -> int:
    #    size = stream.filesize
    #    x = size - bytes_remaining + 1000000

    #    self.progressDialog.setValue(percentage := round((x/1000000) * 100, 2))

    def createErrorPopup(self, text="An error occurred downloading the video. Are you sure you entered the right information?"):
        QMessageBox.critical(self, "Error", text)

    @staticmethod
    def getDownloadPath() -> str:
        """Returns the default downloads path for linux or windows"""

        if platform.system().lower() == 'windows':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]

            return location

        elif platform.system().lower() == 'linux':
            return os.path.join(os.path.expanduser('~'), 'downloads')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    lication = App()
    sys.exit(app.exec_())
