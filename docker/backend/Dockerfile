# Use an official Python image
FROM python:3.10-alpine

# Set the working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy necessary files
COPY data_processor.py location_cache.db routes.py ./

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "routes.py"]
