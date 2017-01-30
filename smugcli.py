#!/usr/bin/python
# Command line tool for SmugMug. Uses SmugMug API V2.

import argparse
import json
import os
import urlparse

import smugmug as smugmug_lib
import smugmug_shell

API_ORIGIN = 'https://api.smugmug.com'
API_REQUEST = 'https://api.smugmug.com/api/developer/apply'

CONFIG_FILE = os.path.expanduser('~/.smugcli')


def do_login(smugmug, args):
  parser = argparse.ArgumentParser(
    description='Login onto the SmugMug service')
  parser.add_argument('--key', type=str, required=True, help='SmugMug API key')
  parser.add_argument('--secret', type=str, required=True, help='SmugMug API secret')
  parsed = parser.parse_args(args)

  smugmug.config['api_key'] = (parsed.key, parsed.secret)
  smugmug.config['access_token'] = smugmug.service.request_access_token()


def do_logout(smugmug, args):
  smugmug.logout()


def do_get(smugmug, args):
  url = args[0]
  scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
  params = urlparse.parse_qs(query)
  result = smugmug.get_json(path, params)
  print json.dumps(result, sort_keys=True, indent=2)

def do_ls(smugmug, args):
  parser = argparse.ArgumentParser(
    description='List the content of a folder or album.')
  parser.add_argument('path', type=str, nargs='?', default='/', help='Path to list.')
  parser.add_argument('-l', help='Show details.', action='store_true')
  parsed = parser.parse_args(args)

  authuser = smugmug.get('/api/v2!authuser')['NickName']
  node = smugmug.fs.path_to_node(authuser, parsed.path)
  if node['Type'] == 'Album':
    children = node.get('Album').get('AlbumImages')
    names = [child['FileName'] for child in children]
  else:
    children = node.get('ChildNodes')
    names = [child['Name'] for child in children]

  if parsed.l:
    print json.dumps(children, sort_keys=True, indent=2)
  else:
    for name in names:
      print name

def do_shell(smugmug, args):
  shell = smugmug_shell.SmugMugShell(smugmug)
  shell.cmdloop()

def main():
  commands = {
    'login': do_login,
    'logout': do_logout,
    'get': do_get,
    'ls': do_ls,
    'shell': do_shell,
  }

  smugmug_shell.SmugMugShell.set_commands(commands)

  parser = argparse.ArgumentParser(description='SmugMug commandline interface.')
  parser.add_argument('command', type=str, choices=commands.keys(),
                 help='The command to run.')
  parser.add_argument('args', nargs=argparse.REMAINDER)
  args = parser.parse_args()

  smugmug = smugmug_lib.SmugMug(CONFIG_FILE)
  commands[args.command](smugmug, args.args)


if __name__ == '__main__':
  main()