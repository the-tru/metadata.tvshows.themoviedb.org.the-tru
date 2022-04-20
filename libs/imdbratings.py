# -*- coding: UTF-8 -*-
#
# Copyright (C) 2020, Team Kodi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# IMDb ratings based on code in metadata.themoviedb.org.python by Team Kodi
# pylint: disable=missing-docstring


import re
import json
from . import api_utils
from . import settings

IMDB_RATINGS_URL = 'https://www.imdb.com/title/{}/'
IMDB_JSON_REGEX = re.compile(
    r'<script type="application\/ld\+json">(.*?)<\/script>')
IMDB_RUNTIME_REGEX = re.compile(
    r'PT([0-9]*)[^0-9]*([0-9]*)')

def get_details(imdb_id):
    if not imdb_id:
        return {}
    votes, rating, runtime = _get_ratinginfo(imdb_id)
    return _assemble_imdb_result(votes, rating, runtime)


def _get_ratinginfo(imdb_id):
    response = api_utils.load_info(IMDB_RATINGS_URL.format(
        imdb_id), default='', resp_type='text', verboselog=settings.VERBOSELOG)
    return _parse_imdb_result(response)


def _assemble_imdb_result(votes, rating, runtime):
    result = {}
    if votes and rating:
        result['ratings'] = {'imdb': {'votes': votes, 'rating': rating}}
    if runtime:
        result['runtime'] = runtime
    return result


def _parse_imdb_result(input_html):
    match = re.search(IMDB_JSON_REGEX, input_html)
    if not match:
        return None, None, 0
    imdb_json = json.loads(match.group(1))
    imdb_ratings = imdb_json.get("aggregateRating", {})
    rating = imdb_ratings.get("ratingValue", None)
    votes = imdb_ratings.get("ratingCount", None)
    runtime_str = imdb_json.get("duration", '')
    match = re.search(IMDB_RUNTIME_REGEX, runtime_str)
    runtime = 0
    if match:
        if match.group(2):
            runtime = int(match.group(1)) * 3600 + int(match.group(2)) * 60
        elif int(match.group(1)) < 10:
            runtime = int(match.group(1)) * 3600
        else:
            runtime = int(match.group(1)) * 60
    return votes, rating, runtime
