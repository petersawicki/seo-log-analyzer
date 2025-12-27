# SEO Log Analyzer

Python tool for analyzing server log files to optimize crawl budget and identify technical SEO issues.

## What it does

- **Crawl Budget Analysis**: Track how search engine bots spend their crawl budget across your site
- **Bot Identification**: Distinguish between Googlebot, Bingbot, and other crawlers (including fake bots)
- **Performance Monitoring**: Identify slow pages that waste crawl budget
- **Error Detection**: Find 404s, 500s, and redirects that bots encounter
- **Crawl Trap Detection**: Discover URLs being crawled excessively
- **Hourly Patterns**: Understand when bots are most active on your site

## Key Features

- Parses Apache/nginx log files
- Generates visual reports (charts, heatmaps, timelines)
- Exports analysis to CSV/JSON for further processing
- Identifies mobile vs desktop Googlebot activity
- Tracks crawl frequency by URL and content type

## Use Cases

- Optimize crawl budget for large websites
- Identify technical issues blocking search engines
- Monitor bot behavior after site migrations
- Validate robots.txt and crawl directives
- Prepare data-driven SEO audits

## Tech Stack

Python 3.8+, Pandas, Matplotlib, Seaborn
