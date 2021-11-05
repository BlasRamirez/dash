FROM python:3.8

# set the working directory in the container
WORKDIR /app
# copy the dependencies file to the working directory
COPY requirements.txt .
# install dependencies
RUN pip install -r requirements.txt
# copy the dash
COPY src/ .

# Expose the API Port
EXPOSE 8080
# Run the server
CMD ["python", "app.py"]