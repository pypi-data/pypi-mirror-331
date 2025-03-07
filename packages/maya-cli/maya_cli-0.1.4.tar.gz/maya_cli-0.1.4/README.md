# Maya CLI - Developer Documentation

## Overview
Maya CLI is a command-line interface (CLI) designed to assist in AI project generation, optimization, security enforcement, and best practices validation. This documentation provides a guide on how to use each CLI command effectively.

# Quick Guide to Getting Started with Maya AI

## Step 1: Installation and Setup Development Environment
To begin using Maya AI, you need to set up your development environment. Follow these steps:

1. Ensure you have Python installed (preferably Python 3.8+).
2. Install the required dependencies using pip:
   ```sh
   pip install click python-dotenv openai
   ```
3. Clone the Maya AI repository (if applicable) or set up your project directory.

## Step 2: Set Up OpenAI Key in Environment Variables
To integrate OpenAI services, you must configure your API key in an `.env` file:

1. Create a `.env` file in your project directory.
2. Use the `set_env` command to store your OpenAI API key:
   ```sh
   maya set-env OPENAI_API_KEY your_api_key_here
   ```
   This command will securely save your key in the `.env` file.

## Step 3: Create a Maya AI Project
Once the environment is set up, you can create a new AI project using the Maya CLI:

1. Run the following command to create a new project:
   ```sh
   maya create your_project_name
   ```
2. This will generate the necessary project structure for your AI application.
3. Navigate into your project directory and start developing.

## Additional Maya AI CLI Commands
- **Check Best Practices:**
  ```sh
  maya check-best-practices path_to_project
  ```
  Ensures your project follows AI development best practices.

- **Optimize a File:**
  ```sh
  maya optimize parent_folder sub_folder filename
  ```
  Automatically imports optimization scripts to improve performance.

- **Check API Security:**
  ```sh
  maya is-secured parent_folder sub_folder filename
  ```
  Runs an AI-based security check on your API implementations.

- **Check Code Ethics:**
  ```sh
  maya check-ethics parent_folder sub_folder filename
  ```
  Reviews code for efficiency, accuracy, and ethical standards.

## Installation
Before using Maya CLI, ensure that the required dependencies are installed:
```sh
pip install -r requirements.txt
```

## Commands
### 1. Create a New AI Project
#### Command:
```sh
maya create <project_name>
```
#### Description:
Creates a new AI project structure.

#### Example:
```sh
maya create my_ai_project
```

### 2. Check Best Practices
#### Command:
```sh
maya check-best-practices [folder] [filename]
```
#### Description:
Validates Python code against best practices.

#### Example:
```sh
maya check-best-practices api my_script.py
```

### 3. Set Environment Variable
#### Command:
```sh
maya set-env <key> <value>
```
#### Description:
Sets a key-value pair in the `.env` file.

#### Example:
```sh
maya set-env OPENAI_API_KEY my_api_key
```

### 4. Optimize AI Scripts
#### Command:
```sh
maya optimize [target]
```
#### Description:
Optimizes AI scripts with caching and async processing.

#### Example:
```sh
maya optimize my_project
```

### 5. Enforce API Security
#### Command:
```sh
maya isSecured <target> [filename]
```
#### Description:
Checks and enforces API security measures including authentication, encryption, and rate limiting.

#### Example:
```sh
maya isSecured api my_api.py
```

### 6. Check Code Ethics
#### Command:
```sh
maya check-ethics <target> [filename]
```
#### Description:
Validates code efficiency, accuracy, and best practices.

#### Example:
```sh
maya check-ethics my_project
```

### 7. Generate Documentation
#### Command:
```sh
maya doc <target> <filename>
```
#### Description:
Generates a `README.md` documentation for the given file.

#### Example:
```sh
maya doc api my_script.py
```

### 8. Generate Codex Report
#### Command:
```sh
maya codex <target> <filename>
```
#### Description:
Provides an in-depth analysis and recommendations for the given file.

#### Example:
```sh
maya codex ai_model model.py
```

### 9. Enforce Compliance & Regulation
#### Command:
```sh
maya regulate <target> [filename]
```
#### Description:
Ensures compliance with GDPR, CCPA, AI Act, and ISO 42001 AI governance standards.

#### Example:
```sh
maya regulate my_project
```

## Logging
Maya CLI logs all operations in `maya_cli.log`. Check this file for debugging and issue tracking.

## Contact
For support or feature requests, reach out to the development team via GitHub or email.
