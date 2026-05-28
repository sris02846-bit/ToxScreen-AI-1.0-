FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8501 8000

# Create startup script
RUN echo '#!/bin/bash\nstreamlit run app.py --server.port 8501 --server.address 0.0.0.0 &\npython3 api.py' > /app/start.sh \
    && chmod +x /app/start.sh

CMD ["/app/start.sh"]
