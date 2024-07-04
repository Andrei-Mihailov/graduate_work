FROM python:3.9-slim

WORKDIR /usr/src/app/

COPY requirements.txt ./

RUN pip install --upgrade pip

RUN pip install -r requirements.txt || cat requirements.txt

RUN pip install flake8 pytest pytest-flask pytest-mock

COPY . .

CMD ["bash", "-c", "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics && flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics && pytest -p no:cacheprovider ugc/tests/*"]
