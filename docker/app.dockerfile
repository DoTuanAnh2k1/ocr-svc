FROM python:3.10.19-slim-bookworm AS base
WORKDIR /app
# Install requirements with pip
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && find /usr/local/lib/python3.10/site-packages -name "*.pyc" -delete
RUN rm /app/requirements.txt

FROM base AS production
# Copy application code
COPY .. /app
# Warmup step to load the model
RUN python __main__.py warmup
# Remove all pycache directories to reduce image size
RUN find /app -type d -name "__pycache__" -exec rm -rf {} +;
# Set environment variables
ENV FLASK_ENV=production
# Expose the application port
EXPOSE 5000
# Command to run the application
CMD ["python", "__main__.py"]