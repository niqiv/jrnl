# JRNL

JRNL is an application for a developers to keep track automatically what they have completed since the last standup. This tool helps them to communicate achievements and completed work to colleagues with the help of LLM.

Output of the application should be informative and suited for the context of the standup group. This could be tuned per organization and developer one-by-one, but also offer a standard format as a default.

User can log work with two methods: global git hooks for commit, or manual log messages. Git hooks should include information about commit message, and commit diff with appropriate context. This information should be passed through an LLM which compresses commit information to a message similar to an user message.

When user attends a daily standup they generate daily message. Standup information should be compacted paragraph of what the user has completed, what to do next, and which obstacles they have currently or are expected to face. Standup is daily at some static time as default. In our process daily is held at 10:30AM, and the user should describe what they have done since last daily. Standups are only held during workdays, not weekends. There is never two standups during a single day. In some days daily is skipped. By default, the daily description should be generated from logs since previous daily description generated. For example, if user generates a daily message on Monday, and wants to regenerate this message after some changes, the message should include logs since last generation for Friday.

User should be able to decide which LLM provider to use. Initially the application should support Anthropic API and Ollama, and later it should be possible to extend for OpenAI and Gemini API's.

## Example Usage

To log a new work manually
    jrnl new -m 'had meeding with customer about the service'
    jrnl new --message 'had meeding with customer about the service'

To log new work from git hook
    jrnl new --git --repo-path REPOPATH --commit-hash COMMITHASH

To generate a standup script, daily and standup are alias
    jrnl daily
    jrnl standup

To generate a standup script for multiple days past
    jrnl daily --days 2
    jrnl daily -d 2

To regenerate last cached daily
    jrnl daily --regenerate
    jrnl daily -r

To read all logs, or filter them by date
    jrnl logs
    jrnl logs --days 2

To list configs and to change some configurables
    jrnl config
    jrnl config set-llm-provider ollama
    jrnl config set-llm-model llama3.1:8b

To install the application, run
    ./install
To uninstall the application, run either of
    ./uninstall
    jrnl uninstall

## Technical architecture

Application itself should be very much stateless, and store configurations and stateful elements in files stored in defined directory for the application. Python3 should be used as the language. All code should be run in a virtual environment for the application, which should be initialized during install.

Application directory path is `$HOME/.jrnl`.

Logs from git and user messages are stored in sqlite database. Table for logs should include following columns:
- timestamp (UTC)
- log message
- type (manual or git-hook)
- label (git commit hash, user defined title or random hash)
Table for generated dailies should include information
- timestamp (UTC)
- daily date
- daily message

Application code structure should be as modular and as human readable as possible. Use classes to implement more complex datastructures passed between function. Separate code in following directories:
- llm_providers
- utils
- database
    - sql statements