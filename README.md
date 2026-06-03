# SaaSCompass

Affiliate marketing site for SaaS tool reviews. Built with Jekyll, hosted on GitHub Pages.

## Setup

1. Install Ruby + Bundler: `gem install bundler`
2. Install deps: `bundle install`
3. Run locally: `bundle exec jekyll serve`
4. Generate content: `python scripts/content_agent.py 3`

## Deploy

Push to `main` branch. GitHub Actions builds and deploys automatically.

## Add Affiliate Links

Edit `scripts/content_agent.py` → `AFFILIATE_LINKS` dict. Replace `YOUR_AFFILIATE_ID` with your real IDs.

## Add New Topics

Edit `TOPICS` list in `scripts/content_agent.py`.
