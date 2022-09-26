FROM python:3.9

WORKDIR /project

RUN useradd -m -r user && \
    chown user /project

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

USER user

ENTRYPOINT [ "python", "upload_changesets_from_replication.py"]