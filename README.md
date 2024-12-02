# Race Walking Data Visualizer

This is the (new) repo for an application which allows a user to display, graph, and modify
a large swathe of race walking data.

## Running the application

First, use pip to install the dependencies.

```shell script
pip install -r requirements.txt
```

Then simply spin up the web server.

```shell script
python app.py
```

View the application now running on [http://localhost:5000](http://localhost:5000).

## Coding Guidelines

This project adheres to Python's official [PEP 8 coding standards](https://peps.python.org/pep-0008/). Key principles include:

- **Readability**: The code is written in a way that is clear and understandable.
- **Consistency**: Naming conventions, indentation, and import ordering are followed consistently across the codebase.
- **Error Handling**: Pythonic error handling is implemented using try-except blocks where necessary.
- **Documentation**: Docstrings and comments are provided for functions and classes to explain their purpose and usage.


## Design Decisions

### **Modular Architecture**
The application is built using a modular design to improve scalability and maintainability. Core functionalities such as data processing, visualization, and scraping are separated into distinct components. This modular approach simplifies debugging and future feature additions.

### **Data Gathering**
Data is gathered using the Selenium library for web scraping on the [World Athletics](https://worldathletics.org/) website. Selenium was specifically chosen because the website is dynamically generated, which makes it unsuitable for scraping with BeautifulSoup.


### **Data Visualization**
We prioritize intuitive and informative data representation by leveraging the popular Python library Bokeh. By utilizing Bokeh, we're able to dynamically generate graphs with various parameters to provide a large range of visualizations.

### **User-Friendly Interface**
The web interface is designed with simplicity in mind...

### **Performance Optimization**
Given the potential size of the race walking datasets, efficient data handling techniques are employed. This includes optimized pandas operations and, where necessary, caching frequently accessed data to reduce computation time.

### **Extensibility**
The codebase is structured to facilitate easy integration of new features, such as additional data formats or visualization options. We have also ensured compatibility with future updates in Python and library dependencies.
