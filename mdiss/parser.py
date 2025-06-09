"""
Markdown Parser for extracting code blocks and commands from markdown files.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .models import FailedCommand


class MarkdownParser:
    """Parser for extracting code blocks and commands from markdown files."""
    
    def __init__(self):
        """Initialize the MarkdownParser."""
        self.code_block_pattern = re.compile(
            r'```(?:\w+)?\s*\n(.*?)```', 
            re.DOTALL | re.MULTILINE
        )
        self.command_pattern = re.compile(
            r'^\s*\$\s*(.+?)(?:\s*#|$)', 
            re.MULTILINE
        )

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a markdown file and extract code blocks and commands.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of dictionaries containing parsed commands and metadata
        """
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            return self.parse_content(content, file_path=file_path)
        except Exception as e:
            return [{
                'error': f"Failed to parse file {file_path}: {str(e)}",
                'file': file_path,
                'commands': []
            }]

    def parse_content(self, content: str, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse markdown content and extract code blocks and commands.
        
        Args:
            content: Markdown content as string
            file_path: Optional path to the source file
            
        Returns:
            List of dictionaries containing parsed commands and metadata
        """
        results = []
        
        # Find all code blocks
        for match in self.code_block_pattern.finditer(content):
            code_block = match.group(1).strip()
            if not code_block:
                continue
                
            # Get line number of the code block
            start_line = content[:match.start()].count('\n') + 1
            end_line = start_line + code_block.count('\n')
            
            # Extract commands from the code block
            commands = self._extract_commands(code_block)
            
            results.append({
                'file': file_path,
                'code_block': code_block,
                'start_line': start_line,
                'end_line': end_line,
                'commands': commands
            })
            
        return results
    
    def _extract_commands(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract shell commands from text.
        
        Args:
            text: Text to extract commands from
            
        Returns:
            List of dictionaries with command information
        """
        commands = []
        for match in self.command_pattern.finditer(text):
            command = match.group(1).strip()
            if command:
                line_number = text[:match.start()].count('\n') + 1
                commands.append({
                    'command': command,
                    'line_number': line_number,
                    'original_line': match.group(0).strip()
                })
        return commands
    
    def parse_commands(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse and extract commands from markdown content.
        
        Args:
            content: Markdown content as string
            
        Returns:
            List of dictionaries with command information
        """
        commands = []
        for block in self.parse_content(content):
            commands.extend(block['commands'])
        return commands

    def find_failed_commands(self, file_path: str) -> List[FailedCommand]:
        """
        Find and return information about failed commands in a markdown file.
        
        Note: This is a placeholder implementation. In a real scenario, you would
        need to implement actual command execution and failure detection.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of FailedCommand objects
        """
        # This is a simplified implementation
        # In a real scenario, you would execute the commands and check for failures
        return []
