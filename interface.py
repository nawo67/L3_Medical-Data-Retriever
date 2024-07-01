import asyncio
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import requests

from pubmed.pubmed_search.pubmed_text import ReqText
from pubmed.pubmed_search.pubmed_mesh_code import ReqMesh
from pubmed.pubmed_search.pubmed_unique_ID import ReqUI
from MeSH.meshData_func import meshSuggestion, UiSuggestion, wikiSuggestion, textInData, meshInData, uiInData, wikiFrenchSuggestion
import wikipedia.wiki_search.wiki_text as wiki_text
import wikipedia.wiki_search.wiki_mesh_code as wiki_mesh_code 
import wikipedia.wiki_search.wiki_unique_id as wiki_unique_id 
from LiSSa.LiSSa_search.LiSSa_text import LiSSaReqText
from LiSSa.LiSSa_search.LiSSa_mesh_code import LiSSaReqMesh
from LiSSa.LiSSa_search.LiSSa_unique_ID import LiSSaReqUI
from mesh_tree import MeshTree

class MainWindow(QMainWindow):
	def __init__(self):
		"""
        Initialize the main window, set up the UI, initialize widget states, set time suggestions, 
        set signals, and load MeSH tree.
        """
		super().__init__()
		
		self.hasChanged = False
		self.changeTemp = False
		self.setup_ui()
		self.initialize_widget_state()
		self.set_time_suggestion()
		self.set_signals()
		self.load_mesh_tree()


	def load_mesh_tree(self):
		"""
        Load the MeSH tree from a binary file.
        """
		with open('MeSH/meshData.bin', 'r', encoding="utf-8", newline='') as file:
			self.meshTree = file.read().splitlines()

	def closeEvent(self, event):
		"""
        Handle the close event, prompting the user to confirm quit action.
        """
		self.quitApp()
		if self.quit == QMessageBox.No:
			event.ignore()

	def setup_ui(self):
		"""
        Set up the main user interface.
        """
		self.setWindowTitle("Data retriever")
		self.setGeometry(100, 100, 1080, 720)
		self.wid = QWidget(self)
		self.setCentralWidget(self.wid)
		self.quit = QMessageBox.No

		# Apply stylesheet
		self.setStyleSheet("""
            QMainWindow {
				background-color: #f5f5f5;
			}

			QGroupBox {
				font: bold;
				border: 2px solid #A8A8A8;
				border-radius: 4px;
				margin-top: 15px;
				margin-bottom: 15px;
				background-color: #ffffff;
			}

			QGroupBox::title {
				subcontrol-origin: margin;
				subcontrol-position: top center;
				padding: 5px;
			}

			QLabel {
				font-size: 18px;
				color: #333333;
			}

			QLineEdit, QSpinBox, QCheckBox, QRadioButton, QComboBox, QPushButton {
				font-size: 16px;
				padding: 8px;
				border: 1px solid #ccc;
				border-radius: 4px;
				background-color: #ffffff;
			}

			QLineEdit {
				padding-left: 12px;
			}

			QPushButton {
				background-color: #007bff;
				color: white;
				border: none;
			}

			QPushButton:hover {
				background-color: #0056b3;
			}

			QPushButton:pressed {
				background-color: #003d7f;
			}

			QProgressBar {
				text-align: center;
				font-size: 14px;
				border: 2px solid #007bff;
				border-radius: 8px;
			}

			QProgressBar::chunk {
				background-color: #007bff;
			}

			/* Style des QRadioButton et QCheckBox */
			QRadioButton::indicator, QCheckBox::indicator {
				width: 16px;
				height: 16px;
			}

			QCheckBox::indicator:unchecked:hover {
				background-color: #C0C0C0;
			}

        """)
	
		self.setup_main_layout()

	def setup_main_layout(self):
		"""
        Set up the main layout, including forms and buttons.
        """
		self.layout = QVBoxLayout()

		# Site selection checkboxes
		self.site_layout = QHBoxLayout()
		self.wiki_checkbox = QCheckBox("Wikipedia", checked=True)
		self.pubmed_checkbox = QCheckBox("PubMed")
		self.lissa_checkbox = QCheckBox("LiSSa")
		self.site_layout.addWidget(self.wiki_checkbox, alignment=Qt.AlignHCenter)
		self.site_layout.addWidget(self.pubmed_checkbox, alignment=Qt.AlignHCenter)
		self.site_layout.addWidget(self.lissa_checkbox, alignment=Qt.AlignHCenter)

		# Add site layout to main layout
		self.layout.addLayout(self.site_layout)

		# Add forms and button to main layout
		self.pubmed_form = self.setup_pubmed_form()
		self.lissa_form = self.setup_lissa_form()
		self.layout.addWidget(self.pubmed_form)
		self.layout.addWidget(self.lissa_form)
		self.layout.addLayout(self.setup_search_form())

        # Gather data button
		self.gather_button = QPushButton('Gather Data')
		self.layout.addWidget(self.gather_button, alignment=Qt.AlignHCenter | Qt.AlignTop)

        # Progress bar
		self.progress_bar = QProgressBar()
		self.progress_bar.hide()
		self.layout.addWidget(self.progress_bar, alignment=Qt.AlignHCenter | Qt.AlignTop)
		self.pubmed_progress_label = QLabel('', alignment=Qt.AlignCenter)
		self.wiki_progress_label = QLabel('', alignment=Qt.AlignCenter)
		self.lissa_progress_label = QLabel('', alignment=Qt.AlignCenter)
		self.layout.addWidget(self.pubmed_progress_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
		self.layout.addWidget(self.wiki_progress_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
		self.layout.addWidget(self.lissa_progress_label, alignment=Qt.AlignHCenter | Qt.AlignTop)

		self.wid.setLayout(self.layout)
	
	def meshtree(self):
		self.mesh_tree_ui = MeshTree(self.search_input, self.text_radio, self.mesh_radio, self.unique_id_radio, self.meshTree)
		self.mesh_tree_ui.show()

	def setup_pubmed_form(self):
		"""
        Set up the PubMed form layout.
        """
		pubmed_form = QGroupBox("PubMed Parameters  ")
		form_layout = QFormLayout()
		
		self.amount_input = self.create_int_line_edit('10', 'Desired amount of data per page (10, 20, 50, 100, 200)')
		self.pages_input = self.create_int_line_edit('1', 'How many pages? (1-50)')
		self.start_page_input = self.create_int_line_edit('1', 'Starting at what page? (1-50)')
		self.year_input = self.create_int_line_edit('2024', 'For what year?')

		form_layout.addRow(QLabel("Amount per page"), self.amount_input)
		form_layout.addRow(QLabel("Number of pages"), self.pages_input)
		form_layout.addRow(QLabel("Start page"), self.start_page_input)
		form_layout.addRow(QLabel("Year"), self.year_input)

		pubmed_form.setLayout(form_layout)
		return pubmed_form
	
	def setup_lissa_form(self):
		"""
        Set up the LiSSa form layout.
        """
		lissa_form = QGroupBox("LiSSa Parameters  ")
		form_layout = QFormLayout()

		self.amount_lissa_input = self.create_int_line_edit('10', 'Desired amount of data per page')
		self.pages_lissa_input = self.create_int_line_edit('1', 'How many pages?')

		form_layout.addRow(QLabel("Amount per page"), self.amount_lissa_input)
		form_layout.addRow(QLabel("Number of pages"), self.pages_lissa_input)

		lissa_form.setLayout(form_layout)
		return lissa_form
	
	def setup_search_form(self):
		"""
        Set up the search form layout, including input fields and language selection.
        """
		search_layout = QVBoxLayout()

        # Search type selection
		self.search_type_layout = QHBoxLayout()
		self.text_radio = QRadioButton("Text", checked=True)
		self.mesh_radio = QRadioButton("MeSH")
		self.unique_id_radio = QRadioButton("Unique ID")
		self.search_type_layout.addWidget(self.text_radio)
		self.search_type_layout.addWidget(self.mesh_radio)
		self.search_type_layout.addWidget(self.unique_id_radio)
		self.search_input = self.create_line_edit('', 'Search Term')
		self.search_type_layout.addWidget(self.search_input)

		# Mesh Tree viewer
		self.link_label = QLabel(self)
		self.link_label.setText('<a href="#">See mesh tree</a>')
		self.link_label.setOpenExternalLinks(False)
		self.link_label.setAlignment(Qt.AlignRight)

        # Search input fields
		self.depth_input = self.create_int_line_edit('', 'Sub-category Depth')
		self.language_layout = self.create_language_layout()
		self.save_name_input = self.create_line_edit('', 'File Name')
		self.overwrite_checkbox = QCheckBox("Overwrite the file?")

        # Add search components to layout
		search_layout.addLayout(self.search_type_layout)
		search_layout.addWidget(self.link_label)
		search_layout.addWidget(self.depth_input)
		search_layout.addLayout(self.language_layout)
		search_layout.addWidget(self.save_name_input)
		search_layout.addWidget(self.overwrite_checkbox, alignment=Qt.AlignCenter)

		return search_layout
	
	def create_language_layout(self):
		"""
        Create the language selection layout with English and French checkboxes.
        """
		language_layout = QHBoxLayout()
		self.english_checkbox = QCheckBox("English", checked=True)
		self.french_checkbox = QCheckBox("French", checked=True)
		language_layout.addWidget(self.english_checkbox, alignment=Qt.AlignHCenter)
		language_layout.addWidget(self.french_checkbox, alignment=Qt.AlignHCenter)
		return language_layout

	def create_int_line_edit(self, default_text, tooltip_text):
		"""
        Create a QLineEdit for integer input with validation.

        Args:
            default_text (str): Default text for the input field.
            tooltip_text (str): Tooltip text for the input field.

        Returns:
            QLineEdit: Configured QLineEdit widget.
        """
		line_edit = QLineEdit(default_text)
		line_edit.setPlaceholderText(tooltip_text)
		line_edit.setValidator(QIntValidator())
		line_edit.setMaxLength(4)
		line_edit.setAlignment(Qt.AlignRight)
		line_edit.setFont(QFont("Arial", 20))
		line_edit.setToolTip(tooltip_text)
		return line_edit
	
	def create_line_edit(self, default_text, tooltip_text):
		"""
        Create a QLineEdit for text input.

        Args:
            default_text (str): Default text for the input field.
            tooltip_text (str): Tooltip text for the input field.

        Returns:
            QLineEdit: Configured QLineEdit widget.
        """
		line_edit = QLineEdit(default_text)
		line_edit.setPlaceholderText(tooltip_text)
		line_edit.setAlignment(Qt.AlignRight)
		line_edit.setFont(QFont("Arial", 20))
		line_edit.setToolTip(tooltip_text)
		return line_edit
	
	def initialize_widget_state(self):
		"""
        Initialize the state of various widgets.
        """
		self.checkState(self.pubmed_checkbox)
		self.checkState(self.lissa_checkbox)
		self.checkState(self.mesh_radio)
		self.checkState(self.french_checkbox)

	def set_time_suggestion(self):
		"""
        Set a timer for suggestions.
        """
		self.timer = QTimer()
		self.timer.timeout.connect(self.makeSuggestion)
		self.timer.start(1000)

	def set_signals(self):
		"""
        Connect signals and slots.
        """
		self.wiki_checkbox.toggled.connect(lambda:self.checkState(self.wiki_checkbox))
		self.pubmed_checkbox.toggled.connect(lambda:self.checkState(self.pubmed_checkbox))
		self.lissa_checkbox.toggled.connect(lambda:self.checkState(self.lissa_checkbox))
		self.mesh_radio.toggled.connect(lambda:self.checkState(self.mesh_radio))
		self.english_checkbox.toggled.connect(lambda:self.checkState(self.english_checkbox))
		self.french_checkbox.toggled.connect(lambda:self.checkState(self.french_checkbox))
		self.gather_button.clicked.connect(self.on_click)
		self.search_input.textChanged.connect(self.textChanged)
		self.save_name_input.textChanged.connect(self.saveTextChanged)
		self.link_label.linkActivated.connect(self.meshtree)

	def checkState(self,widget):
		"""
        Check the state of a checkbox or radio button and set related widget states accordingly.

        Args:
            widget (QWidget): Checkbox or radio button to check.
        """
		if widget.text() == self.wiki_checkbox.text():
			if widget.isChecked() == False:
				if self.pubmed_checkbox.isChecked() == False and self.lissa_checkbox.isChecked() == False:
					widget.setChecked(True)
				
		if widget.text() == self.pubmed_checkbox.text():
			if widget.isChecked() == False:
				if self.wiki_checkbox.isChecked() == False and self.lissa_checkbox.isChecked() == False:
					widget.setChecked(True)
				else:
					self.pubmed_form.hide()
			else:
				self.pubmed_form.show()
		
		if widget.text() == self.lissa_checkbox.text():
			if widget.isChecked() == False:
				if self.pubmed_checkbox.isChecked() == False and self.wiki_checkbox.isChecked() == False:
					widget.setChecked(True)
				else:
					self.lissa_form.hide()
			else:
				self.lissa_form.show()

		if widget.text() == self.english_checkbox.text():
			if widget.isChecked() == False:
				if self.french_checkbox.isChecked() == False:
					widget.setChecked(True)
				else:
					self.pubmed_checkbox.hide()
					if self.lissa_checkbox.isChecked() == False and self.wiki_checkbox.isChecked() == False:
						self.wiki_checkbox.setChecked(True)
					self.pubmed_checkbox.setChecked(False)

			else:
				self.pubmed_checkbox.show()

		if widget.text() == self.french_checkbox.text():
			if widget.isChecked() == False:
				if self.english_checkbox.isChecked() == False:
					widget.setChecked(True)
				else:
					self.lissa_checkbox.hide()
					if self.pubmed_checkbox.isChecked() == False and self.wiki_checkbox.isChecked() == False:
						self.wiki_checkbox.setChecked(True)
					self.lissa_checkbox.setChecked(False)
			else:
				self.lissa_checkbox.show()

		if widget.text() == self.mesh_radio.text():
			if widget.isChecked() == False:
				self.depth_input.hide()
			else:
				self.depth_input.show()

	def saveTextChanged(self):
		"""
		Ensure the save name input does not contain invalid characters for filenames.
		If an invalid character is detected, it is removed from the input.

		Invalid characters: > : " / \ ? *
		"""
		if len(self.save_name_input.text()) > 0 and self.save_name_input.text()[-1] in '>:"/\?*':
			self.save_name_input.setText(self.save_name_input.text()[:-1])
			self.changeTemp = True

	def textChanged(self):
		"""
		Handle text changes in the search input field based on the selected search type.
		
		If MeSH or Unique ID search is selected, convert the input to uppercase and ensure it contains only one word.
		For other search types, simply mark the text as changed.

		This method also manages state flags to track whether changes have been made.
		"""
		if self.mesh_radio.isChecked() or self.unique_id_radio.isChecked():
			self.search_input.setText(self.search_input.text().upper())
			if len(self.search_input.text().split(" ")) > 1:
				self.changeTemp = True
				self.search_input.setText(self.search_input.text().split(" ")[0])
			else:
				if not self.changeTemp:
					self.hasChanged = True
				else:
					self.changeTemp = False
		else:
			self.hasChanged = True

	def textSuggestion(self):
		"""
        Make search suggestions based on user input.
        """
		self.hasChanged = False
		text = self.search_input.text()
		if self.wiki_checkbox.isChecked():
			if self.french_checkbox.isChecked() and self.english_checkbox.isChecked():
				textSuggestions = wikiFrenchSuggestion(text,self.meshTree) + wikiSuggestion(text, self.meshTree)
			elif self.french_checkbox.isChecked() :
				textSuggestions = wikiFrenchSuggestion(text,self.meshTree)
			elif self.english_checkbox.isChecked():
				textSuggestions = wikiSuggestion(text, self.meshTree) 
		else:
			suggestions = requests.get(f"https://pubmed.ncbi.nlm.nih.gov/suggestions/?term={text}")
			textSuggestions = suggestions.json()["suggestions"]
		completer = QCompleter(textSuggestions)
		completer.popup().setFont(QFont("Arial",12))
		self.search_input.setCompleter(completer)
		completer.complete()

	def meshSuggestion(self):
		"""
		Generate and display MeSH term suggestions based on the current text in the search input field.
		
		This method retrieves MeSH suggestions, sorts them, and sets up a QCompleter to show these suggestions.
		"""
		self.hasChanged = False
		text = self.search_input.text()
		meshsuggestion = meshSuggestion(text, self.meshTree)
		meshsuggestion.sort()
		completer = QCompleter(meshsuggestion)
		completer.popup().setFont(QFont("Arial",12))
		self.search_input.setCompleter(completer)
		completer.complete()
	
	def uiSuggestion(self):
		"""
		Generate and display Unique ID suggestions based on the current text in the search input field.
		
		This method retrieves Unique ID suggestions, removes duplicates, sorts them, 
		and sets up a QCompleter to show these suggestions.
		"""
		self.hasChanged = False
		text = self.search_input.text()
		uisuggestion = list(set(UiSuggestion(text, self.meshTree)))
		uisuggestion.sort()
		completer = QCompleter(uisuggestion)
		completer.popup().setFont(QFont("Arial",12))
		self.search_input.setCompleter(completer)
		completer.complete()
		
	def makeSuggestion(self):
		"""
		Trigger the appropriate suggestion method based on the selected search type and if the text has changed.
		
		If the text search type is selected, call textSuggestion.
		If the MeSH search type is selected, call meshSuggestion.
		If the Unique ID search type is selected, call uiSuggestion.
		"""
		if self.hasChanged and self.text_radio.isChecked():
			self.textSuggestion()
		elif self.hasChanged and self.mesh_radio.isChecked():
			self.meshSuggestion()
		elif self.hasChanged and self.unique_id_radio.isChecked():
			self.uiSuggestion()

	def quitApp(self):
		"""
		Display a confirmation dialog to confirm if the user wants to quit the application.
		
		If the user confirms, exit the application.
		"""
		self.quit = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if self.quit == QMessageBox.Yes:
			sys.exit(0)

	def inputs_values(self):
		"""
		Read and validate input values from various input fields.
		
		This method reads the input values for amount, pages, start page, year, amount for Lissa, 
		pages for Lissa, search term, selected search type, save file name, depth, 
		and overwrite option, ensuring they are correctly parsed to integers where applicable.
		"""
		if self.amount_input.text() != "":
			self.nbId = int(self.amount_input.text())
		else:
			self.nbId = self.amount_input.text()
		
		if self.pages_input.text() != "":
			self.nbPage = int(self.pages_input.text())
		else:
			self.nbPage = self.pages_input.text()

		if self.start_page_input.text() != "":
			self.nbPageMin = int(self.start_page_input.text())
		else:
			self.nbPageMin = self.start_page_input.text()

		if self.year_input.text() != "":
			self.year = int(self.year_input.text())
		else:
			self.year = self.year_input.text()

		if self.amount_lissa_input.text() != "":
			self.nbIdLissa = int(self.amount_lissa_input.text())
		else:
			self.nbIdLissa = self.amount_lissa_input.text()
		
		if self.pages_lissa_input.text() != "":
			self.nbPageLissa = int(self.pages_lissa_input.text())
		else:
			self.nbPageLissa = self.pages_lissa_input.text()

		self.search = self.search_input.text()

		self.text = self.text_radio.isChecked()

		self.mesh = self.mesh_radio.isChecked()

		self.uniqueID = self.unique_id_radio.isChecked()

		self.fileName = self.save_name_input.text()
		
		if self.depth_input.text() != "":
			self.depths = int(self.depth_input.text())
		else:
			self.depths = self.depth_input.text()

		self.openType = "w" if self.overwrite_checkbox.isChecked() else "a"
	
	def pubmed_data_gathering(self):
		"""
		Gather data from PubMed based on user inputs and selected options.

		This method handles the gathering of data from PubMed. It validates the input parameters 
		and triggers data gathering accordingly. It also updates progress labels and displays 
		appropriate error messages if needed.
		"""
		if self.pubmed_checkbox.isChecked() and (self.nbId in [10,20,50,100,200] and self.nbPage != "" and self.nbPage > 0 and self.nbPageMin != "" and self.nbPageMin > 0 and self.search != "" and self.fileName != ""):
			self.pubmed_progress_label.setText("PUBMED --- /%")
			if self.wiki_checkbox.isChecked() and self.search != "" and self.fileName != "":
				self.wiki_progress_label.setText("WIKIPEDIA --- /%")
			if self.lissa_checkbox.isChecked() and self.search != "" and self.fileName != "":
				self.lissa_progress_label.setText("LISSA --- /%")
			QApplication.processEvents()
			if self.text:
				if ReqText(self.nbId, self.nbPage, self.nbPageMin, self.search, self.fileName, self.year, self.openType, self.meshTree, self.progress_bar, self.pubmed_progress_label) == False and not self.wiki_checkbox.isChecked() and not self.lissa_checkbox.isChecked():
					QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
			elif self.mesh:
				if not meshInData(self.search, self.meshTree):
					QMessageBox.question(self, 'Pubmed Error', "Be sure to use a mesh code available in the suggestions", QMessageBox.Ok, QMessageBox.Ok)
				elif self.depths != "" and self.depths >= 0:
					if ReqMesh(self.nbId, self.nbPage, self.nbPageMin, self.search, self.fileName, self.year, self.depths, self.openType, self.meshTree, self.progress_bar, self.pubmed_progress_label) == False and not self.wiki_checkbox.isChecked() and not self.lissa_checkbox.isChecked():
						QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
				else:
					QMessageBox.question(self, 'Pubmed Error', "Depth input is wrong", QMessageBox.Ok, QMessageBox.Ok)
			elif self.uniqueID:
				if not uiInData(self.search, self.meshTree):
					QMessageBox.question(self, 'Pubmed Error', "Be sure to use a unique ID available in the suggestions", QMessageBox.Ok, QMessageBox.Ok)
				elif ReqUI(self.nbId, self.nbPage, self.nbPageMin, self.search, self.fileName, self.year, self.openType, self.meshTree, self.progress_bar, self.pubmed_progress_label) == False and not self.wiki_checkbox.isChecked() and not self.lissa_checkbox.isChecked():
					QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
		elif self.pubmed_checkbox.isChecked():
			QMessageBox.question(self, 'Pubmed Error', "One or several of the input given for pubmed search is/are wrong", QMessageBox.Ok, QMessageBox.Ok)

	def wikipedia_data_gathering(self):
		"""
		Gather data from Wikipedia based on user inputs and selected options.

		This method handles the gathering of data from Wikipedia. It validates the input parameters 
		and triggers data gathering accordingly. It also updates progress labels and displays 
		appropriate error messages if needed.
		"""
		if self.wiki_checkbox.isChecked() and self.search != "" and self.fileName != "":
			self.progress_bar.setValue(0)
			self.wiki_progress_label.setText("WIKIPEDIA --- /%")
			if self.lissa_checkbox.isChecked() and self.search != "" and self.fileName != "":
				self.lissa_progress_label.setText("LISSA --- /%")
			QApplication.processEvents()
			if self.text:
				if not textInData(self.search, self.meshTree):
					QMessageBox.question(self, 'Wikipedia Error', "Be sure to use a search available in the suggestions if wikipedia search is enabled", QMessageBox.Ok, QMessageBox.Ok)
				elif asyncio.run(wiki_text.launch(self.search, self.fileName, self.openType, self.meshTree, self.progress_bar, self.wiki_progress_label, self.french_checkbox.isChecked(), self.english_checkbox.isChecked())) == False and not self.lissa_checkbox.isChecked():
					QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)

			elif self.mesh :
				if not meshInData(self.search, self.meshTree):
					QMessageBox.question(self, 'Wikipedia Error', "Be sure to use a mesh code available in the suggestions", QMessageBox.Ok, QMessageBox.Ok)
				elif self.depths != "" and self.depths >= 0:
					if asyncio.run(wiki_mesh_code.launch(self.search, self.depths, self.fileName, self.openType, self.meshTree, self.progress_bar, self.wiki_progress_label, self.french_checkbox.isChecked(), self.english_checkbox.isChecked())) == False and not self.lissa_checkbox.isChecked():
						QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
				else:
					QMessageBox.question(self, 'Wikipedia Error', "Depth input is wrong", QMessageBox.Ok, QMessageBox.Ok)
			elif self.uniqueID:
				if not uiInData(self.search, self.meshTree):
					QMessageBox.question(self, 'Wikipedia Error', "Be sure to use a unique ID available in the suggestions", QMessageBox.Ok, QMessageBox.Ok)
				elif asyncio.run(wiki_unique_id.launch(self.search, self.fileName, self.openType, self.meshTree, self.progress_bar, self.wiki_progress_label, self.french_checkbox.isChecked(), self.english_checkbox.isChecked())) == False and not self.lissa_checkbox.isChecked():
					QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
		elif self.wiki_checkbox.isChecked():
			QMessageBox.question(self, 'Wikipedia Error', "One or several of the input given for wikipedia search is/are wrong", QMessageBox.Ok, QMessageBox.Ok)

	def lissa_data_gathering(self):
		"""
		Gather data from LiSSa based on user inputs and selected options.

		This method handles the gathering of data from LiSSa. It validates the input parameters 
		and triggers data gathering accordingly. It also updates progress labels and displays 
		appropriate error messages if needed.
		"""
		if self.lissa_checkbox.isChecked() and self.search != "" and self.fileName != "" and self.nbIdLissa != "" and self.nbPageLissa != "":
			self.progress_bar.setValue(0)
			self.lissa_progress_label.setText("LISSA --- /%")
			QApplication.processEvents()
			if self.text:
				if not textInData(self.search, self.meshTree):
					QMessageBox.question(self, 'LiSSa Error', "Be sure to use a search available in the suggestions if LiSSa search is enabled", QMessageBox.Ok, QMessageBox.Ok)
				elif LiSSaReqText(self.search, self.fileName, self.nbPageLissa, self.nbIdLissa, self.meshTree, self.progress_bar, self.lissa_progress_label) == False:
					QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
			elif self.mesh :
				if not meshInData(self.search, self.meshTree):
					QMessageBox.question(self, 'LiSSa Error', "Be sure to use a search available in the suggestions if LiSSa search is enabled", QMessageBox.Ok, QMessageBox.Ok)
				elif LiSSaReqMesh(self.search, self.fileName, self.nbPageLissa, self.nbIdLissa, self.depths, self.meshTree, self.progress_bar, self.lissa_progress_label) == False:
					QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
			elif self.uniqueID:
				if not uiInData(self.search, self.meshTree):
					QMessageBox.question(self, 'LiSSa Error', "Be sure to use a search available in the suggestions if LiSSa search is enabled", QMessageBox.Ok, QMessageBox.Ok)
				elif LiSSaReqUI(self.search, self.fileName, self.nbPageLissa, self.nbIdLissa, self.meshTree, self.progress_bar, self.lissa_progress_label) == False:
					QMessageBox.question(self, 'End', "There is no more data for this research", QMessageBox.Ok, QMessageBox.Ok)
		elif self.lissa_checkbox.isChecked():
			QMessageBox.question(self, 'LiSSa Error', "One or several of the input given for LiSSa search is/are wrong", QMessageBox.Ok, QMessageBox.Ok)

	def on_click(self):
		"""
		Handle the click event of the gather button.

		This method is triggered when the gather button is clicked. It hides the gather button, 
		shows the progress bar, retrieves input values, validates search inputs, triggers data 
		gathering methods, hides the progress bar after data gathering, and shows the gather button again.
		"""
		
		self.inputs_values()
		
		# Validate search inputs and provide feedback if invalid
		if self.wiki_checkbox.isChecked() and self.text and not textInData(self.search, self.meshTree):
			QMessageBox.question(self, 'Wikipedia Error', "Be sure to use a search available in the suggestions if wikipedia search is enabled", QMessageBox.Ok, QMessageBox.Ok)
			return
		
		self.gather_button.hide()

		self.progress_bar.show()
		
		self.pubmed_data_gathering()

		self.wikipedia_data_gathering()
		
		self.lissa_data_gathering()
		
		self.progress_bar.hide()
		self.progress_bar.setValue(0)
		self.wiki_progress_label.setText("")
		self.pubmed_progress_label.setText("")
		self.lissa_progress_label.setText("")

		self.gather_button.show()

def main(args):
	app = QApplication(args)
	win = MainWindow()
	win.show()
	app.exec_()

if __name__ == "__main__":
	main(sys.argv)
