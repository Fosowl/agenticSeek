#!/bin/bash

# AgenticSeek Installation Script for Ubuntu
# This script automatically installs AgenticSeek - a fully local AI assistant
# Author: Khaled El-Slahaty
# Requirements: Ubuntu Linux, sudo privileges

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}   AgenticSeek Auto Installer   ${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Ubuntu version
check_ubuntu() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot determine OS version"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        print_error "This script is designed for Ubuntu Linux"
        exit 1
    fi
    
    print_status "Detected Ubuntu $VERSION_ID"
}

# Function to install Docker
install_docker() {
    if command_exists docker; then
        print_status "Docker is already installed"
        docker --version
    else
        print_status "Installing Docker..."
        
        # Update package index
        sudo apt-get update
        
        # Install packages to allow apt to use a repository over HTTPS
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Add Docker's official GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # Set up the repository
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Update package index again
        sudo apt-get update
        
        # Install Docker Engine, containerd, and Docker Compose
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # Add current user to docker group
        sudo usermod -aG docker $USER
        
        print_status "Docker installed successfully"
        print_warning "You may need to log out and log back in for Docker group permissions to take effect"
    fi
}

# Function to install prerequisites
install_prerequisites() {
    print_status "Installing system prerequisites..."
    
    sudo apt-get update
    sudo apt-get install -y \
        git \
        curl \
        wget \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        openssl
    
    print_status "Prerequisites installed successfully"
}

# Function to display AI provider introduction
show_provider_intro() {
    echo
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}   AI Provider Configuration    ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
    echo "AgenticSeek supports multiple AI providers. Here are your options:"
    echo
    echo -e "${GREEN}1. OpenAI${NC}"
    echo "   - Models: GPT-4, GPT-4-turbo, GPT-3.5-turbo"
    echo "   - Requires: API key from OpenAI"
    echo "   - Cost: Pay-per-use"
    echo "   - Best for: High-quality responses, reliability"
    echo
    echo -e "${GREEN}2. Anthropic Claude${NC}"
    echo "   - Models: Claude-3.5-sonnet, Claude-3-haiku"
    echo "   - Requires: API key from Anthropic"
    echo "   - Cost: Pay-per-use"
    echo "   - Best for: Thoughtful analysis, coding tasks"
    echo
    echo -e "${GREEN}3. Local Models (Ollama)${NC}"
    echo "   - Models: Llama, Mistral, CodeLlama, Deepseek-coder"
    echo "   - Requires: Ollama installation, sufficient RAM (8GB+ recommended)"
    echo "   - Cost: Free (uses your hardware)"
    echo "   - Best for: Privacy, offline use, no API costs"
    echo
    echo -e "${GREEN}4. LM Studio${NC}"
    echo "   - Local models with easy GUI management"
    echo "   - Requires: LM Studio installation"
    echo "   - Cost: Free (uses your hardware)"
    echo "   - Best for: User-friendly local model management"
    echo
    echo -e "${GREEN}5. DeepSeek${NC}"
    echo "   - Models: DeepSeek-coder, DeepSeek-chat"
    echo "   - Requires: API key from DeepSeek"
    echo "   - Cost: Very cost-effective"
    echo "   - Best for: Coding tasks, budget-friendly"
    echo
    echo -e "${GREEN}6. Google AI${NC}"
    echo "   - Models: Gemini Pro, Gemini Flash"
    echo "   - Requires: Google AI API key"
    echo "   - Cost: Competitive pricing"
    echo "   - Best for: Multimodal capabilities"
    echo
    echo -e "${GREEN}7. OpenRouter${NC}"
    echo "   - Access to multiple models (Claude, GPT, Llama, etc.)"
    echo "   - Requires: OpenRouter API key"
    echo "   - Cost: Varies by model"
    echo "   - Best for: Model flexibility, one API for many providers"
    echo
    echo -e "${GREEN}8. Together AI${NC}"
    echo "   - Open-source models (Llama, Mistral, etc.)"
    echo "   - Requires: Together AI API key"
    echo "   - Cost: Cost-effective for open models"
    echo "   - Best for: Open-source model access"
    echo
    echo -e "${GREEN}9. Multiple Providers${NC}"
    echo "   - Configure multiple providers at once"
    echo "   - Best for: Flexibility and redundancy"
    echo
}

# Function to get user input with validation
get_user_input() {
    local prompt="$1"
    local default="$2"
    local validation="$3"
    local input
    
    while true; do
        if [[ -n "$default" ]]; then
            read -p "$prompt [$default]: " input
            input=${input:-$default}
        else
            read -p "$prompt: " input
        fi
        
        # If no validation function provided, accept any non-empty input
        if [[ -z "$validation" ]] && [[ -n "$input" ]]; then
            echo "$input"
            return
        elif [[ -n "$validation" ]] && eval "$validation '$input'"; then
            echo "$input"
            return
        else
            print_error "Invalid input. Please try again."
        fi
    done
}

# Validation functions
validate_provider_choice() {
    [[ "$1" =~ ^[1-9]$ ]]
}

validate_api_key() {
    [[ -n "$1" && ${#1} -gt 10 ]]
}

validate_url() {
    [[ "$1" =~ ^https?://.+ ]]
}

validate_port() {
    [[ "$1" =~ ^[0-9]+$ ]] && [[ "$1" -ge 1 && "$1" -le 65535 ]]
}

# Function for interactive provider configuration
configure_ai_provider() {
    show_provider_intro
    
    local provider_choice
    provider_choice=$(get_user_input "Choose your AI provider (1-9)" "" "validate_provider_choice")
    
    # Initialize variables for all possible API keys
    local openai_key="optional"
    local anthropic_key="optional"  
    local deepseek_key="optional"
    local google_key="optional"
    local openrouter_key="optional"
    local together_key="optional"
    local ollama_port="11434"
    local lm_studio_port="1234"
    local custom_port="11435"
    local work_dir=""
    
    case $provider_choice in
        1)  # OpenAI
            echo
            print_status "Configuring OpenAI..."
            echo "You can get your API key from: https://platform.openai.com/api-keys"
            openai_key=$(get_user_input "Enter your OpenAI API key (or press Enter to skip)" "optional" "")
            ;;
        2)  # Anthropic
            echo
            print_status "Configuring Anthropic Claude..."
            echo "You can get your API key from: https://console.anthropic.com/"
            anthropic_key=$(get_user_input "Enter your Anthropic API key (or press Enter to skip)" "optional" "")
            ;;
        3)  # Ollama
            echo
            print_status "Configuring Ollama..."
            echo "Make sure Ollama is installed and running on your system"
            echo "Install Ollama from: https://ollama.ai/"
            echo "Popular models: llama3, mistral, codellama, deepseek-coder"
            echo "Install models with: ollama pull <model_name>"
            ollama_port=$(get_user_input "Ollama port" "11434" "validate_port")
            ;;
        4)  # LM Studio
            echo
            print_status "Configuring LM Studio..."
            echo "Make sure LM Studio is installed and running"
            echo "Download from: https://lmstudio.ai/"
            echo "Start the local server in LM Studio"
            lm_studio_port=$(get_user_input "LM Studio port" "1234" "validate_port")
            ;;
        5)  # DeepSeek
            echo
            print_status "Configuring DeepSeek..."
            echo "You can get your API key from: https://platform.deepseek.com/"
            deepseek_key=$(get_user_input "Enter your DeepSeek API key (or press Enter to skip)" "optional" "")
            ;;
        6)  # Google AI
            echo
            print_status "Configuring Google AI..."
            echo "You can get your API key from: https://makersuite.google.com/app/apikey"
            google_key=$(get_user_input "Enter your Google AI API key (or press Enter to skip)" "optional" "")
            ;;
        7)  # OpenRouter
            echo
            print_status "Configuring OpenRouter..."
            echo "You can get your API key from: https://openrouter.ai/keys"
            echo "OpenRouter provides access to many models including GPT-4, Claude, Llama, etc."
            openrouter_key=$(get_user_input "Enter your OpenRouter API key (or press Enter to skip)" "optional" "")
            ;;
        8)  # Together AI
            echo
            print_status "Configuring Together AI..."
            echo "You can get your API key from: https://api.together.xyz/settings/api-keys"
            together_key=$(get_user_input "Enter your Together AI API key (or press Enter to skip)" "optional" "")
            ;;
        9)  # Multiple providers
            echo
            print_status "Configuring Multiple Providers..."
            echo "You can configure multiple providers. Leave empty (press Enter) to skip any provider."
            echo
            echo "OpenAI (https://platform.openai.com/api-keys):"
            openai_key=$(get_user_input "OpenAI API key" "optional" "")
            echo "Anthropic (https://console.anthropic.com/):"
            anthropic_key=$(get_user_input "Anthropic API key" "optional" "")
            echo "DeepSeek (https://platform.deepseek.com/):"
            deepseek_key=$(get_user_input "DeepSeek API key" "optional" "")
            echo "Google AI (https://makersuite.google.com/app/apikey):"
            google_key=$(get_user_input "Google AI API key" "optional" "")
            echo "OpenRouter (https://openrouter.ai/keys):"
            openrouter_key=$(get_user_input "OpenRouter API key" "optional" "")
            echo "Together AI (https://api.together.xyz/settings/api-keys):"
            together_key=$(get_user_input "Together AI API key" "optional" "")
            echo "Local services:"
            ollama_port=$(get_user_input "Ollama port" "11434" "validate_port")
            lm_studio_port=$(get_user_input "LM Studio port" "1234" "validate_port")
            custom_port=$(get_user_input "Custom additional LLM port" "11435" "validate_port")
            ;;
    esac
    
    # Get work directory
    echo
    work_dir=$(get_user_input "Work directory for AgenticSeek" "$HOME/agenticseek_workspace" "")
    mkdir -p "$work_dir"
    
    # Return configuration
    echo "OPENAI_API_KEY=$openai_key"
    echo "ANTHROPIC_API_KEY=$anthropic_key"
    echo "DEEPSEEK_API_KEY=$deepseek_key"
    echo "GOOGLE_API_KEY=$google_key"
    echo "OPENROUTER_API_KEY=$openrouter_key"
    echo "TOGETHER_API_KEY=$together_key"
    echo "OLLAMA_PORT=$ollama_port"
    echo "LM_STUDIO_PORT=$lm_studio_port"
    echo "CUSTOM_ADDITIONAL_LLM_PORT=$custom_port"
    echo "WORK_DIR=$work_dir"
}

# Function to generate .env file
generate_env_file() {
    local config="$1"
    local env_file="$2"
    
    # Parse configuration
    eval "$config"
    
    print_status "Generating environment configuration..."
    
    # Generate .env file with the exact structure from AgenticSeek
    cat > "$env_file" << EOF
# AgenticSeek Configuration
# Generated by auto-installer

# Search Engine Configuration  
SEARXNG_BASE_URL="http://127.0.0.1:8080"

# Redis Configuration (Docker internal networking)
REDIS_BASE_URL="redis://redis:6379/0"

# Work Directory
WORK_DIR="$WORK_DIR"

# Local Model Ports
OLLAMA_PORT="$OLLAMA_PORT"
LM_STUDIO_PORT="$LM_STUDIO_PORT"
CUSTOM_ADDITIONAL_LLM_PORT="$CUSTOM_ADDITIONAL_LLM_PORT"

# API Keys (set to 'optional' if not configured)
OPENAI_API_KEY='$OPENAI_API_KEY'
DEEPSEEK_API_KEY='$DEEPSEEK_API_KEY'
OPENROUTER_API_KEY='$OPENROUTER_API_KEY'
TOGETHER_API_KEY='$TOGETHER_API_KEY'
GOOGLE_API_KEY='$GOOGLE_API_KEY'
ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'
EOF
    
    print_status "Environment file generated successfully!"
    
    # Show configuration summary
    echo
    echo -e "${BLUE}Configuration Summary:${NC}"
    echo "Work Directory: $WORK_DIR"
    echo "Ollama Port: $OLLAMA_PORT"
    echo "LM Studio Port: $LM_STUDIO_PORT"
    echo "Custom LLM Port: $CUSTOM_ADDITIONAL_LLM_PORT"
    echo
    echo -e "${BLUE}Configured API Keys:${NC}"
    [[ "$OPENAI_API_KEY" != "optional" ]] && echo "✓ OpenAI"
    [[ "$ANTHROPIC_API_KEY" != "optional" ]] && echo "✓ Anthropic Claude"
    [[ "$DEEPSEEK_API_KEY" != "optional" ]] && echo "✓ DeepSeek"
    [[ "$GOOGLE_API_KEY" != "optional" ]] && echo "✓ Google AI"
    [[ "$OPENROUTER_API_KEY" != "optional" ]] && echo "✓ OpenRouter"
    [[ "$TOGETHER_API_KEY" != "optional" ]] && echo "✓ Together AI"
    echo "✓ Local services (Ollama, LM Studio) - configure separately"
    echo
}

# Function to clone and setup AgenticSeek
setup_agenticseek() {
    print_status "Setting up AgenticSeek..."
    
    # Create installation directory
    INSTALL_DIR="$HOME/agenticSeek"
    
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "AgenticSeek directory already exists. Removing old installation..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone the repository
    print_status "Cloning AgenticSeek repository..."
    git clone https://github.com/Fosowl/agenticSeek.git "$INSTALL_DIR"
    
    # Navigate to the directory
    cd "$INSTALL_DIR"
    
    # Interactive AI provider configuration
    echo
    print_status "Let's configure your AI provider..."
    local config
    config=$(configure_ai_provider)
    
    # Generate .env file with user configuration
    generate_env_file "$config" "$INSTALL_DIR/.env"
    
    print_status "AgenticSeek setup completed in $INSTALL_DIR"
}

# Function to create startup script
create_startup_script() {
    print_status "Creating startup script..."
    
    cat > "$HOME/start-agenticseek.sh" << 'EOF'
#!/bin/bash

# AgenticSeek Startup Script
cd "$HOME/agenticSeek"

echo "Starting AgenticSeek services..."

# Start with Docker Compose
if [[ -f "docker-compose.yml" ]]; then
    docker compose up -d
    echo "AgenticSeek services started successfully!"
    echo "Check the logs with: docker compose logs -f"
    echo "Stop services with: docker compose down"
else
    echo "docker-compose.yml not found. Please check your installation."
fi
EOF

    chmod +x "$HOME/start-agenticseek.sh"
    print_status "Startup script created at $HOME/start-agenticseek.sh"
}

# Function to display final instructions
show_final_instructions() {
    print_header
    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Your AI provider has been configured automatically!"
    echo "   Configuration file: $HOME/agenticSeek/.env"
    echo
    echo "2. Start AgenticSeek services:"
    echo "   cd $HOME/agenticSeek"
    echo "   docker compose up -d"
    echo
    echo "3. Or use the convenient startup script:"
    echo "   $HOME/start-agenticseek.sh"
    echo
    echo "4. Access the web interface (check docker-compose.yml for the correct port):"
    echo "   http://localhost:PORT"
    echo
    echo -e "${YELLOW}Important Notes:${NC}"
    echo "- If this is your first Docker installation, you may need to log out and back in"
    echo "- Your API keys have been configured based on your choices"
    echo "- For local models (Ollama/LM Studio), make sure they're running before starting AgenticSeek"
    echo "- The work directory has been created at: $(grep "^WORK_DIR=" $HOME/agenticSeek/.env 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "Not set")"
    echo "- Redis uses Docker internal networking (redis://redis:6379/0)"
    echo "- Check the official documentation for advanced configuration options"
    echo
    echo -e "${BLUE}Useful commands:${NC}"
    echo "- View logs: docker compose logs -f"
    echo "- Stop services: docker compose down"
    echo "- Update: cd $HOME/agenticSeek && git pull"
    echo
}

# Main installation function
main() {
    print_header
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    # Check Ubuntu
    check_ubuntu
    
    # Install prerequisites
    install_prerequisites
    
    # Install Docker
    install_docker
    
    # Setup AgenticSeek
    setup_agenticseek
    
    # Create startup script
    create_startup_script
    
    # Show final instructions
    show_final_instructions
}

# Run main function
main "$@"
