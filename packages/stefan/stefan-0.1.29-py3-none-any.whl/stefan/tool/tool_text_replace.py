
import os
from typing import Any, Dict

from stefan.execution_context import ExecutionContext
from stefan.tool.tool_definition import ToolDefinition
from stefan.utils.multiline import multiline

class TextReplaceToolDefinition(ToolDefinition):
    name: str = "text_replace"

    description: str = multiline("""
        Performs a precise replacement of a given text snippet in a specified file.
                                 
        The tool will:
        1. Read the file contents.
        2. Search for `old_text` within the file.
        3. If found, replace the first occurrence of `old_text` with `new_text` (only one occurrence).
        4. Write the modified content back to the file.
        5. Return a success message if successful, or indicate that the old_text was not found.
                                 
        Should be used when you need to replace only a specific text in a file or when file is too long to be copy pasted.
        """)

    parameters: Dict[str, str] = {
        "file_path": "(required) The path to the target file.",
        "old_text": "(required) The exact substring that should be replaced.",
        "new_text": "(required) The new substring that replaces the old one.",
    }

    usage: str = multiline("""
        <text_replace>
            <file_path>...</file_path>
            <old_text>...</old_text>
            <new_text>...</new_text>
        </write_to_file>
        """)

    def execute_tool(self, args: Dict[str, Any], context: ExecutionContext) -> str:
        path = args.get("file_path")
        old_text = args.get("old_text")
        new_text = args.get("new_text")

        # Check if file exists
        if not os.path.isfile(path):
            return f"Error: File does not exist at path: {path}"

        # Read the file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"

        # Locate the old_text in the file
        index = content.find(old_text)
        if index == -1:
            return f"'{old_text}' not found in the file. No changes made."

        # Replace the first occurrence of old_text with new_text
        # Since find gave us the exact start, we can do a direct substring replacement:
        new_content = content[:index] + new_text + content[index+len(old_text):]

        # Write the updated content back to the file
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            return f"Error writing updated content to file {path}: {str(e)}"

        return f"Successfully replaced '{old_text}' with '{new_text}' in {path}."