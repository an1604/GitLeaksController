FROM ubuntu:latest

# CKV_DOCKER_5: Using update instruction alone
RUN apt-get update

# Installing packages without cleanup
RUN apt-get install -y python3 python3-pip curl

# Adding credentials directly in Dockerfile - security leak
ENV AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
ENV AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Working as root - not creating a user
# CKV_DOCKER_3: Ensure that a user for the container has been created
WORKDIR /app

COPY . .

# Exposing multiple ports including sensitive ones
EXPOSE 22 80 443 8080

# Running as root by default
CMD ["python3", "app.py"] 