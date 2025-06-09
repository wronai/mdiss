# Installation Guide

## Requirements

- Python 3.8 or higher
- pip or Poetry
- Git (for development)

## Installation Methods

### 1. From PyPI (Recommended)

```bash
pip install mdiss
```

### 2. From Source

```bash
git clone https://github.com/wronai/mdiss.git
cd mdiss
pip install -e .
```

### 3. Using Poetry

```bash
git clone https://github.com/wronai/mdiss.git
cd mdiss
poetry install
poetry shell
```

### 4. Development Installation

```bash
git clone https://github.com/wronai/mdiss.git
cd mdiss
make dev
```

## Verification

Verify the installation:

```bash
mdiss --version
```

Expected output:
```
mdiss, version 1.0.60
```

## GitHub Token Setup

mdiss requires a GitHub token to create issues. The setup command will guide you through the process:

```bash
mdiss setup
```

This will:
1. Open GitHub token generation page
2. Pre-select required permissions (`repo`, `write:issues`)
3. Guide you through token creation
4. Optionally save the token locally

### Manual Token Creation

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Select scopes:
   - `repo` - Full control of private repositories
   - `write:issues` - Write access to issues
4. Copy the generated token
5. Save it securely

### Token Storage Options

#### Option 1: File Storage (Recommended)
```bash
echo "your_token_here" > .mdiss_token
echo ".mdiss_token" >> .gitignore
```

#### Option 2: Environment Variable
```bash
export GITHUB_TOKEN="your_token_here"
```

#### Option 3: Command Line Parameter
```bash
mdiss create file.md owner repo --token your_token_here
```

## Configuration

### Global Configuration

Create a global config file at `~/.mdiss/config.toml`:

```toml
[github]
default_owner = "myorg"
default_assignees = ["dev1", "dev2"]

[analysis]
confidence_threshold = 0.8
auto_assign_by_type = true

[output]
default_format = "table"
use_colors = true
```

### Project Configuration

Create a local config file at `.mdiss.toml`:

```toml
[github]
owner = "myorg"
repo = "myproject"
milestone = 5

[labels]
priority_prefix = "priority:"
category_prefix = "type:"
```

## Troubleshooting

### Common Issues

#### 1. Command not found
```bash
# Check if mdiss is in PATH
which mdiss

# If not found, try:
python -m mdiss --version
```

#### 2. Import errors
```bash
# Reinstall with dependencies
pip install --force-reinstall mdiss
```

#### 3. Token issues
```bash
# Test token validity
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

#### 4. Permission errors
```bash
# Check token scopes
curl -H "Authorization: token YOUR_TOKEN" -I https://api.github.com/user
# Look for X-OAuth-Scopes header
```

### Platform-Specific Notes

#### Windows
```powershell
# Use PowerShell or Command Prompt
pip install mdiss

# If PATH issues:
python -m pip install mdiss
python -m mdiss --version
```

#### macOS
```bash
# May need to use pip3
pip3 install mdiss

# Or with Homebrew Python
/usr/local/bin/pip3 install mdiss
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3-pip
pip3 install mdiss

# CentOS/RHEL
sudo yum install python3-pip
pip3 install mdiss
```

### Virtual Environments

#### venv
```bash
python -m venv mdiss-env
source mdiss-env/bin/activate  # Linux/Mac
# mdiss-env\Scripts\activate  # Windows
pip install mdiss
```

#### conda
```bash
conda create -n mdiss python=3.11
conda activate mdiss
pip install mdiss
```

#### Poetry
```bash
mkdir my-project && cd my-project
poetry init
poetry add mdiss
poetry shell
```

## Uninstallation

```bash
pip uninstall mdiss
```

For development installations:
```bash
# If installed with -e
pip uninstall mdiss

# Clean Poetry environment
poetry env remove python
```

## Next Steps

After installation:

1. [Quick Start Guide](quickstart.md) - Get started quickly
2. [CLI Reference](cli.md) - Learn all commands
3. [Configuration](configuration.md) - Customize behavior
4. [Examples](examples/basic.md) - See practical examples