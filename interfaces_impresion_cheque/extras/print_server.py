import socket, threading,win32ui,win32print,win32con    
class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)
    def run(self):
        print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        #while True:
        data = self.csocket.recv(64000)
        msg = data.decode('utf-8')
        self.csocket.send(msg.encode('utf-8'))
        self.imprimir(msg)
        print ("Client at ", clientAddress , " disconnected...")

    def imprimir(self,texto):
        para_imprimir=texto.split('\n')
        print("para_imprimir: ", para_imprimir)
        dc = win32ui.CreateDC()
        dc.CreatePrinterDC()
        
        dc.StartDoc('My Python Document')
        dc.StartPage()
        #fontdata = { 'name':'Draft', 'height':10, 'italic':False, 'weight':win32con.FW_NORMAL}
        # fontdata = { 'name':'Arial', 'height':11}
        # fontdata = {'name': 'Lucida Console', 'height': 10, 'italic': False, 'weight': win32con.FW_NORMAL}
        # fontdata = {'name': 'Droid Sans Mono', 'height': 13, 'italic': False, 'weight': win32con.FW_NORMAL}  pruede ser
        fontdata = {'name': 'PT Mono', 'height': 10, 'italic': False, 'weight': win32con.FW_NORMAL}
        # fontdata = {'name': 'PT Mono', 'height': 11, 'italic': False, 'weight': win32con.FW_NORMAL}
        # fontdata = {'name': 'PT Mono', 'height': 9, 'italic': False, 'weight': win32con.FW_NORMAL}

        font = win32ui.CreateFont(fontdata)
        dc.SelectObject(font)
        h=0
        for i in range(0,len(para_imprimir)):
            dc.TextOut(1,h, para_imprimir[i])
            h=h+16
        dc.EndPage()
        dc.EndDoc()
        # self.imprimir2(dc.GetObject(OBJ_BITMAP))

    def imprimir2(self,texto):
        printer_name = win32print.GetDefaultPrinter()
        raw_data = texto
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("test of raw data", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, raw_data.encode())
                win32print.EndPagePrinter(hPrinter)
            except:
                raise
            finally:
                win32print.EndDocPrinter(hPrinter)
        except:
            raise
        finally:
            win32print.ClosePrinter(hPrinter)

LOCALHOST = "192.168.0.159"
PORT = 8090
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("Server started")
print("Waiting for client request..")
while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
