# Race Walking Data Visualizer

This is the (new) repo for an application which allows a user to display, graph, and modify
a large swathe of race walking data.

## Prerequisites

First install to a location of your choosing [wkhtmltodpf](https://wkhtmltopdf.org/downloads.html) and add its bin folder to your path.

Then, use pip to install the dependencies.

```shell script
pip install -r requirements.txt
```

## Running the application

Spin up the web server with the following command:

```shell script
python app.py
```

You can view the application now running on [http://localhost:5000](http://localhost:5000).

## Coding Guidelines

This project adheres to Python's official [PEP 8 coding standards](https://peps.python.org/pep-0008/). Key principles include:

- **Readability**: The code is written in a way that is clear and understandable.
- **Consistency**: Naming conventions, indentation, and import ordering are followed consistently across the codebase.
- **Error Handling**: Pythonic error handling is implemented using try-except blocks where necessary.
- **Documentation**: Docstrings and comments are provided for functions and classes to explain their purpose and usage.
