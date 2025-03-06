import os

from AnyQt.QtWidgets import QApplication
import Orange.data
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.settings import Setting
from AnyQt.QtWidgets import QLineEdit, QLabel

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_ini

@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWExtraChunks(widget.OWWidget):
    name = "Extra Chunks"
    description = "Extract surrounding chunks from a dataset"
    icon = "icons/extra_chunks.png"
    want_control_area = False
    priority = 1001

    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owextrachunks.ui")

    class Inputs:
        complete_data = Input("Complete Dataset", Orange.data.Table)
        selected_data = Input("Chunks", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    extra_chunks: int = Setting(2)

    @Inputs.complete_data
    def set_complete_data(self, data):
        self.complete_data = data
        if self.autorun:
            self.process()

    @Inputs.selected_data
    def set_selected_data(self, data):
        self.selected_data = data
        if self.autorun:
            self.process()

    def __init__(self):
        super().__init__()
        # UI setup
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        # Data attributes
        self.complete_data = None
        self.selected_data = None
        self.autorun = True

        self.edit_extrachunks = self.findChild(QLineEdit, 'QExtraChunks')
        self.edit_extrachunks.setText(str(self.extra_chunks))
        self.edit_extrachunks.textChanged.connect(self.update_extrachunks)

        # Assurez-vous que extra_chunks est bien un entier
        self.extra_chunks = int(self.edit_extrachunks.text()) if self.edit_extrachunks.text().isdigit() else 2

    def update_extrachunks(self, text):
        self.extra_chunks = int(text) if text.isdigit() else 2

    def process(self):
        if self.complete_data is None or self.selected_data is None:
            return

        domain = self.complete_data.domain
        if "Chunks index" not in domain or "path" not in domain:
            return

        index_var = domain["Chunks index"]
        path_var = domain["path"]

        selected_indices_by_path = {}
        for row in self.selected_data:
            path_value = row[path_var]
            index_value = int(row[index_var])
            if path_value not in selected_indices_by_path:
                selected_indices_by_path[path_value] = []
            selected_indices_by_path[path_value].append(index_value)

        complete_indices_by_path = {}
        for row in self.complete_data:
            path_value = row[path_var]
            index_value = int(row[index_var])
            if path_value not in complete_indices_by_path:
                complete_indices_by_path[path_value] = []
            complete_indices_by_path[path_value].append(index_value)

        full_indices = set()
        for path_value, selected_indices in selected_indices_by_path.items():
            if path_value in complete_indices_by_path:
                complete_indices = complete_indices_by_path[path_value]
                min_idx, max_idx = min(complete_indices), max(complete_indices)
                for idx in selected_indices:
                    start_idx = max(min_idx, idx - self.extra_chunks)
                    end_idx = min(max_idx, idx + self.extra_chunks)

                    full_indices.update((path_value, i) for i in range(start_idx, end_idx + 1))

        selected_rows = [row for row in self.complete_data if (row[path_var], int(row[index_var])) in full_indices]

        output_data = Orange.data.Table(self.complete_data.domain, selected_rows)
        self.Outputs.data.send(output_data)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = OWExtraChunks()
    window.show()
    sys.exit(app.exec_())
