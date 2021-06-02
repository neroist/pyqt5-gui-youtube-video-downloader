from PyQt5.QtWidgets import QLabel, QDialog, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import QUrl


class DownloadPopup(QDialog):
    """
    Download Popup for when the Youtube video downloads.
    """

    def __init__(self, video_path, parent=None):
        super().__init__(parent=parent)

        #set window title
        self.setWindowTitle("Video Downloaded")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()

        path = bytearray(QUrl.fromLocalFile("file:///"+video_path).toEncoded()).decode() # i have no idea what this means or does, but it works!
        message = QLabel(f'The video was just downloaded. Click <a href="{path}">here</a> to see the video in it\'s folder.', self)
        message.setOpenExternalLinks(True)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
