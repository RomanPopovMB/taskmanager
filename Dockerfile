# Use the official Python image as a base.
FROM python:3.13-slim

# Set the working directory.
WORKDIR /

# Copy only the requirements file to leverage Docker cache.
COPY requirements.txt .

# Install dependencies.
RUN pip install -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose the application port.
EXPOSE 8000

# Run the application.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]