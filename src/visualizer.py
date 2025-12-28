"""
SEO Log Visualizer
Creates visualizations for SEO log analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional
import warnings
warnings.filterwarnings('ignore')


class SEOLogVisualizer:
    """
    Create visualizations for SEO log analysis
    """
    
    def __init__(self, analyzer):
        """
        Args:
            analyzer: SEOLogAnalyzer instance
        """
        self.analyzer = analyzer
        sns.set_style('whitegrid')
        plt.rcParams['figure.facecolor'] = 'white'
    
    def plot_bot_distribution(self, save_path: Optional[str] = None):
        """
        Pie chart of bot traffic distribution
        
        Args:
            save_path: Optional path to save the figure
        """
        bot_dist = self.analyzer.bot_distribution()
        
        if bot_dist.empty:
            print("No bot data available for visualization")
            return
        
        plt.figure(figsize=(10, 6))
        colors = sns.color_palette('Set2', len(bot_dist))
        
        plt.pie(bot_dist['total_requests'], 
                labels=bot_dist.index, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors)
        
        plt.title('Bot Traffic Distribution', fontsize=16, fontweight='bold', pad=20)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_hourly_crawl_pattern(self, bot_type: str = 'googlebot', save_path: Optional[str] = None):
        """
        Bar chart of crawl activity by hour
        
        Args:
            bot_type: Bot type to analyze
            save_path: Optional path to save the figure
        """
        googlebot_data = self.analyzer.googlebot_analysis()
        
        if 'error' in googlebot_data:
            print(f"Error: {googlebot_data['error']}")
            return
        
        hourly_data = pd.Series(googlebot_data['crawl_by_hour']).sort_index()
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(hourly_data.index, hourly_data.values, color='#4285f4', edgecolor='#1a73e8', linewidth=1.5)
        
        plt.title(f'{bot_type.title()} Hourly Crawl Pattern', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Hour of Day', fontsize=12)
        plt.ylabel('Number of Requests', fontsize=12)
        plt.xticks(range(24), fontsize=10)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_status_codes_heatmap(self, save_path: Optional[str] = None):
        """
        Heatmap of status codes by bot type
        
        Args:
            save_path: Optional path to save the figure
        """
        status_df = self.analyzer.status_code_analysis()
        
        if status_df.empty:
            print("No status code data available for visualization")
            return
        
        # Select only the summary columns
        summary_cols = ['2xx', '3xx', '4xx', '5xx']
        plot_data = status_df[[col for col in summary_cols if col in status_df.columns]]
        
        if plot_data.empty:
            print("No status code summary data available")
            return
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(plot_data, 
                    annot=True, 
                    fmt='g', 
                    cmap='RdYlGn_r',
                    cbar_kws={'label': 'Number of Requests'},
                    linewidths=0.5)
        
        plt.title('HTTP Status Codes by Bot Type', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Bot Type', fontsize=12)
        plt.xlabel('Status Code Category', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_crawl_timeline(self, bot_type: Optional[str] = None, save_path: Optional[str] = None):
        """
        Line chart of crawl activity over time
        
        Args:
            bot_type: Optional bot type to filter
            save_path: Optional path to save the figure
        """
        time_series = self.analyzer.time_series_analysis(bot_type)
        
        if time_series.empty:
            print("No time series data available for visualization")
            return
        
        plt.figure(figsize=(14, 6))
        
        plt.plot(time_series.index, time_series['total_crawls'], 
                marker='o', linewidth=2.5, markersize=6, 
                label='Total Crawls', color='#4285f4')
        
        plt.plot(time_series.index, time_series['successful_crawls'], 
                marker='s', linewidth=2.5, markersize=6, 
                label='Successful Crawls', color='#34a853', alpha=0.8)
        
        title = f'Crawl Activity Over Time'
        if bot_type:
            title += f' - {bot_type.title()}'
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Requests', fontsize=12)
        plt.legend(fontsize=11, loc='best')
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_top_crawled_paths(self, top_n: int = 20, save_path: Optional[str] = None):
        """
        Horizontal bar chart of most crawled paths
        
        Args:
            top_n: Number of top paths to display
            save_path: Optional path to save the figure
        """
        path_freq = self.analyzer.crawl_frequency_by_path()
        
        if path_freq.empty:
            print("No path frequency data available")
            return
        
        top_paths = path_freq.head(top_n).sort_values('crawl_count')
        
        plt.figure(figsize=(12, 10))
        
        colors = ['#34a853' if rate > 90 else '#fbbc04' if rate > 70 else '#ea4335' 
                 for rate in top_paths['success_rate']]
        
        plt.barh(range(len(top_paths)), top_paths['crawl_count'], color=colors, edgecolor='black', linewidth=0.5)
        
        # Truncate long paths for readability
        labels = [path[:50] + '...' if len(path) > 50 else path for path in top_paths.index]
        plt.yticks(range(len(top_paths)), labels, fontsize=9)
        
        plt.xlabel('Number of Crawls', fontsize=12)
        plt.title(f'Top {top_n} Most Crawled Paths', fontsize=16, fontweight='bold', pad=20)
        plt.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add legend for colors
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#34a853', label='Success Rate > 90%'),
            Patch(facecolor='#fbbc04', label='Success Rate 70-90%'),
            Patch(facecolor='#ea4335', label='Success Rate < 70%')
        ]
        plt.legend(handles=legend_elements, loc='lower right', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_error_distribution(self, save_path: Optional[str] = None):
        """
        Pie chart showing distribution of error types
        
        Args:
            save_path: Optional path to save the figure
        """
        status_df = self.analyzer.status_code_analysis()
        
        if status_df.empty:
            print("No error data available")
            return
        
        error_cols = ['4xx', '5xx']
        error_data = status_df[[col for col in error_cols if col in status_df.columns]].sum()
        
        if error_data.sum() == 0:
            print("No errors found in the data")
            return
        
        plt.figure(figsize=(10, 6))
        colors = ['#fbbc04', '#ea4335']
        
        plt.pie(error_data.values, 
                labels=error_data.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                explode=[0.05] * len(error_data))
        
        plt.title('Error Distribution (4xx vs 5xx)', fontsize=16, fontweight='bold', pad=20)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def create_dashboard(self, save_path: Optional[str] = None):
        """
        Create a comprehensive dashboard with multiple visualizations
        
        Args:
            save_path: Optional path to save the figure
        """
        fig = plt.figure(figsize=(18, 12))
        
        # Bot Distribution
        ax1 = plt.subplot(2, 3, 1)
        bot_dist = self.analyzer.bot_distribution()
        if not bot_dist.empty:
            bot_dist['total_requests'].plot(kind='pie', autopct='%1.1f%%', ax=ax1)
            ax1.set_title('Bot Distribution', fontweight='bold')
            ax1.set_ylabel('')
        
        # Hourly Pattern
        ax2 = plt.subplot(2, 3, 2)
        googlebot_data = self.analyzer.googlebot_analysis()
        if 'crawl_by_hour' in googlebot_data:
            hourly = pd.Series(googlebot_data['crawl_by_hour']).sort_index()
            hourly.plot(kind='bar', ax=ax2, color='#4285f4')
            ax2.set_title('Hourly Crawl Pattern', fontweight='bold')
            ax2.set_xlabel('Hour')
            ax2.set_ylabel('Requests')
        
        # Timeline
        ax3 = plt.subplot(2, 3, 3)
        time_series = self.analyzer.time_series_analysis()
        if not time_series.empty:
            time_series['total_crawls'].plot(ax=ax3, marker='o', color='#4285f4')
            ax3.set_title('Crawl Timeline', fontweight='bold')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Crawls')
        
        # Status Codes
        ax4 = plt.subplot(2, 3, 4)
        status_df = self.analyzer.status_code_analysis()
        if not status_df.empty and '2xx' in status_df.columns:
            status_summary = status_df[['2xx', '3xx', '4xx', '5xx']].sum()
            status_summary.plot(kind='bar', ax=ax4, color=['#34a853', '#4285f4', '#fbbc04', '#ea4335'])
            ax4.set_title('Status Code Summary', fontweight='bold')
            ax4.set_xlabel('Status Type')
            ax4.set_ylabel('Count')
        
        # Top Paths
        ax5 = plt.subplot(2, 3, 5)
        path_freq = self.analyzer.crawl_frequency_by_path()
        if not path_freq.empty:
            top_10 = path_freq.head(10).sort_values('crawl_count')
            top_10['crawl_count'].plot(kind='barh', ax=ax5, color='#34a853')
            ax5.set_title('Top 10 Crawled Paths', fontweight='bold')
            ax5.set_xlabel('Crawls')
        
        # Summary Stats
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        summary = self.analyzer.crawl_budget_summary()
        summary_text = f"""
        CRAWL BUDGET SUMMARY
        
        Total Requests: {summary['total_requests']:,}
        Bot Requests: {summary['bot_requests']:,}
        Bot %: {summary['bot_percentage']}%
        
        Unique Bots: {summary['unique_bots']}
        Unique Pages: {summary['unique_pages_crawled']:,}
        
        Date Range:
        {summary['date_range']['start']} to
        {summary['date_range']['end']}
        """
        ax6.text(0.1, 0.5, summary_text, fontsize=11, family='monospace', 
                verticalalignment='center')
        
        plt.suptitle('SEO Log Analysis Dashboard', fontsize=18, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
