FROM python:3.10-alpine

# copy files to container
COPY . .

# update and install the requirements
RUN pip install .
ENTRYPOINT ["python", "run.py"]
