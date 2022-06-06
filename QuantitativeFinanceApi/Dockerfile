FROM python:3.9-slim
WORKDIR /usr/src/app
COPY .. .
RUN pip install pipenv
RUN pipenv install
RUN pip install -r requirements.txt --src /usr/src/app
EXPOSE 5000
ENTRYPOINT ["pipenv", "run", "python", "QuantitativeFinance.py"]