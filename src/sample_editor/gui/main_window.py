"""PySide6 GUI for the SampleEditor MVP."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from sample_editor.core.config import load_runtime_paths, persist_runtime_paths
from sample_editor.core.mapping import load_mapping_safe
from sample_editor.core.slides import (
    compare_slides,
    describe_case_files,
    describe_slide,
    extract_he_id,
    list_slide_files,
    replace_label_and_write,
)


class MainWindow(QMainWindow):
    """Main window for the SampleEditor MVP."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SampleEditor MVP")
        self.resize(1100, 760)

        self.base_dir = Path(__file__).resolve().parents[3]
        self.paths = load_runtime_paths(self.base_dir)
        self.paths["input_folder"].mkdir(parents=True, exist_ok=True)
        self.paths["output_folder"].mkdir(parents=True, exist_ok=True)

        self.input_path_edit = QLineEdit(str(self.paths["input_folder"]))
        self.output_path_edit = QLineEdit(str(self.paths["output_folder"]))
        self.mapping_path_edit = QLineEdit(str(self.paths["csv_mapping_path"]))

        self.input_list = QListWidget()
        self.output_list = QListWidget()
        self.case_files_view = QPlainTextEdit()
        self.case_files_view.setReadOnly(True)
        self.case_files_view.setPlaceholderText(
            "Select a file to see all related .isyntax/.ndpi files in that case."
        )
        self.file_details_view = QPlainTextEdit()
        self.file_details_view.setReadOnly(True)
        self.file_details_view.setPlaceholderText(
            "Selected file details will appear here."
        )
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Activity log will appear here.")

        self._build_ui()
        self.input_list.currentItemChanged.connect(self.update_case_context)
        self.output_list.currentItemChanged.connect(self.update_case_context)
        self.input_list.itemDoubleClicked.connect(self.view_selected_slide)
        self.output_list.itemDoubleClicked.connect(self.view_selected_slide)
        self.refresh_lists()

    def _build_ui(self) -> None:
        container = QWidget()
        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        root_layout.addWidget(self._build_paths_group())
        root_layout.addWidget(self._build_actions_group())
        root_layout.addWidget(self._build_file_splitter(), stretch=1)
        root_layout.addWidget(self._build_case_context_group(), stretch=1)
        root_layout.addWidget(self._build_log_group(), stretch=1)

        self.setCentralWidget(container)

    def _build_paths_group(self) -> QGroupBox:
        group = QGroupBox("Project Paths")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        layout.addWidget(QLabel("Input Folder"), 0, 0)
        layout.addWidget(self.input_path_edit, 0, 1)
        layout.addWidget(self._make_button("Browse", self.choose_input_folder), 0, 2)

        layout.addWidget(QLabel("Output Folder"), 1, 0)
        layout.addWidget(self.output_path_edit, 1, 1)
        layout.addWidget(
            self._make_button("Browse", self.choose_output_folder),
            1,
            2,
        )

        layout.addWidget(QLabel("Mapping CSV"), 2, 0)
        layout.addWidget(self.mapping_path_edit, 2, 1)
        layout.addWidget(
            self._make_button("Browse", self.choose_mapping_file),
            2,
            2,
        )

        save_button = self._make_button("Save Paths", self.save_paths)
        refresh_button = self._make_button("Refresh Files", self.refresh_lists)
        layout.addWidget(save_button, 3, 1)
        layout.addWidget(refresh_button, 3, 2)
        return group

    def _build_actions_group(self) -> QGroupBox:
        group = QGroupBox("Actions")
        layout = QHBoxLayout(group)
        layout.setSpacing(10)

        buttons = [
            ("Convert Selected Input", self.convert_selected_input),
            ("Batch Convert New", self.batch_convert_new),
            ("View Selected File", self.view_selected_slide),
            ("Compare Selected Pair", self.compare_selected_pair),
        ]
        for label, handler in buttons:
            layout.addWidget(self._make_button(label, handler))
        return group

    def _build_file_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Horizontal)

        input_group = QGroupBox("Input Slides")
        input_layout = QVBoxLayout(input_group)
        input_layout.addWidget(self.input_list)

        output_group = QGroupBox("Output Slides")
        output_layout = QVBoxLayout(output_group)
        output_layout.addWidget(self.output_list)

        splitter.addWidget(input_group)
        splitter.addWidget(output_group)
        splitter.setSizes([520, 520])
        return splitter

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("Log")
        layout = QVBoxLayout(group)
        layout.addWidget(self.log_output)
        return group

    def _build_case_context_group(self) -> QGroupBox:
        group = QGroupBox("Case Context")
        layout = QHBoxLayout(group)
        layout.addWidget(self.case_files_view)
        layout.addWidget(self.file_details_view)
        return group

    def _make_button(self, label: str, handler: object) -> QPushButton:
        button = QPushButton(label)
        button.clicked.connect(handler)  # type: ignore[arg-type]
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return button

    def choose_input_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose input folder",
            self.input_path_edit.text(),
        )
        if folder:
            self.input_path_edit.setText(folder)

    def choose_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose output folder",
            self.output_path_edit.text(),
        )
        if folder:
            self.output_path_edit.setText(folder)

    def choose_mapping_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Choose mapping CSV",
            self.mapping_path_edit.text(),
            "CSV Files (*.csv);;All Files (*.*)",
        )
        if filename:
            self.mapping_path_edit.setText(filename)

    def current_paths(self) -> dict[str, Path]:
        return {
            "input_folder": Path(self.input_path_edit.text().strip()),
            "output_folder": Path(self.output_path_edit.text().strip()),
            "csv_mapping_path": Path(self.mapping_path_edit.text().strip()),
            "config_path": self.paths["config_path"],
        }

    def save_paths(self) -> None:
        self.paths = self.current_paths()
        self.paths["input_folder"].mkdir(parents=True, exist_ok=True)
        self.paths["output_folder"].mkdir(parents=True, exist_ok=True)
        persist_runtime_paths(self.paths)
        self.append_log("Saved paths to config.")
        self.refresh_lists()

    def refresh_lists(self) -> None:
        self.paths = self.current_paths()
        self.input_list.clear()
        self.output_list.clear()

        for filename in list_slide_files(self.paths["input_folder"]):
            self.input_list.addItem(QListWidgetItem(filename))
        for filename in list_slide_files(self.paths["output_folder"]):
            self.output_list.addItem(QListWidgetItem(filename))

        self.append_log(
            f"Refreshed file lists. "
            f"{self.input_list.count()} input / {self.output_list.count()} output files."
        )
        self.update_case_context()

    def append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)

    def selected_input_path(self) -> Path | None:
        item = self.input_list.currentItem()
        if item is None:
            return None
        return self.current_paths()["input_folder"] / item.text()

    def selected_output_path(self) -> Path | None:
        item = self.output_list.currentItem()
        if item is None:
            return None
        return self.current_paths()["output_folder"] / item.text()

    def mapping(self) -> dict[str, str]:
        return load_mapping_safe(self.current_paths()["csv_mapping_path"])

    def selected_slide_path(self) -> Path | None:
        return self.selected_input_path() or self.selected_output_path()

    def update_case_context(self) -> None:
        slide_path = self.selected_slide_path()
        if slide_path is None:
            self.case_files_view.clear()
            self.file_details_view.clear()
            return

        case_descriptions = describe_case_files(slide_path)
        if case_descriptions:
            lines = [f"Case folder: {slide_path.parent}"]
            for entry in case_descriptions:
                marker = "HE candidate" if entry["is_largest"] else "USS/other"
                lines.append(
                    f"- {entry['name']} | {entry['size_mb']} MB | {marker}"
                )
            self.case_files_view.setPlainText("\n".join(lines))
        else:
            self.case_files_view.setPlainText("No related case files found.")

        self.file_details_view.setPlainText(
            "\n".join(
                [
                    f"Selected file: {slide_path.name}",
                    f"Folder: {slide_path.parent}",
                    f"Extension: {slide_path.suffix}",
                ]
            )
        )

    def convert_selected_input(self) -> None:
        slide_path = self.selected_input_path()
        if slide_path is None:
            self.show_warning("Select an input slide first.")
            return

        mapping = self.mapping()
        he_id = extract_he_id(slide_path.name)
        block_id = mapping.get(he_id)
        if not block_id:
            block_id, accepted = QInputDialog.getText(
                self,
                "Enter Block ID",
                f"No mapping found for {slide_path.name}.\nEnter a Block ID:",
            )
            if not accepted or not block_id.strip():
                self.append_log("Conversion cancelled by user.")
                return
            block_id = block_id.strip()

        out_path = self.current_paths()["output_folder"] / f"{block_id}{slide_path.suffix}"
        try:
            replace_label_and_write(slide_path, block_id, out_path)
        except Exception as exc:
            self.show_error(f"Conversion failed:\n{exc}")
            self.append_log(f"Conversion failed for {slide_path.name}: {exc}")
            return

        self.append_log(f"Converted {slide_path.name} -> {out_path.name}")
        self.refresh_lists()

    def batch_convert_new(self) -> None:
        paths = self.current_paths()
        mapping = self.mapping()
        input_files = list_slide_files(paths["input_folder"])
        output_ids = {Path(name).stem for name in list_slide_files(paths["output_folder"])}

        files_to_convert: list[tuple[Path, str]] = []
        for filename in input_files:
            he_id = extract_he_id(filename)
            block_id = mapping.get(he_id)
            if not block_id:
                self.append_log(f"Skipped {filename}: no mapping found.")
                continue
            if block_id not in output_ids:
                files_to_convert.append((paths["input_folder"] / filename, block_id))

        if not files_to_convert:
            self.show_info("No new mapped files to convert.")
            self.append_log("Batch convert found no new mapped files.")
            return

        for slide_path, block_id in files_to_convert:
            out_path = paths["output_folder"] / f"{block_id}{slide_path.suffix}"
            try:
                replace_label_and_write(slide_path, block_id, out_path)
                self.append_log(f"Converted {slide_path.name} -> {out_path.name}")
            except Exception as exc:
                self.append_log(f"Failed to convert {slide_path.name}: {exc}")

        self.refresh_lists()
        self.show_info(f"Batch conversion finished for {len(files_to_convert)} files.")

    def view_selected_slide(self) -> None:
        slide_path = self.selected_input_path() or self.selected_output_path()
        if slide_path is None:
            self.show_warning("Select a slide from either list first.")
            return

        try:
            pages = describe_slide(slide_path)
        except Exception as exc:
            self.show_error(f"Could not read slide:\n{exc}")
            return

        details = "\n".join(
            f"Page {page['page_number']}: shape={page['shape']}, "
            f"description={page['description']}"
            for page in pages
        )
        QMessageBox.information(
            self,
            f"File Details: {slide_path.name}",
            details or "No page details available.",
        )
        self.append_log(f"Viewed {slide_path.name}")
        self.update_case_context()

    def compare_selected_pair(self) -> None:
        input_path = self.selected_input_path()
        output_path = self.selected_output_path()
        if input_path is None or output_path is None:
            self.show_warning("Select one input slide and one output slide first.")
            return

        try:
            comparison = compare_slides(input_path, output_path)
        except Exception as exc:
            self.show_error(f"Could not compare slides:\n{exc}")
            return

        original = "\n".join(
            f"Page {page['page_number']}: shape={page['shape']}, "
            f"description={page['description']}"
            for page in comparison["original"]
        )
        new = "\n".join(
            f"Page {page['page_number']}: shape={page['shape']}, "
            f"description={page['description']}"
            for page in comparison["new"]
        )
        QMessageBox.information(
            self,
            "Compare Slides",
            f"Original: {input_path.name}\n\n{original}\n\n"
            f"New: {output_path.name}\n\n{new}",
        )

    def show_warning(self, message: str) -> None:
        QMessageBox.warning(self, "SampleEditor", message)

    def show_info(self, message: str) -> None:
        QMessageBox.information(self, "SampleEditor", message)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "SampleEditor", message)
