# Contributing to Opportunity Hunter
Thank you for your interest in contributing!

## Ways to Contribute

- Add new sources to config.yaml
- Improve keyword matching
- Bug fixes
- New notification channels (Email, Discord, Slack)
- Windows / Linux scheduler equivalent

## How to Submit a Pull Request

1. Fork the repository
2. Create a branch: git checkout -b my-improvement
3. Make your changes
4. Test: python3 opportunity_hunter.py
5. Commit and push
6. Open a Pull Request on GitHub

## Adding a New Source

Open config.yaml and add under sources:

    - name: "Site Name"
      url: "https://example.com/news"
      selector: "h2 a, h3 a, article a"
      base_url: "https://example.com"
      category: "Category Name"
      priority: HIGH

## Code Style

- Python 3.10+ compatible
- No hardcoded personal info in code
- All settings belong in config.yaml

## Reporting Issues

Open a GitHub Issue with a description and relevant log lines from data/log.txt
