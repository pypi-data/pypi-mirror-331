# The purpose of this file is to assess the answers by students taking a corresponding Python course
# Students should install this code either via pip or directly placing the file in the folder they will be coding in
# The notebooks provided to the students will then import this file and make calls to it
# Each function corresponds to a quiz question in a quiz that is associated with the notebook they are working through
# If the student's answer is correct, the function will output a keyword or phrase to answer the quiz question with
# If the answer is incorrect, the function will output a statement telling them their answer was incorrect
# Risks associated with beginner python students finding answers in this file was felt to be minimal and worth alternatives

# install dependencies
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import omdb

#print("Didgeridoo")


# Project 1 Problem 1
def test1_1(answer):
    if answer == 500000000:
        print("Tytastic")
    else:
        print("Your production_costs variable is not correct.")


def test1_2(answer):
    if answer == 1000000:
        print("Roger Roger")
    else:
        print("Your marketing_costs variable is not correct.")


def test1_3(answer):
    if answer == 1000000000:
        print("Grifftacular")
    else:
        print("Your ticket_sales variable is not correct.")


def test1_4(answer):
    if answer == 0.1:
        print("Turbo Man")
    else:
        print("Your theater_commission variable is not correct.")


def test1_5(answer):
    if answer == 399000000.0:
        print("Evil chickens")
    else:
        print("Your estimated_profits variable is not correct.")


# Project 1 Problem 2
def test1_6(answer):
    if answer == 500000:
        print("Go go gocarts")
    else:
        print("Your total_seats variable is not correct.")


def test1_7(answer):
    if answer == 13:
        print("Space monkeys")
    else:
        print("Your seat_batches variable is not correct.")


def test1_8(answer):
    if answer == 7:
        print("Dang those naughty space monkeys")
    else:
        print("Your remaining_seats variable is not correct.")


# Project 1 Problem 3
def test1_9(answer):
    if answer == 0:
        print("Manic manikin")
    else:
        print("Your kyle_production variable is not correct.")


def test1_10(answer):
    if answer == 0:
        print("Manic Monday")
    else:
        print("Your kelly_production variable is not correct.")


def test1_11(answer):
    if answer == 1:
        print("Manic monkeys")
    else:
        print("Your konner_production variable is not correct.")


def test1_12(answer):
    if answer == 4:
        print("Manic money")
    else:
        print("Your kevin_production variable is not correct.")


def test1_13(answer):
    if answer == 3:
        print("Manic munchkins")
    else:
        print("Your kassy_production variable is not correct.")


def test1_14(answer):
    if answer == 3:
        print("Manic munchies")
    else:
        print("Your kali_production variable is not correct.")


def test1_15(answer):
    if answer == 6:
        print("Manic motors")
    else:
        print("Your krissy_production variable is not correct.")


def test1_16(answer):
    if answer == 6:
        print("Manic makeup")
    else:
        print("Your kendall_production variable is not correct.")


def test1_17(answer):
    if answer == 0:
        print("Manic mill")
    else:
        print("Your kassy2_production variable is not correct.")


def test1_18(answer):
    if answer == (0.5 + 0.5 + 1 + 2):
        print("Manic mastif")
    else:
        print("Your kris_production variable is not correct.")


def test1_19(answer):
    if answer == (2 + 2 + 1 + 6):
        print("Manic moonlight")
    else:
        print("Your katelynn_production variable is not correct.")


def test1_20(answer):
    if answer == 0:
        print("Manic mayor")
    else:
        print("Your todd_production variable is not correct.")


def test1_21(answer):
    if answer == 38.0:
        print('Manic "m" words')
    else:
        print("Your total_production variable is not correct.")


# Project 1 Problem 4
def test1_22(answer):
    if answer == 1000000000:
        print("Wowzers!")
    else:
        print("Your number_of_funny_people variable does not return 1000000000")

# Project 1 Problem 5
def test1_23(business, street, city, state, zipcode, whole_address):
        if business == "Wile E. Coyote's Ballistics" and street == '3210 "Fullproof" Way' and city == 'Backfire' and state == 'Onyou' and zipcode == '92328' and whole_address == """Wile E. Coyote's Ballistics, 3210 "Fullproof" Way, Backfire, Onyou 92328""":
            print("Meep Meep!")
        else:
            print("One or more of your variables are not formatted properly")

# Project 1 Problem 6
def test1_24(boolean1, boolean2, boolean3, boolean4):
    if boolean1 and boolean2 and boolean3 and boolean4:
        print('I am not responsible for any injury or death which may occur as a result of Rabid Rabbit Wrangling')
    else:
        print('You answer is incorrect')


# Project 2 Problem 1
def test2_1(favorite_things):
    if len(favorite_things) and favorite_things[3] == "Cinnamon Rolls":
        print('Cinnamon + Sugar = Yummy')
    else:
        print("Your list is either the wrong length or the 'Cinnamon Rolls' item is in the wrong index")

def test2_2(favorite_things, favorite_things_str):
        joined_ls = ', '.join(favorite_things)
        str_intro = "A few of my favorite things: "
        favorite_str = str_intro + joined_ls
        if favorite_things_str == favorite_str:
            print('Cinnamontopia')
        else:
            print('Your favorite things string is incorrect')

def test2_3(favorite_things_ls, sadly_shorter_favorite_things_ls):
    if favorite_things_ls[:-1] == sadly_shorter_favorite_things_ls:
        print('Mount Kerinci - world cinnamon capitol')
    else:
        print('Your shortened list is incorrect')

def test2_4(bugs_height):
    if bugs_height == '3 ft. 3 in':
        print("Say, you wouldn't be that scwewy wabbit, would you?")
    else:
        print('Incorrect')

def test2_5(bugs_third_nemesis):
    if bugs_third_nemesis == "Cecil Turtle":
        print("Now take rabbits. They're built all wrong for racing")
    else:
        print('Incorrect')

def test2_6(daffy_second_episode_year):
    if daffy_second_episode_year == 1951:
        print("I'm rich! I'm wealthy! I'm independent! I'm socially secure!")
    else:
        print('Incorrect')

def test2_7(yosemite_third_catchphrase):
    if yosemite_third_catchphrase == "Ooooo! I hate that rabbit!":
        print("Welcome to the house of Sam.")
    else:
        print('Incorrect')

def test2_8(dad_jokes, dad_jokes_modified):
    try:
        if dad_jokes_modified == dad_jokes.replace('!', '.'):
            print('Pickle suckers')
        else:
            print('Your modified dad jokes text is incorrect')
    except:
        print('Incorrect')

def test2_9(total_jokes, cow_jokes, perc_cow_jokes):
    if total_jokes == 185 and cow_jokes == 11:
        if perc_cow_jokes == cow_jokes / total_jokes:
            print("Cowabunga")
        else:
            print('Your percentage is incorrect')
    else:
        print('Either your total_jokes or your cow_jokes or both are incorrect')

def test2_10(dad_jokes, dad_jokes_ls):
    joke_ls = dad_jokes.split('\n')
    if joke_ls == dad_jokes_ls:
        print("Monty Python")
    else:
        print("Your list is incorrect")

def test2_11(dad_jokes, mod_jokes_ls):
    joke_ls = dad_jokes.split('\n')[3:]
    if joke_ls == mod_jokes_ls:
        print('Nokia brick phones')
    else:
        print('Your modified list is incorrect')

def test2_12(dad_jokes, joke_index):
    joke_ls = dad_jokes.split('\n')[3:]
    joke_idx = joke_ls.index('Why don’t eggs tell jokes? They’d crack each other up.')
    if joke_idx == joke_index:
        print("Two roads diverged")
    else:
        print('Your index is incorrect')

def test2_13(weapons, places, suspects, possible_solutions):
    answer = []
    try:
        for weapon in weapons:
            for place in places:
                for suspect in suspects:
                    combo = "Ty was killed by " + weapon + " in the " + place + " by " + suspect
                    answer.append(combo)
    except:
        print('There is an error with the weapons, places, and/or suspects variable(s)')

    try:
        if answer == possible_solutions:
            print('Rikki-tikky-tavi')
        else:
            print('Your possible_solutions list is incorrect')
    except:
        print('Your possible_solutions list is incorrect')

# Project 3 Problem 1
def test3_1(answer1, answer2):
    if answer1 in [70, 77] and answer2 == 80:
        print("Tacolicious")
    else:
        print("Your ty_luck and/or ty_skill variable(s) is/are incorrect.")

def test3_2(answer):
    if answer == "Anywhere and Anything":
        print("Chicken chapstick")
    else:
        print(
            "You're condition for a bank account with $10,000 or more in it is incorrect."
        )


def test3_3(answer):
    if answer == "Fine dining establishment and order a decent meal":
        print("Cool whip machine gun")
    else:
        print(
            "You're condition for a bank account with less than $10,000 but more than $5,000 is incorrect."
        )


def test3_4(answer):
    if answer == "Average fast food restaurant occasionally":
        print("Yabadabadoo!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test3_5(answer):
    if answer == "Average fast food restaurant occasionally":
        print("Jinkees!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test3_6(answer):
    if answer == "Average fast food restaurant occasionally":
        print("To infinity, and beyond!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test3_7(answer):
    if answer == "Hearty home-cooked meal at home sweet home":
        print("Tarter sauce!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test3_8(answer):
    if answer == "Modest meal at home":
        print("Ninja archer")
    else:
        print(
            "You're condition for what choice to make when you have $1,000 or less but more than $0 is incorrect."
        )


def test3_9(answer):
    if answer == "Meals involving primarily noodles or rice":
        print("Sumo suit scuba diving")
    else:
        print(
            "You're condition for what choice to make when you have $1,000 or less but more than $0 is incorrect."
        )


def test3_10(answer):
    if (
        answer
        == "Research how to make the stray cat that foolishly wandered into your yard last for more than 3 meals"
    ):
        print("Creative juices smoothie")
    else:
        print("You're condition for what choice to make when you have $0 is incorrect.")


def test3_11(answer, noun, verb, adjective, story_list):
    noun = noun
    verb = verb
    adjective = adjective

    story_test = ""
    for i in story_list:
        if isinstance(i, str):
            story_test += i
        else:
            if i == 1:
                story_test += noun
            elif i == 2:
                story_test += verb
            else:
                story_test += adjective

    if answer == story_test:
        print("Snozzberries")
    else:
        print("You did not create the mad_libs function correctly.")
        print(story_test)


#PROJECT 4
def test4_1(answer):
    if answer == -0.2222222222222222:
        print("Kamikaze kitty")
    else:
        print("Your answer is incorrect")

def test4_2(answer):
    if answer == 4:
        print("Self-cleaning toilets, it's going to be big")
    else:
        print("Your answer is incorrect")

def test4_3(answer):
    if answer == 7:
        print("Kangarodeo")
    else:
        print("Your answer is incorrect")

def test4_4(answer):
    if answer == 1:
        print("Strazbanana")
    else:
        print("Your answer is incorrect")

def test4_5(answer):
    if answer == 0:
        print("Wilderpeople")
    else:
        print("Your answer is incorrect")

def test4_6(incident_ls, answer_df):
    incident_df = pd.DataFrame(incident_ls, columns=['Date', 'Category', 'Details', 'Estimated Cost'])
    if incident_df.equals(answer_df):
        print("Gravity Falls")
    else:
        print("Your dataframe is incorrect")

def test4_7(incident_ls, answer):
    incident_df = pd.DataFrame(incident_ls, columns=['Date', 'Category', 'Details', 'Estimated Cost'])
    index_value = incident_df.iloc[3,2]
    if index_value == answer:
        print("Gruncle Stan")
    else:
        print("Your answer is incorrect")

def test4_8(incident_ls, answer_df):
    incident_df = pd.DataFrame(incident_ls, columns=['Date', 'Category', 'Details', 'Estimated Cost'])
    filtered_df = incident_df[incident_df['Estimated Cost'] > 500000]
    if filtered_df.equals(answer_df):
        print("Angry Angels")
    else:
        print("Your answer is incorrect")

def test4_9(incident_ls, answer_df):
    incident_df = pd.DataFrame(incident_ls, columns=['Date', 'Category', 'Details', 'Estimated Cost'])
    grouped_df = incident_df.groupby('Category')['Estimated Cost'].sum().reset_index()
    if grouped_df.equals(answer_df):
        print("Haunted Hot Dogs")
    else:
        print("Your answer is incorrect")

def test4_10(incident_ls, answer_df):
    incident_df = pd.DataFrame(incident_ls, columns=['Date', 'Category', 'Details', 'Estimated Cost'])
    top_3_df = incident_df.sort_values(['Estimated Cost'], ascending=False).head(3)
    if top_3_df.equals(answer_df):
        print("Goat Warriors")
    else:
        print("Your answer is incorrect")



# PROJECT 5

# Question 1
def test5_1(answer):
    if answer == "bed_bath_table":
        print("Taco Tornado")
    else:
        print("Your answer is incorrect.")


# Question 2
def test5_2(answer):
    if answer == "health_beauty":
        print("Enchilada Earthquake")
    else:
        print("Your answer is incorrect.")


# Question 3
def test5_3(answer):
    if answer == '6560211a19b47992c3666cc44a7e94c0':
        print("Hummus Hurricane")
    else:
        print("Your answer is incorrect.")


# Question 4
def test5_4(answer):
    if answer == "computers_accessories":
        print("Hamburger Hailstorm")
    else:
        print("Your answer is incorrect.")


# Question 5
def test5_5(answer):
    data = {
        "month": [
            "2017-01",
            "2017-02",
            "2017-03",
            "2017-04",
            "2017-05",
            "2017-06",
            "2017-07",
            "2017-08",
            "2017-09",
            "2017-10",
            "2017-11",
            "2017-12",
        ],
        "avg_order": [
            173.88,
            165.19,
            163.59,
            172.49,
            160.16,
            156.35,
            147.39,
            155.65,
            169.79,
            168.41,
            158.25,
            153.55,
        ],
    }

    df = pd.DataFrame(data)
    if df.equals(answer):
        print("French Fries Flash Flood")
    else:
        print("Your answer is incorrect.")


# Question 6
def test5_6(answer1, answer2):
    if answer1 == 4.29 and answer2 == 2.35:
        print("Avocado Avalanche")
    else:
        print("Your answer is incorrect.")


# Question 7
def test5_7(answer):
    if answer == 0.51:
        print("Lasagna Lighting Storm")
    else:
        print("Your answer is incorrect.")


#PROJECT 6
def content_scoring_test(r):
    if r == "G":
        return 0
    elif r == "PG":
        return 1
    elif r == "PG-13":
        return 2
    elif r == "R":
        return 3
    else:
        return 4


def movie_filter_test(movie_tuples):
    movies_list = []
    omdb.set_default("apikey", "c0e2b3c2")
    for m in movie_tuples:
        movie = omdb.get(title=m[0], year=m[1], fullplot=True)
        if movie == {}:
            continue
        content = movie["rated"]
        genres = movie["genre"]
        try:
            imdb_rating = float(movie["imdb_rating"])
        except:
            imdb_rating = 0
        movie_list = [
            m[0],
            m[1],
            content,
            genres,
            imdb_rating,
        ]
        movies_list.append(movie_list)

    return movies_list


def filter_test(
    movies_list, content=None, genre=None, imdb=None, rotten=None, meta=None
):
    keeper_movies = []
    for m in movies_list:
        if content:
            if content_scoring_test(m[2]) <= content_scoring_test(content):
                pass
            else:
                continue
        if genre:
            if genre.lower() in m[3].lower():
                pass
            else:
                continue
        if imdb:
            if m[4] >= imdb:
                pass
            else:
                continue
        keeper_movies.append(m)
    return keeper_movies


def test6_1(
    answer, movies, content=None, genre=None, imdb=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, content=content, genre=genre)

    if filtered_movies == answer:
        print("Candy-Filled Fireworks")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, 'G', genre='Animation')'"
        )


def test6_2(
    answer, movies, content=None, genre=None, imdb=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, content=content, imdb=imdb)

    if filtered_movies == answer:
        print("Chocolate Syrup Shower")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, 'R', imdb=8.0)'"
        )


def test6_3(
    answer, movies, content=None, genre=None, imdb=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, content=content, imdb=imdb)

    if filtered_movies == answer:
        print("Gumball Bullets")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, 'PG', imdb=7.5)'"
        )


def test6_4(
    answer, movies, content=None, genre=None, imdb=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, genre=genre, imdb=imdb)

    if filtered_movies == answer:
        print("Fully Automatic PEZ Dispensers")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, genre='Action', imdb=8.2)'"
        )



#PROJECT 7
def test7_1(answer):
    test = [
        (
            "tconst",
            "titleType",
            "primaryTitle",
            "originalTitle",
            "isAdult",
            "startYear",
            "endYear",
            "runtimeMinutes",
            "genres",
        ),
        (
            "tt0000001",
            "short",
            "Carmencita",
            "Carmencita",
            0,
            1894,
            "\\N",
            1,
            "Documentary,Short",
        ),
        (
            "tt0000002",
            "short",
            "Le clown et ses chiens",
            "Le clown et ses chiens",
            0,
            1892,
            "\\N",
            5,
            "Animation,Short",
        ),
        (
            "tt0000003",
            "short",
            "Pauvre Pierrot",
            "Pauvre Pierrot",
            0,
            1892,
            "\\N",
            4,
            "Animation,Comedy,Romance",
        ),
        (
            "tt0000004",
            "short",
            "Un bon bock",
            "Un bon bock",
            0,
            1892,
            "\\N",
            12,
            "Animation,Short",
        ),
        (
            "tt0000005",
            "short",
            "Blacksmith Scene",
            "Blacksmith Scene",
            0,
            1893,
            "\\N",
            1,
            "Comedy,Short",
        ),
        (
            "tt0000006",
            "short",
            "Chinese Opium Den",
            "Chinese Opium Den",
            0,
            1894,
            "\\N",
            1,
            "Short",
        ),
        (
            "tt0000007",
            "short",
            "Corbett and Courtney Before the Kinetograph",
            "Corbett and Courtney Before the Kinetograph",
            0,
            1894,
            "\\N",
            1,
            "Short,Sport",
        ),
        (
            "tt0000008",
            "short",
            "Edison Kinetoscopic Record of a Sneeze",
            "Edison Kinetoscopic Record of a Sneeze",
            0,
            1894,
            "\\N",
            1,
            "Documentary,Short",
        ),
        (
            "tt0000009",
            "movie",
            "Miss Jerry",
            "Miss Jerry",
            0,
            1894,
            "\\N",
            45,
            "Romance",
        ),
    ]
    if answer == test:
        print("Bippity Boppity Boo")
    else:
        print(
            "Your result for 'SELECT * FROM movies_basics ORDER BY tconst LIMIT 10' does not match the expected result."
        )


def test7_2(answer):
    test = [
        (
            "tt0102291",
            "movie",
            "Der letzte Winter",
            "Der letzte Winter",
            0,
            1991,
            "\\N",
            55,
            "Drama",
        ),
        (
            "tt0102290",
            "tvMovie",
            "Not Mozart: Letters, Riddles and Writs",
            "Not Mozart: Letters, Riddles and Writs",
            0,
            1991,
            "\\N",
            30,
            "\\N",
        ),
        (
            "tt0102289",
            "tvMovie",
            "Lethal Innocence",
            "Lethal Innocence",
            0,
            1991,
            "\\N",
            90,
            "Drama",
        ),
        (
            "tt0102288",
            "movie",
            "Let Him Have It",
            "Let Him Have It",
            0,
            1991,
            "\\N",
            115,
            "Crime,Drama,History",
        ),
        ("tt0102287", "tvMovie", "Leporella", "Leporella", 0, 1991, "\\N", 74, "Drama"),
        (
            "tt0102286",
            "movie",
            "Tiger Cage III",
            "Leng mian ju ji shou",
            0,
            1991,
            "\\N",
            94,
            "Action",
        ),
        (
            "tt0102285",
            "movie",
            "Lena's Holiday",
            "Lena's Holiday",
            0,
            1991,
            "\\N",
            100,
            "Comedy,Romance,Thriller",
        ),
        (
            "tt0102284",
            "movie",
            "Leise Schatten",
            "Leise Schatten",
            0,
            1992,
            "\\N",
            91,
            "Drama",
        ),
        (
            "tt0102283",
            "movie",
            "Legal Tender",
            "Legal Tender",
            0,
            1991,
            "\\N",
            95,
            "Action,Thriller",
        ),
        (
            "tt0102282",
            "movie",
            "Lebewohl, Fremde",
            "Lebewohl, Fremde",
            0,
            1991,
            "\\N",
            100,
            "Drama,Romance",
        ),
    ]
    if answer == test:
        print("Alakazam!")
    else:
        print(
            "Your result for 'SELECT * FROM movies_basics ORDER BY tconst DESC LIMIT 10' does not match the expected result."
        )


# # Project 7 Problem 1
# def test7_1(answer):
#     test = [
#         ("tconst", "directors", "writers"),
#         ("tt0000001", "nm0005690", "\\N"),
#         ("tt0000002", "nm0721526", "\\N"),
#         ("tt0000003", "nm0721526", "\\N"),
#         ("tt0000004", "nm0721526", "\\N"),
#         ("tt0000005", "nm0005690", "\\N"),
#         ("tt0000006", "nm0005690", "\\N"),
#         ("tt0000007", "nm0005690,nm0374658", "\\N"),
#         ("tt0000008", "nm0005690", "\\N"),
#         ("tt0000009", "nm0085156", "nm0085156"),
#     ]
#     if answer == test:
#         print("Succotash")
#     else:
#         print(
#             "Your result for 'SELECT * FROM movies_crew ORDER BY tconst LIMIT 10' does not match the expected result."
#         )


# def test7_2(answer):
#     test = [
#         ("tt0102291", "nm0881355", "\\N"),
#         ("tt0102290", "nm0310561,nm0628430", "nm0310561,nm0628430,nm0006219"),
#         ("tt0102289", "nm0926301", "nm0926301"),
#         ("tt0102288", "nm0575389", "nm0701031,nm0905498"),
#         ("tt0102287", "nm0198699", "nm0198699,nm0959003"),
#         ("tt0102286", "nm0950759", "nm2060068,nm0504980"),
#         ("tt0102285", "nm0450661", "nm0863503,nm0450661"),
#         ("tt0102284", "nm0394776", "nm0394776"),
#         ("tt0102283", "nm0612730", "nm0730848"),
#         ("tt0102282", "nm0059725", "nm0059725"),
#     ]
#     if answer == test:
#         print("Sassafras")
#     else:
#         print(
#             "Your result for 'SELECT * FROM movies_crew ORDER BY tconst DESC LIMIT 10' does not match the expected result."
#         )


# # Project 7 Problem 2
# def test7_3(answer):
#     test = [
#         ("tconst", "averageRating", "numVotes"),
#         ("tt0000001", 5.7, 1993),
#         ("tt0000002", 5.8, 268),
#         ("tt0000003", 6.5, 1879),
#         ("tt0000004", 5.5, 177),
#         ("tt0000005", 6.2, 2662),
#         ("tt0000006", 5.0, 182),
#         ("tt0000007", 5.4, 834),
#         ("tt0000008", 5.4, 2136),
#         ("tt0000009", 5.3, 206),
#     ]
#     if answer == test:
#         print("Marmalade")
#     else:
#         print(
#             "Your result for 'SELECT * FROM movies_ratings ORDER BY tconst LIMIT 10' does not match the expected result."
#         )


# def test7_4(answer):
#     test = [
#         ("tt0139287", 6.8, 12),
#         ("tt0139286", 6.1, 13),
#         ("tt0139283", 6.8, 102),
#         ("tt0139276", 7.1, 105),
#         ("tt0139275", 5.7, 136),
#         ("tt0139274", 5.2, 140),
#         ("tt0139272", 5.5, 140),
#         ("tt0139269", 5.7, 26),
#         ("tt0139267", 5.1, 22),
#         ("tt0139266", 5.3, 113),
#     ]
#     if answer == test:
#         print("Periwinkle")
#     else:
#         print(
#             "Your result for 'SELECT * FROM movies_ratings ORDER BY tconst DESC LIMIT 10' does not match the expected result."
#         )


# # Project 7 Problem 3
# def test7_5(answer):
#     test = [
#         ("The Simpsons", 8.7, 424381),
#         ("Star Wars: Episode IV - A New Hope", 8.6, 1414060),
#         ("Mr. Bean", 8.6, 128266),
#         ("Apocalypse Now", 8.4, 692100),
#         ("Amadeus", 8.4, 416996),
#         ("Network", 8.1, 165776),
#         ("Dog Day Afternoon", 8.0, 267726),
#         ("The Conversation", 7.8, 117551),
#         ("Serpico", 7.7, 130667),
#         ("The Godfather Part III", 7.6, 413886),
#     ]
#     if answer == test:
#         print("Vantablack")
#     else:
#         print(
#             "Your query does not return the expected results. The top 10 expected films (not in order) are: The Godfather Part III, The Conversation, Network, Apocalypse Now, Star Wars: Episode IV - A New Hope, Sercipo, Dog Day Afternoon, Amadeus, Mr. Bean, The Simpsons"
#         )


