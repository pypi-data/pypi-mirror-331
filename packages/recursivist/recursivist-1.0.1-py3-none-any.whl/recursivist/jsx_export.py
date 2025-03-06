"""
React component export functionality for the Recursivist directory visualization tool.

This module generates a JSX file with a sophisticated, interactive directory viewer component
with properly functioning folder toggling and breadcrumbs navigation.
"""

import html
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def generate_jsx_component(
    structure: Dict[str, Any],
    root_name: str,
    output_path: str,
    show_full_path: bool = False,
) -> None:
    """
    Generate a React component file for directory structure visualization.

    The component includes:
    - Reliable folder expand/collapse functionality
    - Breadcrumbs navigation
    - Search functionality with highlighted matches
    - Dark mode toggle

    Args:
        structure: Directory structure dictionary
        root_name: Root directory name
        output_path: Path where the React component file will be saved
        show_full_path: Whether to show full paths instead of just filenames
    """

    def _build_structure_jsx(
        structure: Dict[str, Any], level: int = 0, path_prefix: str = ""
    ) -> str:
        jsx_content = []

        # Process directories first
        for name, content in sorted(
            [
                (k, v)
                for k, v in structure.items()
                if k != "_files" and k != "_max_depth_reached"
            ],
            key=lambda x: x[0].lower(),
        ):
            # Track the current path for this folder
            current_path = f"{path_prefix}/{name}" if path_prefix else name
            path_parts = current_path.split("/") if current_path else [name]

            # Handle the case when root is already included
            if path_parts[0] == root_name and len(path_parts) > 1:
                path_parts = [root_name] + [p for p in path_parts[1:] if p]
            else:
                path_parts = [p for p in path_parts if p]
                if not path_parts or path_parts[0] != root_name:
                    path_parts = [root_name] + path_parts

            path_json = ",".join([f'"{html.escape(part)}"' for part in path_parts])

            jsx_content.append(
                f"<DirectoryItem "
                f'name="{html.escape(name)}" '
                f"level={{{level}}} "
                f"path={{[{path_json}]}} "
                f'type="directory">'
            )

            next_path = current_path
            if isinstance(content, dict):
                if content.get("_max_depth_reached"):
                    jsx_content.append(
                        '<div className="p-3 bg-gray-50 rounded-lg border border-gray-100 ml-4 my-1">'
                    )
                    jsx_content.append(
                        '<p className="text-gray-500">⋯ (max depth reached)</p>'
                    )
                    jsx_content.append("</div>")
                else:
                    jsx_content.append(
                        _build_structure_jsx(content, level + 1, next_path)
                    )
            jsx_content.append("</DirectoryItem>")

        # Process files
        if "_files" in structure:
            files = structure["_files"]
            for file_item in sorted(
                files, key=lambda f: f[0].lower() if isinstance(f, tuple) else f.lower()
            ):
                if show_full_path and isinstance(file_item, tuple):
                    file_name, full_path = file_item
                    display_path = html.escape(full_path)

                    # Fix path parts construction
                    if path_prefix:
                        path_parts = path_prefix.split("/")
                        # Handle the case when root is already included
                        if path_parts and path_parts[0] == root_name:
                            path_parts = [root_name] + [p for p in path_parts[1:] if p]
                        else:
                            path_parts = [p for p in path_parts if p]
                            if not path_parts or path_parts[0] != root_name:
                                path_parts = [root_name] + path_parts
                    else:
                        path_parts = [root_name]  # Ensure root is always included

                    path_parts.append(file_name)
                else:
                    file_name = file_item
                    if isinstance(file_name, tuple):
                        file_name = file_name[0]
                    display_path = html.escape(file_name)

                    # Fix path parts construction
                    if path_prefix:
                        path_parts = path_prefix.split("/")
                        # Handle the case when root is already included
                        if path_parts and path_parts[0] == root_name:
                            path_parts = [root_name] + [p for p in path_parts[1:] if p]
                        else:
                            path_parts = [p for p in path_parts if p]
                            if not path_parts or path_parts[0] != root_name:
                                path_parts = [root_name] + path_parts
                    else:
                        path_parts = [root_name]  # Ensure root is always included

                    path_parts.append(file_name)

                path_json = ",".join(
                    [f'"{html.escape(part)}"' for part in path_parts if part]
                )
                jsx_content.append(
                    f"<FileItem "
                    f'name="{html.escape(file_name if isinstance(file_name, str) else file_name[0])}" '
                    f'displayPath="{display_path}" '
                    f"path={{[{path_json}]}} "
                    f"level={{{level}}} />"
                )

        return "\n".join(jsx_content)

    component_template = f"""import React, {{ useState, useEffect, useRef }} from 'react';
    import {{
      ChevronDown,
      ChevronUp,
      Folder,
      FolderOpen,
      File,
      Maximize2,
      Minimize2,
      Search,
      X,
      Info,
      Home,
      ChevronRight,
      Copy,
      Check
    }} from 'lucide-react';

    const AppContext = React.createContext();

    const highlightMatch = (text, searchTerm) => {{
      if (!searchTerm) return text;

      const parts = text.split(new RegExp(`(${{searchTerm}})`, 'gi'));
      return (
        <>
          {{parts.map((part, i) =>
            part.toLowerCase() === searchTerm.toLowerCase()
              ? <mark key={{i}} className="bg-yellow-200 px-1 rounded">{{part}}</mark>
              : part
          )}}
        </>
      );
    }};

    const Breadcrumbs = () => {{
      const {{
        currentPath,
        setCurrentPath,
        selectedItem,
        darkMode
      }} = React.useContext(AppContext);

      const [copied, setCopied] = useState(false);
      const breadcrumbRef = useRef(null);

      const copyPath = () => {{
        let path = currentPath.join('/');
        if (selectedItem) {{
          path = [...currentPath, selectedItem.name].join('/');
        }}
        navigator.clipboard.writeText(path).then(() => {{
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        }});
      }};

      const navigateTo = (index) => {{
        setCurrentPath(currentPath.slice(0, index + 1));
      }};

      useEffect(() => {{
        if (breadcrumbRef.current) {{
          breadcrumbRef.current.scrollLeft = breadcrumbRef.current.scrollWidth;
        }}
      }}, [currentPath, selectedItem]);

      return (
        <div className={{`sticky top-0 left-0 right-0 ${{darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-800'}} p-3 shadow-md z-50 overflow-visible`}}>
          <div className="container mx-auto max-w-5xl flex items-center justify-between">
            <div
              ref={{breadcrumbRef}}
              className="overflow-x-auto whitespace-nowrap flex items-center flex-grow mr-2"
              style={{{{ overflowX: 'auto' }}}}
            >
              <button
                onClick={{() => navigateTo(0)}}
                className={{`${{darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-800'}} flex items-center mr-1 flex-shrink-0`}}
                title="Home directory"
              >
                <Home className="w-4 h-4 mr-1" />
                <span className="font-medium">{{currentPath[0]}}</span>
              </button>

              {{currentPath.length > 1 && currentPath.slice(1).map((segment, index) => (
                <React.Fragment key={{index}}>
                  <ChevronRight className={{`w-4 h-4 mx-1 ${{darkMode ? 'text-gray-500' : 'text-gray-400'}} flex-shrink-0`}} />
                  <button
                    onClick={{() => navigateTo(index + 1)}}
                    className={{`${{
                      index === currentPath.length - 2 && !selectedItem ?
                        (darkMode ? 'text-yellow-300 font-medium' : 'text-blue-700 font-medium') :
                        (darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-800')
                    }} flex-shrink-0`}}
                  >
                    {{segment}}
                  </button>
                </React.Fragment>
              ))}}

              {{selectedItem && (
                <>
                  <ChevronRight className={{`w-4 h-4 mx-1 ${{darkMode ? 'text-gray-500' : 'text-gray-400'}} flex-shrink-0`}} />
                  <span className={{`${{darkMode ? 'text-yellow-300 font-medium' : 'text-blue-700 font-medium'}} flex-shrink-0`}}>
                    {{selectedItem.name}}
                  </span>
                </>
              )}}
            </div>

            <div className="flex items-center space-x-2 flex-shrink-0">
              {{copied ? (
                <span className={{`text-xs px-2 py-1 rounded ${{darkMode ? 'bg-green-800 text-green-200' : 'bg-green-100 text-green-800'}}`}}>
                  <Check className="w-3 h-3 inline mr-1" />
                  Copied
                </span>
              ) : (
                <button
                  onClick={{copyPath}}
                  className={{`p-1 rounded ${{darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}}`}}
                  title="Copy path"
                >
                  <Copy className="w-4 h-4" />
                </button>
              )}}
            </div>
          </div>
        </div>
      );
    }};

    const DirectoryItem = ({{ name, children, level = 0, path = [] }}) => {{
      const {{
        openFolders,
        setOpenFolders,
        searchTerm,
        darkMode,
        expandAll,
        collapseAll,
        setCurrentPath,
        currentPath,
        setSelectedItem
      }} = React.useContext(AppContext);

      const folderId = path.join('/');

      const isOpen = openFolders.has(folderId);

      const isCurrentPath = currentPath.length === path.length &&
        path.every((segment, index) => segment === currentPath[index]);

      const isInCurrentPath = currentPath.length > path.length &&
        path.every((segment, index) => segment === currentPath[index]);

      const matchesSearch = searchTerm && name.toLowerCase().includes(searchTerm.toLowerCase());

      const toggleFolder = (e) => {{
        e.stopPropagation();

        const newOpenFolders = new Set(openFolders);
        if (isOpen) {{
          newOpenFolders.delete(folderId);
        }} else {{
          newOpenFolders.add(folderId);
        }}
        setOpenFolders(newOpenFolders);
      }};

      const navigateToFolder = (e) => {{
        e.stopPropagation();
        setCurrentPath(path);
        setSelectedItem(null);
      }};

      useEffect(() => {{
        if (expandAll) {{
          setOpenFolders(prev => new Set([...prev, folderId]));
        }}
      }}, [expandAll, folderId]);

      useEffect(() => {{
        if (collapseAll && folderId !== '{html.escape(root_name)}') {{
          setOpenFolders(prev => {{
            const newFolders = new Set(prev);
            newFolders.delete(folderId);
            return newFolders;
          }});
        }}
      }}, [collapseAll, folderId]);

      useEffect(() => {{
        if (searchTerm && matchesSearch) {{
          setOpenFolders(prev => new Set([...prev, folderId]));
        }}
      }}, [searchTerm, matchesSearch, folderId]);

      useEffect(() => {{
        if (isCurrentPath || isInCurrentPath) {{
          setOpenFolders(prev => new Set([...prev, folderId]));
        }}
      }}, [isCurrentPath, isInCurrentPath, folderId]);

      const indentClass = level === 0 ? '' : 'ml-4';

      const currentPathClass = isCurrentPath
        ? darkMode
          ? 'bg-blue-900 hover:bg-blue-800'
          : 'bg-blue-100 hover:bg-blue-200'
        : isInCurrentPath
          ? darkMode
            ? 'bg-blue-800/50 hover:bg-blue-800'
            : 'bg-blue-50 hover:bg-blue-100'
          : darkMode
            ? 'bg-gray-800 hover:bg-gray-700'
            : 'bg-gray-50 hover:bg-gray-100';

      const searchMatchClass = matchesSearch
        ? darkMode
          ? 'ring-1 ring-yellow-500'
          : 'ring-1 ring-yellow-300'
        : '';

      return (
        <div className={{`w-full ${{indentClass}}`}} data-folder={{folderId}}>
          <div className={{`flex items-center justify-between p-2 mb-1 rounded-lg ${{currentPathClass}} ${{searchMatchClass}}`}}>
            <div className="flex items-center flex-grow cursor-pointer" onClick={{navigateToFolder}}>
              {{isOpen
                ? <FolderOpen className={{`w-5 h-5 mr-2 ${{isCurrentPath ? (darkMode ? 'text-yellow-300' : 'text-blue-600') : darkMode ? 'text-blue-400' : 'text-blue-500'}}`}} />
                : <Folder className={{`w-5 h-5 mr-2 ${{isCurrentPath ? (darkMode ? 'text-yellow-300' : 'text-blue-600') : darkMode ? 'text-blue-400' : 'text-blue-500'}}`}} />
              }}
              <span className={{`font-medium truncate ${{isCurrentPath ? (darkMode ? 'text-yellow-300' : 'text-blue-700') : ''}}`}}>
                {{searchTerm ? highlightMatch(name, searchTerm) : name}}
              </span>
            </div>
            <button
              className={{`p-1 rounded-full ${{darkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-200'}}`}}
              onClick={{toggleFolder}}
              data-testid="folder-toggle"
            >
              {{isOpen ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}}
            </button>
          </div>

          {{isOpen && (
            <div className="py-1">
              {{children}}
            </div>
          )}}
        </div>
      );
    }};

    const FileItem = ({{ name, displayPath, path = [], level = 0 }}) => {{
      const {{
        searchTerm,
        darkMode,
        currentPath,
        setCurrentPath,
        selectedItem,
        setSelectedItem
      }} = React.useContext(AppContext);

      const matchesSearch = searchTerm && name.toLowerCase().includes(searchTerm.toLowerCase());

      const isSelected = selectedItem &&
        selectedItem.path &&
        selectedItem.path.length === path.length &&
        selectedItem.path.every((segment, index) => segment === path[index]);

      const handleFileSelect = () => {{
        setCurrentPath(path.slice(0, -1));
        setSelectedItem({{
          type: 'file',
          name,
          displayPath,
          path
        }});
      }};

      const indentClass = 'ml-4';

      const selectedClass = isSelected
        ? darkMode
          ? 'bg-blue-900 hover:bg-blue-800'
          : 'bg-blue-100 hover:bg-blue-200'
        : darkMode
          ? 'bg-gray-800 hover:bg-gray-700'
          : 'bg-white hover:bg-gray-50';

      const searchMatchClass = matchesSearch
        ? darkMode
          ? 'ring-1 ring-yellow-500'
          : 'ring-1 ring-yellow-300'
        : '';

      return (
        <div className={{`w-full ${{indentClass}}`}}>
          <div
            className={{`flex items-center p-2 rounded-lg border cursor-pointer ${{selectedClass}} ${{searchMatchClass}} ${{darkMode ? 'border-gray-700' : 'border-gray-100'}} my-1`}}
            onClick={{handleFileSelect}}
          >
            <File className={{`w-5 h-5 mr-2 ${{isSelected ? (darkMode ? 'text-yellow-300' : 'text-blue-600') : darkMode ? 'text-blue-400/70' : 'text-blue-400'}}`}} />
            <div className="min-w-0 overflow-hidden">
              <span className={{`truncate block ${{isSelected ? (darkMode ? 'text-yellow-300 font-medium' : 'text-blue-700 font-medium') : ''}}`}}>
                {{searchTerm ? highlightMatch(displayPath, searchTerm) : displayPath}}
              </span>
            </div>
          </div>
        </div>
      );
    }};

    const SearchBar = () => {{
      const {{ searchTerm, setSearchTerm, darkMode }} = React.useContext(AppContext);

      return (
        <div className="relative mb-4">
          <div className={{`flex items-center border rounded-lg overflow-hidden ${{
            darkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'
          }}`}}>
            <div className="p-2">
              <Search className={{`w-5 h-5 ${{darkMode ? 'text-gray-400' : 'text-gray-500'}}`}} />
            </div>
            <input
              type="text"
              value={{searchTerm}}
              onChange={{(e) => setSearchTerm(e.target.value)}}
              placeholder="Search files and folders..."
              className={{`flex-grow p-2 outline-none ${{
                darkMode ? 'bg-gray-700 text-white placeholder-gray-400' : 'bg-white text-gray-800 placeholder-gray-400'
              }}`}}
            />
            {{searchTerm && (
              <button
                onClick={{() => setSearchTerm('')}}
                className={{`p-2 ${{darkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-100'}}`}}
              >
                <X className={{`w-4 h-4 ${{darkMode ? 'text-gray-400' : 'text-gray-500'}}`}} />
              </button>
            )}}
          </div>
        </div>
      );
    }};

    const DirectoryViewer = () => {{
      const [openFolders, setOpenFolders] = useState(new Set(['{html.escape(root_name)}']));
      const [searchTerm, setSearchTerm] = useState('');
      const [darkMode, setDarkMode] = useState(false);

      const [currentPath, setCurrentPath] = useState(['{html.escape(root_name)}']);
      const [selectedItem, setSelectedItem] = useState(null);

      const [expandAll, setExpandAll] = useState(false);
      const [collapseAll, setCollapseAll] = useState(false);

      const handleExpandAll = () => {{
        setExpandAll(true);
        setTimeout(() => setExpandAll(false), 100);
      }};

      const handleCollapseAll = () => {{
        setCollapseAll(true);
        setTimeout(() => setCollapseAll(false), 100);
      }};

      const toggleDarkMode = () => {{
        setDarkMode(!darkMode);
      }};

      useEffect(() => {{
        if (darkMode) {{
          document.body.classList.add('dark-mode');
        }} else {{
          document.body.classList.remove('dark-mode');
        }}
      }}, [darkMode]);

      return (
        <AppContext.Provider value={{{{
          openFolders,
          setOpenFolders,
          searchTerm,
          setSearchTerm,
          darkMode,
          expandAll,
          collapseAll,
          currentPath,
          setCurrentPath,
          selectedItem,
          setSelectedItem
        }}}}>
          <div className={{`min-h-screen ${{darkMode ? 'bg-gray-900 text-gray-100' : 'bg-gray-50 text-gray-900'}}`}}>
            <style>{{`
              body.dark-mode {{
                background-color: rgb(17, 24, 39);
                color: rgb(243, 244, 246);
              }}
              .overflow-x-auto {{
                overflow-x: auto;
                white-space: nowrap;
              }}
            `}}</style>

            <Breadcrumbs />

            <div className="container mx-auto max-w-5xl p-4">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6">
                <div>
                  <h1 className="text-xl font-bold flex items-center">
                    <FolderOpen className={{`w-6 h-6 mr-2 ${{darkMode ? 'text-blue-400' : 'text-blue-500'}}`}} />
                    Directory Structure: {html.escape(root_name)}
                  </h1>
                  <p className={{`mt-1 text-sm ${{darkMode ? 'text-gray-400' : 'text-gray-500'}}`}}>
                    Explore and navigate through the directory structure
                  </p>
                </div>

                <div className="flex mt-4 sm:mt-0 space-x-2">
                  <button
                    onClick={{handleExpandAll}}
                    className={{`flex items-center px-3 py-1.5 text-sm rounded-md ${{
                      darkMode ? 'bg-gray-800 hover:bg-gray-700 text-blue-400' : 'bg-blue-100 hover:bg-blue-200 text-blue-700'
                    }}`}}
                  >
                    <Maximize2 className="w-4 h-4 mr-1" />
                    <span className="hidden sm:inline">Expand All</span>
                  </button>
                  <button
                    onClick={{handleCollapseAll}}
                    className={{`flex items-center px-3 py-1.5 text-sm rounded-md ${{
                      darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-gray-200 hover:bg-gray-300'
                    }}`}}
                  >
                    <Minimize2 className="w-4 h-4 mr-1" />
                    <span className="hidden sm:inline">Collapse All</span>
                  </button>
                  <button
                    onClick={{toggleDarkMode}}
                    className={{`px-3 py-1.5 text-sm rounded-md ${{
                      darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-gray-200 hover:bg-gray-300'
                    }}`}}
                  >
                    {{darkMode ? 'Light' : 'Dark'}}
                  </button>
                </div>
              </div>

              <SearchBar />

              <div className={{`p-4 rounded-lg shadow ${{darkMode ? 'bg-gray-800' : 'bg-white'}}`}}>
                <DirectoryItem
                  name="{html.escape(root_name)}"
                  level={{0}}
                  path={{["{html.escape(root_name)}"]}}
                >
    {_build_structure_jsx(structure, 1, root_name if show_full_path else "")}
                </DirectoryItem>

                {{/* Empty state for search */}}
                {{searchTerm && openFolders.size <= 1 && (
                  <div className="py-8 text-center">
                    <Info className={{`w-12 h-12 mx-auto mb-3 ${{darkMode ? 'text-gray-600' : 'text-gray-300'}}`}} />
                    <h3 className="text-lg font-medium">No matching files or folders</h3>
                    <p className={{`mt-1 text-sm ${{darkMode ? 'text-gray-400' : 'text-gray-500'}}`}}>
                      Try a different search term or check spelling
                    </p>
                  </div>
                )}}
              </div>
            </div>
          </div>
        </AppContext.Provider>
      );
    }};

    export default DirectoryViewer;
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_template)
    except Exception as e:
        logger.error(f"Error exporting to React component: {e}")
        raise
