FROM python

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["sh", "-c", "python configs/mysql-config.py && python run.py"]