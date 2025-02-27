# Use an official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy necessary files
COPY main.py requirements.txt lahaina-label.tsv ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]
