# Start from a base image with Python 3.10
FROM python:3.10

# Install system dependencies required for Chrome & ChromeDriver
RUN echo "Step 1: Installing system dependencies..." \
    && apt-get update && apt-get install -y \
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

# Download and install Google Chrome 133
RUN echo "Step 2: Downloading Chrome 133..." \
    && wget -q -O chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.98/linux64/chrome-linux64.zip" \
    && echo "Step 3: Extracting Chrome 133..." \
    && unzip chrome-linux64.zip \
    && echo "Step 4: Moving Chrome to /opt/google/chrome..." \
    && mv chrome-linux64 /opt/google/chrome \
    && echo "Step 5: Creating symlink for Google Chrome..." \
    && ln -s /opt/google/chrome/chrome /usr/bin/google-chrome \
    && rm chrome-linux64.zip \
    && echo "Step 6: Verifying Chrome installation..." \
    && ls -l /opt/google/chrome \
    && ls -l /usr/bin/google-chrome

# Debugging: Verify Chrome installation
RUN echo "Step 7: Checking Chrome version..." \
    && which google-chrome \
    && google-chrome --version

# Download and install ChromeDriver 133 (matching Chrome 133)
RUN echo "Step 8: Downloading ChromeDriver 133..." \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.98/linux64/chromedriver-linux64.zip" \
    && echo "Step 9: Extracting ChromeDriver 133..." \
    && unzip chromedriver-linux64.zip \
    && echo "Step 10: Moving ChromeDriver to /usr/local/bin..." \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64 \
    && echo "Step 11: Verifying ChromeDriver installation..." \
    && ls -l /usr/local/bin/chromedriver

# Debugging: Verify ChromeDriver installation
RUN echo "Step 12: Checking ChromeDriver version..." \
    && which chromedriver \
    && chromedriver --version

# Update PATH environment variable (if needed)
ENV PATH="/usr/local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN echo "Step 13: Installing Python dependencies..." \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Start the FastAPI server using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
