"""
Documentation retrieval logic for Rust documentation
"""

import os
import re
import shutil
import subprocess
import tempfile
import json
from typing import List, Optional

from rich.console import Console

console = Console(stderr=True)


class DocRetriever:
    """Responsible for retrieving Rust documentation"""

    def run_rustdoc(self, working_dir: str, *args: str) -> str:
        """
        This method is retained for compatibility but is no longer the primary approach.
        We now use locally installed documentation rather than running rustdoc directly.
        """
        console.log(f"Note: run_rustdoc called but we now prefer using locally installed documentation")
        
        # For standard library items, redirect to the proper method
        if args and self.is_std_lib(args[-1]):
            return self.get_std_lib_doc(args[-1])
            
        # For other cases, return a helpful message suggesting the new approach
        path = args[-1] if args else "unknown_path"
        return (
            f"Documentation for {path} wasn't found using the local documentation approach.\n"
            f"Try running `cargo doc` in your project directory first, then provide the project_path parameter."
        )

    def _try_rustup_doc(self, path: str) -> str:
        """Try to use rustup doc as a fallback for standard library"""
        try:
            # Run rustup doc with --path option to get the HTML file path
            cmd = ["rustup", "doc", "--std", "--path", path]
            console.log(f"Trying rustup fallback: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # The output of this command is the HTML file path
            html_file_path = result.stdout.strip()

            if not os.path.exists(html_file_path):
                return f"Rustup found documentation but the file doesn't exist: {html_file_path}"

            # Read and process the HTML to extract documentation
            with open(html_file_path, "r") as f:
                html_content = f.read()

            # Very simple HTML to text conversion - in practice you might want
            # to use a proper HTML parser like BeautifulSoup
            text_content = self._extract_text_from_html(html_content)

            return text_content
        except Exception as e:
            return f"Failed to get documentation using rustup: {str(e)}"

    def _extract_text_from_html(self, html: str) -> str:
        """Extract documentation text from HTML content using advanced parsing"""
        # Install BeautifulSoup if not already installed
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # Install BeautifulSoup at runtime if needed
            try:
                import subprocess

                subprocess.run(
                    ["pip", "install", "beautifulsoup4", "--quiet"],
                    check=True,
                    capture_output=True,
                )
                from bs4 import BeautifulSoup
            except Exception as e:
                console.log(
                    f"Warning: BeautifulSoup not available. Using simple parsing: {str(e)}"
                )
                return self._extract_text_from_html_simple(html)

        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            # Initialize result sections
            result_sections = []

            # Extract the main content
            main_content = soup.find(id="main-content")
            if not main_content:
                return self._extract_text_from_html_simple(html)

            # Extract module/item title
            title_element = main_content.find(class_="fqn")
            if title_element:
                result_sections.append(f"# {title_element.get_text().strip()}")

            # Extract summary (first paragraph of docblock)
            docblock = main_content.find(class_="docblock")
            if docblock:
                summary_paragraphs = []
                for p in docblock.find_all("p", recursive=False):
                    summary_paragraphs.append(p.get_text().strip())

                if summary_paragraphs:
                    result_sections.append("\n".join(summary_paragraphs))

            # Extract type declaration for structs/enums/traits
            type_decl = main_content.find(class_="type-decl")
            if type_decl:
                result_sections.append(f"```rust\n{type_decl.get_text().strip()}\n```")

            # Extract method signatures
            method_section = None
            impl_items = main_content.find(class_="impl-items")
            if impl_items:
                methods = []
                for method in impl_items.find_all(class_="method"):
                    method_text = method.get_text().strip()
                    # Remove [src] from the end of the line
                    method_text = re.sub(r"\[src\]\s*$", "", method_text)
                    methods.append(method_text)

                if methods:
                    method_section = (
                        "## Methods\n\n```rust\n" + "\n".join(methods) + "\n```"
                    )
                    result_sections.append(method_section)

            # Extract enum variants
            variants = []
            for variant_elem in main_content.find_all(
                lambda tag: tag.name == "section"
                and tag.get("id")
                and tag.get("id").startswith("variant.")
            ):
                variant_name = variant_elem.get("id").replace("variant.", "")
                variant_text = variant_elem.get_text().strip()
                # Remove [src] from the end of the line
                variant_text = re.sub(r"\[src\]\s*$", "", variant_text)
                variants.append(f"- **{variant_name}**: {variant_text}")

            if variants:
                result_sections.append("## Variants\n\n" + "\n".join(variants))

            # Extract tables of related items (modules, structs, traits, etc.)
            section_tables = {}
            for section_header in main_content.find_all(class_="section-header"):
                section_id = section_header.get("id")
                if not section_id:
                    continue

                section_title = section_header.get_text().strip()

                # Look for a table after the section header
                table = section_header.find_next("table")
                if not table:
                    continue

                rows = []
                for row in table.find_all("tr"):
                    cells = [
                        cell.get_text().strip() for cell in row.find_all(["th", "td"])
                    ]
                    if cells:
                        rows.append(" | ".join(cells))

                if rows:
                    section_tables[section_id] = (
                        f"## {section_title.title()}\n\n" + "\n".join(rows)
                    )

            # Add section tables in a specific order
            for section_id in [
                "modules",
                "traits",
                "types",
                "constants",
                "structs",
                "enums",
                "functions",
                "macros",
            ]:
                if section_id in section_tables:
                    result_sections.append(section_tables[section_id])

            # Extract code examples
            examples = []
            for example in main_content.find_all(class_="example-wrap"):
                example_text = example.get_text().strip()
                if example_text:
                    examples.append(f"```rust\n{example_text}\n```")

            if examples:
                result_sections.append("## Examples\n\n" + "\n\n".join(examples))

            # Join all sections with spacing
            result = "\n\n".join(result_sections)

            # Clean up spacing and formatting
            result = re.sub(r"\n{3,}", "\n\n", result)  # Remove excessive newlines
            result = re.sub(r"\[src\]", "", result)  # Remove [src] links

            return result.strip()

        except Exception as e:
            console.log(f"Error parsing HTML with BeautifulSoup: {str(e)}")
            # Fall back to simple parsing if anything goes wrong
            return self._extract_text_from_html_simple(html)

    def _extract_text_from_html_simple(self, html: str) -> str:
        """Simple fallback method for HTML extraction when BeautifulSoup is not available"""
        # Remove all script tags and their contents
        html = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)

        # Remove all style tags and their contents
        html = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL)

        # Extract main content from the HTML - focus on the main documentation content
        # This targets the rustdoc main content container
        main_content_match = re.search(
            r'<div id="main-content">(.*?)<div class="bottom-row">', html, re.DOTALL
        )
        if main_content_match:
            html = main_content_match.group(1)

        # Handle different heading levels for a better structured text output
        html = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n\n# \1\n\n", html)
        html = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n\n## \1\n\n", html)
        html = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n\n### \1\n\n", html)
        html = re.sub(r"<h4[^>]*>(.*?)</h4>", r"\n\n#### \1\n\n", html)

        # Format code blocks nicely
        html = re.sub(
            r"<pre[^>]*>(.*?)</pre>", r"\n```rust\n\1\n```\n", html, flags=re.DOTALL
        )

        # Handle common inline elements
        html = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", html)
        html = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", html)
        html = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", html)

        # Convert line breaks to actual newlines
        html = html.replace("<br>", "\n")
        html = html.replace("<br/>", "\n")
        html = html.replace("<br />", "\n")

        # Handle list items
        html = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", html, flags=re.DOTALL)

        # Remove all remaining HTML tags
        text = re.sub(r"<[^>]*>", "", html)

        # Decode HTML entities
        text = self._decode_html_entities(text)

        # Clean up whitespace (but keep paragraph structure)
        text = re.sub(r" +", " ", text)  # Collapse multiple spaces to one
        text = re.sub(r"\n{3,}", "\n\n", text)  # Max two consecutive newlines

        return text.strip()

    def _decode_html_entities(self, text: str) -> str:
        """Decode common HTML entities"""
        entities = {
            # Basic HTML entities
            "&lt;": "<",
            "&gt;": ">",
            "&amp;": "&",
            "&quot;": '"',
            "&apos;": "'",
            "&nbsp;": " ",
            # Additional common entities
            "&ndash;": "–",
            "&mdash;": "—",
            "&lsquo;": "'",
            "&rsquo;": "'",
            "&ldquo;": """,
            "&rdquo;": """,
            "&bull;": "•",
            "&hellip;": "…",
            "&copy;": "©",
            "&reg;": "®",
            "&trade;": "™",
            # Technical symbols often found in Rust docs
            "&rArr;": "→",
            "&rarr;": "→",
            "&larr;": "←",
            "&uarr;": "↑",
            "&darr;": "↓",
        }

        # Apply all entity replacements
        for entity, char in entities.items():
            text = text.replace(entity, char)

        # Also handle numeric entities
        text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
        text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)

        return text

    def create_temp_project(self, crate_path: str) -> str:
        """Create temporary directory for documentation queries"""
        # Create a simple temporary directory for working with documentation
        temp_dir = tempfile.mkdtemp(prefix="rustdoc-mcp-")
        console.log(f"Created temp directory for {crate_path}: {temp_dir}")
        return temp_dir

    def is_std_lib(self, path: str) -> bool:
        """Check if path refers to standard library"""
        std_lib_prefixes = ["std::", "core::", "alloc::", "test::", "proc_macro::"]
        return any(path.startswith(prefix) for prefix in std_lib_prefixes)

    def _extract_crate_name(self, path: str) -> str:
        """Extract crate name from path like crate::module::item"""
        return path.split("::")[0]

    def find_cargo_project(self, path: str) -> Optional[str]:
        """Find nearest directory with Cargo.toml"""
        if os.path.isfile(path):
            path = os.path.dirname(path)

        current = os.path.abspath(path)
        while current != os.path.dirname(current):  # Stop at root
            if os.path.exists(os.path.join(current, "Cargo.toml")):
                return current
            current = os.path.dirname(current)
        return None

    def get_std_lib_doc(self, path: str, target: Optional[str] = None) -> str:
        """Get documentation for standard library item using rustup doc"""
        try:
            # For standard library, use rustup doc --path directly
            cmd = ["rustup", "doc", "--std", "--path", path]
            console.log(f"Getting standard library documentation using: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            html_file_path = result.stdout.strip()
            
            if not os.path.exists(html_file_path):
                return f"Standard library documentation path found but file doesn't exist: {html_file_path}"
            
            console.log(f"Found standard library documentation at: {html_file_path}")
            
            # Read and process the HTML
            with open(html_file_path, "r") as f:
                html_content = f.read()
            
            # Extract the content
            return self._extract_text_from_html(html_content)
        except Exception as e:
            console.log(f"Error accessing standard library documentation: {str(e)}")
            
            # Provide a helpful error message
            return (f"Could not access documentation for {path}. "
                    f"Make sure standard library documentation is installed with: rustup doc --std")

    def get_crate_doc(
        self,
        crate_name: str,
        target: Optional[str] = None,
        working_dir: Optional[str] = None,
        flags: Optional[List[str]] = None,
        project_path: Optional[str] = None,
    ) -> str:
        """Get documentation for an external crate using locally installed docs"""
        # Extract base crate and path components
        base_crate = self._extract_crate_name(crate_name)
        
        # First attempt: Try to find documentation using rustup doc --path (for both std lib and external crates)
        try:
            console.log(f"Searching for installed documentation for {crate_name}")
            # Use rustup to find the documentation path
            cmd = ["rustup", "doc", "--path", crate_name]
            console.log(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                # Success! Read the HTML file and extract content
                html_file_path = result.stdout.strip()
                console.log(f"Found documentation at {html_file_path}")
                
                if os.path.exists(html_file_path):
                    with open(html_file_path, "r") as f:
                        html_content = f.read()
                    return self._extract_text_from_html(html_content)
                else:
                    console.log(f"Warning: Found path {html_file_path} but file doesn't exist")
        except Exception as e:
            console.log(f"Rustup doc --path approach failed: {str(e)}")
            
        # Second attempt: Look for local crate docs in the cargo doc output directory
        try:
            # Get the Rust sysroot to locate documentation
            sysroot_result = subprocess.run(
                ["rustc", "--print", "sysroot"], 
                capture_output=True, 
                text=True,
                check=True
            )
            sysroot = sysroot_result.stdout.strip()
            
            # Check for cargo doc directory (where cargo-installed crates have docs)
            cargo_doc_path = self._find_cargo_doc_dir(project_path)
            if cargo_doc_path and os.path.exists(cargo_doc_path):
                console.log(f"Found cargo doc directory at {cargo_doc_path}")
                
                # The path structure follows the structure described in the "roc" tool
                if "::" in crate_name:
                    # For paths like serde::ser::Serializer
                    parts = crate_name.split("::")
                    base_crate = parts[0]
                    modules = parts[1:]
                    
                    # List of possible files to check for the item
                    possible_paths = []
                    
                    # Handle base crate path (e.g., serde/index.html)
                    if len(modules) == 0:
                        possible_paths.append(os.path.join(cargo_doc_path, base_crate, "index.html"))
                        # Also check with underscores instead of hyphens
                        possible_paths.append(os.path.join(cargo_doc_path, base_crate.replace("-", "_"), "index.html"))
                    
                    # Handle module path (e.g., serde/ser/index.html)
                    elif len(modules) == 1 and not modules[0][0].isupper():
                        module_path = modules[0] 
                        possible_paths.append(os.path.join(cargo_doc_path, base_crate, module_path, "index.html"))
                        # With underscores
                        possible_paths.append(os.path.join(cargo_doc_path, base_crate.replace("-", "_"), module_path, "index.html"))
                    
                    # Handle specific item path (e.g. serde/ser/trait.Serialize.html)
                    else:
                        # Last part is the item name
                        item_name = modules[-1]
                        # Earlier parts form the module path
                        module_path = "/".join(modules[:-1]) if len(modules) > 1 else ""
                        
                        # Check various item types (struct, enum, trait, etc.)
                        for item_type in ["trait", "struct", "enum", "fn", "mod", "module", "constant", "macro"]:
                            if module_path:
                                path = os.path.join(
                                    cargo_doc_path, 
                                    base_crate, 
                                    module_path, 
                                    f"{item_type}.{item_name}.html"
                                )
                                possible_paths.append(path)
                                # Also try with underscores
                                path_with_underscores = os.path.join(
                                    cargo_doc_path, 
                                    base_crate.replace("-", "_"), 
                                    module_path, 
                                    f"{item_type}.{item_name}.html"
                                )
                                possible_paths.append(path_with_underscores)
                            else:
                                path = os.path.join(
                                    cargo_doc_path, 
                                    base_crate, 
                                    f"{item_type}.{item_name}.html"
                                )
                                possible_paths.append(path)
                                # With underscores
                                path_with_underscores = os.path.join(
                                    cargo_doc_path, 
                                    base_crate.replace("-", "_"), 
                                    f"{item_type}.{item_name}.html"
                                )
                                possible_paths.append(path_with_underscores)
                else:
                    # Just the crate itself (e.g., "serde")
                    possible_paths = [
                        os.path.join(cargo_doc_path, crate_name, "index.html"),
                        # Try with underscores instead of hyphens
                        os.path.join(cargo_doc_path, crate_name.replace("-", "_"), "index.html")
                    ]
                    
                # Try each possible path
                for path in possible_paths:
                    if os.path.exists(path):
                        console.log(f"Found documentation at {path}")
                        with open(path, "r") as f:
                            html_content = f.read()
                        return self._extract_text_from_html(html_content)
                
                # If we get here, we didn't find the documentation
                # Let's list available crates to provide suggestions
                available_crates = []
                try:
                    for item in os.listdir(cargo_doc_path):
                        if os.path.isdir(os.path.join(cargo_doc_path, item)):
                            available_crates.append(item)
                            
                    if available_crates:
                        console.log(f"Available crates: {', '.join(available_crates)}")
                        return (f"Could not find documentation for '{crate_name}', "
                                f"but these crates are available: {', '.join(sorted(available_crates))}")
                except Exception as e:
                    console.log(f"Error listing available crates: {str(e)}")
        except Exception as e:
            console.log(f"Error searching local documentation: {str(e)}")
        
        # If we reach here, we couldn't find the documentation anywhere
        console.log(f"Could not find documentation for {crate_name}")
        
        # Get a list of available crates that the user could try instead
        if project_path:
            # Try to run cargo tree to get a list of dependencies
            try:
                result = subprocess.run(
                    ["cargo", "tree"], 
                    cwd=project_path, 
                    capture_output=True, 
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    tree_output = result.stdout.strip()
                    crate_list = []
                    for line in tree_output.split("\n"):
                        # Extract crate names from cargo tree output
                        if line.strip() and " " in line:
                            parts = line.strip().split(" ")
                            if len(parts) >= 2 and not parts[0].startswith("│") and not parts[0].startswith("├"):
                                crate_list.append(parts[0])
                    
                    if crate_list:
                        return (f"Could not find documentation for '{crate_name}'. "
                                f"Available crates in this project: {', '.join(sorted(set(crate_list)))}.\n\n"
                                f"Try running `cargo doc` in the project directory first, or provide a different project path.")
            except Exception as e:
                console.log(f"Error getting crate list: {str(e)}")
                
        # Generic error message with suggestions
        suggestions = [
            f"Documentation for '{crate_name}' was not found in the local filesystem.",
            f"To generate documentation locally, run:",
            f"  1. `cargo new temp-project`",
            f"  2. Add `{crate_name} = \"*\"` to Cargo.toml",
            f"  3. `cargo doc`",
            f"  4. Then run this command again with `--project-path temp-project`"
        ]
        
        return "\n".join(suggestions)
    
    def _find_cargo_doc_dir(self, project_path: Optional[str] = None) -> Optional[str]:
        """Find the directory where cargo stores documentation for installed crates"""
        try:
            # Build list of paths to check
            cargo_doc_paths = []
            
            # If a specific project path is provided, prioritize it
            if project_path:
                # Check for target/doc in the provided project path
                project_doc_path = os.path.join(project_path, "target", "doc")
                cargo_doc_paths.append(project_doc_path)
                
                # Also try to find Cargo.toml and use its parent directory
                try:
                    for root, dirs, files in os.walk(project_path):
                        if "Cargo.toml" in files:
                            cargo_toml_dir = root
                            cargo_doc_paths.append(os.path.join(cargo_toml_dir, "target", "doc"))
                        # Don't go too deep
                        if len(cargo_doc_paths) >= 3 or root.count(os.sep) - project_path.count(os.sep) > 3:
                            break
                except Exception as e:
                    console.log(f"Error walking project directory: {str(e)}")
            
            # Add standard locations
            home_dir = os.path.expanduser("~")
            # Standard locations
            cargo_doc_paths.extend([
                # Standard cargo doc location
                os.path.join(home_dir, ".cargo", "doc"),
                # Check target/doc in current directory (local project)
                os.path.join(os.getcwd(), "target", "doc"),
            ])
            
            # Try to find the actual location by running cargo doc
            try:
                # Run cargo doc and check where it puts the documentation
                cmd = ["cargo", "doc", "--no-deps", "--quiet"]
                # Use project path if provided for cargo doc
                cwd = project_path if project_path else os.getcwd()
                subprocess.run(cmd, cwd=cwd, capture_output=True, check=True)
                # The docs should be in target/doc
                local_doc_path = os.path.join(cwd, "target", "doc")
                if os.path.exists(local_doc_path):
                    cargo_doc_paths.insert(0, local_doc_path)  # Prioritize this
            except Exception:
                pass  # Ignore failure to run cargo doc
                
            # Also check if cargo tells us its root directory and look for docs there
            try:
                cmd = ["cargo", "locate-project", "--workspace"]
                # Use project path if provided for locate-project
                cwd = project_path if project_path else os.getcwd()
                result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
                if result.stdout:
                    try:
                        cargo_path = json.loads(result.stdout)["root"]
                        cargo_dir = os.path.dirname(cargo_path)
                        cargo_doc_paths.append(os.path.join(cargo_dir, "target", "doc"))
                    except (json.JSONDecodeError, KeyError):
                        pass  # Ignore if response isn't valid JSON or doesn't have 'root'
            except Exception:
                pass  # Ignore failure to run cargo locate-project
            
            # Remove duplicates from the path list while preserving order
            unique_paths = []
            for path in cargo_doc_paths:
                if path not in unique_paths:
                    unique_paths.append(path)
            cargo_doc_paths = unique_paths
            
            # Check each potential path
            for path in cargo_doc_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    console.log(f"Found cargo doc directory at {path}")
                    return path
                    
            # Try one more approach: use rustup to find the documentation root
            try:
                cmd = ["rustup", "doc", "--path"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    doc_path = os.path.dirname(result.stdout.strip())
                    if os.path.exists(doc_path):
                        console.log(f"Found documentation root via rustup at {doc_path}")
                        return doc_path
            except Exception:
                pass  # Ignore failure to run rustup doc
                
            # If we get here, we couldn't find the cargo doc directory
            return None
            
        except Exception as e:
            console.log(f"Error finding cargo doc directory: {str(e)}")
            return None

    def get_local_doc(
        self,
        path: str,
        target: Optional[str] = None,
        working_dir: Optional[str] = None,
        flags: Optional[List[str]] = None,
    ) -> str:
        """Get documentation for local project item by finding and parsing local docs"""
        if not working_dir:
            working_dir = self.find_cargo_project(path)
            if not working_dir:
                return "Could not find Cargo.toml for path"
    
        # Look for existing documentation in the project
        doc_dir = os.path.join(working_dir, "target", "doc")
        
        console.log(f"Looking for local documentation in {doc_dir}")
        
        # Check if documentation exists
        if not os.path.exists(doc_dir):
            return (f"Documentation not found in {doc_dir}.\n" 
                    f"Run `cargo doc` in {working_dir} to generate documentation first.")
        
        # Extract the file path from the absolute path
        rel_path = os.path.relpath(path, working_dir)
        
        # Try to find the right documentation file
        # This is complex because the path between source code and documentation
        # can have different structures
        
        # First try: direct path mapping
        possible_paths = []
        
        # For a path like src/main.rs, look for doc/crate_name/main.html
        crate_name = os.path.basename(working_dir)
        file_name = os.path.basename(path)
        base_name = os.path.splitext(file_name)[0]
        
        # If it's a module, look for the index.html file
        if base_name == "mod" or base_name == "lib":
            # For src/module/mod.rs, look for doc/crate_name/module/index.html
            module_path = os.path.dirname(rel_path)
            if module_path.startswith("src/"):
                module_path = module_path[4:]  # Remove src/ prefix
            possible_paths.append(os.path.join(doc_dir, crate_name, module_path, "index.html"))
        else:
            # For regular files like src/foo.rs, look for different variations
            for item_type in ["fn", "struct", "enum", "trait", "mod", "constant", "macro"]:
                possible_paths.append(os.path.join(doc_dir, crate_name, f"{item_type}.{base_name}.html"))
        
        # Try each path
        for possible_path in possible_paths:
            if os.path.exists(possible_path):
                console.log(f"Found documentation at: {possible_path}")
                with open(possible_path, "r") as f:
                    html_content = f.read()
                return self._extract_text_from_html(html_content)
        
        # If specific documentation file not found but doc directory exists,
        # suggest browsing the documentation directory
        return (f"Could not find specific documentation for {path}.\n"
                f"Browse all generated documentation in {doc_dir}")

    def cleanup_temp_dirs(self, temp_dirs: List[str]) -> None:
        """Remove all temporary directories"""
        for dir_path in temp_dirs:
            try:
                shutil.rmtree(dir_path)
                console.log(f"Cleaned up temp directory: {dir_path}")
            except Exception as e:
                console.log(f"Error cleaning up {dir_path}: {e}")
