"""A tiny MQTT 3.1.1 broker over WebSocket, for testing cross-play without the internet: the web game (window.CR_BROKERS)
and the PC build (CR_BROKERS) both talk to it the way they talk to the public brokers. QoS 0, exact topics, no retained
messages: just what the games use. Standard library only.
Usage: python3 tools/mqtt_broker.py [port]   (default 8765; path /mqtt)"""
import asyncio, base64, hashlib, struct, sys

GUID = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
subs = {}   # topic -> set of clients


class Client:
    def __init__(self, w):
        self.w = w
        self.topics = set()
        self.buf = b''

    def send_ws(self, data):
        n = len(data)
        if n < 126:
            hdr = bytes([0x82, n])
        elif n < 65536:
            hdr = bytes([0x82, 126]) + struct.pack('>H', n)
        else:
            hdr = bytes([0x82, 127]) + struct.pack('>Q', n)
        try:
            self.w.write(hdr + data)
        except Exception:
            pass


def mqtt_len(n):
    out = bytearray()
    while True:
        d = n % 128
        n //= 128
        if n:
            d |= 128
        out.append(d)
        if not n:
            return bytes(out)


def handle_packets(c):
    b = c.buf
    i = 0
    while True:
        if len(b) - i < 2:
            break
        ln, m, j = 0, 1, i + 1
        while True:
            if j >= len(b):
                ln = -1
                break
            x = b[j]
            j += 1
            ln += (x & 127) * m
            m *= 128
            if not x & 128:
                break
        if ln < 0 or j + ln > len(b):
            break
        typ = b[i] >> 4
        qos = (b[i] >> 1) & 3
        body = b[j:j + ln]
        i = j + ln
        if typ == 1:     # CONNECT
            c.send_ws(bytes([0x20, 2, 0, 0]))
        elif typ == 8:   # SUBSCRIBE
            pid = body[:2]
            k = 2
            codes = bytearray()
            while k + 2 <= len(body):
                tl = (body[k] << 8) | body[k + 1]
                t = body[k + 2:k + 2 + tl].decode()
                k += 2 + tl + 1
                c.topics.add(t)
                subs.setdefault(t, set()).add(c)
                codes.append(0)
            c.send_ws(bytes([0x90]) + mqtt_len(2 + len(codes)) + pid + bytes(codes))
        elif typ == 3:   # PUBLISH
            tl = (body[0] << 8) | body[1]
            t = body[2:2 + tl].decode()
            p = 2 + tl + (2 if qos else 0)
            payload = body[p:]
            tb = t.encode()
            pkt_body = struct.pack('>H', len(tb)) + tb + payload
            pkt = bytes([0x30]) + mqtt_len(len(pkt_body)) + pkt_body
            for o in list(subs.get(t, ())):
                o.send_ws(pkt)
        elif typ == 12:  # PINGREQ
            c.send_ws(bytes([0xD0, 0]))
    c.buf = b[i:]


async def serve(r, w):
    c = Client(w)
    try:
        req = b''
        while b'\r\n\r\n' not in req:
            ch = await r.read(4096)
            if not ch:
                return
            req += ch
        head, rest = req.split(b'\r\n\r\n', 1)
        key = b''
        for line in head.split(b'\r\n'):
            if line.lower().startswith(b'sec-websocket-key:'):
                key = line.split(b':', 1)[1].strip()
        acc = base64.b64encode(hashlib.sha1(key + GUID).digest())
        w.write(b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                b'Sec-WebSocket-Accept: ' + acc + b'\r\nSec-WebSocket-Protocol: mqtt\r\n\r\n')
        data = rest
        while True:
            while len(data) < 2:
                ch = await r.read(65536)
                if not ch:
                    return
                data += ch
            op = data[0] & 15
            ln = data[1] & 127
            k = 2
            if ln == 126:
                while len(data) < 4:
                    data += await r.read(65536)
                ln = struct.unpack('>H', data[2:4])[0]
                k = 4
            elif ln == 127:
                while len(data) < 10:
                    data += await r.read(65536)
                ln = struct.unpack('>Q', data[2:10])[0]
                k = 10
            masked = data[1] & 128
            need = k + (4 if masked else 0) + ln
            while len(data) < need:
                ch = await r.read(65536)
                if not ch:
                    return
                data += ch
            if masked:
                mk = data[k:k + 4]
                pl = bytes(x ^ mk[n % 4] for n, x in enumerate(data[k + 4:need]))
            else:
                pl = data[k:need]
            data = data[need:]
            if op == 8:
                return
            if op == 9:
                w.write(bytes([0x8A, len(pl)]) + pl)
                continue
            if op in (0, 1, 2):
                c.buf += pl
                handle_packets(c)
    except Exception:
        pass
    finally:
        for t in c.topics:
            subs.get(t, set()).discard(c)
        try:
            w.close()
        except Exception:
            pass


async def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    srv = await asyncio.start_server(serve, '127.0.0.1', port)
    print('broker on ws://127.0.0.1:%d/mqtt' % port, flush=True)
    async with srv:
        await srv.serve_forever()


asyncio.run(main())
