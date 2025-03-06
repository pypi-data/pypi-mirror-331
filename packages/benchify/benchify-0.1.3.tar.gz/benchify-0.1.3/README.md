# Benchify CLI

A powerful command-line interface for [Benchify](https://benchify.com/) that helps you manage and tweak your Benchify configuration.

## Installation

```bash
pip install benchify
```

## Commands

### Authentication

```bash
# Log in to Benchify
benchify auth login

# Log out from Benchify
benchify auth logout
```

### Configuration

```bash
# Initialize Benchify configuration for your repository
benchify init

# Test your Benchify configuration
benchify test
```

## Getting Started

1. **Login**: Start by authenticating with Benchify:
   ```bash
   benchify login
   ```
   This will open a browser window for authentication. Follow the prompts to complete the login process.

2. **Initialize Configuration**: Set up Benchify in your repository:
   ```bash
   benchify init
   ```
   This command will:
   - Verify your repository details
   - Generate and download the necessary configuration files
   - Create a `.benchify` directory with your project configuration

3. **Test Configuration**: Validate your setup:
   ```bash
   benchify test
   ```
   This will run a test of your configuration and provide detailed feedback.

## Configuration Structure

After initialization, Benchify creates a `.benchify` directory containing:
- `benchify.json`: Main configuration file
- `benchify.sh`: Main script for setting up the environment
- Environment configuration files
- Language configuration files

## Feedback and Debugging

The CLI provides rich feedback with:
- Detailed error messages
- Test results summary
- Debug information when available
- Color-coded output for better visibility

