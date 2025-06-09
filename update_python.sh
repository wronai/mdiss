#!/bin/bash

# Universal Python Update Script for Linux
# Supports major distributions: Ubuntu/Debian, CentOS/RHEL/Fedora, Arch, openSUSE, Alpine

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. This is generally not recommended for Python installations."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Detect Linux distribution
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [[ -f /etc/redhat-release ]]; then
        DISTRO="rhel"
    elif [[ -f /etc/debian_version ]]; then
        DISTRO="debian"
    else
        error "Cannot detect Linux distribution"
        exit 1
    fi

    log "Detected distribution: $DISTRO $VERSION"
}

# Get current Python version
get_current_python_version() {
    if command -v python3 &> /dev/null; then
        CURRENT_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log "Current Python3 version: $CURRENT_VERSION"
    else
        warning "Python3 not found"
        CURRENT_VERSION="Not installed"
    fi

    if command -v python &> /dev/null; then
        PYTHON2_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        log "Python2 version: $PYTHON2_VERSION"
    fi
}

# Update package manager
update_package_manager() {
    log "Updating package manager..."

    case $DISTRO in
        ubuntu|debian|pop|mint|kali)
            sudo apt update && sudo apt upgrade -y
            ;;
        fedora)
            sudo dnf update -y
            ;;
        centos|rhel|rocky|almalinux)
            if command -v dnf &> /dev/null; then
                sudo dnf update -y
            else
                sudo yum update -y
            fi
            ;;
        arch|manjaro|endeavouros)
            sudo pacman -Syu --noconfirm
            ;;
        opensuse*|sles)
            sudo zypper refresh && sudo zypper update -y
            ;;
        alpine)
            sudo apk update && sudo apk upgrade
            ;;
        *)
            warning "Unknown distribution. Attempting generic update..."
            ;;
    esac
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python build dependencies..."

    case $DISTRO in
        ubuntu|debian|pop|mint|kali)
            sudo apt install -y \
                build-essential \
                zlib1g-dev \
                libncurses5-dev \
                libgdbm-dev \
                libnss3-dev \
                libssl-dev \
                libsqlite3-dev \
                libreadline-dev \
                libffi-dev \
                curl \
                libbz2-dev \
                pkg-config \
                make \
                wget
            ;;
        fedora)
            sudo dnf groupinstall -y "Development Tools"
            sudo dnf install -y \
                zlib-devel \
                bzip2-devel \
                openssl-devel \
                ncurses-devel \
                sqlite-devel \
                readline-devel \
                tk-devel \
                gdbm-devel \
                libffi-devel \
                curl \
                make \
                wget
            ;;
        centos|rhel|rocky|almalinux)
            if command -v dnf &> /dev/null; then
                sudo dnf groupinstall -y "Development Tools"
                sudo dnf install -y \
                    zlib-devel \
                    bzip2-devel \
                    openssl-devel \
                    ncurses-devel \
                    sqlite-devel \
                    readline-devel \
                    tk-devel \
                    gdbm-devel \
                    libffi-devel \
                    curl \
                    make \
                    wget
            else
                sudo yum groupinstall -y "Development Tools"
                sudo yum install -y \
                    zlib-devel \
                    bzip2-devel \
                    openssl-devel \
                    ncurses-devel \
                    sqlite-devel \
                    readline-devel \
                    tk-devel \
                    gdbm-devel \
                    libffi-devel \
                    curl \
                    make \
                    wget
            fi
            ;;
        arch|manjaro|endeavouros)
            sudo pacman -S --noconfirm \
                base-devel \
                openssl \
                zlib \
                gdbm \
                ncurses \
                sqlite \
                libffi \
                tk \
                bzip2 \
                readline \
                curl \
                wget
            ;;
        opensuse*|sles)
            sudo zypper install -y \
                gcc \
                make \
                zlib-devel \
                bzip2 \
                libopenssl-devel \
                ncurses-devel \
                sqlite3-devel \
                readline-devel \
                tk-devel \
                gdbm-devel \
                libffi-devel \
                curl \
                wget
            ;;
        alpine)
            sudo apk add \
                build-base \
                zlib-dev \
                ncurses-dev \
                openssl-dev \
                sqlite-dev \
                readline-dev \
                tk-dev \
                bzip2-dev \
                libffi-dev \
                curl \
                wget \
                make
            ;;
    esac
}

# Update Python via package manager
update_python_package_manager() {
    log "Updating Python via package manager..."

    case $DISTRO in
        ubuntu|debian|pop|mint|kali)
            sudo apt install -y python3 python3-pip python3-venv python3-dev
            # Try to install latest Python if available
            sudo apt install -y python3.11 python3.11-venv python3.11-dev 2>/dev/null || true
            sudo apt install -y python3.12 python3.12-venv python3.12-dev 2>/dev/null || true
            ;;
        fedora)
            sudo dnf install -y python3 python3-pip python3-devel
            ;;
        centos|rhel|rocky|almalinux)
            if command -v dnf &> /dev/null; then
                sudo dnf install -y python3 python3-pip python3-devel
            else
                sudo yum install -y python3 python3-pip python3-devel
            fi
            ;;
        arch|manjaro|endeavouros)
            sudo pacman -S --noconfirm python python-pip
            ;;
        opensuse*|sles)
            sudo zypper install -y python3 python3-pip python3-devel
            ;;
        alpine)
            sudo apk add python3 py3-pip python3-dev
            ;;
    esac
}

# Get latest Python version from python.org
get_latest_python_version() {
    log "Checking latest Python version..."
    LATEST_VERSION=$(curl -s https://www.python.org/ftp/python/ | grep -oE 'href="[0-9]+\.[0-9]+\.[0-9]+/"' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)
    if [[ -z "$LATEST_VERSION" ]]; then
        error "Could not fetch latest Python version"
        exit 1
    fi
    log "Latest Python version: $LATEST_VERSION"
}

# Compile and install Python from source
install_python_from_source() {
    read -p "Do you want to compile Python $LATEST_VERSION from source? This will take several minutes. (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    log "Downloading and compiling Python $LATEST_VERSION from source..."

    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    # Download Python source
    wget "https://www.python.org/ftp/python/$LATEST_VERSION/Python-$LATEST_VERSION.tgz"
    tar -xzf "Python-$LATEST_VERSION.tgz"
    cd "Python-$LATEST_VERSION"

    # Configure with optimizations
    ./configure --enable-optimizations --with-ensurepip=install

    # Compile (use all available cores)
    make -j$(nproc)

    # Install
    sudo make altinstall

    # Clean up
    cd /
    rm -rf "$TEMP_DIR"

    success "Python $LATEST_VERSION installed from source"
}

# Update pip
update_pip() {
    log "Updating pip..."

    if command -v python3 &> /dev/null; then
        # Check if we're in a virtual environment
        if [[ -n "$VIRTUAL_ENV" ]]; then
            log "Virtual environment detected, updating pip without --user flag"
            python3 -m pip install --upgrade pip
        else
            python3 -m pip install --upgrade pip --user
        fi
    fi

    # Update pip for the newly installed version if available
    if [[ -n "$LATEST_VERSION" ]] && command -v "python${LATEST_VERSION%.*}" &> /dev/null; then
        if [[ -n "$VIRTUAL_ENV" ]]; then
            "python${LATEST_VERSION%.*}" -m pip install --upgrade pip
        else
            "python${LATEST_VERSION%.*}" -m pip install --upgrade pip --user
        fi
    fi
}

# Install pyenv (Python version manager)
install_pyenv() {
    read -p "Do you want to install pyenv for managing multiple Python versions? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    log "Installing pyenv..."

    # Install pyenv
    curl https://pyenv.run | bash

    # Add to shell profile
    SHELL_PROFILE=""
    if [[ -f ~/.bashrc ]]; then
        SHELL_PROFILE=~/.bashrc
    elif [[ -f ~/.zshrc ]]; then
        SHELL_PROFILE=~/.zshrc
    fi

    if [[ -n "$SHELL_PROFILE" ]]; then
        echo '' >> "$SHELL_PROFILE"
        echo '# Pyenv configuration' >> "$SHELL_PROFILE"
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> "$SHELL_PROFILE"
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> "$SHELL_PROFILE"
        echo 'eval "$(pyenv init -)"' >> "$SHELL_PROFILE"

        success "Pyenv installed. Restart your shell or run: source $SHELL_PROFILE"
        log "Then you can install any Python version with: pyenv install <version>"
    fi
}

# Summary
show_summary() {
    echo
    success "Python update process completed!"
    echo
    log "Current Python versions:"

    if command -v python3 &> /dev/null; then
        echo "  Python3: $(python3 --version)"
    fi

    if command -v python &> /dev/null; then
        echo "  Python2: $(python --version 2>&1)"
    fi

    # Check for additional Python versions
    for py_version in python3.{8..12}; do
        if command -v "$py_version" &> /dev/null; then
            echo "  $py_version: $($py_version --version)"
        fi
    done

    if command -v pip3 &> /dev/null; then
        echo "  pip3: $(pip3 --version)"
    fi

    echo
    log "Recommendations:"
    echo "  - Use 'python3' and 'pip3' commands"
    echo "  - Create virtual environments: python3 -m venv myenv"
    echo "  - Activate virtual environments: source myenv/bin/activate"
    echo "  - Install packages in virtual environments to avoid conflicts"
}

# Main execution
main() {
    log "Starting Python update process..."

    check_root
    detect_distro
    get_current_python_version

    # Ask what the user wants to do
    echo
    echo "What would you like to do?"
    echo "1) Update Python via package manager (recommended)"
    echo "2) Compile latest Python from source"
    echo "3) Both package manager update and source compilation"
    echo "4) Install pyenv only"
    echo "5) Full update (package manager + dependencies + pyenv option)"

    read -p "Enter your choice (1-5): " -n 1 -r
    echo

    case $REPLY in
        1)
            update_package_manager
            update_python_package_manager
            update_pip
            ;;
        2)
            install_dependencies
            get_latest_python_version
            install_python_from_source
            update_pip
            ;;
        3)
            update_package_manager
            install_dependencies
            update_python_package_manager
            get_latest_python_version
            install_python_from_source
            update_pip
            ;;
        4)
            install_dependencies
            install_pyenv
            ;;
        5)
            update_package_manager
            install_dependencies
            update_python_package_manager
            get_latest_python_version
            install_python_from_source
            update_pip
            install_pyenv
            ;;
        *)
            error "Invalid choice"
            exit 1
            ;;
    esac

    show_summary
}

# Run main function
main "$@"