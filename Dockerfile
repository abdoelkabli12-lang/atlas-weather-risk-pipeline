FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/streamlit/streamlit-example.git .

EXPOSE 8501

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]