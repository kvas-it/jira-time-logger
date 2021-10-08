"""Log time in Jira."""

import argparse
import re
import os
import sys

import jira
import keyring


WORKLOG_RX = re.compile(
    r'\-\s+\[(?P<state>[\. x])\]\s*'
    r'(?P<prefix>\W*)\s+'
    r'(?P<comment>[\w\s\.,;\-\/]+)\s+'
    r'(?P<time>\@\d+)?\s*'
    r'\- (?P<issue>[A-Z]+\-\d+)\s+'
    r'\[\d*(?P<tracking>[\.\;\,\s]*)\]'
)

parser = argparse.ArgumentParser(description=__doc__)
subparsers = parser.add_subparsers(
    help='Subcommands: use jtl <cmd> -h to get detailed help',
)


def command(*args, **kw):
    """Return a decorator for command functions.

    This decorator will create a subparser for the command function passing
    all the arguments of `command()` to `.add_parser()`. If no name and help
    are provided for the command, they will be taken from the function name
    and docstring (only the first line of the docstring is used) of the
    decorated function.

    """

    def decorator(func):
        nonlocal args, kw

        # Add arguments that all commands have.
        func = server_arg()(func)
        func = user_arg()(func)

        if not args:
            args = [func.__name__]
        if 'help' not in kw:
            kw['help'] = func.__doc__.split('\n')[0]

        cmd = subparsers.add_parser(*args, **kw)
        for arg in reversed(getattr(func, '__args__', [])):
            cmd.add_argument(*arg['args'], **arg['kw'])
        cmd.set_defaults(func=func)

        return func

    return decorator


def arg(*args, **kw):
    """Return a decorator that will add an argument to a command function.

    All parameters passed to the decorator will be passed to `.add_argument()`
    call of the subparser corresponding to the decorated function.

    """

    def decorator(func):
        nonlocal args, kw

        if not hasattr(func, '__args__'):
            func.__args__ = []
        func.__args__.append({'args': args, 'kw': kw})

        return func

    return decorator


def server_arg():
    """Return a decorator for --jira-server option."""
    default = os.getenv('JIRA_SERVER')
    def_help = default or 'JIRA_SERVER environment variable'
    return arg('--jira-server', '-j', default=default, type=str,
               help='Jira server (default: {})'.format(def_help))


def user_arg():
    """Return a decorator for --jira-user option."""
    default = os.getenv('JIRA_USER')
    def_help = default or 'JIRA_USER environment variable'
    return arg('--jira-user', '-u', default=default, type=str,
               help='Jira user (default: {})'.format(def_help))


@command(aliases=['l'])
@arg('issue', help='Issue id')
@arg('amount', help='Amount of time to log')
@arg('comment', help='Comment')
# @arg('--start-time', '-s', help='Start time in the log record')
def log(args):
    """Log time"""
    issue = args.jira.issue(args.issue)
    args.jira.add_worklog(
        issue=issue,
        timeSpent=args.amount,
        comment=args.comment,
    )


@command(aliases=['v'])
def vimlog(args):
    """Log time from vim worklog"""
    line = input()
    match = WORKLOG_RX.match(line)
    if not match:
        print(line + '?')
        return
    if match.group('state') == 'x':
        print(line + '!')
        return
    minutes = 0
    for c in match.group('tracking'):
        if c == '.':
            minutes += 30
        if c == ';':
            minutes += 15
        if c == ',':
            minutes += 5
    if minutes > 0:
        args.jira.add_worklog(
            issue=match.group('issue'),
            timeSpent=f'{minutes}m',
            comment=match.group('comment'),
        )
        print('- [x]' + line[5:])
    else:
        print(line)


@command(aliases=['i'])
def issues(args):
    """List assigned issues"""
    for issue in args.jira.search_issues('assignee = currentUser()'):
        print('{}: {}'.format(issue.key, issue.fields.summary))


def make_jira_client(args):
    """Instantiate and configure Jira client."""
    if args.jira_server is None:
        sys.exit('Please set JIRA_SERVER or provide --jira-server argument')
    if args.jira_user is None:
        sys.exit('Please set JIRA_USER or provide --jira-user argument')
    password = keyring.get_password(args.jira_server, args.jira_user)
    if password is None:
        sys.exit('Please add password to keyring (run "keyring set {} {}")'
                 .format(args.jira_server, args.jira_user))
    return jira.JIRA(args.jira_server, basic_auth=(args.jira_user, password)) 


def main():
    """Run the CLI."""
    args = parser.parse_args()
    if callable(getattr(args, 'func', None)):
        args.jira = make_jira_client(args)
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
