# [pypi_update_strategy] PyPI Update Notification Theory
**Date**: 2026-05-19  **Type**: T1 (core theory)

## Core Theory
Update notification for Python packages has two separate goals:
1. **Retention**: Existing users know about new versions and upgrade
2. **Acquisition**: New users discover and install the package

These require DIFFERENT channels — retention = push to known users, acquisition = discovery in new contexts.

## Retention Channels (existing users)
| Channel | Reach | Friction | Cost |
|---------|-------|----------|------|
| In-tool version check banner | HIGH (every launch) | Zero (automatic) | Dev effort |
| ntfy.sh broadcast topic | MEDIUM (only subscribers) | Low | Zero |
| GitHub Releases + Watch | LOW (opted-in stargazers) | Medium (must watch) | Zero |
| Email newsletter | MEDIUM | High (signup required) | $0-$20/mo |

## Acquisition Channels (new installs)
| Channel | Reach | WTP Signal | Best For |
|---------|-------|-----------|----------|
| Show HN / r/ClaudeAI posts | HIGH | Weak | Spike installs |
| awesome-claude-code PRs | MEDIUM | Medium | Sustained passive |
| YouTube Shorts (hub-system) | HIGH | Strong | Brand + install |
| PyPI keywords/description | LOW | Weak | Long-tail SEO |
| Changelog page (SEO) | LOW | Medium | Developer search |

## Highest-ROI Pattern (validated)
In-tool update check (update-checker library) → startup banner → clear `pip install --upgrade` command.
This converts 30-50% of active users to upgrades without any email/push infrastructure.

## ntfy.sh repurpose for releases
Current: PTY idle notifications (single user).
Upgrade: make topic hub-moat-jayone a PUBLIC channel → post release notes on each PyPI publish.
Users who subscribed to ntfy.sh for hub-system automatically receive release notifications.
