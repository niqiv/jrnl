#!/bin/bash
#
# JRNL Uninstallation Script
#

JRNL_DIR="$HOME/.jrnl"
LOCAL_BIN="$HOME/.local/bin"

echo "JRNL Uninstaller"
echo

# Confirm uninstall
read -p "Are you sure you want to uninstall JRNL? (y/N): " confirm
if [[ ! "$confirm" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Uninstall cancelled"
    exit 0
fi

# Offer database backup
if [ -f "$JRNL_DIR/jrnl.db" ]; then
    echo
    read -p "Backup database before uninstalling? (Y/n): " backup
    backup=${backup:-Y}

    if [[ "$backup" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        BACKUP_FILE="$HOME/jrnl_backup_$(date +%Y%m%d_%H%M%S).db"
        cp "$JRNL_DIR/jrnl.db" "$BACKUP_FILE"
        echo "✓ Database backed up to $BACKUP_FILE"
    fi
fi

echo
echo "Uninstalling JRNL..."

# Remove git hooks
remove_git_hooks() {
    HOOKS_PATH=$(git config --global core.hooksPath 2>/dev/null || echo "")

    if [ -n "$HOOKS_PATH" ] && [ -f "$HOOKS_PATH/post-commit" ]; then
        echo "Removing JRNL from git hooks..."

        # Remove JRNL-specific lines
        if grep -q "JRNL" "$HOOKS_PATH/post-commit"; then
            # Create temp file without JRNL lines
            grep -v "JRNL" "$HOOKS_PATH/post-commit" | \
            grep -v "jrnl" | \
            grep -v "disown" > "$HOOKS_PATH/post-commit.tmp"

            # Check if hook is now empty (only shebang or empty)
            if [ $(wc -l < "$HOOKS_PATH/post-commit.tmp") -le 2 ]; then
                rm "$HOOKS_PATH/post-commit"
                echo "✓ Removed empty post-commit hook"
            else
                mv "$HOOKS_PATH/post-commit.tmp" "$HOOKS_PATH/post-commit"
                chmod +x "$HOOKS_PATH/post-commit"
                echo "✓ Removed JRNL from post-commit hook"
            fi

            # Clean up temp file if it exists
            rm -f "$HOOKS_PATH/post-commit.tmp"
        fi
    fi
}

# Remove JRNL directory
if [ -d "$JRNL_DIR" ]; then
    rm -rf "$JRNL_DIR"
    echo "✓ Removed $JRNL_DIR"
fi

# Remove CLI wrapper
if [ -f "$LOCAL_BIN/jrnl" ]; then
    rm "$LOCAL_BIN/jrnl"
    echo "✓ Removed $LOCAL_BIN/jrnl"
fi

# Remove git hooks
remove_git_hooks

echo
echo "============================================================"
echo "JRNL uninstalled successfully"
echo "============================================================"
echo

if [ -f "$HOME/jrnl_backup_"*.db ]; then
    echo "Your database backup(s) are in your home directory"
fi
