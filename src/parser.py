"""
Apache Log Parser for SEO Analysis
Parses Apache Combined Log Format and identifies search engine bots
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class ApacheLogParser:
    """
    Parser for Apache Combined Log Format
    Designed for SEO crawl analysis
    """
    
    # Regex pattern for Apache Combined format
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d.]+) '
        r'- - '
        r'\[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d.]+" '
        r'(?P<status>\d+) '
        r'(?P<bytes>\d+|-) '
        r'"(?P<referer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )
    
    # Common SEO bots
    BOT_PATTERNS = {
        'googlebot': r'Googlebot',
        'googlebot_mobile': r'Googlebot-Mobile',
        'bingbot': r'bingbot',
        'yandex': r'YandexBot',
        'baidu': r'Baiduspider',
        'duckduckgo': r'DuckDuckBot',
        'semrush': r'SemrushBot',
        'ahrefs': r'AhrefsBot',
        'screaming_frog': r'Screaming Frog',
        'mj12bot': r'MJ12bot',
        'dotbot': r'DotBot',
        'ahrefsbot': r'AhrefsBot',
        'semrushbot': r'SemrushBot'
    }
    
    def __init__(self):
        """Initialize parser"""
        self.parsed_logs = []
    
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        Parse single log line into structured dict
        
        Args:
            line: Raw log line string
            
        Returns:
            Dict with parsed fields or None if parsing fails
        """
        match = self.LOG_PATTERN.match(line)
        
        if not match:
            return None
        
        data = match.groupdict()
        
        # Convert timestamp to datetime
        try:
            data['timestamp'] = datetime.strptime(
                data['timestamp'], 
                '%d/%b/%Y:%H:%M:%S %z'
            )
        except ValueError:
            # Fallback for logs without timezone
            try:
                data['timestamp'] = datetime.strptime(
                    data['timestamp'].split()[0], 
                    '%d/%b/%Y:%H:%M:%S'
                )
            except ValueError:
                return None
        
        # Convert status and bytes to int
        data['status'] = int(data['status'])
        data['bytes'] = int(data['bytes']) if data['bytes'] != '-' else 0
        
        # Identify bot type
        data['bot_type'] = self._identify_bot(data['user_agent'])
        data['is_bot'] = data['bot_type'] is not None
        
        return data
    
    def _identify_bot(self, user_agent: str) -> Optional[str]:
        """
        Identify bot type from user agent string
        
        Args:
            user_agent: User agent string
            
        Returns:
            Bot type name or None if not a bot
        """
        for bot_name, pattern in self.BOT_PATTERNS.items():
            if re.search(pattern, user_agent, re.IGNORECASE):
                return bot_name
        return None
    
    def parse_file(self, filepath: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Parse entire log file into pandas DataFrame
        
        Args:
            filepath: Path to log file
            limit: Optional limit on number of lines to parse
            
        Returns:
            DataFrame with parsed log data
        """
        parsed_data = []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                
                parsed = self.parse_line(line.strip())
                if parsed:
                    parsed_data.append(parsed)
        
        df = pd.DataFrame(parsed_data)
        
        # Add useful SEO columns
        if not df.empty:
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['is_html'] = df['path'].str.endswith(('.html', '.htm', '/'))
            df['file_extension'] = df['path'].str.extract(r'\.([a-z0-9]+)$')[0]
            
        return df
    
    def parse_string(self, log_string: str) -> pd.DataFrame:
        """
        Parse log data from string (useful for testing)
        
        Args:
            log_string: Multi-line string of log entries
            
        Returns:
            DataFrame with parsed log data
        """
        parsed_data = []
        
        for line in log_string.strip().split('\n'):
            parsed = self.parse_line(line.strip())
            if parsed:
                parsed_data.append(parsed)
        
        df = pd.DataFrame(parsed_data)
        
        # Add useful SEO columns
        if not df.empty:
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['is_html'] = df['path'].str.endswith(('.html', '.htm', '/'))
            df['file_extension'] = df['path'].str.extract(r'\.([a-z0-9]+)$')[0]
            
        return df
