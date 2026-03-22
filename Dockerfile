# version
FROM python:3.12.6-slim

# working dir
WORKDIR /app

# copy and install requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the code
COPY . .

# expose port
EXPOSE 5000

# start command
CMD ["python3", "app.py"]
