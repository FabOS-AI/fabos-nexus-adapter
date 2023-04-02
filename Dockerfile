FROM python:3.11.1

# Install pip modules (slim image requires to pull and remove build dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python-dev\
    && rm -rf /var/lib/apt/lists/* 

# Add pip requirements file
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt  

# Add python script
COPY main.py /
COPY nexus_* /
COPY slm_client.py /

# Trigger Python script
CMD ["python", "-u", "./main.py"]
