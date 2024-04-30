FROM python

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

RUN python configs/mysql-config.py

CMD [ "python", "run.py" ]