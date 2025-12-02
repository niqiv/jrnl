#!/bin/bash
#
# JRNL Installation Script
#

set -e  # Exit on error

JRNL_DIR="$HOME/.jrnl"
VENV_DIR="$JRNL_DIR/venv"
LOCAL_BIN="$HOME/.local/bin"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing JRNL..."
echo

# Check Python 3.8+
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is required but not found"
        exit 1
    fi

    python_version=$(python3 --version | cut -d' ' -f2)
    major=$(echo "$python_version" | cut -d'.' -f1)
    minor=$(echo "$python_version" | cut -d'.' -f2)

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        echo "Error: Python 3.8+ required, found $python_version"
        exit 1
    fi

    echo "✓ Python $python_version found"
}

# Create directory structure
setup_directories() {
    mkdir -p "$JRNL_DIR/logs"
    mkdir -p "$LOCAL_BIN"
    echo "✓ Created directories"
}

# Create virtual environment
setup_venv() {
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r "$REPO_DIR/requirements.txt" > /dev/null 2>&1
    pip install -e "$REPO_DIR" > /dev/null 2>&1
    deactivate
    echo "✓ Virtual environment created and dependencies installed"
}

# Initialize database
init_database() {
    echo "Initializing database..."
    "$VENV_DIR/bin/python" -c "
import sys
sys.path.insert(0, '$REPO_DIR')
from jrnl.database.connection import init_database
init_database()
"
    echo "✓ Database initialized"
}

# Create default configuration
create_config() {
    if [ ! -f "$JRNL_DIR/config.json" ]; then
        echo "Creating default configuration..."
        cat > "$JRNL_DIR/config.json" << 'EOF'
{
  "active_llm_provider": "anthropic",
  "llm_providers": {
    "anthropic": {
      "api_key": "",
      "model": "claude-3-5-sonnet-20241022",
      "max_tokens_commit": 200,
      "max_tokens_daily": 500
    },
    "ollama": {
      "url": "http://localhost:11434",
      "model": "llama3.1:8b",
      "max_tokens_commit": 200,
      "max_tokens_daily": 500
    }
  },
  "git_hooks_enabled": true,
  "excluded_repos": [],
  "standup_time": "10:30",
  "timezone": "local"
}
EOF
        chmod 600 "$JRNL_DIR/config.json"
        echo "✓ Configuration created at $JRNL_DIR/config.json"
    else
        echo "✓ Configuration already exists"
    fi
}

# Install git hooks
install_git_hooks() {
    echo
    read -p "Install global git hooks to automatically track commits? (Y/n): " response
    response=${response:-Y}

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Installing git hooks..."

        # Get current global hooks path
        HOOKS_PATH=$(git config --global core.hooksPath 2>/dev/null || echo "")

        # If no hooks path set, use ~/.git-hooks
        if [ -z "$HOOKS_PATH" ]; then
            HOOKS_PATH="$HOME/.git-hooks"
            mkdir -p "$HOOKS_PATH"
            git config --global core.hooksPath "$HOOKS_PATH"
            echo "✓ Set global hooks path to $HOOKS_PATH"
        fi

        POST_COMMIT="$HOOKS_PATH/post-commit"

        # Check if post-commit exists
        if [ -f "$POST_COMMIT" ]; then
            # Check if jrnl is already in the hook
            if grep -q "JRNL" "$POST_COMMIT"; then
                echo "✓ JRNL already configured in post-commit hook"
            else
                echo "Appending JRNL to existing post-commit hook..."
                cat >> "$POST_COMMIT" << 'HOOKEOF'

# JRNL - Automatic commit logging
JRNL_CMD="$HOME/.local/bin/jrnl"
if [ -f "$JRNL_CMD" ]; then
    REPO_PATH=$(git rev-parse --show-toplevel 2>/dev/null)
    COMMIT_HASH=$(git rev-parse HEAD 2>/dev/null)
    if [ -n "$REPO_PATH" ] && [ -n "$COMMIT_HASH" ]; then
        "$JRNL_CMD" new --git \
            --repo-path "$REPO_PATH" \
            --commit-hash "$COMMIT_HASH" \
            >> "$HOME/.jrnl/logs/hook.log" 2>&1 &
        disown
    fi
fi
HOOKEOF
                echo "✓ Added JRNL to existing post-commit hook"
            fi
        else
            # Create new hook from template
            cp "$REPO_DIR/hooks/post-commit.template" "$POST_COMMIT"
            chmod +x "$POST_COMMIT"
            echo "✓ Created post-commit hook"
        fi
    else
        echo "Skipping git hooks installation"
    fi
}

# Create CLI wrapper
setup_cli() {
    echo "Setting up CLI command..."

    cat > "$LOCAL_BIN/jrnl" << CLIEOF
#!/bin/bash
exec "$VENV_DIR/bin/python" -m jrnl "\$@"
CLIEOF

    chmod +x "$LOCAL_BIN/jrnl"
    echo "✓ CLI command installed to $LOCAL_BIN/jrnl"

    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
        echo
        echo "⚠  $LOCAL_BIN is not in your PATH"
        echo
        echo "Add it by running one of the following:"
        echo

        if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
            echo "  For zsh:"
            echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
            echo "  source ~/.zshrc"
        fi

        if [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
            echo "  For bash:"
            echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
            echo "  source ~/.bashrc"
        fi

        echo
    else
        echo "✓ $LOCAL_BIN is in your PATH"
    fi
}

# Main installation flow
main() {
    check_python
    setup_directories
    setup_venv
    init_database
    create_config
    install_git_hooks
    setup_cli

    echo
    echo "============================================================"
    echo "JRNL installed successfully!"
    echo "============================================================"
    echo
    echo "Next steps:"
    echo "1. Add your API key:"
    echo "   jrnl config set anthropic api_key YOUR_KEY"
    echo
    echo "2. Test manual logging:"
    echo "   jrnl new -m 'Test message'"
    echo
    echo "3. Generate a standup:"
    echo "   jrnl daily"
    echo
    echo "Configuration file: $JRNL_DIR/config.json"
    echo
}

main
