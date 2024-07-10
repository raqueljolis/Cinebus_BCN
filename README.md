# CINEBUS 🎬🚌

This page describes the **CineBus project**, a practice of the AP2 course in GCED of the **Universitat Politècnica de Catalunya.** 

The project aims to create an interface that helps users find movies and navigate to cinemas based on their film preferences and help them arrive to the cinema destination, either by bus or walking, in the minimum time possible. 


# Table of Contents

1.  [Installation](#installation)
2. [Modules of the project](#modules-of-the-project)
   - [Billboard](#billboard)
   - [Buses](#buses)
   - [City](#city)
    - [Demo](#demo)

3.  [Important Notes](#important-notes)
4.  [Built with](#built-with)
5.  [Information sources](#information-sources)
6.  [Authors](#authors)

# Installation

This project requires some libraries to be installed for the correct operation of the program:

- **requests** for downloading data files
- **yogi** to read data
- **beatifulsoup** for parsing HTML tress
- **networkx** for manipulating graphs
- **osmnx** for obtaining graphs of places
- **haversine** for calculating distances between coordinates
- **staticmap** for drawing maps
- **tabulate** for printing tables with a readable presentation of mixed textual and numeric data
- **scikit-learn** as a requirement for the function osmnx.distance.nearest_nodes
presentation of mixed textual and numeric data

You will need to have `pyhon3` and `pip3` updated. Check it with:


```python
pip3 install --upgrade pip3
pip3 install --upgrade python3
```

All the libraries can be installed using the requirements file. Once you have updated your pip, you just need to insert the command:
 ```python
 pip3 install -r requirements.txt 
 ```


# MODULES OF THE PROJECT

This project is divided in four parts:


# Billboard
This module provides classes and functions to read and filter information about the film billboard in Barcelona. It retrieves data from the [Sensacine](malito:https://www.sensacine.com/cines/cines-en-72480/?page=1) website and allows you to search for films, cinemas, and projections based on various criteria.

Several functions have been implemented in order to offer the user a way to filter the information of the films according to their preferences.

**Since the amount of data films is huge, we have used the lambda function toghether with `filter` and `yield`, to filter the film propieties according to the user's input.**

The filtering options are: by title, by genre, by cinema and by actors. We have chosen this ones because we consider they are the most common 
characteristics for users to decide the film they want to see.

```pyhon
def filter_title(self, title: str) -> Iterator[Projection]
```
```pyhon
def filter_genre(self, genre: str) -> Iterator[Film]
```
```pyhon
def filter_cinema(self, cine: str) -> Iterator[Projection]
```
```pyhon
def filter_actors(self, actor: str) -> Iterator[Film]
```


The module provides the following data classes:

- **Film**: Represents information about a film, including title, genre, director, actors, and ID.

- **Cinema**: Stores information about a cinema, including name, address, and coordinates.

- **Projection**: Contains details about a film projection, such as the film, cinema, time, and language.

- **Billboard**: Represents the movie billboard for a specific day, including lists of films, cinemas, and projections.

The main function is `read()` that is the one responsible for scrapping the data. **We have decided that we would only get information from the three main web pages of sensacine.** Although more information is available in other specific links that refer to films, accessing different links would cost a lot of time. That is why we have adhered to the information offered by these three links, so that we can obtain a substantial and varied amount of information in a short period of time.

## Getting the coordinates of the cinema

In the billboard module we have implemented a function that stores in a list all the addresses of cinemas and finds its coordinates to add it to the class Cinema. This will be useful for further calculations of paths. 
However, it is important to note that due to the `geocode` sensitivity some adresses have been renamed in order to be able to detect their coordinates. 


# Buses

## Graph Construction 

 In order to avoid possible errors, **we have decided to limit the information referring to cinemas, buses and streets strictly of the Barcelona area.** Although the sensacine website offers us information on projections in other places such as Sant Cugat or Badalona, ​​errors can sometimes arise because the streets may have the same name.

The `get_buses_graph()` function is the one responsible for downloading the data from the [AMB](malito:https://www.amb.cat/es/home) website and creates the graph.

## Visualization

In order to show the graph to the user, we have implemented:
- `show()`: displays the graph interactively using the `nx.draw()`
- `plot()`:  saves the graph as an image file with the city map of Barcelona in the background.

# City

## Graph Construction

We have created the function `build_city_graph(g1: OsmnxGraph, g2: BusesGraph)` that takes an **Osmnx graph** `g1` representing the streets of Barcelona and the **Buses Graph** `g2` created in the buses module, containing the bus lines data. Combining this both graphs we have created the city graph.

## Shortest path and time to arrive calculation 

The function `find_path(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord)` recieves the source and destination coordinates and returns the shortest path as a list of nodes. 

Once the path is decided, in order to calculate how much time does it take to arrive to a certain cinema, **we have established the average both walking and by bus speed, measured in m/s, so that, along with the length of the edges, we can calculate approximately how much time will take a person to arrive to their destination**.

The function to calculate the path time is: `find_path_time(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord)`.

The global constants we established are:

- `WALK_SPEED= 1.25 #m/s`

- `BUS_SPEED= 3.5 #m/s`

## Visualization

There are three main functions to visualize the graph: 
 
 - `show(g: CityGraph)` : Basically displays the city graph interactively in a window. 
 - `plot(G: CityGraph, filename: str)`: saves the city graph in a file with the city map in the background
 - `plot_path(g: CityGraph, p: Path, filename: str)`: shows the route that the user must take to reach their destination


# Demo

To display the information, **we decided that the best thing to do was to create a menu, so that the user could navigate through it and choose which feature to use.** That is why we have created a main menu with options, where we distinguish the main actions that can be carried out.

As the utility of the terminal is quite reduced in terms of printing parameters on the screen, the menu is simply a scale of numbers with their respective actions. **Users just have to press the number of the option they want.** From there, in some options it is possible that another secondary menu will be displayed, with more options related to the previous one.
*The user will always have the option of returning to the main menu and from there leaving the program.*

Regarding the options to show the billboard and information related to the movies, **we have decided to use the 'tabulate' library** that is used to print tables in the terminal. 

In this way, we can show in a visual and clear way the information of your films with cells, which refer to characteristics of the film such as its genre, its actors or simply the cinema where it is projected.

*Check the [Notes](#important-notes) to see important information related to the tabulate mode and its visualization in the terminal.

## Instructions of usage


1- Execute the demo.py file from the terminal using the following command: `python demo.py`.

2- The main menu will be displayed with the following options:

       1.  Show the name of the authors of the project
       
       2.  Show the billboard
*Note: Some options may require additional input from the user, such as film titles, genres, or cinema names.*

*The information is given in a 10-row table. If you want to see more information press '1'.*

       3.  Show the bus graph interactively
    
       4.  Save an image of the buses graph in your computer
*The image is saved in the same directory as the project is saved. The name will be: 'graf_buses_bcn.png'*

       5.  Show the city graph interactively

       6.  Show an image of the city graph in your computer
*The image is saved in the same directory as the project is saved. The name will be: 'bcn_city_graph.png'*

       7.  Show the path to a movie

- *The blue lines represent the route by bus. The green lines represent the route walking.*
- *The black circle marker is the source adress and the red circle marker is the destination adress. 
Additional information is displayed in the terminal referring the cinema name, adress, time of the projection and language.* 

       0.  Exit

3- Choose an option by entering the corresponding number and pressing Enter.

4- Follow the instructions provided by the interface to navigate through the different features.




# Important Notes

- The project uses the 'tabulate' module that allows to visualize the information with tables. However, in order that the design of tables does not become dislodged and disordered, it is necessary to reduce the size of the terminal to fit all the data.

**To view the information properly in the terminal, reduce the terminal size using the `Ctrl -` key combination**.

- Regarding the filters to search for an specific trait of a film (such as the name of the cinema where it is projected, the name of the film, the genre, the authors that participate, etc.) it is very important that the information is introduced as seen in the output, since the filtering function is very sensitive. In future versions of the interface, this will be improved.

- When wanting to search the path to go and see a film, it's really important to write the location specifically as said in the terminal. Otherwise, the adress is not recognised an error like this will appear:
    `raise ValueError(f'Nominatim could not geocode query "{query}"')
ValueError: Nominatim could not geocode query "Calle Salvador Espriu, 61, 08005 Barcelona"`


# Built with

- All the information of the films and cinemas in Barcelona has been scrapped from [Sensacine](malito:https://www.sensacine.com/cines/cines-en-72480/?page=1), which is a website that provides information about all the cinemas in Spain. However we have reduced our project to cinemas in Barcelona.

- All the information about the bus lines has been extracted from the [AMB](malito:https://www.amb.cat/es/home) website. 

- The map of the streets of Barcelona extracted from [OpenStreetMap](malito:https://www.openstreetmap.org/)

# Information sources

- [File lessons in pyton](malito:https://lliçons.jutge.org/python/fitxers-i-formats.html)
- [Python Pickle Module for saving Objects by serialization](malito:https://pythonprogramming.net/python-pickle-module-save-objects-serialization/)
- [NetworkX Tutorial](malito:https://networkx.github.io/documentation/stable/tutorial.html)
- [OSMnx Tutorial](malito:https://geoffboeing.com/2016/11/osmnx-python-street-networks/)
- [Requests tutorial](malito:https://realpython.com/python-requests/)
- [Data Science Essentials: Scraping Data From the Web](malito:https://medium.com/swlh/data-science-essentials-scraping-data-from-the-web-3c84e194538d)



# Authors

*Raquel Jolis* and *Maria Sans*. Idea of the project and instructions provided by *Jordi Petit*.

 SOURCE OF THE PROJECT: https://github.com/jordi-petit/ap2-cinebus-2023/blob/main/README.md


Enjoy using the Cinema Interface Demo! If you have any questions or encounter any issues, please contact [maria.sans.bosch@estudiantat.upc.edu](mailto:maria.sans.bosch@estudiantat.upc.edu) or [raquel.jolis@estudiantat.upc.edu](mailto:raquel.jolis@estudiantat.upc.edu)
