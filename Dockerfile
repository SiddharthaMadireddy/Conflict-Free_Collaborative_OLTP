# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies (none currently required besides stdlib, but listed for future-proofing)
# RUN pip install -r requirements.txt

# Command to run the reference scenario by default
CMD ["python", "test_scenario.py"]
