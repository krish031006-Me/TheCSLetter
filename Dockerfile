# This is the base image pythoen to be specific
FROM python:3.11-slim AS base

# Set the working directory inside of it by the name /app
WORKDIR /app

# Copy the requirement files and all
COPY requirements.txt .

# Install dependencies and use --no-cache--
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code, here dot refers to all the files that are present in the root and second dot tells it to put all those files inside /app
COPY . .

# Expose the default port of Flask ~ This tells it that app inside container listens to port 5000 
EXPOSE 5000

# Running the command in CMD to start app.py/
CMD ["python","app.py"]
