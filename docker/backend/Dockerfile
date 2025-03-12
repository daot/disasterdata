# Use an official Python image
FROM python:3.10-alpine

# Set the working directory
WORKDIR /app

# Copy necessary files
COPY data_processor.py lahaina-label.tsv merged-reduced.tsv requirements.txt routes.py ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "routes.py"]
