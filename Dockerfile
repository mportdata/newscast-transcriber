# Step 1: Use the official Apache Beam Python SDK image as the base image
FROM apache/beam_python3.12_sdk

# Step 2: Install system dependencies (e.g., libsndfile)
RUN apt-get update && apt-get install -y libsndfile1 && apt-get clean

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy your source code and modules into the container
COPY src/ /app/src/

# Optional: Specify the default entry point for the container
ENTRYPOINT ["python", "src/main.py"]
