"""
.. module:: dataextraction
    :synopsis: A module to extract various kinds of movie data from the IMSDb HTML pages

.. moduleauthor:: Pedro Araujo <pedroaraujo@colorlesscube.com>
.. moduleauthor:: Pedro Nogueira <pedro.fig.nogueira@gmail.com>
"""

import re
import difflib
import logging

from classMovieCharacter import *

def extract_movie_characters(movie_html_script):
    """This function receives as a parameter a list containing the movie
    lines in the format of the IMSDb HTML page.

    The HTML page will be parsed using a regular expression which will
    extract all the possible candidates for movie characters.

    After the extraction of those candidates, the function will reject all
    false positives classified as such by the function valid_movie_character().

    Each character will be added to a new object from the
    class classMovieCharacter.

    Each object will then be added to a list of objects to be returned in
    the end of the function.

    No repeated characters shall be added to the list.

    Args:
        movie_html_script (list of strings): The file containing the
        IMSDb HTML page

    Returns:
        list of classMovieCharacter: This list contains all the detected
        movie characters from the IMSDb movie script
    """

    logger = logging.getLogger(__name__)
    logger.info('Extracting the characters...')

    movie_extracted_characters = []
    movie_characters_list = []

    # Regex used to extract the movie characters
    regex_code = ur'<b>(?!EXT)(?!SUPER)(?P<movie_char>.*?)<\/b>(?P<movie_text>.*?)(?=<b>)'

    for m in re.finditer(regex_code, movie_html_script):
        movie_extracted_characters.append(m.group('movie_char'))
    
    for l in movie_extracted_characters:
        if not valid_movie_character(l):
            continue
        
        movie_character_name = strip_unwanted_strings(l)

        # TODO: Remove this hack and fix the issue
        # The movie script as characters represented as "Merry & Pippin"
        # And the Regex code is extracting empty strings as characters
        if '&amp;' in movie_character_name or not movie_character_name:
            logger.debug('Rejecting possible invalid character: ' + movie_character_name)
            continue

        if similar_movie_character_already_added(movie_characters_list, movie_character_name):
            continue

        # Check if the character was already collected in the list
        for existent_movie_character in movie_characters_list:
            if movie_character_name in existent_movie_character.name:
                break
        else:
            logger.info('Adding character... ' + movie_character_name)
            movie_characters_list.append(classMovieCharacter(movie_character_name))

    return movie_characters_list

def valid_movie_character(possible_movie_character_name):
    """This function analyzes the candidate to be added to the movie
    character list and detects if it is a valid character of not.

    The function is needed because the regex used will parse the meta
    tags from the movie script, like 'INT', 'EXT' or 'CONTINUATION',
    as a movie character, as these tags are at bold in the HTML script
    like a normal movie character.

    A valid character is considered the one that it is a bold (already
    parsed by the script) and centered in the text.
    If the candidate string is not centered, it will be marked as invalid.

    Args:
        possible_movie_character_name (string): The name of the candidate
        string to movie character

    Returns:
        Bool: True if it is a valid character name, False otherwise
    """
    logger = logging.getLogger(__name__)

    # Consider valid characters the names that are centered
    numberWhitespaces = len(possible_movie_character_name) - len(possible_movie_character_name.lstrip(' '))

    if numberWhitespaces<20 or numberWhitespaces>30:
        logger.debug('Rejecting possible invalid character due to the number' \
                     'of whitespaces at the start of the string \
                     (' + str(numberWhitespaces) + '): ' + possible_movie_character_name)
        return False
    else:
        return True

def strip_unwanted_strings(movie_character_name):
    """This function remove any unwanted strings from the character's names.

    The unwanted strings are:
        - "(V.O.)"
        - "(CONT'D)"
        - Any multiple whitespaces

    Args:
        movie_character_name (string): The name of the movie character

    Returns:
        String: Returns a string clean from all unwanted strings
    """
    # Remove "(V.O.)" and "(CONT'D)" from characters' names
    stripped_movie_character_name = movie_character_name.split('(')[0]

    # Remove all of the unecessary whitespaces
    stripped_movie_character_name = " ".join(stripped_movie_character_name.split())

    return stripped_movie_character_name

def similar_movie_character_already_added(movie_characters_list, movie_character_name):
    """The API assumes that the movie script has misspelled character names,
    so this function checks if the new candidate to movie character has a
    similar character name already added to the list.

    The function will reject names with 90% of similarity, or more, with any
    of the already present movie characters' name in the list.

    Args:
        movie_characters_list (list of classMovieCharacter): List of all movie
        characters already collected
        movie_character_name (string): The name of the candidate to
        movie character

    Returns:
        Bool: True if already exists a character with a similar name,
        False otherwise
    """
    logger = logging.getLogger(__name__)

    # The "Fellowship of the Ring" script sometimes misspells "FRODO" as
    # "FRO DO" this function attempts to fix that
    for l in movie_characters_list:
        similarityRatio = difflib.SequenceMatcher(None,
                                                  movie_character_name.lower(),
                                                  l.name.split(' ')[0].lower())
        similarityRatio = similarityRatio.ratio()

        if similarityRatio>0.9 and similarityRatio<1.0:
            logger.debug('Possible character already added: ' + \
                         movie_character_name)
            return True
    else:
        return False
