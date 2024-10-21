# Use the official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file to the working directory
COPY ./requirements.txt /code/estate_management/requirements.txt

# Install the Python dependencies
RUN pip3 install -r ./estate_management/requirements.txt

# Copy the application code to the working directory
COPY . /code/estate_management

# Expose the port on which the application will run
EXPOSE 8080

# Run the FastAPI application using uvicorn server
CMD ["uvicorn", "estate_management.main:app", "--host", "0.0.0.0", "--port", "8080"]