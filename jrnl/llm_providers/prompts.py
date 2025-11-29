"""LLM prompt templates."""

COMPRESS_COMMIT_PROMPT = """You are helping a developer track their work for daily standups.

Given this git commit information:

COMMIT MESSAGE:
{commit_message}

COMMIT DIFF:
{commit_diff}

Compress this into a single concise paragraph (max 300 chars) that describes what work was completed. Focus on WHAT was done, not HOW. Use past tense. This will be used in a standup summary.

Examples:
- "Fixed authentication bug in user login flow"
- "Added dark mode toggle to settings page"
- "Refactored database connection handling"
- "Updated API documentation for new endpoints"

Your response:"""

GENERATE_DAILY_PROMPT = """You are helping a developer prepare for their daily standup meeting.

Generate a standup summary from the following work logs covering the past {days} day(s):

{logs}

Create a compact paragraph (3-5 sentences) covering:
1. What was completed (synthesize related items)
2. What's planned next (infer from recent work)
3. Any obstacles or blockers (mention if none)

Keep it professional but conversational. Use past tense for completed work.

Your standup summary:"""
