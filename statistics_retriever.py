import asyncio
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QListWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from stats import stats

class FileSelector(QWidget):
    """
    An application for selecting and retrieving statistics from CSV files
    located in specific directories.
    """

    def __init__(self):
        """
        Initializes the FileSelector widget.

        Sets up initial directories, selected files list, and calls initUI() to build the UI.
        """
        super().__init__()
        self.directories = self.check_directory_existence()
        self.selected_files = []
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface with necessary widgets: folder and file list,
        text input for folder path, and buttons for file selection and statistics retrieval.
        """
        self.layout = QVBoxLayout()

        self.label = QLabel("Files available:")
        self.layout.addWidget(self.label)

        self.folder_list = QListWidget()
        self.folder_list.setSelectionMode(QListWidget.MultiSelection)
        for directory in self.directories:
            folder_item = QListWidgetItem(QIcon("images/folder_icon.png"), directory)
            self.folder_list.addItem(folder_item)
        self.folder_list.itemSelectionChanged.connect(self.onFoldersChanged)
        self.layout.addWidget(self.folder_list)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.file_list)

        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter the name of the folder where the statistics will be saved")
        self.layout.addWidget(self.text_input)

        self.selectButton = QPushButton("Retrieve stats", self)
        self.selectButton.clicked.connect(self.selectFiles)
        self.layout.addWidget(self.selectButton)

        self.text_input.textChanged.connect(self.saveTextChanged)

        self.setLayout(self.layout)
        self.setWindowTitle('Statistics retriever')
        self.setGeometry(300, 300, 500, 400)

    def onFoldersChanged(self):
        """
        Called when the selection in the folder_list widget changes.
        Updates the file_list widget based on the selected folders.
        """
        selected_folders = [item.text() for item in self.folder_list.selectedItems()]
        self.populateFileList(selected_folders)

    def populateFileList(self, folders):
        """
        Populates the file_list widget with CSV files from selected folders.

        Args:
        - folders (list): List of folder paths from which to populate CSV files.
        """
        self.file_list.clear()
        for folder in folders:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path) and filename.endswith(".csv"):
                    file_item = QListWidgetItem(QIcon("images/csv_icon.png"), f"{filename} ({folder})")
                    self.file_list.addItem(file_item)
                    file_item.setData(1000, file_path) 

    def selectFiles(self):
        """
        Retrieves statistics for selected CSV files and saves them in a specified folder.
        """
        selected_items = self.file_list.selectedItems()
        full_paths = [item.data(1000) for item in selected_items]  
        
        folder_text = self.text_input.text()
        if folder_text != "":
            if asyncio.run(stats(full_paths, folder_text)):
                QMessageBox.question(self, 'End', "Data have been correctly retrieved", QMessageBox.Ok, QMessageBox.Ok)
        else :
            QMessageBox.question(self, 'Error', "Give a folder name", QMessageBox.Ok, QMessageBox.Ok)

    def saveTextChanged(self):
        """
        Ensure the save name input does not contain invalid characters for filenames.
        If an invalid character is detected, it is removed from the input.

        Invalid characters: > : " / \ ? *
        """
        if len(self.text_input.text()) > 0 and self.text_input.text()[-1] in '>:"/\?*':
            self.text_input.setText(self.text_input.text()[:-1])
            self.changeTemp = True

    def check_directory_existence(self):
        """
        Checks the existence of predefined directories where CSV files are stored.

        Returns:
        - list: List of existing directories.
        """
        directories = []
        if os.path.exists("LiSSa/LiSSa_data") and os.path.isdir("LiSSa/LiSSa_data"):
            directories.append("LiSSa/LiSSa_data")
        if os.path.exists("wikipedia/wiki_data") and os.path.isdir("wikipedia/wiki_data"):
            directories.append("wikipedia/wiki_data")
        if os.path.exists("pubmed/pubmed_data") and os.path.isdir("pubmed/pubmed_data"):
            directories.append("pubmed/pubmed_data")
        return directories

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    fileSelector = FileSelector()
    fileSelector.show()
    
    sys.exit(app.exec_())
