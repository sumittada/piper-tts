FROM python:3.10

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for voice models if it doesn't exist
RUN mkdir -p voices


# Expose the port the app runs on
EXPOSE 5501

# Command to run the application
CMD ["python", "app.py"]