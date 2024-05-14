try:
  import usocket as socket
except:
  import socket

from machine import Pin
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'myWifi'
password = '1234567890'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

led = Pin(2, Pin.OUT)


def web_page():
  html = """<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Botón 1 </title>
        <style>
            h1 {
            color: black;
            font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            text-align: center;
            }

            h4 {
            color: black;
            font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            line-height: 0;
            text-align: center;
            }

            body{
                background-color: #fcfaf2;
            }

            .caja{
                width: 80%; 
                margin: 0 auto; 
                padding: auto;
                box-sizing: border-box; 
                display: flex; 
                justify-content: center;
                align-items: center; 
                flex-direction: column;
            }
            .contenedor-botones {
                display: flex;
                justify-content: center; 
            }
            .contenedor-botones button {
                margin: 0 10px; 
            }
        </style>
        
    </head>
    <body>
        <div>
            <div class="caja">
                <img src="Images/uv_logo.png" style=" height:130px; width:130px; top: 0; left: 0; position: absolute;"/>
                <h4> Facultad de Instrumentación electrónica</h4>
                <h4> Ingeniería Biomédica</h4>
                <h4> TSIB: Internet de las Cosas</h4>
                <img src="Images/fie_logo.png" style="height:100px; width:60px; top: 0; right: 0; position: absolute;"/>
            </div>
            <div style="height: 50;"></div>
            <div class="caja">
                <h1>ESP Web Server</h1>
            </div>
            <div class="contenedor-botones">
                <a href=\"?led=on\"><button >ON</button></a>&nbsp;
                <a href=\"?led=off\"><button>OFF</button></a>
            </div>
            
        </div>
    </body>
</html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  try:
    if gc.mem_free() < 102000:#number of bytes 
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)#Tiempo (s) de espera en operacion blocking
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)#recibe datos (bytes) max cant inf simult.
    conn.settimeout(None)#blocking socket
    request = str(request)
    #print('Content = %s' % request)
    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    if led_on == 6:
      print('LED ON', request)
      led.value(1)
    if led_off == 6:
      print('LED OFF', request)
      led.value(0)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')