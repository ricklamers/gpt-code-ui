# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install Node.js for building the frontend
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install gcc and python3-dev for building psutil
RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install frontend dependencies and build the frontend
WORKDIR /app/frontend
RUN npm ci && \
    VITE_APP_VERSION=$(cat package.json | grep version | head -1 | awk -F: '{ print $2 }' | sed 's/[",]//g' | tr -d '[[:space:]]') && \
    export VITE_APP_VERSION=$VITE_APP_VERSION && \
    npm run build

# Move the frontend build to the expected location
RUN cp -r /app/frontend/dist/* /app/gpt_code_ui/webapp/static/

# Move back to the /app directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install the gpt-code-ui package
RUN pip install .

# Make port 8080 and 5010 available to the world outside this container
EXPOSE 8080 5010

# Define environment variable
ENV FLASK_APP=gpt_code_ui.webapp.main
ENV PYTHONPATH=/app

# Run the main.py script when the container launches
CMD ["python", "gpt_code_ui/main.py"]