"""
SEO Log Analyzer
Analyzes parsed log data for SEO insights and crawl budget optimization
"""

import pandas as pd
from typing import Dict, List, Optional
from collections import Counter


class SEOLogAnalyzer:
    """
    Analyze parsed log data for SEO insights
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with parsed log DataFrame
        
        Args:
            df: DataFrame from ApacheLogParser
        """
        self.df = df
        self.bot_df = df[df['is_bot'] == True].copy() if 'is_bot' in df.columns else pd.DataFrame()
    
    def crawl_budget_summary(self) -> Dict:
        """
        High-level crawl budget metrics
        
        Returns:
            Dict with key metrics
        """
        total_requests = len(self.df)
        bot_requests = len(self.bot_df)
        
        return {
            'total_requests': total_requests,
            'bot_requests': bot_requests,
            'bot_percentage': round(bot_requests / total_requests * 100, 2) if total_requests > 0 else 0,
            'unique_bots': int(self.bot_df['bot_type'].nunique()) if not self.bot_df.empty else 0,
            'unique_pages_crawled': int(self.bot_df['path'].nunique()) if not self.bot_df.empty else 0,
            'date_range': {
                'start': str(self.df['timestamp'].min()) if not self.df.empty else None,
                'end': str(self.df['timestamp'].max()) if not self.df.empty else None
            }
        }
    
    def bot_distribution(self) -> pd.DataFrame:
        """
        Breakdown of requests by bot type
        
        Returns:
            DataFrame with bot stats
        """
        if self.bot_df.empty:
            return pd.DataFrame()
        
        bot_stats = self.bot_df.groupby('bot_type').agg({
            'path': 'count',
            'status': lambda x: (x == 200).sum(),
            'bytes': 'sum'
        }).rename(columns={
            'path': 'total_requests',
            'status': 'successful_requests',
            'bytes': 'total_bytes'
        })
        
        bot_stats['success_rate'] = round(
            bot_stats['successful_requests'] / bot_stats['total_requests'] * 100, 2
        )
        
        return bot_stats.sort_values('total_requests', ascending=False)
    
    def googlebot_analysis(self) -> Dict:
        """
        Deep dive into Googlebot behavior
        
        Returns:
            Dict with Googlebot-specific metrics
        """
        if self.bot_df.empty:
            return {'error': 'No bot activity found'}
        
        googlebot_df = self.bot_df[
            self.bot_df['bot_type'].str.contains('googlebot', na=False, case=False)
        ]
        
        if googlebot_df.empty:
            return {'error': 'No Googlebot activity found'}
        
        return {
            'total_crawls': int(len(googlebot_df)),
            'mobile_vs_desktop': googlebot_df['bot_type'].value_counts().to_dict(),
            'crawl_by_hour': googlebot_df.groupby('hour')['path'].count().to_dict(),
            'top_crawled_paths': googlebot_df['path'].value_counts().head(20).to_dict(),
            'status_codes': googlebot_df['status'].value_counts().to_dict(),
            'avg_response_size': round(googlebot_df['bytes'].mean(), 2) if len(googlebot_df) > 0 else 0
        }
    
    def status_code_analysis(self) -> pd.DataFrame:
        """
        Analyze HTTP status codes for bot traffic
        
        Returns:
            DataFrame with status code breakdown
        """
        if self.bot_df.empty:
            return pd.DataFrame()
        
        status_analysis = self.bot_df.groupby(['bot_type', 'status']).size().unstack(fill_value=0)
        
        # Add categories
        status_cols = status_analysis.columns
        status_analysis['2xx'] = status_analysis[[col for col in status_cols if 200 <= col < 300]].sum(axis=1)
        status_analysis['3xx'] = status_analysis[[col for col in status_cols if 300 <= col < 400]].sum(axis=1)
        status_analysis['4xx'] = status_analysis[[col for col in status_cols if 400 <= col < 500]].sum(axis=1)
        status_analysis['5xx'] = status_analysis[[col for col in status_cols if 500 <= col < 600]].sum(axis=1)
        
        return status_analysis
    
    def crawl_frequency_by_path(self, min_crawls: int = 5) -> pd.DataFrame:
        """
        Identify most frequently crawled paths
        
        Args:
            min_crawls: Minimum number of crawls to include
            
        Returns:
            DataFrame with path crawl frequency
        """
        if self.bot_df.empty:
            return pd.DataFrame()
        
        path_freq = self.bot_df.groupby('path').agg({
            'timestamp': 'count',
            'bot_type': lambda x: x.value_counts().index[0] if len(x) > 0 else None,
            'status': lambda x: (x == 200).sum() / len(x) * 100 if len(x) > 0 else 0
        }).rename(columns={
            'timestamp': 'crawl_count',
            'bot_type': 'primary_bot',
            'status': 'success_rate'
        })
        
        path_freq = path_freq[path_freq['crawl_count'] >= min_crawls]
        
        return path_freq.sort_values('crawl_count', ascending=False)
    
    def identify_crawl_traps(self, threshold: int = 100) -> List[str]:
        """
        Find URLs that might be crawl traps (crawled excessively)
        
        Args:
            threshold: Number of crawls to consider excessive
            
        Returns:
            List of potential crawl trap URLs
        """
        if self.bot_df.empty:
            return []
        
        crawl_counts = self.bot_df['path'].value_counts()
        traps = crawl_counts[crawl_counts > threshold].index.tolist()
        
        return traps
    
    def time_series_analysis(self, bot_type: Optional[str] = None) -> pd.DataFrame:
        """
        Crawl activity over time
        
        Args:
            bot_type: Optional filter for specific bot
            
        Returns:
            DataFrame with daily crawl counts
        """
        if self.bot_df.empty:
            return pd.DataFrame()
        
        df = self.bot_df if bot_type is None else self.bot_df[self.bot_df['bot_type'] == bot_type]
        
        if df.empty:
            return pd.DataFrame()
        
        time_series = df.groupby('date').agg({
            'path': 'count',
            'status': lambda x: (x == 200).sum()
        }).rename(columns={
            'path': 'total_crawls',
            'status': 'successful_crawls'
        })
        
        return time_series
    
    def response_time_analysis(self) -> Dict:
        """
        Analyze response times (bytes as proxy for response time)
        Note: Real response time would need to be logged separately
        
        Returns:
            Dict with response size statistics
        """
        if self.bot_df.empty:
            return {'error': 'No bot data available'}
        
        return {
            'avg_bytes': round(self.bot_df['bytes'].mean(), 2),
            'median_bytes': round(self.bot_df['bytes'].median(), 2),
            'max_bytes': int(self.bot_df['bytes'].max()),
            'min_bytes': int(self.bot_df['bytes'].min()),
            'total_bandwidth': int(self.bot_df['bytes'].sum())
        }
    
    def get_error_pages(self, status_code: int = 404) -> pd.DataFrame:
        """
        Get all pages returning specific error code
        
        Args:
            status_code: HTTP status code to filter (default 404)
            
        Returns:
            DataFrame with error pages and their crawl frequency
        """
        if self.bot_df.empty:
            return pd.DataFrame()
        
        error_df = self.bot_df[self.bot_df['status'] == status_code]
        
        if error_df.empty:
            return pd.DataFrame()
        
        error_summary = error_df.groupby('path').agg({
            'timestamp': 'count',
            'bot_type': lambda x: ', '.join(x.unique())
        }).rename(columns={
            'timestamp': 'error_count',
            'bot_type': 'bots_affected'
        }).sort_values('error_count', ascending=False)
        
        return error_summary
    
    def daily_crawl_report(self) -> pd.DataFrame:
        """
        Generate daily summary report
        
        Returns:
            DataFrame with daily metrics
        """
        if self.bot_df.empty:
            return pd.DataFrame()
        
        daily_report = self.bot_df.groupby('date').agg({
            'path': 'count',
            'status': [
                ('successful', lambda x: (x == 200).sum()),
                ('errors_4xx', lambda x: ((x >= 400) & (x < 500)).sum()),
                ('errors_5xx', lambda x: ((x >= 500) & (x < 600)).sum())
            ],
            'bot_type': lambda x: x.nunique(),
            'bytes': 'sum'
        })
        
        daily_report.columns = ['total_crawls', 'successful', 'errors_4xx', 'errors_5xx', 'unique_bots', 'total_bytes']
        
        return daily_report
