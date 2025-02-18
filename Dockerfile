# Start from a base image with Python 3.10
FROM python:3.10

# Install system dependencies required for Chrome & ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    ca-certificates \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libasound2 \
    libgbm1 \
    libgtk-3-0 \
    libu2f-udev \
    xvfb \
    libvulkan1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Download and install Google Chrome 113
RUN wget -q -O chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/113.0.5672.63/linux64/chrome-linux64.zip" \
    && unzip chrome-linux64.zip \
    && mv chrome-linux64 /opt/google/chrome \
    && ln -s /opt/google/chrome/chrome /usr/bin/google-chrome \
    && rm chrome-linux64.zip

# (Optional Debug Step: Verify Chrome is installed)
RUN which google-chrome && google-chrome --version

# Download and install ChromeDriver 113 (matching Chrome 113)
RUN wget -q "https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Update PATH environment variable (if needed)
ENV PATH="/usr/local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Start the FastAPI server using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
