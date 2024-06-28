from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import json
from typing import Tuple, Iterator
import osmnx as ox


@dataclass
class Film:
    """
    Class that stores the information of each film
    """
    title: str  # the tile of the film
    genre: list[str]  # a list of genres associated with the film
    director: list[str]  # a list of directors who directed the film
    actors: list[str]  # a list of actors that are in the film
    id: str  # a unique identifier for the film

    def __hash__(self):
        return hash(self.id)


@dataclass
class Cinema:
    """
    Class that stores the information of each cinema
    """
    name: str  # The name of the cinema.
    adress: str  # The street adress of the cinema.
    coordinates: tuple[float, float]


@dataclass
class Projection:
    """
    Class that storess the information of each session
    """

    film: Film  # The film being projected
    cinema: Cinema  # The cinema where the film is projected
    time: tuple[int, int]  # The hour when it's projected
    language: str  # The language of the film


@dataclass
class Billboard:
    """
    Reads the data relating to the current day's Barcelona cinemas
    and searches them.
     """

    films: list[Film]
    cinemas: list[Cinema]
    projections: list[Projection]

    def filter_title(self, title: str) -> list[Projection]:
        """
        Filters the films of the projection for a given title using lambda function
        and filter iterator. Returns a list of Projections.
        """

        return list(filter(lambda projec: title.lower() == projec.film.title.lower(), self.projections))
        # lower() is used to avoid errors of capital letters on the user writting

    def filter_genre(self, genre: str) -> Iterator[Film]:
        """
        Filters the films by genre. Returns an iterator with the film corresponding to the genre.
        """

        for film in self.films:
            if genre in film.genre:
                yield film

    def filter_cinema(self, cine: str) -> list[Projection]:
        """
        Given a cinema, filters all the movies shown in that cinema. returns a list of Projections shown in the cinema.
        """

        return list(filter(lambda projec: cine.lower() == projec.cinema.name.lower(), self.projections))

    def filter_actors(self, actor: str) -> Iterator[Film]:
        """Filters the movies where the actor appears. 
        Returns an iterator with the list of films where the actor appears.
        """

        for film in self.films:
            if actor in film.actors:
                yield film


def get_coordinates(address: str) -> Tuple[float, float]:
    """
    Returns the coodinates lattitude and longitud of the addreses of the each cinema
    """

    # Takes control of the misspellings of Sensacine's web in order to avoid problems with geocode
    address = address.replace('Calle', 'Carrer')\
        .replace('Avenida', 'Avinguda')\
        .replace('Avda.', 'Avinguda')\
        .replace('Paseig', 'Passeig')\
        .replace('Centro Comercial Splau! -', '')\
        .replace('- Centro Comercial Gran Vía 2', '')\
        .replace('Paseo', 'Passeig')\
        .replace('Sta Fé', 'Carrer de Santa Fe')\
        .replace('- Centro Comercial La Maquinista', '')\
        .replace('Andreu', 'D\'Andreu')\
        .replace('s/n - Pintor Alzamora', '')\
        .replace('Avinguda Josep Tarradellas', 'Avinguda de Josep Tarradellas i Joan')\
        .replace('Avinguda Virgen Montserrat', 'Avinguda Verge de Montserrat')\
        .replace('Centro Comercial Baricentro - Carretera Nacional 150', 'N-150')\
        .replace('Carrer Salvador Espriu', 'Carrer de Salvador Espriu')\
        .replace('Carrer Verdi', 'C/ de Verdi')\
        .replace('Carrer Aribau', "Aribau - Gran Via")

    """if address == 'Calle Aribau, 8, 08011 Barcelona':
        location = (41.3876521, 2.1602093)"""

    location = ox.geocoder.geocode(address)

    return location


def translate_genres(new_film: Film) -> list:
    """
    Translates the genres of each film from Spanish to English
    """

    genre_translations: dict[str, str] = {'Animación': 'Animation', 'Familia': 'Family', 'Guerra': 'War', 'Suspense': 'Suspense', 'Terror': 'Horror', 'Drama': 'Drama', 'Romántico': 'Romantic', 'Biografía': 'Biography', 'Acción': 'Action', 'Western': 'Western', 'Comedia musical': 'Musical Comedy',
                                          'Erótico': 'Erotic', 'Aventura': 'Adventure', 'Crimen': 'Crime', 'Documental': 'Documental', 'Fantasía': 'Fantasy', 'Histórico': 'Historic', 'Comedia': 'Comedy', 'Comedia dramática': 'Dramatic comedy', 'Judicial': 'Judicial', 'Ciencia ficción': 'Science Fiction'}

    english_genres: set[str] = set()
    for genre in new_film.genre:
        try:
            translation = genre_translations[genre]
        except:
            translation = 'Others'

        # A set is used because if there are more than one genre that are not in the dictionary others does not appered more than once
        english_genres.add(translation)
    return list(english_genres)


def read() -> Billboard:

    set_films: set[Film] = set()
    dict_cinemas: dict[str, Tuple[str, Tuple[float, float]]] = dict()

    list_films: list[Film] = []
    list_cinemas: list[Cinema] = []
    list_projections: list[Projection] = []

    # Searches for all the relevant information of the three pages of the sensacine website
    for i in range(1, 4):
        if i == 1:
            link = 'https://www.sensacine.com/cines/cines-en-72480/'
        else:
            link = 'https://www.sensacine.com/cines/cines-en-72480/?page=' + \
                str(i)

        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'lxml')

        # Entries of films filtred by 'div' and the class 'item_resa'
        divslist = soup.find_all('div', attrs={'class': 'item_resa'})

        # Entries of cinema name filtred by 'a' and class 'no_underline j_entities'
        cin_names = soup.find_all(
            'a', attrs={'class': 'no_underline j_entities'})

        # Entries of cinema adress filtred by 'span' and class 'lighten'
        cinlist = soup.find_all('span', attrs={'class': 'lighten'})

        # In the even postions there is information we do not need
        directions = [cinlist[x].text.strip()
                      for x in range(1, len(cinlist), 2)]

        directions_bcn: list[str] = []

        for addres in directions:
            city = addres.split()[-1]
            if city == 'Barcelona':
                directions_bcn.append(addres)

        coordinates = [get_coordinates(adress) for adress in directions_bcn]

        # Creates a dictionary of cinemas where the key is its name and the value its direction
        dict_cinemas = {k.text.strip(): (v1, v2) for k,
                        v1, v2 in zip(cin_names, directions_bcn, coordinates)}

        for k, v in dict_cinemas.items():
            list_cinemas.append(Cinema(k, v[0], v[1]))

        for div in divslist:

            # the class j_w is selected fot the film and cinema information and list_hours for the projections
            new = div.find('div', attrs={'class': 'j_w'})

            # Searches for the language of the cinema in 'span' class 'bold'
            language = div.find('span', attrs={'class': 'bold'}).text

            if language == ' Versión Original':
                language = 'Original Version'
            else:
                language = 'Spanish'

            cine_name = (new['data-theater'])
            film_name = (new['data-movie'])

            # Converts the data to a python's dictionary using json
            cine = json.loads(str(cine_name))
            film = json.loads(str(film_name))

            c_name = cine['name'].rstrip()

            if c_name in dict_cinemas:

                adress = dict_cinemas[c_name]
                new_cinema = Cinema(c_name, adress[0], adress[1])

                new_film = Film(film['title'], film['genre'],
                                film['directors'], film['actors'], film['id'])

                if new_film.title not in set_films:
                    set_films.add(film['title'])
                    list_films.append(new_film)

                new_film.genre = translate_genres(new_film)

                # Searches all the sessions of the film in 'em' and we append each projection in the list of projections
                all_hours = div.find_all('em')

                for em in all_hours:
                    hour, minut = em.text.split(':')
                    hour = int(hour)
                    minut = int(minut)
                    p = Projection(new_film, new_cinema,
                                   (hour, minut), language)

                    list_projections.append(p)

    return Billboard(list_films, list_cinemas, list_projections)


if __name__ == '__main__':
    read()
