FROM python

WORKDIR /app/text-extractor

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY . .

CMD [ "python", "src/main.py" ]