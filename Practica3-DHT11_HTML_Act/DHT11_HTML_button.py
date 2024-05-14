try:
    import usocket as socket
except:
    import socket

import network
from machine import Pin
import time
import dht

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'NadGGNetwork'
password = 'b2pxwk3uPi7'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

sensor = dht.DHT11(Pin(15))

t_value = h_value = "0"

####MAIN
def read_sensor():
    global t_value, h_value
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        if isinstance(temp, (float, int)) and isinstance(hum, (float, int)):
            temp = int(temp)
            hum = int(hum)
        else:
            return None, None
        
        temp = min(temp, 100)
        hum = min(hum, 100)

        t_value = get_string_value(temp)
        h_value = get_string_value(hum)


        return t_value, h_value
    except OSError as e:
        return None, None

def get_string_value(input: int):    
    return str(input)

def web_page():
    sensor_readings = read_sensor()

    html = """
<html>
        <head>
            <title>Lector de temperatura y humedad
            </title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="icon" href="data:,">
            <style>
                meter {
                    -webkit-writing-mode: horizontal-tb !important;
                    appearance: auto;
                    box-sizing: border-box;
                    display: inline-block;
                    height: 3em;
                    width: 13em;
                    vertical-align: -1.0em;
                    -webkit-user-modify: read-only !important;
                }
        
                html {
                    font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;;
                    display: inline-block;
                    margin: 0px auto;
                    text-align: center;
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

                h1 {
                    color: black;
                    font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
                    text-align: center;
                    padding: 2vh;
                }

                h4 {
                    color: black;
                    font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
                    line-height: 0;
                    text-align: center;
                }
        
                p {
                    font-size: 1.5rem;
                }
        
                table {
                    margin: auto;
                }
        
                td {
                    padding: 7px;           
                }
        
                .Button {
                    border-radius: 31px;
                    display: inline-block;
                    cursor: pointer;
                    color: #ffffff;
                    font-family: Arial;
                    font-size: 10px;
                    font-weight: bold;
                    font-style: italic;
                    padding: 4px 5px;
                    text-decoration: none;
                }
        
                .ButtonR {
                    background-color: #D7F9BF;
                    border: 3px solid #7CA75D;
                    text-shadow: 0px 2px 2px #3F6324;
                }
        
                .ButtonR:hover {
                    background-color: #508D23;
                }
        
                .Button:active {
                    position: relative;
                    top: 1px;
                }
                
            </style>
        </head>
        
        <body>
            <div class="caja">
                <img src="Images/uv_logo.png" style=" height:130px; width:130px; top: 0; left: 0; position: absolute;"/>
                <h1> Facultad de Instrumentaci&oacute;n electr&oacute;nica</h1>
                <h4> Ingenier&iacute;a Biom&eacute;dica</h4>
                <h4> TSIB: Internet de las Cosas</h4>
                <img src="Images/fie_logo.png" style="height:100px; width:60px; top: 0; right: 0; position: absolute;"/>
            </div>
            <div style="height: 50;"></div>
            <div class="caja">
                <h1>ESP Web Server</h1>
            </div>
        
        
            <table>
                <tbody>
                    <tr>
                        <td>
                            <p><a href="/update"><button class="ButtonR Button">Actualizar</button></a></p>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <strong> """+ t_value +""" °C</strong>
                            <meter id="fuel" min="0" max="100" low="10" high="30" optimum="20" value=" @@"""+ t_value +""" @@">
                                at 50/100
                            </meter>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <strong> """+ h_value +""" %</strong>
                            <meter id="fuel" min="0" max="100" low="30" high="70" optimum="80" value=" @@"""+ h_value +""" @@">
                                at 50/100
                            </meter>
                        </td>
                    </tr>
                    <tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    
    request = str(request)
    print('Content = %s' % request)
    
    update = request.find('/update')
    if update == 6:
        print('update')
        r_value, g_value = read_sensor()  # Obtener los valores de los sensores
        print(r_value, g_value)
    
    response = web_page()
    response = response.replace(" @@", "")
    
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()

