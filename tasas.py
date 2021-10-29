import pyRofex
import yfinance as yf
import time
import json


#config file
with open('config.json') as f:
    config = json.load(f)


class Rates_arbitrage:


    def __init__(self):
        
        #defino variables globales

        #futuros que vamos a estar mirando para hacer tasa
        self.futures = ["DLR/Dic21", "GGAL/Dic21", "PAMP/Dic21", "YPFD/Dic21"]
        self.fut_prices = dict()     #key: instrument , value: [offer, bid]

        #instrumentos spot (yfinance)
        self.spots = ["ARS=X", "GGAL.BA", "PAMP.BA", "YPFD.BA"]
        self.spot_data = yf.Tickers
        self.spot_prices = dict()    #key: instrument , value: [offer, bid]

        self.testOP = dict()         #para testear

        self.entries = [pyRofex.MarketDataEntry.BIDS,
                        pyRofex.MarketDataEntry.OFFERS]

        print("\n checking for oportunities....")


        #initialize the environment
        pyRofex.initialize(user=config["user"],
                        password=config["password"],
                        account=config["account"],
                        environment=pyRofex.Environment.REMARKET)

    

    #----------#----------#----------#----------#----------#----------#----------#


    #estos son los handlers que son los que van a procesar los mensajes que lleguen

    #me van a entrar mensajes en tiempo real de update de precios de las puntas de los futuros
    def market_data_handler(self, message):

        #que instrumento es?
        fut = message["instrumentId"]["symbol"]
        
        #me fijo si hay BID y ASK para el instrumento
        #comento que utlizando REMARKETS me pasa que varios de 
        #los intrumentos que me pideron usar no tiene puntas.
        #no tuve tiempo de conseguir autorizacion para usar LIVE 
        #pero con esa hubiera conseguido la cotizacion de rofex sin prob.

        if not message["marketData"]["OF"] or not message["marketData"]["BI"]:
            #si hay alguna punta vacia...saco al instrumento
            del self.spots[self.futures.index(fut)]
            self.futures.remove(fut)
        else:
            #agrego bid y ask price al dict, la key siendo el contrato
            self.fut_prices[fut] = [ message["marketData"]["OF"][0]["price"],
                                     message["marketData"]["BI"][0]["price"] ]


    #pyRofex library
    def order_report_handler(message):
        print("Order Report Message Received: {0}".format(message))
    def error_handler(message):
        print("Error Message Received: {0}".format(message))
    def exception_handler(e):
        print("Exception Occurred: {0}".format(e.message))

    #
    #
    #
    #
    #


    # ---------------------------- Funciones aux -----------------------------------#

    #lleno los diccionarios de futuros con sus valores actuales
    def init_instruments(self):

        #pido por Rest las cotizaciones actuales
        for f in self.futures:
            message = pyRofex.get_market_data(ticker=f, entries=self.entries)
            
            #para simplificar y que quede prolijo
            #si no consigue la data de las puntas ---> eliminar instrumento
            if not message["marketData"]["OF"] or not message["marketData"]["BI"]:
                del self.spots[self.futures.index(f)]
                self.futures.remove(f)
            else:
                self.fut_prices[f] = [ message["marketData"]["OF"][0]["price"], message["marketData"]["BI"][0]["price"] ]

        if(len(self.futures)<= 2):
            print("\n ERROR: THERE'S NOT ENOUGH INSTRUMENTS \n")
            self.kill_process()


    def update_spots(self):
        #actualizo precios spot
        self.spot_data = yf.Tickers(' '.join(self.spots))     #no es optimo pedirle a yf los precios spot
        for s in self.spots:
            sp = []
            sp.append(self.spot_data.tickers[s].info["ask"])
            sp.append(self.spot_data.tickers[s].info["bid"])
            self.spot_prices[s] = sp


    def update_rates(self):
        #calculo todas las tasas nuevas dados los cambios en precios
        new_colocadora = []
        new_tomadora = []

        for i in range(len(self.spots)):
            s = self.spots[i]
            f = self.futures[i]
            #las tasas deberian estar normalizadas con respecto a dias restantes para el vencimiento
            #pero utilizamos contratos con el mismo vencimiento asique no lo hacemos            
            tasa_c = round( (self.fut_prices[f][1] - self.spot_prices[s][0] - config["comi_c"] )/self.fut_prices[f][1] * 100, 3) #sell fut buy spot
            tasa_t = round( -(self.spot_prices[s][1] - self.fut_prices[f][0] - config["comi_t"] )/self.spot_prices[s][1] * 100, 3) #sell spot buy fut

            new_colocadora.append(tasa_c)
            new_tomadora.append(tasa_t)

        return new_colocadora, new_tomadora


    def print_rates(self,tasa_c,tasa_t):
        print("------------------------------------------------------")
        print("\n NUEVAS TASAS \n")
        for i in range(len(self.spots)):
            print(self.spots[i]," -- ", self.futures[i],"||| Tasa Colocadora: ", tasa_c[i],"% ||| Tasa Tomadora: ", tasa_t[i],"% \n" )
        print("------------------------------------------------------")
        

    def check_arbitrage(self, sleep):
        #comi = config["comision"]
        
        #tasas actuales
        tasa_colocadora = [0]*len(self.spots)
        tasa_tomadora = [0]*len(self.spots)

        #corro un loop infinito que chequea si hay cambios en las tasas
        while True:
            #si hay menos de 2 instrumentos, corto
            if len(self.spots) <= 2:
                print("THERES NOT ENOUGH INTRUMENTS TO WORK WITH")
                break
            
            #update de spots
            self.update_spots()
            #hago update de las tasas
            new_colocadora, new_tomadora = self.update_rates()

            #Si hay cambio en las tasas, nos fijamos si hay oportunidades (e imprimo por consola)
            if( (tasa_colocadora != new_colocadora) or (tasa_tomadora != new_tomadora) ):
                tasa_colocadora = new_colocadora
                tasa_tomadora = new_tomadora
                self.print_rates(tasa_colocadora,tasa_tomadora)       #print por consola nuevas tasas
                self.compare_rates(tasa_colocadora, tasa_tomadora)
            
            time.sleep(sleep)



    #chequea si hay oportunidad (colocadora > tomadora)
    def compare_rates(self, tasa_c, tasa_t, esTest=0):

        for i in range(len(tasa_c)):

            #para testeo nomas
            if(esTest):
                self.testOP[tasa_c[i]] = []

            for j in range(len(tasa_t)):
                #comparo cada colocadora vs todas las tomadoras (a menos que sea el mismo instrumento)

                if ( (i!=j) and (tasa_c[i] > tasa_t[j])):
                    #si hay oportunidad, envio las ordenes en remarkets
                    #en este caso simplemente imprimo por pantalla los detalles

                    spot_c = self.spots[i]; spot_t = self.spots[j]
                    fut_c = self.futures[i]; fut_t = self.futures[j]
                    profit = round((tasa_c[i] - tasa_t[j]), 2)
                    print(
                        "\n Oportunidad de Arbitraje!"
                        "\n TASA COLOCADORA: Comprar spot de ", spot_c, " a ", self.spot_prices[spot_c][0],
                        "---- Vender futuro de ", fut_c, " a ", self.fut_prices[fut_c][1],
                        "---- alcanzando una tasa del ", tasa_c[i],"%",

                        "\n TASA TOMADORA: Vender spot de ", spot_t, " a ", self.spot_prices[spot_t][1],
                        "---- Comprar futuro de ", fut_t, " a ", self.fut_prices[fut_t][0],
                        "---- alcanzando una tasa del ", tasa_t[j],"%",

                        "\n PROFIT ESPERADO: ", profit, "%\n"
                    )
                    
                    #Agrego esto para testear mas rapido
                    if(esTest):
                        self.testOP[tasa_c[i]].append(tasa_t[j])

                    #Aca mandaria las ordenes a traves de pyRofex con el metodo send_order()


  

    def subscribe_md(self):
        #me contecto y le paso los handlers que defini
        pyRofex.init_websocket_connection(market_data_handler=self.market_data_handler, 
                                        order_report_handler=self.order_report_handler,
                                        error_handler=self.error_handler,
                                        exception_handler=self.exception_handler)
        
        pyRofex.order_report_subscription()

        #suscripcion para recibir market data messages (entries) de los siguientes instrumentos (tickers)
        pyRofex.market_data_subscription(tickers=self.futures, 
                                        entries=self.entries)

    def kill_process(self):
        print('Killing Process..')
        pyRofex.close_websocket_connection()
        exit()
        

    # ---------------------------- Funciones test -----------------------------------#

    #lleno los dicts de futuros y spots con valores ficticios para testear
    def init_instruments_test(self):

        #defino valores para los 4 futuros
        self.fut_prices["DLR/Dic21"] = [108.0, 179.99]
        self.fut_prices["GGAL/Dic21"] = [242.5, 241.25]
        self.fut_prices["PAMP/Dic21"] = [168.75, 166.05]
        self.fut_prices["YPFD/Dic21"] = [1000.0, 993.0]

        self.spot_prices["ARS=X"] = [99.69, 99.68]
        self.spot_prices["GGAL.BA"] = [227.7, 227.55]
        self.spot_prices["PAMP.BA"] = [158.35, 157.55]
        self.spot_prices["YPFD.BA"] = [915.5, 915.0]


    def finish_test(self):
        print('finished test block')
        pyRofex.close_websocket_connection()
        exit()


    


if __name__ == "__main__":
    runArb = Rates_arbitrage()
    runArb.init_instruments()
    runArb.subscribe_md()
    runArb.check_arbitrage(sleep=1)
