# Use an official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy necessary files
COPY monitor.py nlp_loader.py preprocess.py geocode_redis.py uscities.csv worldcities.csv requirements.txt ./
COPY data_model/models/lgbm_model_encoder_v1.pkl ./data_model/models/lgbm_model_encoder_v1.pkl

# Install dependencies
RUN apt update
RUN apt install -y libgomp1
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Expose the Flask port
# EXPOSE 5000

# Run the Flask app
CMD ["python", "monitor.py"]
