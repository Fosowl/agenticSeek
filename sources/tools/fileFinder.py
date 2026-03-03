import os, sys
import stat
import mimetypes
import configparser

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sources.tools.tools import Tools

class FileFinder(Tools):
    """
    A tool that finds files in the current directory and returns their information.
    """
    def __init__(self):
        super().__init__()
        self.tag = "file_finder"
        self.name = "File Finder"
        self.description = "Finds files in the current directory and returns their information."
    
    def read_file(self, file_path: str) -> str:
        """
        Reads the content of a file.
        Args:
            file_path (str): The path to the file to read
        Returns:
            str: The content of the file
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {e}"
        
    def read_arbitrary_file(self, file_path: str, file_type: str) -> str:
        """
        Reads the content of a file with arbitrary encoding.
        Args:
            file_path (str): The path to the file to read
        Returns:
            str: The content of the file in markdown format
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith(('image/', 'video/', 'audio/')):
                return "can't read file type: image, video, or audio files are not supported."
        content_raw = self.read_file(file_path)
        if "text" in file_type:
            content = content_raw
        elif "pdf" in file_type:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            content = '\n'.join([pt.extract_text() for pt in reader.pages])
        elif "binary" in file_type:
            content = content_raw.decode('utf-8', errors='replace')
        else:
            content = content_raw
        return content
    
    def get_file_info(self, file_path: str) -> str:
        """
        Gets information about a file, including its name, path, type, content, and permissions.
        Args:
            file_path (str): The path to the file
        Returns:
            str: A dictionary containing the file information
        """
        if os.path.exists(file_path):
            stats = os.stat(file_path)
            permissions = oct(stat.S_IMODE(stats.st_mode))
            file_type, _ = mimetypes.guess_type(file_path)
            file_type = file_type if file_type else "Unknown"
            content = self.read_arbitrary_file(file_path, file_type)
            
            result = {
                "filename": os.path.basename(file_path),
                "path": file_path,
                "type": file_type,
                "read": content,
                "permissions": permissions
            }
            return result
        else:
            return {"filename": file_path, "error": "File not found"}
    
    def recursive_search(self, directory_path: str, filename: str) -> str:
        """
        Recursively searches for files in a directory and its subdirectories.
        Args:
            directory_path (str): The directory to search in
            filename (str): The filename to search for
        Returns:
            str | None: The path to the file if found, None otherwise
        """
        file_path = None
        excluded_files = [".pyc", ".o", ".so", ".a", ".lib", ".dll", ".dylib", ".so", ".git"]
        for root, dirs, files in os.walk(directory_path):
            for f in files:
                if f is None:
                    continue
                if any(excluded_file in f for excluded_file in excluded_files):
                    continue
                if filename.strip() in f.strip():
                    file_path = os.path.join(root, f)
                    return file_path
        return None
        

    def execute(self, blocks: list, safety:bool = False) -> str:
        """
        Executes the file finding operation for given filenames.
        Args:
            blocks (list): List of filenames to search for
        Returns:
            str: Results of the file search
        """
        if not blocks or not isinstance(blocks, list):
            return "Error: No valid filenames provided"

        output = ""
        for block in blocks:
            filename = self.get_parameter_value(block, "name")
            action = self.get_parameter_value(block, "action")
            if filename is None:
                output = "Error: No filename provided\n"
                return output
            if action is None:
                action = "info"
            print("File finder: recursive search started...")
            file_path = self.recursive_search(self.work_dir, filename)
            if file_path is None:
                output = f"File: {filename} - not found\n"
                continue
            result = self.get_file_info(file_path)
            if "error" in result:
                output += f"File: {result['filename']} - {result['error']}\n"
            else:
                if action == "read":
                    output += "Content:\n" + result['read'] + "\n"
                else:
                    output += (f"File: {result['filename']}, "
                              f"found at {result['path']}, "
                              f"File type {result['type']}\n")
        return output.strip()

    def execution_failure_check(self, output: str) -> bool:
        """
        Checks if the file finding operation failed.
        Args:
            output (str): The output string from execute()
        Returns:
            bool: True if execution failed, False if successful
        """
        if not output:
            return True
        if "Error" in output or "not found" in output:
            return True
        return False

    def interpreter_feedback(self, output: str) -> str:
        """
        Provides feedback about the file finding operation.
        Args:
            output (str): The output string from execute()
        Returns:
            str: Feedback message for the AI
        """
        if not output:
            return "No output generated from file finder tool"
        
        feedback = "File Finder Results:\n"
        
        if "Error" in output or "not found" in output:
            feedback += f"Failed to process: {output}\n"
        else:
            feedback += f"Successfully found: {output}\n"
        return feedback.strip()

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tool = FileFinder()
    result = tool.execute(["""
action=read
name=tools.py
"""], False)
    print("Execution result:")
    print(result)
    print("\nFailure check:", tool.execution_failure_check(result))
    print("\nFeedback:")
    print(tool.interpreter_feedback(result))