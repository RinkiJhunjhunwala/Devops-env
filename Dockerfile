FROM python:3.11-slim

WORKDIR /app

# Prevent python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment source
COPY . /app/

# The runner script
CMD ["python", "inference.py"]
