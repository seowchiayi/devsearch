# Use the official Python 3.9 image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential curl sqlite3 libsqlite3-dev lzma lzma-dev

# Install Node.js (required for building Next.js projects)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Copy project files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
RUN npm install

# Build the Next.js project
RUN npm run build

# Start the server
CMD ["npm", "start"]
