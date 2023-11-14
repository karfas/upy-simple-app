from binascii import hexlify

reserved = b'!#$%&\'()*+,/:;=?@[] '

def url_encode(str):
    ret = ''
    str = bytes(str, 'utf-8')
    for i,v in enumerate(str):
        if v >= 127 or v in reserved:
            ret = ret + '%' + hexlify(str[i:i+1]).decode()
        else:
            ret += chr(v)
    return ret

if __name__ == '__main__':
    print(url_encode('Hello, wörld!'))
