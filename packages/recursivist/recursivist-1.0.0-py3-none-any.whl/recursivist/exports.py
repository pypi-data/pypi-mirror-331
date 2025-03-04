"""
Export functionality for the Recursivist directory visualization tool.

This module handles the export of directory structures to various formats including text (ASCII tree), JSON, HTML, Markdown, and JSX (React component).

The DirectoryExporter class provides a unified interface for transforming the directory structure dictionary into different output formats with consistent styling and organization.
"""

import html
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from recursivist.jsx_export import generate_jsx_component

logger = logging.getLogger(__name__)


def sort_files_by_type(
    files: List[Union[str, Tuple[str, str]]],
) -> List[Union[str, Tuple[str, str]]]:
    """Sort files by extension and then by name.

    Handles mixed input of both strings and tuples, ensuring correct sorting in either case. The extension is the primary sort key, followed by the filename as a secondary key.

    Args:
        files: List of filenames or (filename, full_path) tuples to sort

    Returns:
        Sorted list of filenames or tuples
    """
    if not files:
        return []
    all_tuples = all(isinstance(item, tuple) for item in files)
    all_strings = all(isinstance(item, str) for item in files)
    if all_strings:
        files_as_strings = cast(List[str], files)
        return cast(
            List[Union[str, Tuple[str, str]]],
            sorted(
                files_as_strings,
                key=lambda f: (os.path.splitext(f)[1].lower(), f.lower()),
            ),
        )
    elif all_tuples:
        files_as_tuples = cast(List[Tuple[str, str]], files)
        return cast(
            List[Union[str, Tuple[str, str]]],
            sorted(
                files_as_tuples,
                key=lambda t: (os.path.splitext(t[0])[1].lower(), t[0].lower()),
            ),
        )
    else:
        str_items: List[str] = []
        tuple_items: List[Tuple[str, str]] = []
        for item in files:
            if isinstance(item, tuple):
                tuple_items.append(cast(Tuple[str, str], item))
            else:
                str_items.append(cast(str, item))
        sorted_strings = sorted(
            str_items, key=lambda f: (os.path.splitext(f)[1].lower(), f.lower())
        )
        sorted_tuples = sorted(
            tuple_items, key=lambda t: (os.path.splitext(t[0])[1].lower(), t[0].lower())
        )
        result: List[Union[str, Tuple[str, str]]] = []
        for item in sorted_strings:
            result.append(item)
        for item in sorted_tuples:
            result.append(item)
        return result


class DirectoryExporter:
    """Handles exporting directory structures to various formats.

    Provides a unified interface for transforming directory structures into different output formats with consistent styling and organization. Supports text (ASCII tree), JSON, HTML, Markdown, and JSX (React component).
    """

    def __init__(
        self, structure: Dict[str, Any], root_name: str, base_path: Optional[str] = None
    ):
        """Initialize the exporter with directory structure and root name.

        Args:
            structure: The directory structure dictionary
            root_name: Name of the root directory
            base_path: Base path for full path display (if None, only show filenames)
        """
        self.structure = structure
        self.root_name = root_name
        self.base_path = base_path
        self.show_full_path = base_path is not None

    def to_txt(self, output_path: str) -> None:
        """Export directory structure to a text file with ASCII tree representation.

        Creates a text file containing an ASCII tree representation of the directory structure using standard box-drawing characters and indentation.

        Args:
            output_path: Path where the txt file will be saved
        """

        def _build_txt_tree(
            structure: Dict[str, Any], prefix: str = "", path_prefix: str = ""
        ) -> List[str]:
            lines = []
            items = sorted(structure.items())
            for i, (name, content) in enumerate(items):
                if name == "_files":
                    for file_item in sort_files_by_type(content):
                        if self.show_full_path and isinstance(file_item, tuple):
                            _, full_path = file_item
                            lines.append(f"{prefix}├── 📄 {full_path}")
                        else:
                            lines.append(f"{prefix}├── 📄 {file_item}")
                elif name == "_max_depth_reached":
                    continue
                else:
                    lines.append(f"{prefix}├── 📁 {name}")
                    next_path = os.path.join(path_prefix, name) if path_prefix else name
                    if isinstance(content, dict):
                        if content.get("_max_depth_reached"):
                            lines.append(f"{prefix}│   ├── ⋯ (max depth reached)")
                        else:
                            lines.extend(
                                _build_txt_tree(content, prefix + "│   ", next_path)
                            )
            return lines

        tree_lines = [f"📂 {self.root_name}"]
        tree_lines.extend(
            _build_txt_tree(
                self.structure, "", self.root_name if self.show_full_path else ""
            )
        )
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(tree_lines))
        except Exception as e:
            logger.error(f"Error exporting to TXT: {e}")
            raise

    def to_json(self, output_path: str) -> None:
        """Export directory structure to a JSON file.

        Creates a JSON file containing the directory structure with options for including full paths. The JSON structure includes a root name and the hierarchical structure of directories and files.

        Args:
            output_path: Path where the JSON file will be saved
        """
        if self.show_full_path:

            def convert_tuples_to_paths(structure):
                result = {}
                for k, v in structure.items():
                    if k == "_files":
                        result[k] = [full_path for _, full_path in v]
                    elif k == "_max_depth_reached":
                        result[k] = v
                    elif isinstance(v, dict):
                        result[k] = convert_tuples_to_paths(v)
                    else:
                        result[k] = v
                return result

            export_structure = convert_tuples_to_paths(self.structure)
        else:
            export_structure = self.structure
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "root": self.root_name,
                        "structure": export_structure,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise

    def to_html(self, output_path: str) -> None:
        """Export directory structure to an HTML file.

        Creates a standalone HTML file with a styled representation of the directory structure using nested unordered lists with CSS styling for colors and indentation.

        Args:
            output_path: Path where the HTML file will be saved
        """

        def _build_html_tree(structure: Dict[str, Any], path_prefix: str = "") -> str:
            html_content = ["<ul>"]
            if "_files" in structure:
                for file_item in sort_files_by_type(structure["_files"]):
                    if self.show_full_path and isinstance(file_item, tuple):
                        _, full_path = file_item
                        html_content.append(
                            f'<li class="file">📄 {html.escape(full_path)}</li>'
                        )
                    else:
                        filename_str = cast(str, file_item)
                        html_content.append(
                            f'<li class="file">📄 {html.escape(filename_str)}</li>'
                        )
            for name, content in sorted(structure.items()):
                if name == "_files" or name == "_max_depth_reached":
                    continue
                html_content.append(
                    f'<li class="directory">📁 <span class="dir-name">{html.escape(name)}</span>'
                )
                next_path = os.path.join(path_prefix, name) if path_prefix else name
                if isinstance(content, dict):
                    if content.get("_max_depth_reached"):
                        html_content.append(
                            '<ul><li class="max-depth">⋯ (max depth reached)</li></ul>'
                        )
                    else:
                        html_content.append(_build_html_tree(content, next_path))
                html_content.append("</li>")
            html_content.append("</ul>")
            return "\n".join(html_content)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Directory Structure - {html.escape(self.root_name)}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 20px;
                }}
                .directory {{
                    color: #2c3e50;
                }}
                .dir-name {{
                    font-weight: bold;
                }}
                .file {{
                    color: #34495e;
                }}
                .max-depth {{
                    color: #999;
                    font-style: italic;
                }}
                .path-info {{
                    margin-bottom: 20px;
                    font-style: italic;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <h1>📂 {html.escape(self.root_name)}</h1>
            {_build_html_tree(self.structure, self.root_name if self.show_full_path else "")}
        </body>
        </html>
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_template)
        except Exception as e:
            logger.error(f"Error exporting to HTML: {e}")
            raise

    def to_markdown(self, output_path: str) -> None:
        """Export directory structure to a Markdown file.

        Creates a Markdown file with a structured representation of the directory hierarchy using headings, lists, and formatting to distinguish between files and directories.

        Args:
            output_path: Path where the Markdown file will be saved
        """

        def _build_md_tree(
            structure: Dict[str, Any], level: int = 0, path_prefix: str = ""
        ) -> List[str]:
            lines = []
            indent = "    " * level
            if "_files" in structure:
                for file_item in sort_files_by_type(structure["_files"]):
                    if self.show_full_path and isinstance(file_item, tuple):
                        _, full_path = file_item
                        lines.append(f"{indent}- 📄 `{full_path}`")
                    else:
                        lines.append(f"{indent}- 📄 `{file_item}`")
            for name, content in sorted(structure.items()):
                if name == "_files" or name == "_max_depth_reached":
                    continue
                lines.append(f"{indent}- 📁 **{name}**")
                next_path = os.path.join(path_prefix, name) if path_prefix else name
                if isinstance(content, dict):
                    if content.get("_max_depth_reached"):
                        lines.append(f"{indent}    - ⋯ *(max depth reached)*")
                    else:
                        lines.extend(_build_md_tree(content, level + 1, next_path))
            return lines

        md_content = [f"# 📂 {self.root_name}", ""]
        md_content.extend(
            _build_md_tree(
                self.structure, 0, self.root_name if self.show_full_path else ""
            )
        )
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_content))
        except Exception as e:
            logger.error(f"Error exporting to Markdown: {e}")
            raise

    def to_jsx(self, output_path: str) -> None:
        """Export directory structure to a React component (JSX file).

        Creates a JSX file containing a React component for interactive visualization of the directory structure with collapsible folders and styling.

        Args:
            output_path: Path where the React component file will be saved
        """
        try:
            generate_jsx_component(
                self.structure,
                self.root_name,
                output_path,
                self.show_full_path,
            )
        except Exception as e:
            logger.error(f"Error exporting to React component: {e}")
            raise
