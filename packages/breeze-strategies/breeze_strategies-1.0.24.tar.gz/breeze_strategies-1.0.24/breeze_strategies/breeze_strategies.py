import json
import threading
import queue
import time 
#import datetime
import sys
import asyncio
import nest_asyncio
from breeze_connect import BreezeConnect
from datetime import datetime
import pandas as pd
# import matplotlib.pyplot as plt
from collections import deque
import logging
import os
import traceback
import re
import signal
from IPython.display import display, Markdown, clear_output

log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


# # Initialize logger for buy/sell signals
# signal_logger = logging.getLogger('SignalLogger')
# signal_logger.setLevel(logging.INFO)
# signal_handler = logging.FileHandler(f'{log_folder}/signal_{timestamp}.log')
# signal_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
# signal_logger.addHandler(signal_handler)

# # Initialize logger for RSI value details
# rsi_logger = logging.getLogger('RSILogger')
# rsi_logger.setLevel(logging.INFO)
# rsi_handler = logging.FileHandler(f'{log_folder}/rsi_{timestamp}.log')
# rsi_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
# rsi_logger.addHandler(rsi_handler)

# orb_logger = logging.getLogger('ORBLogger')
# orb_logger.setLevel(logging.INFO)
# orb_handler = logging.FileHandler(f'{log_folder}/orb_{timestamp}.log')
# orb_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
# orb_logger.addHandler(orb_handler)

FourLeg_logger = logging.getLogger('FourLegLogger')
FourLeg_logger.setLevel(logging.INFO)
FourLeg_logger.setLevel(logging.ERROR)
FourLeg_logger.setLevel(logging.DEBUG)  #
FourLeg_handler = logging.FileHandler(f'{log_folder}/FourLeg_strategy.log')
FourLeg_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
FourLeg_logger.addHandler(FourLeg_handler)

FourLeg_api_logger = logging.getLogger('FourLegAPILogger')
FourLeg_api_logger.setLevel(logging.INFO)
FourLeg_api_logger.setLevel(logging.ERROR)
FourLeg_api_logger.setLevel(logging.DEBUG)  #
FourLeg_api_handler = logging.FileHandler(f'{log_folder}/FourLeg_API.log')
FourLeg_api_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
FourLeg_api_logger.addHandler(FourLeg_api_handler)

FourLeg_order_logger = logging.getLogger('FourLegORDERLogger')
FourLeg_order_logger.setLevel(logging.INFO)
FourLeg_order_logger.setLevel(logging.ERROR)
FourLeg_order_logger.setLevel(logging.DEBUG)  #
FourLeg_order_handler = logging.FileHandler(f'{log_folder}/FourLeg_order.log')
FourLeg_order_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
FourLeg_order_logger.addHandler(FourLeg_order_handler)

FourLeg_Live_logger = logging.getLogger('FourLegLIVELogger')
FourLeg_Live_logger.setLevel(logging.INFO)
FourLeg_Live_logger.setLevel(logging.ERROR)
FourLeg_Live_logger.setLevel(logging.DEBUG)  #
FourLeg_Live_handler = logging.FileHandler(f'{log_folder}/FourLeg_Live.log')
FourLeg_Live_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
FourLeg_Live_logger.addHandler(FourLeg_Live_handler)

FourLeg_PL_logger = logging.getLogger('FourLegPLLogger')
FourLeg_PL_logger.setLevel(logging.INFO)
FourLeg_PL_logger.setLevel(logging.ERROR)
FourLeg_PL_logger.setLevel(logging.DEBUG)  #
FourLeg_PL_handler = logging.FileHandler(f'{log_folder}/FourLeg_PL.log')
FourLeg_PL_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
FourLeg_PL_logger.addHandler(FourLeg_PL_handler)

FourLeg_Error_logger = logging.getLogger('FourLegErrorLogger')
FourLeg_Error_logger.setLevel(logging.INFO)
FourLeg_Error_logger.setLevel(logging.ERROR)
FourLeg_Error_logger.setLevel(logging.DEBUG)  #
FourLeg_Error_handler = logging.FileHandler(f'{log_folder}/FourLeg_Error.log')
FourLeg_Error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
FourLeg_Error_logger.addHandler(FourLeg_Error_handler)



# class KeyboardInterruptHandler:
#     def __init__(self, strategy):
#         self.strategy = strategy
#         self.stop_flag = threading.Event()

#     def start(self):
#         def signal_handler(signum, frame):
#             print("\nKeyboard interrupt detected1. Stopping strategy...")
#             self.stop_flag.set()
#             self.strategy.stop_strategy()

#         # Set up the signal handler
#         signal.signal(signal.SIGINT, signal_handler)

#         while not self.stop_flag.is_set():
#             time.sleep(0.1)  # Small sleep to prevent CPU overuse

#         print("Keyboard interrupt handler stopped.")
        
# def create_keyboard_interrupt_thread(strategy):
#     handler = KeyboardInterruptHandler(strategy)
#     thread = threading.Thread(target=handler.start, name="KeyboardInterruptHandler")
#     thread.daemon = True  # This ensures the thread will exit when the main program does
#     return thread

class Strategies:
    
    #initialize strategy object
    def __init__(self,app_key,secret_key,api_session,max_profit = "-1",max_loss = "-1",trailing_stoploss = "-1"):
        
        self.maxloss = float(max_loss)
        self.maxprofit = float(max_profit)
        self.currentcall = 0
        self.currentput = 0
        self.flag = False
        self.client = BreezeConnect(app_key)
        self.client.generate_session(secret_key,api_session)
        self.client.ws_connect()
        self.trailing_stoploss = int(trailing_stoploss)
        self.keyboard_interrupt_thread = None
        self.quantity = 0
        self.exchange_code = ""
        self.stock_code = ""
        self.product_type = ""
        self.expiry_date = ""
        self.strike_price = ""
        self.order_type = ""
        self.validity = ""
        self.stoploss = ""
        self.validity_date = ""
        self.callexecution = ""
        self.putexecution = ""
        self.strategy_type = ""
        self.socket = 0
        self.right = ""
        self.sp1_price = 0
        self.sp2_price = 0
        self.sp3_price = 0
        
        self.strategy_running = False
        self.stop_event = threading.Event()
        #self._setup_signal_handler()
        
        
    # def _setup_signal_handler(self):
    #     signal.signal(signal.SIGINT, self._signal_handler)

    # def _signal_handler(self, signum, frame):
    #     print("\nKeyboard interrupt detected. Stopping strategy...")
        #self.stop_strategy()

    def squareoff(self,exchange_code, stock_code, product_type, expiry_date, strike_price, order_type, validity, stoploss, quantity, price,validity_date, trade_password, disclosed_quantity,right):
        action = "buy"
        #print("quantity",quantity,"right",right)
        if(self.strategy_type.lower() == "short"):
            action = "buy"
        else:
            action = "sell"

        data = self.client.square_off(exchange_code=exchange_code,
                            product="options",
                            stock_code=stock_code,
                            expiry_date=expiry_date,
                            right=right,
                            strike_price=strike_price,
                            action=action,
                            order_type=order_type,
                            validity=validity,
                            stoploss="0",
                            quantity=quantity,
                            price=price,
                            validity_date=validity_date,
                            trade_password="",
                            disclosed_quantity="0")

        print(f"Squaring off {right} ..")
        response = None
        if(data['Status'] == 200):
            response = data['Success']['message']
            print(f"Success : {response}")
        else:
            response = data['Error']
            print(f"Error : {response}")
        return(data)
        
    def get_date_format(self,expiry_date):
        #print("exp=",expiry_date)
        month_names = {
                            '01': 'Jan',
                            '02': 'Feb',
                            '03': 'Mar',
                            '04': 'Apr',
                            '05': 'May',
                            '06': 'Jun',
                            '07': 'Jul',
                            '08': 'Aug',
                            '09': 'Sep',
                            '10': 'Oct',
                            '11': 'Nov',
                            '12': 'Dec'
                      }
        year = expiry_date[:4]
        month = expiry_date[5:7]
        day = expiry_date[8:10]
        formatted_date = f"{day}-{month_names[month]}-{year}"
        
        #print("format data : ",formatted_date)
        return(formatted_date)
        
    def trigger(self,product_type, rightval, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price, call_execution,put_execution,single_leg,strike_price_call, strike_price_put, is_strangle):
        net_gain_loss = (self.currentcall + self.currentput)*int(quantity)
        print(f"P&L (NET) : {round(net_gain_loss,2)}/- Rs")
        print("----------------------------------------")
        formatted_date = self.get_date_format(expiry_date)
        
        if(self.trailing_stoploss!=-1):
            if(net_gain_loss <= self.trailing_stoploss):
                print("Strategy Exiting...")
                if(is_strangle):
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_call, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_put, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    self.stop(is_strangle)
                else:
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    #print("single_leg : ",single_leg)
                    self.stop(single_leg)
                self.flag = True
                return
            else:
                print(f"trailing stoploss updated to {round(net_gain_loss,2)}")
                self.trailing_stoploss = net_gain_loss
        else:
            if(net_gain_loss >= self.maxprofit):
                print("TakeProfit reached...")
                #print("SquareOff operation on both contracts call and put begins....")
                #print(single_leg,is_strangle)
                if(is_strangle):
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_call, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_put, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    self.stop(is_strangle = True)
                elif(single_leg == True):
                    if(self.right.lower() == "call"):
                        self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    elif(self.right.lower() == "put"):
                        self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    self.stop(single_leg)
                else:
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    self.stop()
            
                self.flag = True
                return
            if(net_gain_loss <= self.maxloss):
                print("MaxLoss reached...")
                #print("SquareOff operation on both contracts call and put begins....")
            
                if(is_strangle):
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_call, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_put, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    self.stop(is_strangle = True)
                elif(single_leg == True):
                    if(self.right.lower() == "call"):
                        self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    elif(self.right.lower() == "put"):
                        self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    self.stop(single_leg = True)
                else:
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Call", get_exchange_quotes=True, get_market_depth=False)
                    self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Put", get_exchange_quotes=True, get_market_depth=False)
                    self.stop()
           
                self.flag = True
                return

    def calculate_current(self,product_type,stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price,put_price,call_execution,put_execution,strike_price_call, strike_price_put, is_strangle,single_leg):
        #print("expiry = ",expiry_date)
        resultcall = []
        formatted_date = self.get_date_format(expiry_date)
        
        def on_ticks(data):
            
            value = data
            
            if(value['right'] == "Call"):
                self.currentcall = round(float(value['last']) - float(call_execution), 2)
                if(self.strategy_type.lower() == "short"):
                    self.currentcall = self.currentcall*-1
                if(self.flag == False):
                    self.trigger(product_type, "Call", stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price,put_price,call_execution,put_execution,single_leg,strike_price_call, strike_price_put, is_strangle)
            
            if(value['right'] == "Put"):
                self.currentput = round(float(value['last']) - float(put_execution), 2)
                if(self.strategy_type.lower() == "short"):
                    self.currentput = self.currentput*-1
                if(self.flag == False):
                    self.trigger(product_type, "Put", stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price,put_price,call_execution,put_execution,single_leg, strike_price_call, strike_price_put, is_strangle)
            
        self.client.on_ticks = on_ticks

        if(is_strangle == True):
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price_call, right = "Call", get_exchange_quotes=True, get_market_depth=False)
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price_put, right = "Put", get_exchange_quotes=True, get_market_depth=False) 
        
        elif(single_leg == False):
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Call", get_exchange_quotes=True, get_market_depth=False)
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Put", get_exchange_quotes=True, get_market_depth=False) 
        
        else:
            if(self.right.lower() == "call"):
                self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Call", get_exchange_quotes=True, get_market_depth=False)
            else:
                self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Put", get_exchange_quotes=True, get_market_depth=False) 

        
    def profit_and_loss(self,product_type, stock_code,strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution,strike_price_call = "-1",strike_price_put = "-1",is_strangle= False,single_leg = False):
        #print("p&l expiry = ",expiry_date)
        self.calculate_current(product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price, call_execution, put_execution, strike_price_call, strike_price_put, is_strangle, single_leg)
        
    def straddle(self, strategy_type,stock_code, strike_price, quantity, expiry_date, stoploss = "", put_price = "0", call_price = "0",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO"):
        
        self.quantity = quantity
        self.strategy_type = strategy_type
        self.exchange_code = exchange_code 
        self.stock_code = stock_code
        self.product_type = product_type 
        self.expiry_date = expiry_date  
        self.strike_price = strike_price
        self.order_type = order_type
        self.validity = validity
        self.stoploss = stoploss
        #self.quantity = quantity
        self.validity_date = validity_date
        self.flag = False
        
        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1
            

        if(strategy_type.lower() not in ["long","short"]):
            return("strategy_type should be either long or short..")

        def place_order_method(stock_code,exchange_code,product,action,order_type,stoploss,quantity,price,validity,validity_date,expiry_date,right,strike_price,res_queue):
         
            data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)
            response = None
            if(data['Status'] == 200):
                response = data['Success']['message']
                print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}")
                res_queue.put(data)
            else:
                response = data['Error']
                print(f"Error : {response} for {right}")
                res_queue.put(data)
            return(data)
                  
        res_queue = queue.Queue()
        action = "buy"

        if(strategy_type.lower()== "short"):
            action = "sell"
        
        #create thread for call and put order to execute simultaneously for buy type
        t1 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,call_price,validity,validity_date,expiry_date,"Call",strike_price,res_queue))
        t1.start()
        t1.join()
        
        firstresponse = res_queue.get()
        
        res_queue = queue.Queue()
        t2 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,put_price,validity,validity_date,expiry_date,"Put",strike_price,res_queue))
        t2.start()
        t2.join()
        secondresponse = res_queue.get()
        
        
        #if one of the order fails then cancel the other one which is successfull
        if(firstresponse.get('Status')==200 and secondresponse.get('Status')==500):
            print("Put Order Failed....")
            order_id = firstresponse['Success']['order_id']
            data  = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)

            if(data.get("Success",None) == None):
                print("Call Order Cancellation has not been successfull")
                print("----------END-------------------")
            else:
                print("Call Order Cancellation has  been successfull")
                print("----------END-------------------")
            
            
        
        elif(secondresponse.get('Status')==200 and firstresponse.get('Status')==500):
            print("Call order failed....")
            order_id = secondresponse['Success']['order_id']
            
            data = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)
            
            if(data.get("Success",None) == None):
                print("Put Order Cancellation has not been successfull")
            else:
                print("Put Order Cancellation has  been successfull")
            
        
        elif(firstresponse.get('Success',None)==None and secondresponse.get('Success',None)==None):
            print("both order call and put have failed")
            print("------------END----------------")
            
        
        else:
            orderids = [] #0th index will contain call order, #1st index will contain put order 
            orderids.append(firstresponse['Success']['order_id']) 
            orderids.append(secondresponse['Success']['order_id'])            
            #define a mechanism to get profit and loss
            print("\n")
            print("----Starting live P&L feed...---")
            time.sleep(5)
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[0])

            call_status = None
            put_status = None

            #print(details)
            call_execution = -1
            put_execution = -1
            
            #print(f"order ids are : {orderids}")
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    call_execution = entry['average_price']
                    call_status = "Executed"
                    self.callexecution = call_execution
                    break
                    
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[1])
            #print(details)
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    put_execution = entry['average_price']
                    put_status = "Executed"
                    self.putexecution = put_execution
                    break
                    
            if(call_execution == -1 or put_execution == -1):
                print("Dear User order could not execute within time limit ..cancelling it")
                
                
                if(call_execution == -1 and put_execution == -1):
                    print("Both Order Call and Put could not execute to so cancelling it ..... ")
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])

                elif(call_execution == -1):
                    #call cancel order api
                    print("call order could not execute due to some reason so cancelling order")
                    #self.squareoff(self,rightval,exchange_code, stock_code, product_type, expiry_date, right, strike_price, action, order_type, validity, stoploss, quantity, price,validity_date, trade_password, disclosed_quantity)
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])

                    print("put order is executed squaring off....")
                    
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")

                elif(put_execution == -1):
                    #call cancel order api
                    print("put order could not execute due to some reason so cancelling order")
                    status = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])
                    print("call order is executed squaring off....")
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
                    
            else:
                print("Call order got executed at price :{0} Rs and Put Order got executed at price : {1} Rs".format(call_execution,put_execution))
                self.profit_and_loss(product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution)    
    
    def rsistrat(self, stock_code=None, strike_price=None, quantity=None, expiry_date=None, right=None, product_type=None, 
             order_type=None, exchange_code=None, interval = None, stock_token=None,stoploss=None,price=None,validity=None,validity_date=None,
             disclosed_quantity=None,settlement_id=None,cover_quantity=None,open_quantity=None,margin_amount=None,trade_password=None, protection_percentage=None):
        
        self.quantity = quantity
        self.exchange_code = exchange_code 
        self.stock_code = stock_code
        self.product_type = product_type 
        self.expiry_date = expiry_date  
        self.strike_price = strike_price
        self.price = price
        self.order_type = order_type
        self.right = right
        self.stock_token = stock_token
        self.interval = interval
        self.stoploss = stoploss
        self.validity = validity
        self.validity_date = validity_date
        self.disclosed_quantity = disclosed_quantity
        self.settlement_id = settlement_id
        self.cover_quantity = cover_quantity
        self.open_quantity = open_quantity
        self.margin_amount = margin_amount
        self.trade_password = trade_password
        self.protection_percentage = protection_percentage
        self.rsiflag = False

        listofcandles = deque(maxlen=14)

        def calculate_rsi(data, period=14):
            df = pd.DataFrame(data)
            df['close'] = pd.to_numeric(df['close'])
            delta = df['close'].diff()
            
            # Calculate gains and losses
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # Calculate average gain and average loss for the first 14 periods
            first_avg_gain = gain.tail(period).mean()
            first_avg_loss = loss.tail(period).mean()

            
            # Initialize lists to store average gains and losses
            avg_gains = [first_avg_gain]
            avg_losses = [first_avg_loss]
            
            # Calculate average gain and average loss for subsequent periods
            for i in range(period, len(data)):
                avg_gain = ((avg_gains[-1] * (period - 1)) + gain[i]) / period
                avg_loss = ((avg_losses[-1] * (period - 1)) + loss[i]) / period
                
                avg_gains.append(avg_gain)
                avg_losses.append(avg_loss)
            
            # Calculate RS
            avg_gains = pd.Series(avg_gains)
            avg_losses = pd.Series(avg_losses)
            rs = avg_gains / avg_losses
            
            # Calculate RSI
            rsi = 100 - (100 / (1 + rs))
            
            rsi = int(rsi.iloc[-1])
            
            return rsi

        def on_ticks(data):
            print("rsitick--",data)
            listofcandles.append(data)
            if(len(listofcandles) == 14):
                rsival = calculate_rsi(listofcandles)
                generatesignal(rsival)

        def buyandsell(sign):
            if(self.rsiflag and sign == "buy"):
                buydata =  self.client.place_order(stock_code=self.stock_code,
                        exchange_code=self.exchange_code,
                        product=self.product_type,
                        action = "buy",
                        order_type=self.order_type,
                        stoploss=self.stoploss,
                        quantity=self.quantity,
                        price = self.price,
                        validity= self.validity,
                        validity_date = self.validity_date,
                        disclosed_quantity = self.disclosed_quantity,
                        expiry_date = self.expiry_date,
                        right= self.right,
                        strike_price=self.strike_price)
                signal_logger.info(f"BuyAPIResponse-- {buydata}")
            if(self.rsiflag and sign == "sell"):
                portfolioapi = self.client.get_portfolio_positions()
                selldata =  self.client.square_off(
                        stock_code=self.stock_code,
                        exchange_code=self.exchange_code,
                        product=self.product_type,
                        action = "sell",
                        order_type=self.order_type,
                        stoploss=self.stoploss,
                        quantity=portfolioapi['Success'][0]['quantity'],
                        price = self.price,
                        validity= self.validity,
                        validity_date = self.validity_date,
                        disclosed_quantity = self.disclosed_quantity,
                        expiry_date = self.expiry_date,
                        right= self.right,
                        strike_price=self.strike_price,
                        protection_percentage=self.protection_percentage,
                        settlement_id=self.settlement_id,
                        cover_quantity=self.cover_quantity,
                        open_quantity=self.open_quantity,
                        margin_amount=self.margin_amount)
                signal_logger.info(f"SellAPIResponse-- {selldata}")   
        
        def generatesignal(rsival):
            if rsival < 30:
                signal = "Buy Signal"
                buyandsell("buy")
                signal_logger.info(f"Signal-- {signal}, RSI Value-- {rsival}")
            elif rsival > 70:
                signal = "Sell Signal"
                buyandsell("sell")
                signal_logger.info(f"Signal-- {signal}, RSI Value-- {rsival}")
            else:
                signal = "No Signal"
                
            rsi_logger.info(f"Signal-- {signal}, RSI Value-- {rsival}")    
            
        self.client.ws_connect()
        self.client.on_ticks = on_ticks

        try:
            while True:
                if self.stock_token and self.stock_token != "":
                    self.client.subscribe_feeds(stock_token=self.stock_token, interval=self.interval)
                else:
                    self.client.subscribe_feeds(exchange_code=self.exchange_code, stock_code=self.stock_code,
                                                product_type=self.product_type, expiry_date=self.expiry_date,
                                                strike_price=self.strike_price, right=self.right, interval=self.interval)
                
                # Other operations
                
                time.sleep(60)  # Sleep for 60 seconds

        except KeyboardInterrupt:
            self.client.unsubscribe_feeds()  # Unsubscribe from feeds
            rsi_logger.info("feeds unsubscribed")
            rsi_logger.error("Keyboard interrupted --- feeds unsubscribed")    
        except Exception as e:
            rsi_logger.error(f"RSI Error: {e}") 
    
    def stop(self,single_leg = False,is_butterfly = False,is_strangle = False):
        print("Stopping Current Strategy")
        if(self.socket == 1):
            self.client.ws_disconnect()
        self.socket = 0
        time.sleep(5)
        print("\n")
        print("Squaring off the  contracts and exiting strategy...")
        print("----------------------------------------")
        if(is_butterfly == True):
            square1 = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = sp1 , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = self.right)
            square2 = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = sp2 , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = self.right)
            square3 = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = sp3 , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = self.right)
            self.report(square1,square2,square3)
        elif(is_strangle == True):
            #print("strangle ke andar")
            square_call = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price_call , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
            square_put = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price_put , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")
            print("----------------------------------------")
            self.create_report(square_call,square_put,single_leg)
        elif(is_butterfly == False and single_leg == False):

            square_call = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
            square_put = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")
            print("----------------------------------------")
            self.create_report(square_call,square_put,single_leg)
        else:
            
            if(self.right.lower() == "call"):
                #print("call ke andar === ")
                square_call = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
                print("----------------------------------------")
                self.create_report(square_call,None,single_leg)
            else:
                #print("put ke andar...")
                square_put = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")
                print("----------------------------------------")
                self.create_report(None,square_put,single_leg)


    def get_pnl(self,is_butterfly = False):
        if(is_butterfly == True):
            outcome = (self.sp1_price + self.sp2_price + self.sp3_price)*int(quantity)
            print(f"P&L (NET) : {round(outcome,2)}/- Rs")
        else:
            outcome = (self.currentcall + self.currentput)*int(self.quantity)
            print(f"P&L (NET) : {round(outcome,2)}/- Rs")

        print("----------------------------------------")

    def report(self,square1,square2,square3):
        if(square1['Status'] == 200 and square2['Status'] == 200 and square3['Status'] == 200):
            sq1_id = square1['Status']['order_id']
            sq2_id = square2['Status']['order_id']
            sq3_id = square3['Status']['order_id']
            print("\nGenerating Final P&L report in 5 seconds....")
            time.sleep(5)
            
            records = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq1_id)
            
            sq1_price = -1
            
            for record in records['Success']:
                if(record['status'] == "Executed"):
                    sq1_price = record["average_price"]
                    break
                
                
            records = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq2_id)
            
            sq2_price = -1
            
            for record in records['Success']:
                if(record['status'] == "Executed"):
                    sq2_price = record["average_price"]
                    break
            
            records = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq3_id)
            
            sq3_price = -1
            
            for record in records['Success']:
                if(record['status'] == "Executed"):
                    sq3_price = record["average_price"]
                    break
                
            p1 = round((float(sq1_price) - float(self.exec1))*int(self.quantity),2) # calculate p & l
            p2 = round((float(sq2_price) - float(self.exec2))*int(self.quantity),2) # calculate p & l
            p3 = round((float(sq3_price) - float(self.exec3))*int(self.quantity),2) # calculate p & l
            
            
            print("----------------------------------------")
            print("Profit and Loss Report........")
            print(f"P&L ({self.sp1}) : {p1}/- Rs")
            print(f"P&L ({self.sp2}) : {p2}/- Rs")
            print(f"P&L ({self.sp3}) : {p3}/- Rs")
            print(f"P&L (NET) : {p1 + p2 + p3}/- Rs")
            
    def create_report(self,sq_call,sq_put,single_leg):

        if(single_leg):
            if(self.right.lower() == "call"):
                if(sq_call['Status'] == 200):
                    sq_callid = sq_call["Success"]['order_id']
                    print("\nGenerating Final P&L report in 5 seconds....")
                    time.sleep(5)
                    callrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq_callid)

                    sqcall_price = -1
                    for record in callrecords['Success']:
                        if(record['status'] == "Executed"):
                            sqcall_price = record["average_price"]
                            break
                    
                    plcall = round((float(sqcall_price) - float(self.callexecution))*int(self.quantity),2)
                    self.currentcall = (float(sqcall_price) - float(self.callexecution))

                    print("----------------------------------------")
                    print("Profit and Loss Report........")
                    print(f"P&L (CALL) : {plcall}/- Rs")
                    
                    print(f"P&L (NET) : {plcall}/- Rs")
                    print("----------------------------------------")
                
                else:
                    print("Error : SquareOff for call operation failed.")
            
            else:
                if(sq_put['Status'] == 200):
                    sq_putid = sq_put["Success"]['order_id']
                    print("\nGenerating Final P&L report in 5 seconds....")
                    time.sleep(5)
                    putrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq_putid)

                    sqput_price = -1
                    for record in putrecords['Success']:
                        if(record['status'] == "Executed"):
                            sqput_price = record["average_price"]
                            break
                    
                    plput = round((float(sqput_price) - float(self.putexecution))*int(self.quantity),2)
                    self.currentput = (float(sqput_price) - float(self.putexecution))

                    print("----------------------------------------")
                    print("Profit and Loss Report........")
                    
                    print(f"P&L (PUT) : {plput}/- Rs")
                    print(f"P&L (NET) : {plput}/- Rs")
                    print("----------------------------------------")
                
                else:
                    print("Error : SquareOff for put operation failed.")

            return
        
        if(sq_call['Status'] == 200 and sq_put['Status'] == 200):
            sq_callid = sq_call["Success"]['order_id']
            sq_putid = sq_put["Success"]['order_id']

            print("\nGenerating Final P&L report in 5 seconds....")
            time.sleep(5)
            callrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                        order_id= sq_callid)

            putrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                        order_id= sq_putid)

            sqcall_price = -1
            sqput_price = -1
            #time.sleep(5)
            for record in callrecords['Success']:
                if(record['status'] == "Executed"):
                    sqcall_price = record["average_price"]
                    break
            for record in putrecords["Success"]:
                if(record['status'] == "Executed"):
                    sqput_price = record["average_price"]
                    break
            
            plcall = round((float(sqcall_price) - float(self.callexecution))*int(self.quantity),2)
            plput = round((float(sqput_price) - float(self.putexecution))*int(self.quantity),2)

            self.currentcall = (float(sqcall_price) - float(self.callexecution))
            self.currentput = (float(sqput_price) - float(self.putexecution))

            print("----------------------------------------")
            print("Profit and Loss Report........")
            print(f"P&L (CALL) : {plcall}/- Rs")
            print(f"P&L (PUT) : {plput}/- Rs")
            print(f"P&L (NET) : {plput + plcall}/- Rs")
            print("----------------------------------------")
        else:
            print("One of Square off operation failed..")


    def single_leg(self,right, strategy_type,stock_code, strike_price, quantity, expiry_date, price = "0", stoploss = "",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO",put_price = "0", call_price = "0"):
        self.quantity = quantity
        self.strategy_type = strategy_type
        self.exchange_code = exchange_code 
        self.stock_code = stock_code
        self.product_type = product_type 
        self.expiry_date = expiry_date  
        self.strike_price = strike_price
        self.order_type = order_type
        self.validity = validity
        self.stoploss = stoploss
        #self.quantity = quantity
        self.validity_date = validity_date
        self.right = right
        self.flag = False

        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1

        action = "buy"

        if(self.strategy_type.lower() == "short"):
            action = "sell"


        data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)

        response = None
        order_id = None
        if(data['Status'] == 200):
            response = data['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}") 
            order_id = data['Success']['order_id']      
        
        else:
            response = data['Error']
            print(f"Error : {response} for {right}")

        if(order_id!=None):
            print("\n")
            print("----Starting live P&L feed...---")
            time.sleep(5)
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_id)

            #execution_price = -1
            
            
            #print(f"order ids are : {orderids}")
            call_execution = "0"
            put_execution = "0"

            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    execution = entry['average_price']
                    #call_status = "Executed"
                    if(right.lower() == "call"):
                        call_execution = execution
                        self.callexecution = execution
                        break
                    else:
                        put_execution = execution
                        self.putexecution = execution
                        break

        self.profit_and_loss(product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution,single_leg = True)

    
    def checklimit(self,sp1,sp2,sp3):
        self.sp1 = sp1
        self.sp2 = sp2
        self.sp3 = sp3
        
        net_gain_loss = (self.sp1_price + self.sp2_price + self.sp3_price)*int(quantity)
        print(f"P&L (NET) : {round(net_gain_loss,2)}/- Rs")
        print("----------------------------------------")
        formatted_date = self.get_date_format(self.expiry_date)

        if(net_gain_loss > 0 and net_gain_loss >= self.maxprofit):
            print("TakeProfit reached...")
            #print("SquareOff operation on both contracts call and put begins....")
            
            
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp1, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp2, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp3, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.stop(is_butterfly = True)
            
            #self.flag = True
            return
        if(net_gain_loss < 0 and net_gain_loss <= self.maxloss):
            print("MaxLoss reached...")
            #print("SquareOff operation on both contracts call and put begins....")
            
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp1, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp2, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp3, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.stop(is_butterfly = True)
            return
        
    def monitor_pnl(self,exec1,exec2,exec3,sp1,sp2,sp3):
        self.exec1 = exec1
        self.exec2 = exec2
        self.exec3 = exec3
        formatted_date = self.get_date_format(self.expiry_date)
        def on_ticks(data):
            value = data
            if(value['strike_price'] == sp1):
                self.sp1_price = round(float(value['last']) - float(exec1), 2)
                if(self.strategy_type.lower() == "short"):
                    self.sp1_price = self.sp1_price*-1
                    
                self.checklimit(sp1,sp2,sp3)
                    
            if(value['strike_price'] == sp2):
                self.sp2_price = round(float(value['last']) - float(exec2), 2)
                if(self.strategy_type.lower() == "short"):
                    self.sp2_price = self.sp2_price*-1
                self.checklimit(sp1,sp2,sp3)
                
            if(value['strike_price'] == sp3):
                self.sp3_price = round(float(value['last']) - float(exec3), 2)
                if(self.strategy_type.lower() == "short"):
                    self.sp3_price = self.sp3_price*-1
                self.checklimit(sp1,sp2,sp3)
                
        self.client.on_ticks = on_ticks
        self.client.subscribe_feeds(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = "options", expiry_date= formatted_date, strike_price=sp1, right = self.right, get_exchange_quotes=True, get_market_depth=False) 
        self.client.subscribe_feeds(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = "options", expiry_date= formatted_date, strike_price=sp2, right = self.right, get_exchange_quotes=True, get_market_depth=False) 
        self.client.subscribe_feeds(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = "options", expiry_date= formatted_date, strike_price=sp3, right = self.right, get_exchange_quotes=True, get_market_depth=False) 

    
    def butterfly(self,right,strategy_type,stock_code,spread, strike_price, quantity, expiry_date, stoploss = "",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO"):
        self.strategy_type = strategy_type
        self.right = right
        self.quantity = quantity
        self.expiry_date = expiry_date
        self.exchange_code = exchange_code
        self.validity_date = validity_date
        self.strike_price = strike_price
        self.order_type = order_type
        self.stoploss = stoploss
        self.validity = validity

        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1
            
        
        action = "sell"
        alternate = dict()
        
        alternate["buy"] = "sell"
        alternate["sell"] = "buy"
        
        
        if(strategy_type.lower() == "short"):
            action = "buy"
        
        data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)
        
        sprice1 = str(float(strike_price) - float(spread))
        sprice2 = str(float(strike_price) + float(spread))

        data2 =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = alternate[action],
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=sprice1)
        
        data3 =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = alternate[action],
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity = quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right = right,
                    strike_price=sprice2)
        order_ids = []
        
        if(data['Status'] == 200):
            response = data['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}") 
            order_id = data['Success']['order_id']      
            order_ids.append(order_id)
            
        else:
            response = data['Error']
            print(f"Error : {response} for {right}")
            
        if(data2['Status'] == 200):
            response = data2['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data2['Success']['order_id']}") 
            order_id = data2['Success']['order_id']      
            order_ids.append(order_id)
        else:
            response = data2['Error']
            print(f"Error : {response} for {right}")


        if(data3['Status'] == 200):
            response = data3['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data3['Success']['order_id']}") 
            order_id = data3['Success']['order_id']     
            order_ids.append(order_id)
            
        else:
            response = data3['Error']
            print(f"Error : {response} for {right}")
        
        time.sleep(5)
        
        execution1 ="0" #first order
        execution2  ="0" # second order
        execution3 ="0" # third order
        
        if(len(order_ids) == 3):
            res1 = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_ids[0])
            res2 = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_ids[1])
            res3 = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_ids[2])
            

            for entry in res1['Success']:
                if(entry['status'] == "Executed"):
                    execution1 = entry['average_price']
                    break
            
            for entry in res2['Success']:
                if(entry['status'] == "Executed"):
                    execution2 = entry['average_price']
                    break
            
            for entry in res3['Success']:
                if(entry['status'] == "Executed"):
                    execution3 = entry['average_price']
                    break
            monitor_pnl(execution1,execution2,execution3,sprice1,strike_price,sprice2)
    
    # implementation of strangle       
    def strangle(self,strike_price_call,strike_price_put, strategy_type,stock_code, quantity, expiry_date, stoploss = "", put_price = "0", call_price = "0",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO"):
        self.quantity = quantity
        self.strategy_type = strategy_type
        self.exchange_code = exchange_code 
        self.stock_code = stock_code
        self.product_type = product_type 
        self.expiry_date = expiry_date  
        #self.strike_price = strike_price
        self.order_type = order_type
        self.validity = validity
        self.stoploss = stoploss
        self.validity_date = validity_date
        self.strike_price_call = strike_price_call
        self.strike_price_put = strike_price_put
        self.flag = False
        
        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1
            

        if(strategy_type.lower() not in ["long","short"]):
            return("strategy_type should be either long or short..")

        def place_order_method(stock_code,exchange_code,product,action,order_type,stoploss,quantity,price,validity,validity_date,expiry_date,right,strike_price,res_queue):
         
            data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)
            response = None
            if(data['Status'] == 200):
                response = data['Success']['message']
                print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}")
                res_queue.put(data)
            else:
                response = data['Error']
                print(f"Error : {response} for {right}")
                res_queue.put(data)
            return(data)
                  
        res_queue = queue.Queue()
        action = "buy"

        if(strategy_type.lower()== "short"):
            action = "sell"
        
        #create thread for call and put order to execute simultaneously for buy type
        t1 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,call_price,validity,validity_date,expiry_date,"Call",strike_price_call,res_queue))
        t1.start()
        t1.join()
        
        firstresponse = res_queue.get()
        
        res_queue = queue.Queue()
        t2 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,put_price,validity,validity_date,expiry_date,"Put",strike_price_put,res_queue))
        t2.start()
        t2.join()
        secondresponse = res_queue.get()
        
        
        #if one of the order fails then cancel the other one which is successfull
        if(firstresponse.get('Status')==200 and secondresponse.get('Status')==500):
            print("Put Order Failed....")
            order_id = firstresponse['Success']['order_id']
            data  = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)

            if(data.get("Success",None) == None):
                print("Call Order Cancellation has not been successfull")
                print("----------END-------------------")
            else:
                print("Call Order Cancellation has  been successfull")
                print("----------END-------------------")
            
            
        
        elif(secondresponse.get('Status')==200 and firstresponse.get('Status')==500):
            print("Call order failed....")
            order_id = secondresponse['Success']['order_id']
            
            data = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)
            
            if(data.get("Success",None) == None):
                print("Put Order Cancellation has not been successfull")
            else:
                print("Put Order Cancellation has  been successfull")
            
        
        elif(firstresponse.get('Success',None)==None and secondresponse.get('Success',None)==None):
            print("both order call and put have failed")
            print("------------END----------------")
            
        
        else:
            orderids = [] #0th index will contain call order, #1st index will contain put order 
            orderids.append(firstresponse['Success']['order_id']) 
            orderids.append(secondresponse['Success']['order_id'])            
            #define a mechanism to get profit and loss
            print("\n")
            print("----Starting live P&L feed...---")
            time.sleep(5)
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[0])

            call_status = None
            put_status = None

            #print(details)
            call_execution = -1
            put_execution = -1
            
            #print(f"order ids are : {orderids}")
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    call_execution = entry['average_price']
                    call_status = "Executed"
                    self.callexecution = call_execution
                    break
                    
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[1])
            #print(details)
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    put_execution = entry['average_price']
                    put_status = "Executed"
                    self.putexecution = put_execution
                    break
                    
            if(call_execution == -1 or put_execution == -1):
                print("Dear User order could not execute within time limit ..cancelling it")
                
                
                if(call_execution == -1 and put_execution == -1):
                    print("Both Order Call and Put could not execute to so cancelling it ..... ")
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])

                elif(call_execution == -1):
                    #call cancel order api
                    print("call order could not execute due to some reason so cancelling order")
                    #self.squareoff(self,rightval,exchange_code, stock_code, product_type, expiry_date, right, strike_price, action, order_type, validity, stoploss, quantity, price,validity_date, trade_password, disclosed_quantity)
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])

                    print("put order is executed squaring off....")
                    
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = strike_price_put , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")

                elif(put_execution == -1):
                    #call cancel order api
                    print("put order could not execute due to some reason so cancelling order")
                    status = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])
                    print("call order is executed squaring off....")
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = strike_price_call , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
                    
            else:
                print("Call order got executed at price :{0} Rs and Put Order got executed at price : {1} Rs".format(call_execution,put_execution))
                self.profit_and_loss(product_type, stock_code,"0", quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution,strike_price_call,strike_price_put,is_strangle = True)
                #self.profit_and_loss(product_type, stock_code, strike_price_put, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution)
                
                
    def strat_subscribe_live_feeds(self,**kwargs):     
        try:
            def on_ticksfeeds(data):
                if 'symbol' in data and 'exchange' in data and 'close' in data:
                    data =json.dumps(data)
                    self.strat_processing(data, source="live_feeds")

            self.client.on_ticks = on_ticksfeeds
            for params in kwargs['kwargs']:
                datetime_obj = datetime.strptime(params['expiry_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                formatted_date_str = datetime_obj.strftime('%d-%b-%Y')
                payload = {'exchange_code':(params['exchange_code']).upper(), 
                           'stock_code':(params['stock_code']).upper(), 
                           'product_type':(params['product_type']), 
                           'expiry_date':formatted_date_str, 
                           'strike_price':(params['strike_price']), 
                           'right':(params['right'])}

                FourLeg_logger.debug(f"live feeds subscribed: {self.client.subscribe_feeds(**payload)}") 
                print(f"Live feeds Subscribed")
    
                
            self.live_feed_running = threading.Event()
            self.live_feed_running.set() 

            while self.live_feed_running.is_set():
                time.sleep(1)  # 
  
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())        

    def strat_unsubscribe_feeds(self,**kwargs):
        try:   
            for params in kwargs['kwargs']:
                datetime_obj = datetime.strptime(params['expiry_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                formatted_date_str = datetime_obj.strftime('%d-%b-%Y')
                payload = {'exchange_code':(params['exchange_code']).upper(), 
                            'stock_code':(params['stock_code']).upper(), 
                            'product_type':(params['product_type']), 
                            'expiry_date':formatted_date_str, 
                            'strike_price':(params['strike_price']), 
                            'right':(params['right'])} 
                FourLeg_logger.debug(f"live feeds unsubscribed: {self.client.unsubscribe_feeds(**payload)}")
                print(f"Live feeds Unsubscribed")

        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())  

    def strat_subscribe_order_feeds(self):
        try:
            def on_ticksorder(data):
                if 'sourceNumber' in data and 'orderMatchAccount' in data and 'stockCode' in data and 'executedQuantity' in data:
                    data = json.dumps(data)
                    self.strat_processing(data, source="order_feeds")

            self.client.on_ticks = on_ticksorder
            FourLeg_order_logger.debug(f"order feeds subscribed: {self.client.subscribe_feeds(get_order_notification=True)}")
            print(f"Order feeds Subscribed")

            self.order_feed_running = threading.Event()
            self.order_feed_running.set()

            while self.order_feed_running.is_set():
                time.sleep(1)  # 
 
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())  

    def FourLeg_place_order(self, option):
        try:

            stock_code = option.get("stock_code", "").upper()
            exchange_code = option.get("exchange_code", "").upper()
            product_type = option.get("product_type", "")
            action = option.get("action", "")
            quantity = option.get("quantity", "")
            validity = option.get("validity", "")
            validity_date = option.get("validity_date", "")
            expiry_date = option.get("expiry_date", "")
            right = option.get("right", "")
            strike_price = option.get("strike_price", "")

            po_payload = {
                "stock_code": stock_code,
                "exchange_code": exchange_code,
                "product": product_type,
                "action": action,
                "quantity": quantity,
                "validity": validity,
                "order_type":"market",
                "validity_date": validity_date,
                "expiry_date": expiry_date,
                "right": right,
                "strike_price": strike_price
            }

            res = self.client.place_order(**po_payload)
            
            api_data = {
                'payload' :po_payload,
                'response': res
            }
            
            self.first_order_api_response_store.append(api_data)
            FourLeg_api_logger.debug(f"place order api data: {api_data}")
            return res
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc()) 


    def fetch_order_ids(self,data):
        order_ids = [entry['response']['Success']['order_id'] for entry in data]
        return order_ids
    
    def strat_trade_list(self):
        try:
            total_pl = 0
            
            payload = {
                "from_date": self.from_date,
                "to_date": self.to_date,
                "exchange_code": self.exchange_code,
                "product_type": self.product_type,
                "action": "",
                "stock_code": "",
            }
            
            res= self.client.get_trade_list(**payload)
            api_data = {
                'payload' :payload,
                'response': res
            }
            
            FourLeg_api_logger.debug(f"trade_list api data: {api_data}")
            FourLeg_api_logger.debug(f"place order store: {self.first_order_api_response_store}")
            order_ids1 = self.fetch_order_ids(self.first_order_api_response_store)
            FourLeg_api_logger.debug(f"place order order_ids1: {order_ids1}")
            FourLeg_api_logger.debug(f"square off order store: {self.square_off_api_response_store}")
            order_ids2 = self.fetch_order_ids(self.square_off_api_response_store)
            FourLeg_api_logger.debug(f"square off order_ids2: {order_ids2}")

            
            for order1 in order_ids1:
                average_cost1, strike_price1, right1, action1 = self.fetch_average_cost(res, order1)
                for order2 in order_ids2:
                    average_cost2, strike_price2, right2, action2 = self.fetch_average_cost(res, order2)
                    if int(strike_price1) == int(strike_price2) and right1.upper() == right2.upper():
                        FourLeg_api_logger.debug(f"price matched")
                        if action1.upper() == 'BUY':
                            pl = (float(average_cost2) - float(average_cost1)) * float(self.quantity)
                            FourLeg_api_logger.debug(f"PLLLLL: {pl}")
                        elif action1.upper() == 'SELL':
                            pl = (float(average_cost1) - float(average_cost2)) * float(self.quantity)
                            FourLeg_api_logger.debug(f"PLLLLL: {pl}")
                        total_pl += pl
                        
            print(f"Profit/Loss booked = {round(total_pl,2)} /- Rs")
            return round(total_pl,2)
        
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())
            
    def fetch_average_cost(self,response, target_order_id):
        for entry in response['Success']:
            if entry['order_id'] == target_order_id:
                 return entry['average_cost'], entry['strike_price'], entry['right'], entry['action']
        time.sleep(1)
        return self.strat_trade_list()

    
    def FourLeg_squareoff(self, option):
        try:
            if option.get("action").upper() == 'BUY':
                manipulate_action = "sell"
            elif option.get("action").upper() == 'SELL':
                manipulate_action = "buy"
            
            stock_code = option.get("stock_code", "").upper()
            exchange_code = option.get("exchange_code", "").upper()
            product_type = option.get("product_type", "")
            action = manipulate_action
            quantity = option.get("quantity", "")
            validity = option.get("validity", "")
            validity_date = option.get("validity_date", "")
            expiry_date = option.get("expiry_date", "")
            right = option.get("right", "")
            strike_price = option.get("strike_price", "")

            po_payload = {
                "stock_code": stock_code,
                "exchange_code": exchange_code,
                "product": product_type,
                "action": action,
                "quantity": quantity,
                "validity": validity,
                "order_type":"market",
                "validity_date": validity_date,
                "expiry_date": expiry_date,
                "right": right,
                "strike_price": strike_price
            }

            res = self.client.square_off(**po_payload)
            api_data = {
                'payload' :po_payload,
                'response': res
            }
            
            self.square_off_api_response_store.append(api_data)
            FourLeg_api_logger.debug(f"sqaureoff api data: {api_data}")
            return res
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())

    def place_multiple_orders(self, options_list):
        try:
            for option in options_list:
                self.FourLeg_place_order(option)
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())

    def squareoff_multiple_orders(self, options_list,option_list_1):
        try:
            for option in options_list:
                time.sleep(1)
                res = self.FourLeg_squareoff(option)
            for option in option_list_1:
                time.sleep(1)
                res = self.FourLeg_squareoff(option)
            return None
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())

    def strat_place_order(self, orders_list):
        try:
            if(self.first_orders_flag == False):
                if (self.fist_order_count == 0):
                    self.place_multiple_orders(orders_list[:2])
                elif(self.fist_order_count == 2):
                    self.place_multiple_orders(orders_list[2:4])
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())
    
    def stop_strat_place_order(self, orders_list):
        try:
            res = self.squareoff_multiple_orders(orders_list[2:4],orders_list[:2])
            return None
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())

    def strat_funds(self):
        try:
            FourLeg_api_logger.debug(f"get margin api payload: {self.exchange_code}")
            res = self.client.get_margin(exchange_code=self.exchange_code)
            FourLeg_api_logger.debug(f"get margin api response: {res}")
            cash_limit = res["Success"]["cash_limit"]
            limit_list = res["Success"]["limit_list"]
            total_funds = cash_limit
            for entry in limit_list:
                total_funds += entry["amount"]
            return total_funds
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())

    def strat_margin_calculator(self):
        try:
            merged_array = []
            for order in self.ic_orders_list:
                time.sleep(1)
                order['price'] = self.FourLeg_quote(order)
                merged_order = {
                    "strike_price": str(order['strike_price']),
                    "quantity": str(order['quantity']),
                    "right": str(order['right']),
                    "product": str(order['product_type']),
                    "action": str(order['action']),
                    "price": str(order['price']),
                    "expiry_date": str(order['expiry_date']),
                    "stock_code": str(order['stock_code']).upper(),
                    "cover_order_flow": "N",
                    "fresh_order_type": "N",
                    "cover_limit_rate": "0",
                    "cover_sltp_price": "0",
                    "fresh_limit_rate": "0",
                    "open_quantity": "0"
                }
                merged_array.append(merged_order)
            FourLeg_api_logger.debug(f"margin_calculator api payload: {merged_array}")
            res = self.client.margin_calculator(merged_array, exchange_code=self.exchange_code.upper())
            FourLeg_api_logger.debug(f"margin_calculator api response: {res}")
            if res["Status"] != 200:
                return None
            else:
                span_margin_required = res["Success"]["span_margin_required"]
                return span_margin_required
    
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())
            # self.stop_strategy(is_FourLeg=True)

    def FourLeg_quote(self,order):
        try:
            FourLeg_api_logger.debug(f"get quote api payload: {order}")
            res = self.client.get_quotes(stock_code=str(order['stock_code']).upper(),
                    exchange_code=str(order['exchange_code']).upper(),
                    expiry_date=str(order['expiry_date']),
                    product_type=str(order['product_type']),
                    right=str(order['right']),
                    strike_price=str(order['strike_price']))
            if isinstance(res, dict):
                dict_str = json.dumps(res)
                FourLeg_api_logger.debug("get quote api response:" + dict_str)  # Log the dictionary as JSON
            else:
                FourLeg_api_logger.debug(f"get_quotes response is not a dictionary: {res}")
                FourLeg_api_logger.error(f"Request failed with status code: {res.status_code}")
                FourLeg_api_logger.error(f"Request failed with body: {order}")
                FourLeg_api_logger.error(f"Response content: {res.text}")
            return res['Success'][0]['ltp']
        except Exception as e:
            FourLeg_Error_logger.debug(f"get quote Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())
            # self.stop_strategy(is_FourLeg=True)

    def sufficient_funds(self):
        try:
            print("Calculating funds ....")
            self.user_funds = self.strat_funds()
            FourLeg_logger.debug(f"Client Fund: {self.user_funds}")
            print(f"Client Fund: {self.user_funds}")
            print("Calculating margin ....")
            self.user_margin = self.strat_margin_calculator()
            FourLeg_logger.debug(f"Margin Required: {self.user_margin}")
            print(f"Margin Required: {self.user_margin}")  


            if self.user_funds == None or self.user_margin == None :
                FourLeg_logger.debug("margin calculator or funds api response not as per requirement")
                print("Order does not get executed")
                self.stop_strategy(is_FourLeg=True)
            else:
                self.order_thread.start()
                self.process_thread.start()
                time.sleep(2)
                if float(self.user_funds) > float(self.user_margin):
                    self.place_order_thread.start()
                    self.place_order_thread.join()
                else:
                    print("Insufficient funds............ ")
                    FourLeg_logger.debug("Insufficient funds")
                    FourLeg_logger.debug(f"Total funds: {self.user_funds}")
                    FourLeg_logger.debug(f"Total margin: {self.user_margin}")
                    self.stop_strategy(is_FourLeg=True)

        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())


    def FourLeg_firstorderflag(self, data):

        try:
            order_data = json.loads(data)
            if(order_data.get('orderStatus') == 'Executed'):
                FourLeg_order_logger.debug(f"order feeds: {data}")
                print(f"Order executed for {order_data.get('optionType')} {order_data.get('orderFlow')} ")
                print("------------------------------------------------------------------------------------------------------------")
                order_id = order_data.get('orderReference')
                order_key = f"{order_data.get('strikePrice')}_{order_data.get('orderFlow')}_{order_data.get('optionType')}"
                FourLeg_order_logger.debug(f"order_key: {order_key}")
                if (order_key not in self.first_order_history):
                    self.first_order_history[order_key] = order_data
                    self.fist_order_count = len(self.first_order_history)
            FourLeg_logger.debug(f"first_order_history: {len(self.first_order_history)}")

            if(self.fist_order_count >= 2 and len(self.first_order_history) >= 2):
                self.FourLeg_countcheck()

        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())


    def FourLeg_countcheck(self):
        try:
            if(self.fist_order_count == 4 and len(self.first_order_history)== 4 and self.Four_leg_level_check == 1):
                self.Four_leg_level_check = 2 
                self.first_orders_flag = True
                self.live_thread.start()
            elif(self.fist_order_count == 2 and len(self.first_order_history) == 2 and self.Four_leg_level_check == 0):
                self.Four_leg_level_check = 1 
                self.strat_place_order(self.ic_orders_list)
            if(self.square_off_count == 4 and len(self.square_off_count) == 4 and self.Four_leg_level_check == 2):
                self.Four_leg_level_check = 4 
                self.square_off__flag = True
            elif(self.square_off_count == 2 and len(self.square_off_count) == 2 and self.Four_leg_level_check == 2):
                self.Four_leg_level_check = 3 
                self.strat_place_order(self.ic_orders_list)
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())

    def strat_processing(self, data, source=None):

        try:
            if (source == "order_feeds"):
                if(self.first_orders_flag):
                    FourLeg_order_logger.debug(f"square order feeds: {data}")
                else:
                    self.FourLeg_firstorderflag(data)
            elif (source == "live_feeds" and self.first_orders_flag == True):
                self.FourLeg_calculation(data)
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())
            


    def FourLeg_calculation(self, data):
        try:
            json_data = json.loads(data)
            ltp = float(json_data['last'])
            for id, details in self.first_order_history.items():
                adjusted_strike_price = int(details['strikePrice']) // 100
                pl_str = f"{str(details['optionType']).upper()}_{str(adjusted_strike_price)}"
                ltp_str = f"{str(json_data['right']).upper()}_{str(json_data['strike_price'])}"
                if ((str(details['optionType']).upper() == str(json_data['right']).upper()) and (str(adjusted_strike_price) == str(json_data['strike_price']))):
                    average_executed_rate = float(details['cancelFlag']) / 100
                    executed_quantity = float(details['executedQuantity'])
                    if details['orderFlow'].upper() == 'BUY':
                        pppp = f"{ltp}_{average_executed_rate}_{executed_quantity}"
                        self.potential_pnl[pl_str] = (ltp - average_executed_rate) * executed_quantity
                    elif details['orderFlow'].upper() == 'SELL':
                        pppp = f"{ltp}_{average_executed_rate}_{executed_quantity}"
                        self.potential_pnl[pl_str] = (average_executed_rate - ltp) * executed_quantity
                    self.overall_profit = round(sum(self.potential_pnl.values()),2)
                    if (len(self.potential_pnl) == 4) and self.PLFlag == False and self.strategy_running:
                        FourLeg_PL_logger.debug(f"P/L= {self.overall_profit}")
                        display(Markdown(f"```\nCurrent P/L = {self.overall_profit} /- Rs\n```"))
                        if self.overall_profit >= self.maxprofit or self.overall_profit <= self.maxloss:
                            self.PLFlag = True
                            FourLeg_PL_logger.debug(f"P/L reached= {self.overall_profit}")
                            FourLeg_PL_logger.debug(f"defined max-profit= {self.maxprofit}")
                            FourLeg_PL_logger.debug(f"defined max-loss= {self.maxloss}")
                            FourLeg_PL_logger.debug(f"All Orders details: {self.potential_pnl}")
                            display(Markdown(f"```\nP/L Reached= {self.overall_profit} /- Rs\n```"))
                            res = self.stop_strat_place_order(self.ic_orders_list)
                            try:
                                print("Calculating Profit/Loss .....")
                                time.sleep(1)
                                restl = self.strat_trade_list()
                                
                            except:
                                print("something error")
                                pass
                            display(Markdown(f"```\nAll Positions Squared off\n```"))
                            self.stop_Fourleg()                
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())      
                
        
    def four_leg(self, stock_code=None, strike_price=None, quantity=None, expiry_date=None, right=None, product_type=None, 
             order_type=None, exchange_code=None, interval = None, stock_token=None, stoploss=None, price=None, validity=None, validity_date=None,
             disclosed_quantity=None, settlement_id=None, cover_quantity=None, open_quantity=None, margin_amount=None, trade_password=None, protection_percentage=None,
             call_short_strike = None, put_short_strike = None, call_long_strike = None, put_long_strike = None, four_leg_strategy = False):

        try:
            
            self.stop_event.clear()
            self.strategy_running = True
            self.stock_code = stock_code
            self.strike_price = strike_price
            self.quantity = quantity
            self.expiry_date = expiry_date
            self.right = right
            self.product_type = product_type
            self.order_type = order_type
            self.exchange_code = exchange_code
            self.interval = interval
            self.stock_token = stock_token
            self.stoploss = stoploss
            self.price = price
            self.validity = validity
            self.validity_date = validity_date
            self.disclosed_quantity = disclosed_quantity
            self.settlement_id = settlement_id
            self.cover_quantity = cover_quantity
            self.open_quantity = open_quantity
            self.margin_amount = margin_amount
            self.trade_password = trade_password
            self.protection_percentage = protection_percentage
            self.potential_pnl = {}
            self.call_short_strike = call_short_strike
            self.put_short_strike = put_short_strike
            self.call_long_strike = call_long_strike
            self.put_long_strike = put_long_strike
            self.four_leg_strategy  = True
            self.today = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            self.dummytoday = datetime.utcnow()
            self.from_date = self.dummytoday.replace(hour=8, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            self.to_date = self.dummytoday.replace(hour=16, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            if self.maxprofit > 0 and self.maxloss < 0:
                if self.four_leg_strategy:
                    FourLeg_logger.info("Starting Four Leg Strategy")
                    print("----------------------------------------------")
                    print("Starting Four Leg Strategy")
                    print("----------------------------------------------")
                    self.start_ic()
            else:
                print("Incorrect Inputs for Max Profit or Max Loss")

        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())  

    def stop_strategy(self,single_leg = False,is_butterfly = False,is_strangle = False, is_FourLeg = False):
        if is_FourLeg == True:
            if not self.strategy_running:
                print("No strategy is currently running.")
                return
            self.strategy_running = False

            print("----------------------------------------------")
            print("Stopping strategy....")
            print("----------------------------------------------")

            self.stop_event.set()
            
            current_thread = threading.current_thread()
            for thread in self.threads:
                if isinstance(thread, threading.Thread):  # Ensure thread is a Thread object
                    if thread.is_alive() and thread is not current_thread:
                        FourLeg_logger.debug(f"Force-terminating thread: {thread.name}")
                        try:
                            thread.join(timeout=10)
                        except RuntimeError as e:
                            FourLeg_logger.error(f"Error joining thread {thread.name}: {e}")
                    elif thread is current_thread:
                        FourLeg_logger.warning(f"Attempted to join the current thread: {thread.name}")
                    else:
                        FourLeg_logger.info(f"Thread {thread.name} is not alive")
                else:
                    FourLeg_logger.error("Item in self.threads is not a valid thread object")
                
            if len(self.first_order_api_response_store) >= 4:
                print("----------------------------------------------")        
                print("Squaring off...")
                print("----------------------------------------------")
                res = self.stop_strat_place_order(self.ic_orders_list)
                try:
                    print("Calculating Profit/Loss .....")
                    time.sleep(1)
                    restl = self.strat_trade_list()
                    
                except:
                    print("Error while calculating profit/loss")
                    pass

            print("----------------------------------------------")
            print("Strategy stopped.")
            print("----------------------------------------------")
        else:
            self.stop(single_leg, is_butterfly, is_strangle)

    def start_ic(self):

        self.exchange_code = "NFO"
        self.product_type = "options"
        self.validity = "day"
        self.validity_date = self.today
        self.feeds_unsubscribed = False
        
        try:
            pass
            self.ic_orders_list = [
                    {
                        'stock_code': self.stock_code.lower(),
                        'exchange_code': self.exchange_code.lower(),
                        'product_type': self.product_type.lower(),
                        'action': "buy",
                        'quantity': self.quantity,
                        'validity': self.validity.lower(),
                        'validity_date': self.validity_date,
                        'expiry_date': self.expiry_date,
                        'right': "call",
                        'strike_price': self.call_long_strike
                    },
                    {
                        'stock_code': self.stock_code.lower(),
                        'exchange_code': self.exchange_code.lower(),
                        'product_type': self.product_type.lower(),
                        'action': "buy",
                        'quantity': self.quantity,
                        'validity': self.validity.lower(),
                        'validity_date': self.validity_date,
                        'expiry_date': self.expiry_date,
                        'right': "put",
                        'strike_price': self.put_long_strike
                    },
                    {
                        'stock_code': self.stock_code.lower(),
                        'exchange_code': self.exchange_code.lower(),
                        'product_type': self.product_type.lower(),
                        'action':"sell",
                        'quantity': self.quantity,
                        'validity': self.validity.lower(),
                        'validity_date': self.validity_date,
                        'expiry_date': self.expiry_date,
                        'right':"call",
                        'strike_price':self.call_short_strike
                    },
                    {
                        'stock_code': self.stock_code.lower(),
                        'exchange_code': self.exchange_code.lower(),
                        'product_type': self.product_type.lower(),
                        'action':"sell",
                        'quantity': self.quantity,
                        'validity': self.validity.lower(),
                        'validity_date': self.validity_date,
                        'expiry_date': self.expiry_date,
                        'right':"put",
                        'strike_price':self.put_short_strike
                    }
            ]


            self.placed_orders_count = 0
            self.total_orders_to_place = 8
            self.all_orders_placed = False
            self.first_orders_flag = False
            self.square_off__flag = False
            self.fist_order_count = 0
            self.square_off_count = 0
            self.first_order_api_response_store = []
            self.order_versus_data = {} 
            self.square_off_api_response_store = []
            self.first_order_history = {}
            self.squareoff_order_history = []
            self.timer_interval = 10
            self.Four_leg_level_check = 0
            self.PLFlag = False
            self.placeorder_orderid = []
            self.squareoff_orderid = []
            self.threads = []

            self.live_thread = threading.Thread(target=self.strat_subscribe_live_feeds, kwargs={'kwargs': self.ic_orders_list})
            self.live_unsub_thread = threading.Thread(target=self.strat_unsubscribe_feeds, kwargs={'kwargs': self.ic_orders_list})
            self.order_thread = threading.Thread(target=self.strat_subscribe_order_feeds)
            self.process_thread = threading.Thread(target=self.strat_processing, args=(self.ic_orders_list,))
            self.place_order_thread = threading.Thread(target=self.strat_place_order, args=(self.ic_orders_list,))
            self.strat_sufficient_funds = threading.Thread(target=self.sufficient_funds)
            
            self.threads.append(self.live_thread)
            self.threads.append(self.live_unsub_thread)
            self.threads.append(self.order_thread)
            self.threads.append(self.process_thread)
            self.threads.append(self.place_order_thread)
            self.threads.append(self.strat_sufficient_funds)


            self.strat_sufficient_funds.start()

        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc())  

    def stop_Fourleg(self):
        try:
            if not self.strategy_running:
                print("----------------------------------------------")
                print("No strategy is currently running.")
                print("----------------------------------------------")
                return
            self.strategy_running = False
            FourLeg_logger.debug("Stopping Threads.....")
            self.stop_event.set()
            for thread in self.threads:
                if thread.is_alive():
                    FourLeg_logger.debug(f"Force-terminating thread: {thread.name}")
                    thread.join(timeout=10)

            display(Markdown(f"```\nStrategy stopped.\n```"))
                 
        except Exception as e:
            FourLeg_Error_logger.debug(f"Exception: {e}")
            FourLeg_Error_logger.error("Detailed error information:\n" + traceback.format_exc()) 