from billboard import *
from tabulate import tabulate
import yogi
from typing import Optional, Tuple


from city import *
from buses import *
from datetime import timedelta, datetime


def print_selected_films(films_filtered: list[Film]) -> None:
    """
    Prints the table of the films that are filtered for some attribute, such as genre or actors.
    """

    list_print: list[str] = []

    list_print = [[film.title, ', '.join(film.genre), ', '.join(
        film.director), ', '.join(film.actors)] for film in films_filtered]
    print(tabulate(list_print, headers=[
          'TITLE', 'GENRE', 'DIRECTOR', 'ACTORS'], tablefmt='fancy_grid'))


def print_table_by_parts(print_list, head: list[str]) -> Optional[bool]:
    """
    Prints the table of a selected information with the corresponding headers(head) by ranges of 20
    """

    more_info = True
    inici = 0
    final = 20

    while more_info and len(print_list) > final - 1:
        print(tabulate(print_list[inici:final],
              headers=head, tablefmt='fancy_grid'))

        print(sep='')
        print('Press 1 to continue reading or 0 if you want to quit')
        decision = yogi.read(int)

        if decision == 1:
            inici += 20
            final += 20
        else:
            more_info = False
            return False


def print_entire_billboard(bill: Billboard) -> None:
    """
    Prints the entire billboard in tables of 20 projections
    """

    info = bill.projections
    list_imp_info = [[projection.film.title, ', '.join(projection.film.genre), projection.cinema.name, projection.cinema.adress,
                      f"{projection.time[0]:02d}:{projection.time[1]:02d}", projection.language] for projection in info]
    headers = ['TITLE', 'GENRE', 'CINEMA NAME',
               'CINEMA ADRESS', 'TIME', 'LANGUAGE']

    if not print_table_by_parts(list_imp_info, headers):
        menu_billboard(bill)


def print_list_films(bill: Billboard) -> None:
    """
    Prints the entire list of films in tables of 20 films
    """

    info = bill.films
    list_info = [[film.title, ', '.join(film.genre), ', '.join(
        film.director), ', '.join(film.actors)] for film in info]
    headers = ['TITLE', 'GENRE', 'DIRECTOR', 'ACTORS']

    if not print_table_by_parts(list_info, headers):
        menu_billboard(bill)


def print_by_title(bill: Billboard) -> None:
    """
    Filters the projections by the title of the film the user has selected'
    """

    print('Enter the entire title of the film:')
    title = input()
    films_filtered = bill.filter_title(title)

    if len(films_filtered) > 0:

        f = films_filtered[0].film  # we get the film selected
        info_film_selec = [['TITLE', f.title], ['GENRE', f.genre], [
            'DIRECTOR', f.director], ['ACTOR', f.actors]]

        # we print the information of the selected film
        print('INFORMATION OF THE FILM:')
        print(tabulate(info_film_selec, tablefmt='fancy_grid'))
        list_print = [[projection.film.title, projection.cinema.name, projection.cinema.adress,
                       f"{projection.time[0]:02d}:{projection.time[1]:02d}", projection.language] for projection in films_filtered]
        print('PROJECTIONS:')
        print(tabulate(list_print, headers=[
            'TITLE', 'CINEMA NAME', 'ADRESS', 'TIME', 'LANGUAGE'], tablefmt='fancy_grid'))

        print('Press 0 to return to the menu')
        decision = yogi.read(int)

        if decision != 0:
            raise Exception('Sorry, this is not a valid character')
        else:
            menu_billboard(bill)

    else:
        print('Today there are no films available with this title.')
        menu_billboard(bill)


def print_by_genre(bill: Billboard) -> None:
    """
    Prints the list of films of the genre selected by the user
    """

    dict_genre: dict[int, str] = {1: 'Adventure', 2: 'Action', 3: 'Animation', 4: 'Biography', 5: 'Comedy', 6: 'Science Fiction', 7: 'Drama',
                                  8: 'Fantasy', 9: 'War', 10: 'Romantic', 11: 'Horror'}

    print('Select the number of the genre you are interested in:')
    for key, value in dict_genre.items():
        print(f'{key}: {value}')

    selection = yogi.read(int)
    genre = dict_genre[selection]
    films_filtered = list(bill.filter_genre(genre))

    if len(films_filtered) > 0:
        print_selected_films(films_filtered)
        menu_billboard(bill)
    else:
        print('Today there are not films available with this genre')
        menu_billboard(bill)


def print_by_actors(bill: Billboard) -> None:
    """
    Prints the films by an actor selected by the user
    """

    print('Enter one actor you are interested in:')
    actor = input()
    films_filtered = list(bill.filter_actors(actor))

    # we consider the case there is no film performed by that actor
    if len(films_filtered) > 0:
        print_selected_films(films_filtered)
    else:
        print('Today there is no film performed by this actor')
        menu_billboard(bill)


def print_by_cinema(bill: Billboard) -> None:
    """
    Prints the projections of the cinema selected by the user
    """

    print('Enter the name of the cinema:')
    name = input()
    projections_filtered = bill.filter_cinema(name)

    if len(projections_filtered) > 0:

        c = projections_filtered[0].cinema
        info_cinema_selec = [['NAME', c.name], ['ADRESS', c.adress]]
        print('INFORMATION OF THE FILM:')
        print(tabulate(info_cinema_selec, tablefmt='fancy_grid'))
        list_print = [[projection.film.title, ','.join(
            projection.film.genre), f"{projection.time[0]:02d}:{projection.time[1]:02d}", projection.language] for projection in projections_filtered]
        print('PROJECTIONS IN', c.name.upper())
        print(tabulate(list_print, headers=[
              'FILM TITLE, GENRE, TIME, LANGUAGE'], tablefmt='fancy_grid'))
        menu_billboard(bill)

    else:
        print('You may have misspelled the name of the cinema. Try again.')
        menu_billboard(bill)


def check_time(time_to_last_cinema: int, projec_time: Tuple[int, int]) -> bool:
    """
    Checks if according to the time that takes to arrive in the cinema we are able to arrive before the film starts
    """

    # time delta is used in order to be able to sum and substract hours easily
    h_cinema = timedelta(seconds=time_to_last_cinema)
    h_projec = timedelta(hours=projec_time[0], minutes=projec_time[1])
    actual_time = datetime.now()
    suma = h_cinema + timedelta(hours=actual_time.hour,
                                minutes=actual_time.minute)

    return suma < h_projec


def best_path(projec_filtered: list[Projection], ox_g: OsmnxGraph, g: CityGraph, source_coord: Tuple[int, int]) -> Path | None:
    """
    Saves an image with the path to arrive to the first projection
    """

    best_projection = None
    last_cinema_name = None
    time_to_last_cinema = None
    best_proj_time = None

    for p in projec_filtered:

        if p.cinema.name != last_cinema_name:
            last_cinema_name = p.cinema.name

            time_to_last_cinema = find_path_time(
                ox_g, g, source_coord, p.cinema.coordinates)

        if check_time(time_to_last_cinema, p.time):
            projec_time = timedelta(hours=p.time[0], minutes=p.time[1])
            if best_projection is None or projec_time < best_proj_time:
                best_projection = p
                best_proj_time = timedelta(
                    hours=best_projection.time[0], minutes=best_projection.time[1])

    if best_projection is None:
        return None
    print(
        f'YOUR BEST SELECTION TO SEE THE EARLIEST PROJECTION OF "{best_projection.film.title.upper()}" IS IN:')

    info: list[list[str]] = [['CINEMA NAME', best_projection.cinema.name], ['ADRESS', best_projection.cinema.adress], [
        'TIME', f"{best_projection.time[0]:02d}:{best_projection.time[1]:02d} h"], ['LANGUAGE', best_projection.language]]
    print(tabulate(info, tablefmt='fancy_grid'))

    return find_path(ox_g, g, source_coord, best_projection.cinema.coordinates)


def menu_billboard(bill: Billboard) -> None:
    menu_options = [
        ["1 -->", "See all billboard of BCN"],
        ["2 -->", "Filter the projections by film title"],
        ["3 -->", "Filter the films by genre"],
        ["4 -->", "See all the movies that are shown today in Barcelona"],
        ["5 -->", "Filter the projections by cinema"],
        ["6 -->", "Filter the films by actors"],
        ["0 -->", "Go to the main menu"]
    ]

    print()
    print('Indicate what do you want to search:')
    table = tabulate(menu_options, headers=[
                     "Option", "Description"], tablefmt="plain", numalign="right")
    print(table)
    print()

    option = yogi.read(int)
    if option == 1:
        print_entire_billboard(bill)

    if option == 2:
        print_by_title(bill)

    if option == 3:
        print_by_genre(bill)

    if option == 4:
        print_list_films(bill)

    if option == 5:
        print_by_cinema(bill)

    if option == 6:
        print_by_actors(bill)

    if option == 0:
        main()


def display_main_menu() -> str:
    menu_options = [
        ["1", "Show the name of the authors of the project"],
        ["2", "Show the billboard"],
        ["3", "Show the bus graph interactively"],
        ["4", "Save an image of the buses graph in your computer"],
        ["5", "Show the city graph interactively"],
        ["6", "Save an image of the city graph in your computer"],
        ["7", "Show the path to a movie"],
        ["0", "Exit"]
    ]
    print()
    print(tabulate(menu_options, headers=["Option", "Description"]))
    print()
    print('Enter your choice: ')
    choice = yogi.read(int)

    return choice


def main() -> None:
    print('Please write the number that corresponds to the information you want to acces in the menu.')
    print()
    bill = read()
    g_ox = None
    g_buses = None
    g_city = None

    while True:
        choice = display_main_menu()

        if choice == 1:
            # Show authors
            print()
            print("Authors: Raquel Jolis and Maria Sans")

        elif choice == 2:
            # Show billboard
            print(
                'PLEASE, IN ORDER TO SEE THE INFORMATION PROPERLY, REDUCE THE SIZE OF THE TERMINAL USING CTRL- ')
            menu_billboard(bill)
            print()

        elif choice == 3:
            # Show the bus graph
            print(
                'REMEMBER TO CLOSE THE SCREEN OF THE GRAPH IF YOU WANT TO CONTINUE USING THIS INTERFACE')
            create_graph('3')
            print()

        elif choice == 4:
            # Save an image of the buses graph in your computer
            print(
                'Wait for the image to be saved in your computer. This can take some time. ')
            create_graph('4')
            print()

        elif choice == 5:
            # show the city graph interactively
            if g_buses is None:
                print("Wait a minute, the city graph is creating...")
                g_buses = get_buses_graph()
            g_ox = get_osmnx_graph()
            g_city = build_city_graph(g_ox, g_buses)
            show(g_city)
            print(
                'PLEASE, TO CONTINUE NAVIGATING THROUGH THE MENU, CLOSE THE GRAPH WINDOW.')

        elif choice == 6:
            # Saves an image of the city graph in your computer
            if g_buses == None:
                print(
                    "Wait a minute, the city graph is being created... The image will appear as a new file in this same directory.")
                g_buses = get_buses_graph()
            if g_city == None:
                g_ox = get_osmnx_graph()
                g_city = build_city_graph(g_ox, g_buses)
            plot(g_city, 'bcn_city_graph.png')

        elif choice == 7:
            # show the shortest path to see a movie

            print("Enter the title of the film you are interested in")
            title = input()

            projec_filtered = bill.filter_title(title)

            if len(projec_filtered) == 0:
                print('Today there are no films available with this title.')
                main()
            else:
                print("\n Enter the name of the street you are, the number of the building, the Postal Code and the city \n Write it as the following example: Carrer de Sants, 125, 08028 Barcelona")

                adress = input()

                location = get_coordinates(adress.strip())

                if g_ox is None:
                    g_ox = get_osmnx_graph()
                if g_buses is None:
                    g_buses = get_buses_graph()
                if g_city is None:
                    g_city = build_city_graph(g_ox, g_buses)

                p = best_path(projec_filtered, g_ox, g_city, location)

                if p is None:
                    print(
                        'THERE IS NO PATH TO ARRIVE TO THE FILM AT TIME. MAYBE YOU COULD TRY TOMORROW!')
                else:
                    num = 0
                    prev_line = None

                    for node in p:
                        if type(node) == str:
                            act_line = node.split('_')
                            if prev_line is None or prev_line[0] != act_line[0]:
                                num += 1
                                prev_line = act_line
                    if num > 0:
                        print("You need to take", num,
                              "different buses to arrive to your selected cinema.")
                    else:
                        print(
                            "You don't need to take any bus. The route is all walking.")
                    plot_path(g_city, p, 'path.png')
                    print('CHECK THE DIRECTORY TO SEE THE PATH')

        elif choice == 0:
            # Exit the program
            print("Exiting... See you soon!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":

    main()
