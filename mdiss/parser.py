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

    def _clean_status(self, status: str) -> str:
        """
        Clean status string by removing emojis and normalizing.
        
        Args:
            status: Status string to clean
            
        Returns:
            Cleaned status string
        """
        if not status:
            return ""
            
        # Remove emojis and extra whitespace
        status = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]', '', status)
        status = status.strip()
        
        # Normalize common status values
        status_map = {
            '❌ Failed': 'Failed',
            '✅ Passed': 'Passed',
            '⚠️ Warning': 'Warning',
            '⏱️ Timeout': 'Timeout'
        }
        
        return status_map.get(status, status)

    def _parse_metadata(self, metadata_text: str) -> Dict[str, str]:
        """
        Parse metadata from markdown text.
        
        Args:
            metadata_text: Metadata text in markdown format (list items with **key:** value)
            
        Returns:
            Dictionary of metadata key-value pairs
        """
        metadata = {}
        if not metadata_text:
            return metadata
            
        # Match lines with **key:** value format
        pattern = r'\*\*([^:]+):\*\*\s*([^\n]+)'
        
        for match in re.finditer(pattern, metadata_text):
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key and value:
                metadata[key] = value
                
        return metadata

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a markdown file and extract code blocks and commands.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of dictionaries containing parsed commands and metadata
            
        Raises:
            FileNotFoundError: If the specified file does not exist
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            content = path.read_text(encoding='utf-8')
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
        
    def get_statistics(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics about the commands.
        
        Args:
            commands: List of command dictionaries
            
        Returns:
            Dictionary with statistics
        """
        if not commands:
            return {
                'total_commands': 0,
                'failed_commands': 0,
                'success_rate': 1.0,
                'error_codes': {},
                'command_types': {}
            }
            
        total = len(commands)
        failed = sum(1 for cmd in commands if cmd.get('exit_code', 0) != 0)
        success_rate = (total - failed) / total if total > 0 else 1.0
        
        error_codes = {}
        command_types = {}
        
        for cmd in commands:
            # Count error codes
            error_code = cmd.get('exit_code', 0)
            error_codes[error_code] = error_codes.get(error_code, 0) + 1
            
            # Count command types from metadata if available
            cmd_type = cmd.get('metadata', {}).get('command_type', 'unknown')
            command_types[cmd_type] = command_types.get(cmd_type, 0) + 1
        
        return {
            'total_commands': total,
            'failed_commands': failed,
            'success_rate': success_rate,
            'error_codes': error_codes,
            'command_types': command_types
        }
