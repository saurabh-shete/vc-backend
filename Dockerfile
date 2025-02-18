# Start from a base image with Python 3.10
FROM python:3.10

# Install system dependencies required for Chrome & ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    ca-certificates \
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

# Install Google Chrome version 113 (which has a matching ChromeDriver)
RUN wget -q -O google-chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_113.0.5672.24-1_amd64.deb \
    && dpkg -i google-chrome.deb || apt-get -fy install \
    && rm google-chrome.deb \
    && if [ ! -e /usr/bin/google-chrome ]; then \
    ln -s /usr/bin/google-chrome-stable /usr/bin/google-chrome; \
    fi

# (Optional Debug Step: Verify Chrome is installed)
RUN which google-chrome && google-chrome --version

# Install ChromeDriver 113 (matching Chrome 113)
RUN wget -q "https://chromedriver.storage.googleapis.com/113.0.5672.24/chromedriver_linux64.zip" \
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
