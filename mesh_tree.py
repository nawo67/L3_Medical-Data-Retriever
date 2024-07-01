from PyQt5.QtWidgets import QMainWindow, QTreeView, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt
from MeSH.meshData_func import MeshToEnglishTitle, MeshToUniqueID, MeshToFrenchTitle

class MeshTree(QMainWindow):
    """
    An interface for viewing MeSH (Medical Subject Headings) data in a hierarchical tree structure.
    """

    def __init__(self, qline, text, mesh, uniqueid, meshTree):
        """
        Initializes the MeshTree widget.

        Args:
        - qline (QLineEdit): QLineEdit widget for displaying selected MeSH data.
        - text (bool): Indicates whether text display mode is selected.
        - mesh (bool): Indicates whether MeSH code display mode is selected.
        - uniqueid (bool): Indicates whether unique ID display mode is selected.
        - meshTree: MeSH tree data structure.
        """
        super().__init__()
        self.qline = qline
        self.text = text
        self.mesh = mesh
        self.uniqueid = uniqueid
        self.meshTree = meshTree
        self.hierarchy = None
        self.model = None
        self.fr_or_en = 2
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface with necessary widgets, styles, and data.

        Loads MeSH data, sets up the tree view, connects signals, and displays the UI.
        """
        self.setWindowTitle('Mesh Data Viewer')
        self.setGeometry(100, 100, 600, 400)

        # Styling the main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }

            /* Style du TreeView */
            QTreeView {
                border: 2px solid #bdbdbd; /* Bordure */
                border-radius: 5px; /* Arrondi des coins */
            }

            QTreeView::item {
                padding: 5px; /* Espacement interne */
            }
                           
            QTreeView::item:hover {
                background-color: #00bfff; /* Couleur de fond lorsqu'élément sélectionné */
            }

            QTreeView::item:selected {
                background-color: #00b3ff; /* Couleur de fond lorsqu'élément sélectionné */
            }
        """)
        
        font = QFont()
        font.setPointSize(10)

        # Labels for language selection (French and English)
        self.fr_label = QLabel(self)
        self.fr_label.setText('<a href="#">FR</a>')
        self.fr_label.setOpenExternalLinks(False)
        self.fr_label.setAlignment(Qt.AlignRight)
        self.fr_label.setFont(font)

        font.setBold(True)

        self.en_label = QLabel(self)
        self.en_label.setText('<a href="#">EN</a>')
        self.en_label.setOpenExternalLinks(False)
        self.en_label.setAlignment(Qt.AlignRight)
        self.en_label.setFont(font)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Horizontal layout for language selection labels
        self.labels_layout = QHBoxLayout()
        self.labels_layout.addWidget(self.fr_label)
        self.labels_layout.addWidget(self.en_label)
        self.labels_layout.addStretch()

        self.tree_view = QTreeView(self)

        # Add layouts and widgets to the main vertical layout
        self.layout.addLayout(self.labels_layout)
        self.layout.addWidget(self.tree_view)
        
        # Connect signals
        self.fr_label.linkActivated.connect(self.langage_fr)
        self.en_label.linkActivated.connect(self.langage_en)
        self.tree_view.clicked.connect(self.on_tree_view_clicked)


        mesh_data = self.load_mesh_data()
        if mesh_data:
            self.populate_tree(mesh_data)
        self.tree_view.collapseAll()

        self.show()

    def langage_fr(self):
        """
        Switches the interface language to French.
        """
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Mesh Tree"])
        self.model.setHeaderData(0, Qt.Horizontal, Qt.AlignHCenter, Qt.TextAlignmentRole)
        self.fr_or_en = 1

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.fr_label.setFont(font)
        font.setBold(False)
        self.en_label.setFont(font)

        self.add_items_to_model(self.hierarchy, self.model, self.fr_or_en)
        
    def langage_en(self):
        """
        Switches the interface language to English.
        """
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Mesh Tree"])
        self.model.setHeaderData(0, Qt.Horizontal, Qt.AlignHCenter, Qt.TextAlignmentRole)
        self.fr_or_en = 2

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.en_label.setFont(font)
        font.setBold(False)
        self.fr_label.setFont(font)

        self.add_items_to_model(self.hierarchy, self.model, self.fr_or_en)

    def load_mesh_data(self):
        """
        Loads MeSH data from the meshData.bin file.

        Returns:
        - list: MeSH data loaded from the file.
        """
        mesh_data = []
        try:
            with open('MeSH/meshData.bin', 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    elements = line.split('|')

                    if len(elements) >= 4:
                        mesh_descriptor = elements[2]
                        mesh_name_fr = elements[0]
                        mesh_name_eng = elements[1]
                        mesh_id = elements[3]
                        mesh_data.append([mesh_descriptor, mesh_name_fr, mesh_name_eng, mesh_id])
        except FileNotFoundError:
            print("Le fichier meshData.bin n'a pas été trouvé.")
        
        mesh_data.sort()
        return mesh_data

    def on_tree_view_clicked(self, index):
        """
        Handles click events on the tree view to update qline text based on selection.

        Args:
        - index: Index of the clicked item.
        """
        model = self.tree_view.model()
        item = model.itemFromIndex(index)
        mesh = item.text().split('[')[-1][:-1]
        if len(mesh)>1:
            if self.text.isChecked() :
                if self.fr_or_en == 1:
                    self.qline.setText(MeshToFrenchTitle(mesh, self.meshTree)[0])
                elif self.fr_or_en ==2:
                    self.qline.setText(MeshToEnglishTitle(mesh, self.meshTree)[0])
            elif self.mesh.isChecked() :
                self.qline.setText(mesh)
            elif self.uniqueid.isChecked():
                self.qline.setText(MeshToUniqueID(mesh, self.meshTree)[0])
        else:
            self.qline.setText("")

    def build_hierarchy(self, data):
        """
        Builds a hierarchical structure from MeSH data.

        Args:
        - data (list): MeSH data containing descriptor, French name, English name, and ID.

        Returns:
        - dict: Hierarchical structure of MeSH data.
        """
        hierarchy = {}
        for descriptor, fr_name, eng_name, mesh_id in data:
            parts = descriptor.split('.')
            current_level = hierarchy
            if len(parts[0]) != 1:
                parts.insert(0, parts[0][0])

            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

            current_level['_data'] = [descriptor, fr_name, eng_name, mesh_id]

        return hierarchy

    def populate_tree(self, mesh_data):
        """
        Populates the tree view with MeSH data.

        Args:
        - mesh_data (list): MeSH data to populate the tree view.
        """
        self.hierarchy = self.build_hierarchy(mesh_data)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Mesh Tree"])
        self.model.setHeaderData(0, Qt.Horizontal, Qt.AlignHCenter, Qt.TextAlignmentRole)
        self.tree_view.setModel(self.model)
        self.add_items_to_model(self.hierarchy, self.model, 2)
        self.tree_view.expandAll()

    def add_items_to_model(self, hierarchy, model, fr_or_en, parent=None):
        """
        Recursively adds items to the model for the tree view.

        Args:
        - hierarchy (dict): Hierarchical structure of MeSH data.
        - model (QStandardItemModel): Model for the tree view.
        - fr_or_en (int): Language mode (1 for French, 2 for English).
        - parent (QStandardItem, optional): Parent item in the model.
        """
        for key, value in hierarchy.items():
            if key == '_data':
                continue
            
            item_data = value.get('_data', ["", "", "", ""])
            display_text = f"{item_data[fr_or_en]} [{item_data[0]}]"
            item = QStandardItem(display_text)
            item.setEditable(False)
            
            if parent is None:
                model.appendRow(item)
            else:
                parent.appendRow(item)

            self.add_items_to_model(value, model, fr_or_en, item)

