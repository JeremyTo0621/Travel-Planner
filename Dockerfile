# Dockerfile

FROM python:3.9-slim

# Set environment variable so pip uses a folder with enough space
ENV TMPDIR=/tmp_pip
RUN mkdir -p $TMPDIR

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"


# Copy all project files
COPY . .

# Copy start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose both ports
EXPOSE 8000 8501

# Run both apps
CMD ["bash", "/app/start.sh"]