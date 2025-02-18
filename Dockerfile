# Start from a base image with Python 3.10
FROM --platform=linux/amd64 python:3.10 AS build

# Install system dependencies required for Chrome & ChromeDriver
RUN echo "Step 1: Installing system dependencies..." \
    && apt-get update && apt-get install -y \
    unzip \
    wget \
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
    libatk-bridge2.0-0 \
    libgbm-dev \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils  \
    && rm -rf /var/lib/apt/lists/*


# Download and install Google Chrome 133
RUN echo "Step 2: Downloading Chrome 133..." \
    && wget -q -O chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.98/linux64/chrome-linux64.zip" \
    && unzip chrome-linux64.zip \
    && mkdir -p /opt/google/chrome \
    && mv chrome-linux64/* /opt/google/chrome/ \
    && ln -s /opt/google/chrome/chrome /usr/bin/google-chrome \
    && rm chrome-linux64.zip

# Verify Chrome installation
RUN google-chrome --version

# Download and install ChromeDriver 133
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.98/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

# Verify ChromeDriver installation
RUN chromedriver --version

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Start the FastAPI server using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]