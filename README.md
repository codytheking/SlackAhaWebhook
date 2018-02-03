# Slack Aha! Webhook

Python script for checking upcoming deadlines on Aha! and posting them in a channel on Slack.

### Usage

Run the script with either zero or one additional argument(s). The argument should be an integer that indicates fetching all dealines that are less than or equal to that number of days away. If no integer value is given, it defaults to 7.

Example: `./reminders 5`

It should work with any Python 3 version. I can't guarantee compatability with Python 2.

