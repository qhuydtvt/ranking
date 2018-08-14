import re

io = [
    ('my name is (?P<name>\w+)', 'Hi there, {name}'),
]

string = input('> ')
for regex, output in io:
    match = re.match(regex, string)
    if match:
        print(output.format(**match.groupdict()))
        break
