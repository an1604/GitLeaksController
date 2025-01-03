# Gitleaks Controller

A Python-based wrapper for [Gitleaks](https://github.com/zricethezav/gitleaks) that provides an easy way to scan
directories for sensitive information leaks. This tool supports running scans locally or within a Docker container and
provides structured outputs for easy integration with other tools.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/an1604/GitLeaksController.git
cd GitLeaksController
docker build -t gitleaks-controller:latest . 
docker run --rm -v "<LOCAL_DIRECTORY_TO_SCAN>:/code/<CHOOSE_DIRECTORY_NAME>" gitleaks-controller:latest --dir /code/<CHOOSE_DIRECTORY_NAME> 
```

### 2. Optional: Run Using Prebuilt Docker Image from Docker Hub

If you prefer not to build the Docker image locally, you can pull the prebuilt image from Docker Hub:

```bash
docker pull avivnat13/gitleaks-controller:latest
docker run --rm -v "<LOCAL_DIRECTORY_TO_SCAN>:/code/<CHOOSE_DIRECTORY_NAME>" avivnat13/gitleaks-controller:latest --dir /code/<CHOOSE_DIRECTORY_NAME>
```

## Flags and Usage

The Gitleaks Controller supports several configurable flags that allow you to customize its behavior. You can use these
flags whether running the tool locally or via Docker.

### **Available Flags**

| Flag                                | Default                                                                             | Description                                                       |
|-------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| `--dir DIRNAME`                     | Your current working directory (`C:/Users/אביב/PycharmProjects/GitLeaksController`) | Path to the directory to scan for sensitive information leaks.    |
| `--output_filename`                 | `output.json`                                                                       | Name of the file where scan results will be saved.                |
| `--show_result`, `--no-show_result` | `True`                                                                              | Print the scan results directly to the terminal after completion. |
| `--bonus`, `--no-bonus`             | `True`                                                                              | Include additional structured output using Pydantic models.       |

### **How to Use the Flags**

You can pass the flags as arguments.

#### 1. Using option 1 (cloning the repo):

```bash
docker run --rm -v "<LOCAL_DIRECTORY_TO_SCAN>:/code" gitleaks-controller:latest --dir /code --output_filename results.json --bonus --show_result
```

#### 2. Using option 2 (optional, pulling from Dockerhub):

```bash
docker run --rm -v "<LOCAL_DIRECTORY_TO_SCAN>:/code" avivnat13/gitleaks-controller:latest --dir /code --output_filename results.json --bonus --show_result
```



