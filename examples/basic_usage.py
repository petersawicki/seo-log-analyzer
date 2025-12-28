"""
Basic usage example for SEO Log Analyzer

This script demonstrates how to use the SEO Log Analyzer to:
1. Parse Apache log files
2. Analyze crawl budget and bot behavior
3. Generate visualizations

Author: Valde Media
"""

import sys
import os

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import ApacheLogParser
from src.analyzer import SEOLogAnalyzer
from src.visualizer import SEOLogVisualizer


def main():
    """
    Main function demonstrating SEO log analysis workflow
    """
    
    print("=" * 60)
    print("SEO LOG ANALYZER - Basic Usage Example")
    print("=" * 60)
    
    # Step 1: Parse log file
    print("\n[1/4] Parsing log file...")
    parser = ApacheLogParser()
    
    # Replace this path with your actual log file
    # For testing, you can use a sample log or limit the number of lines
    log_file_path = 'data/sample_logs/access.log'
    
    # Check if file exists
    if not os.path.exists(log_file_path):
        print(f"\nError: Log file not found at {log_file_path}")
        print("\nTo use this example:")
        print("1. Place your Apache access.log file in data/sample_logs/")
        print("2. Or modify the log_file_path variable to point to your log file")
        print("\nExample log line format (Apache Combined):")
        print('127.0.0.1 - - [01/Dec/2024:10:30:45 +0000] "GET /page.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (compatible; Googlebot/2.1)"')
        return
    
    # Parse the file (limit to first 10000 lines for quick testing)
    df = parser.parse_file(log_file_path, limit=10000)
    
    print(f"✓ Parsed {len(df)} log entries")
    
    if df.empty:
        print("\nNo data parsed. Please check your log file format.")
        return
    
    # Step 2: Initialize analyzer
    print("\n[2/4] Analyzing crawl data...")
    analyzer = SEOLogAnalyzer(df)
    
    # Get crawl budget summary
    print("\n" + "=" * 60)
    print("CRAWL BUDGET SUMMARY")
    print("=" * 60)
    summary = analyzer.crawl_budget_summary()
    for key, value in summary.items():
        if key != 'date_range':
            print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print(f"\nDate Range:")
            print(f"  Start: {value['start']}")
            print(f"  End: {value['end']}")
    
    # Bot distribution
    print("\n" + "=" * 60)
    print("BOT DISTRIBUTION")
    print("=" * 60)
    bot_dist = analyzer.bot_distribution()
    if not bot_dist.empty:
        print(bot_dist.to_string())
    else:
        print("No bot traffic detected")
    
    # Googlebot analysis
    print("\n" + "=" * 60)
    print("GOOGLEBOT ANALYSIS")
    print("=" * 60)
    googlebot = analyzer.googlebot_analysis()
    if 'error' not in googlebot:
        print(f"Total Googlebot crawls: {googlebot.get('total_crawls', 0)}")
        print(f"Average response size: {googlebot.get('avg_response_size', 0)} bytes")
        print(f"\nMobile vs Desktop:")
        for bot_type, count in googlebot.get('mobile_vs_desktop', {}).items():
            print(f"  {bot_type}: {count}")
        print(f"\nTop 5 crawled paths:")
        for path, count in list(googlebot.get('top_crawled_paths', {}).items())[:5]:
            print(f"  {path}: {count} crawls")
    else:
        print(googlebot['error'])
    
    # Crawl traps
    print("\n" + "=" * 60)
    print("POTENTIAL CRAWL TRAPS (>100 crawls)")
    print("=" * 60)
    traps = analyzer.identify_crawl_traps(threshold=100)
    if traps:
        for i, trap in enumerate(traps[:10], 1):
            print(f"{i}. {trap}")
    else:
        print("No crawl traps detected")
    
    # Error pages
    print("\n" + "=" * 60)
    print("404 ERRORS")
    print("=" * 60)
    errors = analyzer.get_error_pages(404)
    if not errors.empty:
        print(errors.head(10).to_string())
    else:
        print("No 404 errors found")
    
    # Step 3: Generate visualizations
    print("\n[3/4] Generating visualizations...")
    viz = SEOLogVisualizer(analyzer)
    
    # Create output directory if it doesn't exist
    output_dir = 'data/output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate individual charts
    try:
        print("  - Bot distribution chart...")
        viz.plot_bot_distribution(save_path=f'{output_dir}/bot_distribution.png')
        
        print("  - Hourly crawl pattern...")
        viz.plot_hourly_crawl_pattern(save_path=f'{output_dir}/hourly_pattern.png')
        
        print("  - Status codes heatmap...")
        viz.plot_status_codes_heatmap(save_path=f'{output_dir}/status_codes.png')
        
        print("  - Crawl timeline...")
        viz.plot_crawl_timeline(save_path=f'{output_dir}/crawl_timeline.png')
        
        print("  - Top crawled paths...")
        viz.plot_top_crawled_paths(save_path=f'{output_dir}/top_paths.png')
        
        print("  - Comprehensive dashboard...")
        viz.create_dashboard(save_path=f'{output_dir}/dashboard.png')
        
        print(f"\n✓ All visualizations saved to {output_dir}/")
        
    except Exception as e:
        print(f"\nNote: Visualization generation skipped ({str(e)})")
        print("This is normal if running in a headless environment")
    
    # Step 4: Export data
    print("\n[4/4] Exporting analysis data...")
    
    # Export bot distribution to CSV
    if not bot_dist.empty:
        bot_dist.to_csv(f'{output_dir}/bot_distribution.csv')
        print(f"✓ Bot distribution exported to {output_dir}/bot_distribution.csv")
    
    # Export daily report
    daily_report = analyzer.daily_crawl_report()
    if not daily_report.empty:
        daily_report.to_csv(f'{output_dir}/daily_report.csv')
        print(f"✓ Daily report exported to {output_dir}/daily_report.csv")
    
    # Export crawl frequency
    path_freq = analyzer.crawl_frequency_by_path()
    if not path_freq.empty:
        path_freq.to_csv(f'{output_dir}/path_frequency.csv')
        print(f"✓ Path frequency exported to {output_dir}/path_frequency.csv")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\nResults saved to: {output_dir}/")
    print("\nNext steps:")
    print("1. Review the generated charts and CSV files")
    print("2. Identify pages wasting crawl budget")
    print("3. Fix errors (404s, 500s) found by bots")
    print("4. Optimize slow pages to improve crawl efficiency")
    print("\nFor more advanced usage, check the documentation in README.md")


if __name__ == "__main__":
    main()
