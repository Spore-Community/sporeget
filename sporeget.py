#!/usr/bin/python
'''Prints a list of spore.com links to download.
Should be used inside of an automatic script along with some downloading tool.
Exit codes:
    0 - success, links returned;
    1 - fail, error printed;
    -1 - not enough arguments, help shown.'''

from sys import exit as system_exit, argv, stdout
from argparse import RawTextHelpFormatter
import re
import xml.etree.ElementTree as ET
import argparse
import requests

__author__ = '0KepOnline' # https://github.com/0KepOnline
__license__ = 'Unlicense' # http://unlicense.org
__maintainer__ = '0KepOnline'
__email__ = 'i.am@scenariopla.net'
__status__ = 'Production'



_WWW_ = 'http://www.spore.com'
REST = _WWW_ + '/rest'
ATOM = _WWW_ + '/atom'
VIEW = _WWW_ + '/view'

_STATIC_ = 'http://static.spore.com'
STATIC = _STATIC_ + '/static'

_POLLINATOR_ = 'http://pollinator.spore.com/pollinator'
ATOM_POLLINATOR = _POLLINATOR_ + '/atom'


REST_PAGE_LIMIT = 500
REQUESTS_TIMEOUT = 30
REGEX_ASSET = r'tag:spore\.com,2006:asset\/(\d+(?=\D))'
REGEX_ASSET_ADV = \
    r'<\/entry>(?:(?!<\/entry>).)*?' \
    r'tag:spore\.com,2006:asset\/(\d+(?=\D))' \
    r'.*?application\/x-adventure\+xml.*?<entry>'
REGEX_TAGLINE = r'<tagline>.*?<\/tagline>'
REGEX_NAME = r'<name>.*?<\/name>'



HELP_COMMANDS = {
    'asset':
        'links for a single creation; creation ID is an argument.',
    'user':
        'links for user data and all the creations made by a user; the username is an argument.',
    'feed':
        'links for all the creations in a feed (sporecast/aggregator); feed ID is an argument.'
}

def help_cmd(command_name):
    '''Returns a command name with ANSI color codes if supported.'''
    if (hasattr(stdout, 'isatty') and stdout.isatty()):
        return f'\x1b[1;39;49m{command_name}\x1b[0;0;0m'
    return command_name

def help_dict(return_names=False):
    '''Interprets the help dictionary for different functions.'''
    dict_parsed = 'commands:\n'
    dict_command_names = []
    for command_name, command_description in HELP_COMMANDS.items():
        dict_command_names.append(command_name)
        dict_parsed += f'  {help_cmd(command_name)}\t— {command_description}\n'
    if return_names is True:
        return dict_command_names
    return dict_parsed


def exit_with_help() -> None:
    '''Prints a help and exits with an exit code of -1.'''
    parser.print_help()
    system_exit(-1)

def exit_with_error(error_text) -> None:
    '''Prints a error and exits with an exit code of 1.'''
    print(error_text)
    system_exit(1)

def exit_with_links(links_array) -> None:
    '''Returns links and exits with an exit code of 0.'''
    links_array_unique = set(links_array)
    for link in links_array_unique:
        print(link)
    system_exit(0)

def print_debug(message_text) -> None:
    '''Prints a debug message (according to the "--debug" option).'''
    if debug is True:
        print(message_text)



def list_rest_pages(arg, endpoint, elem, subtype=None, return_tree=False):
    '''Returns links to all the REST pages; requires an Internet connection.'''
    page = 0
    links = []
    tree = []
    while True:
        print_debug(f'Retrieving {endpoint} page {page + 1} for {arg}...')
        rest_page_link = f'{REST}/{endpoint}/{arg}/{page * REST_PAGE_LIMIT}/{REST_PAGE_LIMIT}'
        if subtype:
            rest_page_link += f'/{subtype}'
        try:
            rest_page = requests.get(
                rest_page_link,
                timeout=REQUESTS_TIMEOUT
            )
        except requests.exceptions.Timeout:
            exit_with_error(
                f'Error on retrieving {endpoint} page {page + 1}: Timed out ({REQUESTS_TIMEOUT}).'
            )
        status_code = rest_page.status_code
        if status_code == 200:
            root = ET.fromstring(rest_page.text)
            rest_page_count = len(root.findall(f'.//{elem}'))
            links.append(rest_page_link)
            if return_tree is True:
                for element in root.findall(f'.//{elem}'):
                    tree.append(element)
            if rest_page_count < REST_PAGE_LIMIT:
                if return_tree is True:
                    return tree
                return links
            page += 1
        else:
            exit_with_error(
                f'Error on retrieving {endpoint} page {page + 1}: status code {status_code}.'
            )

def to_user_id(username):
    '''Returns user ID for a username; requires an Internet connection.'''
    rest_user_link = f'{REST}/user/{username}'
    try:
        rest_user_response = requests.get(
            rest_user_link,
            timeout=REQUESTS_TIMEOUT
        )
    except requests.exceptions.Timeout:
        exit_with_error(
            f'Error on retrieving user ID for {username}: Timed out ({REQUESTS_TIMEOUT}).'
        )
    status_code = rest_user_response.status_code
    if status_code == 200:
        root = ET.fromstring(rest_user_response.text)
        status = int(root.find('status').text)
        if status == 1:
            user_id = root.find('id').text
            if user_id:
                return user_id
            exit_with_error(
                f'Error on retrieving user ID for {username}.'
            )
        else:
            exit_with_error(
                f'Error on retrieving user ID for {username}: user not found.'
            )
    else:
        exit_with_error(
            f'Error on retrieving user ID for {username}: status code {status_code}.'
        )
    return None

def to_links(arg, argtype=0):
    '''Returns all the links for an argument according to the type of it:
    argtype = 0 is for a creation ID (default);
    argtype = 1 is for a username;
    argtype = 2 is for a feed ID.'''
    links = []
    if argtype == 0:
        asset_id = arg
        if thumb_only is True:
            return [
                f'{STATIC}/thumb/{asset_id[0:3]}/{asset_id[3:6]}/{asset_id[6:9]}/{asset_id}.png'
            ]
        f_links_www_static = [
            f'{STATIC}/model/{asset_id[0:3]}/{asset_id[3:6]}/{asset_id[6:9]}/{asset_id}.xml',
            f'{STATIC}/thumb/{asset_id[0:3]}/{asset_id[3:6]}/{asset_id[6:9]}/{asset_id}.png',
            f'{STATIC}/image/{asset_id[0:3]}/{asset_id[3:6]}/{asset_id[6:9]}/{asset_id}_lrg.png'
        ]
        f_links_www_static_additional_images = [
            f'{STATIC}/image/{asset_id[0:3]}/{asset_id[3:6]}/{asset_id[6:9]}/{asset_id}_2_lrg.png',
            f'{STATIC}/image/{asset_id[0:3]}/{asset_id[3:6]}/{asset_id[6:9]}/{asset_id}_3_lrg.png',
            f'{STATIC}/image/{asset_id[0:3]}/{asset_id[3:6]}/{asset_id[6:9]}/{asset_id}_4_lrg.png'
        ]
        f_links_www_rest = [
            f'{REST}/creature/{asset_id}',
            f'{REST}/asset/{asset_id}'
        ]
        f_links_www_atom = [
            f'{ATOM}/events/asset/{asset_id}'
        ]
        f_links_pollinator_atom = [
            f'{ATOM_POLLINATOR}/asset/{asset_id}',
            f'{ATOM_POLLINATOR}/asset?id={asset_id}'
        ]

        links += f_links_www_static
        if exclude_quad_images is False:
            links += f_links_www_static_additional_images
        if static_only is False:
            if disable_comments_pagination is True:
                f_links_www_rest.append(f'{REST}/comments/{asset_id}/0/{REST_PAGE_LIMIT}')
            else:
                f_links_www_rest += list_rest_pages(asset_id, 'comments', 'comment')

            links += f_links_www_rest
            links += f_links_www_atom
            if exclude_pollinator is False:
                links += f_links_pollinator_atom

    if argtype == 1:
        username = arg
        user_id = to_user_id(arg)
        f_links_www_rest = [
            f'{REST}/user/{username}',
            f'{REST}/sporecasts/{username}'
        ]
        f_links_www_atom = [
            f'{ATOM}/assets/user/{username}',
            f'{ATOM}/events/user/{username}'
        ]
        f_links_www_view = [
            f'{VIEW}/user-thumbnail-count/{user_id}/0/100'
        ]
        f_links_www_view_myspore = [
            f'{VIEW}/myspore/{username}',
            f'{VIEW}/points/{username}',
            f'{VIEW}/trophies/{username}',
            f'{VIEW}/buddies/{username}',
            f'{VIEW}/events/{username}',
            f'{VIEW}/achievements/{username}'
        ]
        f_links_pollinator_atom = [
            f'{ATOM_POLLINATOR}/user/{user_id}'
        ]

        f_links_www_rest += list_rest_pages(username, 'assets/user', 'asset')
        #f_links_www_rest += list_rest_pages(username, 'assets/user', 'asset', 'CREATURE')
        #f_links_www_rest += list_rest_pages(username, 'assets/user', 'asset', 'BUILDING')
        #f_links_www_rest += list_rest_pages(username, 'assets/user', 'asset', 'VEHICLE')
        #f_links_www_rest += list_rest_pages(username, 'assets/user', 'asset', 'UFO')
        #f_links_www_rest += list_rest_pages(username, 'assets/user', 'asset', 'ADVENTURE')
        f_links_www_rest += list_rest_pages(username, 'achievements', 'achievement')
        f_links_www_rest += list_rest_pages(username, 'users/buddies', 'buddy')
        f_links_www_rest += list_rest_pages(username, 'users/subscribers', 'buddy')

        links += f_links_www_rest
        links += f_links_www_atom
        links += f_links_www_view
        if exclude_myspore is False:
            links += f_links_www_view_myspore
        if exclude_pollinator is False:
            links += f_links_pollinator_atom
    if argtype == 2:
        feed_id = arg
        f_links_www_atom = [
            f'{ATOM}/sporecast/{feed_id}'
        ]
        f_links_pollinator_atom = [
            f'{ATOM_POLLINATOR}/aggregator/{feed_id}'
        ]

        f_links_www_rest = []
        f_links_www_rest += list_rest_pages(feed_id, 'assets/sporecast', 'asset')

        links += f_links_www_rest
        links += f_links_www_atom
        if exclude_pollinator is False:
            links += f_links_pollinator_atom
    print_debug(f'Added links for {arg}')
    return links



def asset(asset_id):
    '''Downloads a single creation ('asset' command).
    Creation ID is an argument.'''
    links = to_links(asset_id)
    if adv_assets is True:
        links += adv(asset_id)
    return links

def user(username):
    '''Downloads everything for a user ('user' command).
    The username is an argument.'''
    links = []
    user_id = to_user_id(username)
    print_debug(f'User ID found: {username} ==> {user_id}')
    if static_only is False:
        links = to_links(username, argtype=1)
    try:
        asset_count_response = requests.get(
            f'{VIEW}/user-thumbnail-count/{user_id}/0/0',
            timeout=REQUESTS_TIMEOUT
        )
    except requests.exceptions.Timeout:
        exit_with_error(
            f'Error on retrieving assets count for {username}: Timed out ({REQUESTS_TIMEOUT}).'
        )
    status_code_asset_count = asset_count_response.status_code
    if status_code_asset_count == 200:
        root_count = ET.fromstring(
            re.sub(REGEX_TAGLINE, '', asset_count_response.text)
        )
        asset_count = int(root_count.get('assetCount'))
        print_debug(f'Asset count for {username}: {asset_count}')
        if asset_count != 0:

            print_debug('Retrieving full assets list...')
            if static_only is False:
                links.append(f'{VIEW}/user-thumbnail-count/{user_id}/0/{asset_count}')
            try:
                asset_list_response = requests.get(
                    f'{VIEW}/user-thumbnail-count/{user_id}/0/{asset_count}',
                    timeout=REQUESTS_TIMEOUT
                )
            except requests.exceptions.Timeout:
                exit_with_error(
                    f'Error on retrieving assets list for {username}: Timed out ({REQUESTS_TIMEOUT}).'
                )
            status_code_asset_list = asset_list_response.status_code
            if status_code_asset_list == 200:
                root_list = ET.fromstring(
                    re.sub(REGEX_NAME, '',
                        re.sub(REGEX_TAGLINE, '', asset_list_response.text)
                    )
                )
                asset_list = root_list.find('.//assets').findall('asset')
                for asset_entry in asset_list:
                    links_asset = to_links(asset_entry.get('id'))
                    links += links_asset

            if adv_assets is True:
                asset_adv_list = list_rest_pages(username, 'assets/user', 'asset', 'ADVENTURE',
                    return_tree=True
                )
                for asset_adv_entry in asset_adv_list:
                    links_asset_adv = adv(asset_adv_entry.find('id').text)
                    links += links_asset_adv
    return links

def feed(feed_id):
    '''Downloads everything inside a feed ('feed' command).
    Feed ID is an argument.'''
    links = []
    if static_only is False:
        links = to_links(feed_id, argtype=2)
    print_debug('Retrieving full assets list...')
    try:
        asset_list_response = requests.get(
            f'{ATOM}/sporecast/{feed_id}',
            timeout=REQUESTS_TIMEOUT
        )
    except requests.exceptions.Timeout:
        exit_with_error(
            f'Error on retrieving assets list for {feed_id}: Timed out ({REQUESTS_TIMEOUT}).'
        )
    status_code = asset_list_response.status_code
    if status_code == 200:
        asset_list_regex = re.findall(REGEX_ASSET, asset_list_response.text)
        for asset_match in asset_list_regex:
            links_asset = to_links(asset_match)
            links += links_asset
        if adv_assets is True:
            asset_list_adv_regex = re.findall(REGEX_ASSET_ADV, asset_list_response.text)
            for asset_adv_match in asset_list_adv_regex:
                links_asset_adv = adv(asset_adv_match)
                links += links_asset_adv

    else:
        exit_with_error(
            f'Error on retrieving assets list for {feed_id}: status code {status_code}.'
        )

    return links

def adv(adv_id):
    '''Downloads an adventure with all the assets ('adv' command).
    Adventure ID is an argument.'''
    links = []
    try:
        adv_model_response = requests.get(
            f'{STATIC}/model/{adv_id[0:3]}/{adv_id[3:6]}/{adv_id[6:9]}/{adv_id}.xml',
            timeout=REQUESTS_TIMEOUT
        )
    except requests.exceptions.Timeout:
        exit_with_error(
            f'Error on retrieving XML model for {adv_id}: Timed out ({REQUESTS_TIMEOUT}).'
        )
    status_code = adv_model_response.status_code
    if status_code == 200:
        root = ET.fromstring(adv_model_response.text)
        adv_asset_list = root.findall('.//asset')
        for asset_entry in adv_asset_list:
            links_asset = to_links(asset_entry.text)
            links += links_asset
    return links



parser = argparse.ArgumentParser(
    prog='sporeget',
    usage=help_cmd('sporeget [command] [argument] (options)'),
    formatter_class=RawTextHelpFormatter,
    description=help_dict(),
    add_help=False
)
parser.add_argument(
    'command',
    help='command name',
    nargs='?',
    choices=help_dict(return_names=True)
)
parser.add_argument(
    'arg',
    help='input data for a command',
    metavar='argument',
    nargs='?'
)

parser.add_argument(
    '--adv',
    help='return links to all the assets used in adventures.',
    action='store_true',
    default=False,
    required=False
)
parser.add_argument(
    '--static-only',
    help='return only links to files.',
    action='store_true',
    default=False,
    required=False
)
parser.add_argument(
    '--thumb-only',
    help='return only links to importable 128x128 PNGs.',
    action='store_true',
    default=False,
    required=False
)
parser.add_argument(
    '--disable-comments-pagination',
    help=f'return only the first comments page (max. {REST_PAGE_LIMIT}), faster.',
    action='store_true',
    default=False,
    required=False
)
parser.add_argument(
    '--exclude-myspore',
    help='exclude MySpore (HTML) pages from the list.',
    action='store_true',
    default=False,
    required=False
)
parser.add_argument(
    '--exclude-pollinator',
    help='exclude Pollinator (in-game asset downloading) endpoints from the list.',
    action='store_true',
    default=False,
    required=False
)
parser.add_argument(
    '--exclude-quad-images',
    help='exclude additional image links for the creations.',
    action='store_true',
    default=False,
    required=False
)
parser.add_argument(
    '--debug',
    help='print debug messages, only for testing.',
    action='store_true',
    default=False,
    required=False
)

argv_parsed = parser.parse_args(argv[1:])
if (argv_parsed.command is None or argv_parsed.arg is None):
    exit_with_help()

command = argv_parsed.command
input_arg = argv_parsed.arg
debug = argv_parsed.debug

thumb_only = argv_parsed.thumb_only
static_only = argv_parsed.static_only or argv_parsed.thumb_only
adv_assets = argv_parsed.adv
disable_comments_pagination = argv_parsed.disable_comments_pagination
exclude_myspore = argv_parsed.exclude_myspore
exclude_pollinator = argv_parsed.exclude_pollinator
exclude_quad_images = argv_parsed.exclude_quad_images

if command == 'asset':
    output_links = asset(input_arg)
elif command == 'user':
    output_links = user(input_arg)
elif command == 'feed':
    output_links = feed(input_arg)
else:
    exit_with_help()

exit_with_links(output_links)
