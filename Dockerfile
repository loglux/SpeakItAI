FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create volume directories for persistent data
VOLUME ["/app/data"]
VOLUME ["/app/audio_outputs"]

# Expose port (adjust as needed)
EXPOSE 9002

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
