FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=10000
ENV DEBUG=false
ENV LLM_PROVIDER=gemini
ENV LLM_MODEL=gemini-2.5-flash
ENV LLM_TEMPERATURE=0.1
ENV LLM_MAX_TOKENS=8192

# Expose the port the app runs on
EXPOSE 10000

# Command to run the application
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
