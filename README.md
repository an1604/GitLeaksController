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
docker run --rm -v <LOCAL_DIRECTORY> gitleaks-controller:latest --dir /code/<CHOOSE_DIRECTORY_NAME> 
```
### 2. Optional: Run Using Prebuilt Docker Image from Docker Hub

If you prefer not to build the Docker image locally, you can pull the prebuilt image from Docker Hub:

```bash
docker pull avivnat13/gitleaks-controller:latest
docker run --rm -v <LOCAL_DIRECTORY_TO_SCAN>:/code avivnat13/gitleaks-controller:latest --dir /code
```