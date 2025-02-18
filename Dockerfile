# Start from a base image with Python
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
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome manually and create a symlink
RUN wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome.deb || apt-get -fy install \
    && rm google-chrome.deb \
    && ln -s /usr/bin/google-chrome-stable /usr/bin/google-chrome

# Install ChromeDriver manually
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+') \
    && CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) \
    && wget -q https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Set environment variables
ENV PATH="/usr/local/bin:${PATH}"

# Set work directory
WORKDIR /app

# Copy files and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]