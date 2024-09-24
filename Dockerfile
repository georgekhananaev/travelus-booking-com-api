# Use the official Python image with version 3.12.4 slim
FROM python:3.12.6-slim

# Metadata as labels
LABEL maintainer="George Khananaev"
LABEL description="FastAPI server with dark-themed docs, authentication, MongoDB and Redis, caching."

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y gcc build-essential && \
    apt-get clean

# Remove bson (if previously installed) to avoid conflicts
RUN pip uninstall -y bson

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ensure motor and pymongo compatibility
RUN pip install --upgrade motor pymongo

# Copy the rest of the application code into the container
COPY . .

## Clean up apt caches to reduce image size
#RUN apt-get remove --purge -y gcc build-essential && \
#    apt-get autoremove -y && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*

# Expose the port on which the app will run
EXPOSE 8088

# Command to run the app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8088", "--workers", "4"]
