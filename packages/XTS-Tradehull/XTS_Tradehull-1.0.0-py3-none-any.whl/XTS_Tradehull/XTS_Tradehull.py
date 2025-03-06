import copy
import pdb
from .Connect import XTSConnect
# from .XTS_websocket import XTS_LTP
import datetime
from datetime import timedelta
import pandas as pd
import traceback
import requests
from pytz import timezone
from dateutil import parser
import random
import os
import time
import json
import math
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
import warnings
import xlwings as xw
import logging
import numpy as np
import mibian
import re
warnings.filterwarnings('ignore')


# =================Install below python dependencies=================================================>
# pip install selenium
# pip install urllib3
# python -m pip install --upgrade pip
# ==================================================================>

class Tradehull:
	interactive_key: str
	interactive_secret: str
	market_key: str
	market_secret: str
	client_code: str
	xts1: None
	xts2: None
	interval_parameters:dict
	params:dict
	instrument_file:pd.core.frame.DataFrame
	filename : str
	step_df:pd.core.frame.DataFrame
	index_step_dict:dict
	index_underlying:dict
	call:str
	put:str

	def __init__(self,interactive_key: str,interactive_secret: str,market_key: str,market_secret: str,client_code: str,root_url:str):

		date_str = str(datetime.datetime.now().today().date())
		if not os.path.exists('Dependencies/log_files'):
			os.makedirs('Dependencies/log_files')
		file = 'Dependencies/log_files/logs' + date_str + '.log'
		logging.basicConfig(filename=file, level=logging.DEBUG,format='%(levelname)s:%(asctime)s:%(threadName)-10s:%(message)s') 
		self.logger = logging.getLogger()
		logging.info('system_Viren.py  started system')
		logging.getLogger('socketio').setLevel(logging.WARNING)
		logging.getLogger('engineio').setLevel(logging.WARNING)
		logging.getLogger("requests").setLevel(logging.WARNING)
		logging.getLogger("urllib3").setLevel(logging.WARNING)
		self.logger.info("STARTED THE PROGRAM")

		try:
			self.token_and_exchange                         = dict()
			self.token_dict                                 = {'NIFTY':{'token':26000,'exchange':'NSECM'},'NIFTY 50':{'token':26000,'exchange':'NSECM'},'BANKNIFTY':{'token':26001,'exchange':'NSECM'},'NIFTY BANK':{'token':26001,'exchange':'NSECM'},'FINNIFTY':{'token':26034,'exchange':'NSECM'},'NIFTY FIN SERVICE':{'token':26034,'exchange':'NSECM'},'MIDCPNIFTY':{'token':26121,'exchange':'NSECM'},'NIFTY MID SELECT':{'token':26121,'exchange':'NSECM'},'SENSEX':{'token':26065,'exchange':'BSECM'},'BANKEX':{'token':26118,'exchange':'BSECM'}}
			self.segment_dict                               = {"NSECM": 1, "NSEFO": 2, "NSECD": 3, "BSECM": 11, "BSEFO": 12, "MCXFO": 51}
			self.get_login(interactive_key, interactive_secret,market_key, market_secret,root_url)
			#self.exchange_dict                             ={'NSEFO':self.xts2.EXCHANGE_NSEFO,'NSECM':self.xts2.EXCHANGE_NSECM,'BSECM':self.xts2.EXCHANGE_BSECM,'NSECD':self.xts2.EXCHANGE_NSECD,'MCXFO':self.xts2.EXCHANGE_MCXFO}
			self.interval_parameters                        = {'1minute':  60,'2minute':  120,'3minute':  180,'4minute':  240,'5minute':  300,'10minute':  600,'15minute':  900,'30minute':  1800,'60minute':  3600,'day':86400}
			self.index_step_dict                            = {'MIDCPNIFTY':25,'SENSEX':100,'BANKEX':100,'NIFTY': 50, 'NIFTY 50': 50, 'NIFTY BANK': 100, 'BANKNIFTY': 100, 'NIFTY FIN SERVICE': 50, 'FINNIFTY': 50}
			self.index_underlying                           = {"NIFTY 50":"NIFTY","NIFTY BANK":"BANKNIFTY","NIFTY FIN SERVICE":"FINNIFTY","NIFTY MID SELECT":"MIDCPNIFTY"}
			self.intervals_dict                             = {'minute': 1, '2minute':2, '3minute': 3, '5minute': 5, '10minute': 10,'15minute': 15, '30minute': 30, '60minute': 60, 'day': 80}
			self.ltp_list                                   = list()
			self.complete_orders                            = list()   

		except Exception as e:
			print(f"Got exception in __init__ as: {e}")	
			self.logger.exception("Failed to initialize XTS TradeHull as: " + str(e))

	def get_login(self,interactive_key, interactive_secret,market_key, market_secret,root_url):
		try:
			self.xts1                                           = XTSConnect(apiKey = interactive_key, secretKey = interactive_secret,source= "WEBAPI",root = root_url)
			self.xts2                                           = XTSConnect(apiKey = market_key, secretKey =market_secret,source= "WEBAPI", root = root_url)
			self.exchange_dict                                  = {self.xts1:{'NSEFO':self.xts1.EXCHANGE_NSEFO,'NSECM':self.xts1.EXCHANGE_NSECM,'BSECM':self.xts1.EXCHANGE_BSECM,'NSECD':self.xts1.EXCHANGE_NSECD,'MCXFO':self.xts1.EXCHANGE_MCXFO},self.xts2:{'NSEFO':self.xts2.EXCHANGE_NSEFO,'NSECM':self.xts2.EXCHANGE_NSECM,'BSECM':self.xts2.EXCHANGE_BSECM,'NSECD':self.xts2.EXCHANGE_NSECD,'MCXFO':self.xts2.EXCHANGE_MCXFO}}
			response1                                           = self.xts1.interactive_login()
			response2                                           = self.xts2.marketdata_login()
			self.set_marketDataToken                            = response2['result']['token']
			self.client_code                                    = response2['result']['userID']
			print(f'Market and Interactive login successful')
			self.instrument_df                                  = self.get_instrument_file()
			print('Got the instrument file')
			# self.xts_ltp                                        = XTS_LTP(self.set_marketDataToken, self.client_code, self.xts2, self.instrument_df)
			# self.ltp_data                                       = self.xts_ltp.ltp_data
			# print("XTS LTP Websocket Connected")
		except Exception as e:
			print("Got exception in get_login as: {e}")	
			self.logger.exception(f'got exception in get_login as {e} ')
			self.logger.exception(response1,response2)
			traceback.print_exc()

	def get_instrument_file(self):
		try:
			global instrument_df
			current_date = time.strftime("%Y-%m-%d")
			expected_file = 'all_instrument ' + str(current_date) + '.csv'
			for item in os.listdir("Dependencies\\"):
				path = os.path.join(item)

				if (item.startswith('all_instrument')) and (current_date not in  item.split(" ")[1]):
					if os.path.isfile("Dependencies\\"+path):
						os.remove("Dependencies\\"+path)
						exchangesegments = [self.xts1.EXCHANGE_NSECM, self.xts1.EXCHANGE_NSEFO, self.xts1.EXCHANGE_MCXFO,self.xts1.EXCHANGE_BSECM,'BSEFO',self.xts1.EXCHANGE_NSECD]
						response3 = self.xts1.get_master(exchangeSegmentList=exchangesegments)
						res = response3['result'].split('\n')
						res = [item.split("|") for item in res]
						instrument_df  = pd.DataFrame(res)
						instrument_df.rename(columns={0:"ExchangeSegment",1:"ExchangeInstrumentID",2:"InstrumentType",3:"Name",4:"Description",5:"Series",6:"NameWithSeries",7:"InstrumentID",8:"PriceBand.High",9:"PriceBand.Low",10:"FreezeQty",11:"TickSize",12:"LotSize",13:"Multiplier",14:"UnderlyingInstrumentId",15:"UnderlyingIndexName",16:"ContractExpiration",17:"StrikePrice",18:"OptionType"},inplace=True)
						instrument_df.to_csv("Dependencies\\" + expected_file)

			if expected_file in os.listdir("Dependencies\\"):
				try:
					print(f"reading existing file {expected_file}")
					instrument_df = pd.read_csv("Dependencies\\"+expected_file,low_memory=False)
					if 'Unnamed: 0' in instrument_df.columns:
						instrument_df = instrument_df.drop(['Unnamed: 0'], axis = 1)

				except Exception as e:
					print("Instrument file is not generated completely")
					pass
			else:
				print("picking new file from XTS")
				exchangesegments = [self.xts1.EXCHANGE_NSECM, self.xts1.EXCHANGE_NSEFO, self.xts1.EXCHANGE_MCXFO,self.xts1.EXCHANGE_BSECM,'BSEFO',self.xts1.EXCHANGE_NSECD]
				response3 = self.xts1.get_master(exchangeSegmentList=exchangesegments)
				res = response3['result'].split('\n')
				res = [item.split("|") for item in res]
				instrument_df  = pd.DataFrame(res)
				instrument_df.rename(columns={0:"ExchangeSegment",1:"ExchangeInstrumentID",2:"InstrumentType",3:"Name",4:"Description",5:"Series",6:"NameWithSeries",7:"InstrumentID",8:"PriceBand.High",9:"PriceBand.Low",10:"FreezeQty",11:"TickSize",12:"LotSize",13:"Multiplier",14:"UnderlyingInstrumentId",15:"UnderlyingIndexName",16:"ContractExpiration",17:"StrikePrice",18:"OptionType"},inplace=True)
				instrument_df.to_csv("Dependencies\\" + expected_file)
			return instrument_df
		except Exception as e:
			print(f"Got exception in get_instrument_file as: {e}")	
			self.logger.exception(f"Getting error at get_instrument_file as {e}")
			return pd.DataFrame()


	def get_data_for_single_script(self, names: list) -> dict:
		try:
			all_quotes_list = []  
			all_list_quotes = []  
			batch_size = 50  
			if type(names) != list:
				names = [names]
			
			for i in range(0, len(names), batch_size):
				batch_names = names[i:i + batch_size]
				instruments = []
				
				for name in batch_names:
					try:
						if (name in self.token_dict) and (name not in self.token_and_exchange):
							token 										= self.token_dict[name]['token']
							token_exchange 								= self.token_dict[name]['exchange']
							self.token_and_exchange[name] = {'token': token, 'token_exchange': token_exchange}
						elif name not in self.token_and_exchange:
							token = self.instrument_df.loc[self.instrument_df['Description'] == name].iloc[0][['ExchangeInstrumentID']][0]
							token_exchange = self.instrument_df.loc[self.instrument_df['Description'] == name].iloc[0][['ExchangeSegment']][0]
							self.token_and_exchange[name] = {'token': token, 'token_exchange': token_exchange}
						else:
							token = self.token_and_exchange[name]['token']
							token_exchange = self.token_and_exchange[name]['token_exchange']
					except Exception as e:
						print(f'{name} is not correct!! Check spelling. Error: {str(e)}')
						self.logger.exception(f'{name} is not correct!! Check spelling. Error: {str(e)}')
						continue 
					
					instrument = {'exchangeSegment': str(self.segment_dict[token_exchange]), 'exchangeInstrumentID': str(token)}
					instruments.append(instrument)
				
				if not instruments:
					continue  
				
				try:
					response = self.xts2.get_quote(Instruments=instruments, xtsMessageCode=1501, publishFormat='JSON')

					quotes_list_data = json.loads(response['result']['quotesList']) if isinstance(response['result']['quotesList'], str) else response['result']['quotesList']
					all_quotes_list.extend(quotes_list_data)
					
					list_quotes_data = json.loads(response['result']['listQuotes']) if isinstance(response['result']['listQuotes'], str) else response['result']['listQuotes']
					all_list_quotes.extend(list_quotes_data)
					
				except Exception as e:
					print(f'Error fetching data for batch: {str(e)}')
					self.logger.exception(f"Error fetching data for batch: {str(e)}")
					continue  
				
				time.sleep(1)  
			
			combined_response = {
				'type': 'success',
				'code': 200,
				'description': 'Combined batch response',
				'result': {
					'mdp': response['result'].get('mdp', {}),
					'quotesList': all_quotes_list,  
					'listQuotes': all_list_quotes  
				}
			}
			
			return combined_response
		
		except Exception as e:
			print(f"Got exception in get_data_for_single_script as: {e}")
			self.logger.exception(f"Getting error at get_data_for_single_script as {e}")
			# # traceback.print_exc()
			# data_ = {'type': 'error', 'code': 500, 'description': 'Failed to get data', 'result': {}}
			# return data_

	def get_quote(self,names):
		try:
			response = self.get_data_for_single_script(names)
			i=0
			result = {}
			if response:
				if type(names)==list:
					for i,data in enumerate(response['result']['listQuotes']):
						data = json.loads(data)
						instruments = [name for name, details in self.token_dict.items() if details['token'] == data['ExchangeInstrumentID']]
						name = instruments[0] if instruments else None
						if name is None:
							name_new = self.instrument_df.loc[self.instrument_df['ExchangeInstrumentID'] == data['ExchangeInstrumentID']]
							if name_new.empty:
								continue
							name = name_new.iloc[0]['Description']
						result[name] = data
					return result
				else:
					data    = response['result']['listQuotes'][0]
					data    = json.loads(data)
					return data
			else:
				print('No data returned from XTS')
				return None
		except Exception as e:
			print(f"Got exception in get_quote as: {e}")
			self.logger.exception(f"Getting error at get_quote as {e}")
			

	def get_ltp(self,names):
		try:
			response = self.get_data_for_single_script(names)
			i=0
			result = {}
			if response:
				if type(names)==list:
					for data in response['result']['listQuotes']:
						data = json.loads(data)
						instruments = [name for name, details in self.token_dict.items() if details['token'] == data['ExchangeInstrumentID']]
						name = instruments[0] if instruments else None
						if name is None:
							name_new = self.instrument_df.loc[self.instrument_df['ExchangeInstrumentID'] == data['ExchangeInstrumentID']]
							if name_new.empty:
								continue
							name = name_new.iloc[0]['Description']
						result[name] = data['LastTradedPrice']
					return result
				else:
					try:
						data 	= response['result']['listQuotes'][0]		
						data 	= json.loads(data)
						return data['LastTradedPrice']
					except:
						print(f'DATA NOT AVAILABLE FOR {names}')
						self.logger.exception(f'DATA NOT AVAILABLE FOR {names}')

						return 0
			else:
				print('No data returned from XTS')
				return 0
		except Exception as e:
			print(f"Got exception in get_ltp as: {e}")
			self.logger.exception(f"Getting error at get_ltp as {e}")
			
			

	# def get_ltp(self,name):
	# 	try:
	# 		if name not in self.ltp_data:
	# 			self.ltp_list.append(name)
	# 			self.xts_ltp.get_ltp_data(self.ltp_list)
	# 			time.sleep(1)
	# 		if name in self.ltp_data:
	# 			ltp = self.ltp_data[name]
	# 			return float(ltp)
	# 		else:
	# 			return None
		
	# 	except Exception as e:
	# 		print(f"Got exception in get_ltp as: {e}")	
	# 		self.logger.exception(f'Getting exception at ltp as {e}')
	# 		return None	

	# def get_quote(self,names):
	# 	try:
	# 		if names not in self.ltp_data:
	# 			self.ltp_list.append(names)
	# 		self.xts_ltp.get_ltp_data(self.ltp_list)
	# 		time.sleep(1)
	# 		quote ={names:self.xts_ltp.quote_data[name]['Touchline'] for name in self.xts_ltp.quote_data if name in self.xts_ltp.quote_data}
	# 		while len(quote)==0:
	# 			quote ={name:self.xts_ltp.quote_data[names]['Touchline'] for name in self.xts_ltp.quote_data if name in self.xts_ltp.quote_data}
	# 		return quote
	# 	except Exception as e:
	# 		print(f"Got exception in get_quote as: {e}")	
	# 		self.logger.exception(f'Getting exception at quote as {e}')
	# 		return None	


	def get_intraday_allowed_script(self) -> list:
		"""
			This function will return the MIS allowed stock for zerodha
		"""
		try:
						 # https://docs.google.com/spreadsheets/d/1fLTsNpFJPK349RTjs0GRSXJZD-5soCUkZt9eSMTJ2m4/edit
			sheet_url = "https://docs.google.com/spreadsheets/d/1fLTsNpFJPK349RTjs0GRSXJZD-5soCUkZt9eSMTJ2m4/edit#gid=288818195"
			url_1 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
			allowed_script = pd.read_csv(url_1)
			allowed_script = allowed_script.iloc[2:,1].to_list()
			return allowed_script

		except Exception as e:
			print(f"Got exception in get_intraday_allowed_script as: {e}")
			self.logger.exception(f"Getting error at get_intraday_allowed_script as {e}")
			traceback.print_exc()
		
		
		# try:
		#   sheet_url = "https://docs.google.com/spreadsheets/d/1ZTyh6GiHTwA1d-ApYdn5iCmRiBLZoAtwigS7VyLUk_Y/edit#gid=0"
		#   url_1 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
		#   allowed_script = pd.read_csv(url_1)
		#   allowed_script = allowed_script['Stocks allowed for MIS'].to_list()
		#   return allowed_script
		# except Exception as e:
		#   print(e)
		#   traceback.print_exc()

	def get_expiry_dates(self,underlying:str,Opt_fut:str):
		# get_expiry_dates(underlying = 'NIFTY',Opt_fut = 'Option')
		try:
			opt_Fut_dict = {'Future':'FUTIDX','Option':'OPTIDX'}
			segment_code = 2 if underlying in ['NIFTY',"BANKNIFTY","FINNIFTY","MIDCPNIFTY"] else 12
			dates = self.xts1.get_expiry_date(exchangeSegment=segment_code,series=opt_Fut_dict[Opt_fut],symbol=underlying)
			sorted_dates = sorted(date.split('T')[0] for date in dates['result'])
			return sorted_dates
		except Exception as e:
			self.logger.exception(f"Error at get_expiry_dates as {e}")

	def check_expiry_date(self,underlying,Expiry):
		try:
			data = self.instrument_df[self.instrument_df['Name']==underlying.upper()].sort_values('ContractExpiration')
			date = pd.to_datetime(data[data['ContractExpiration']!='1']['ContractExpiration']).dt.date.unique()
			if Expiry in date:
				return True,date
			else:
				return False,date
		except Exception as e:
			print(f"Got exception in check_expiry_date as: {e}")	
			self.logger.exception(f"Error at checking_expiry_date as {e}")
	
	def get_lot_size(self,script_name: str):
		try:
			data = self.instrument_df[(self.instrument_df['Description'] == script_name)]
			if len(data) == 0:
				raise NameError("Enter valid Script Name")
				return 0
			else:
				quantity_per_lot = data.iloc[0]['LotSize']
				return int(quantity_per_lot)
		except Exception as e:
			print(f"Got exception in get_lot_size as: {e}")	
			self.logger.exception(f"Getting error at Lot size as {e}")
			return None
	
	def get_freeze_quantity(self,strike):
		try:
			data =  self.instrument_df[(self.instrument_df['Description'] == strike)]
			if len(data) == 0:
				raise NameError("Enter valid Script Name")
				return 0
			else:
				freez_qty = data.iloc[0]['FreezeQty']
				return int(int(freez_qty) - 1)
		except Exception as e:
			print(f"Got exception in get_freeze_quantity as: {e}")	
			self.logger.exception(f"Getting error at Freeze quantity as {e}")
			return None
	
	

	def get_historical_data(self,name: str, timeframe: str, interval: int) -> pd.core.frame.DataFrame:
		try:
			timeframe_param = {1: 60, 2: 120, 3: 180, 5: 300, 10: 600, 15: 900, 30: 1800, 60: 3600}
			index = {"BANKNIFTY": "NIFTY BANK","NIFTY":"NIFTY 50","MIDCPNIFTY":"NIFTY MID SELECT", "FINNIFTY":"NIFTY FIN SERVICE","SENSEX":"SENSEX","BANKEX":"BANKEX"}
			exchange_index = {"BANKNIFTY": "NSECM","NIFTY":"NSECM","MIDCPNIFTY":"NSECM", "FINNIFTY":"NSECM","SENSEX":"BSECM","BANKEX":"BSECM"}
			if name not in index:
				exchangeInstrument = self.instrument_df.loc[(self.instrument_df['Description'] == name)]
				exchangeInstrumentID = exchangeInstrument.iloc[0]['ExchangeInstrumentID']
				exchange = exchangeInstrument.iloc[0]['ExchangeSegment']
			if name in index:
				exchangeInstrumentID = index[name]
				exchange = exchange_index[name]
			timeframe = self.interval_parameters[timeframe]
			to_date = datetime.datetime.today().date()
			from_date = to_date - datetime.timedelta(days=interval)
			start = datetime.datetime.strftime(from_date, "%b %d %Y %H%M%S")
			end = datetime.datetime.strftime(to_date, "%b %d %Y %H%M%S")
			start = start[:11] + " 091500"
			end = end[:11] + " 235959"
			
			time.sleep(1)
			response = self.xts2.get_ohlc(exchangeSegment=exchange, exchangeInstrumentID=exchangeInstrumentID, startTime=start,endTime=end, compressionValue=timeframe)
			data = response['result']['dataReponse'].split(",")
			res = [item.split("|") for item in data]
			data = pd.DataFrame(res)
			col = {0: 'date', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume', 6: 'oi'}
			data = data.rename(columns=col)
			# data['date'] = [datetime.datetime.fromtimestamp(int(date)).strftime("%Y-%m-%d %I:%M:%S") for date in
			#                 data['date']]

			# data["date"] = pd.to_datetime(data["date"], unit="s")
			data['date'] = data['date'].astype('int').astype('datetime64[s]')
			data.drop([7], axis=1, inplace=True)
			data[['open','high','low','close','volume','oi']] =data[['open','high','low','close','volume','oi']].astype('float')
			# data=data[data['date'].dt.date>=datetime.datetime.now().date()]
			return data
		except Exception as e:
			print(f"Got exception in get_historical_data as: {e}")	
			self.logger.exception(f"Historical data error for {name} as {e}")
			return pd.DataFrame()

	def get_atm(self,ltp,underlying,expiry,script_type) -> str:
		"""
		ltp should be float or int
		underlying should be string
		expiry should be in int format 
		0 - curent expiry
		1 - next expiry
		2 - third expiry from now 
		"""
		try:
			if underlying in self.index_step_dict.keys():
				Steps_value = self.index_step_dict[underlying]
			else:
				raise TypeError('Unknown underlying name')
			

			Strike = round(ltp / Steps_value)*Steps_value
			expiry_dates = self.get_expiry_dates(underlying ,'Option')
			date = expiry_dates[expiry] + 'T14:30:00'
			data = self.instrument_df[(self.instrument_df['Name'] == underlying) & (self.instrument_df['StrikePrice'] == str(Strike)) & (self.instrument_df['ContractExpiration'] == date)& (self.instrument_df['Description'].str[-2:]== script_type)]
			if len(data) == 1:
				return data['Description'].iloc[0]
			else:
				raise('check the input parametere corrrectly')
		except Exception as e:
			print(f"Got exception in get_atm as: {e}")	
			self.logger.exception(f"Historical data error for get_atm {underlying} as {e}")
			return None

	def get_itm(self,ltp,underlying,expiry,script_type,multiplier) -> str:
		"""
		ltp should be float or int
		underlying should be string
		expiry and multiplier should be in int format 
		0 - curent expiry
		1 - next expiry
		2 - third expiry from now 
		"""
		try:
			if underlying in self.index_step_dict.keys():
				Steps_value = self.index_step_dict[underlying]
			else:
				raise TypeError('Unknown underlying name')

			atm_strike = round(ltp / Steps_value)*Steps_value
			if script_type == 'CE':
				strike_price = atm_strike - (Steps_value*multiplier)
			
			elif script_type == 'PE':
				strike_price = atm_strike + (Steps_value*multiplier)
			else:
				raise TypeError("check input parameter correctly for get_itm()")
			
			expiry_dates = self.get_expiry_dates(underlying ,'Option')
			date = expiry_dates[expiry] + 'T14:30:00'
			data = self.instrument_df[(self.instrument_df['Name'] == underlying) & (self.instrument_df['StrikePrice'] == str(strike_price)) & (self.instrument_df['ContractExpiration'] == date)& (self.instrument_df['Description'].str[-2:]== script_type)]
			if len(data) == 1:
				return data['Description'].iloc[0]
			else:
				raise('check the input parametere corrrectly')
		except Exception as e:
			print(f"Got exception in get_itm as: {e}")	
			self.logger.exception(f"Historical data error for get_itm {underlying} as {e}")
			return None			

	def get_otm(self,ltp,underlying,expiry,script_type,multiplier) -> str:
		"""
		ltp should be float or int
		underlying should be string
		expiry and multiplier should be in int format 
		0 - curent expiry
		1 - next expiry
		2 - third expiry from now 
		"""
		try:
			if underlying in self.index_step_dict.keys():
				Steps_value = self.index_step_dict[underlying]
   
			else:
				raise TypeError('Unknown underlying name')

			atm_strike = round(ltp / Steps_value)*Steps_value
			if script_type == 'CE':
				strike_price = atm_strike + (Steps_value*multiplier)
			
			elif script_type == 'PE':
				strike_price = atm_strike - (Steps_value*multiplier)
			else:
				raise TypeError("check input parameter correctly for get_otm()")
			
			expiry_dates = self.get_expiry_dates(underlying ,'Option')
			date = expiry_dates[expiry] + 'T14:30:00'
			data = self.instrument_df[(self.instrument_df['Name'] == underlying) & (self.instrument_df['StrikePrice'] == str(strike_price)) & (self.instrument_df['ContractExpiration'] == date)& (self.instrument_df['Description'].str[-2:]== script_type)]
			if len(data) == 1:
				return data['Description'].iloc[0]
			else:
				raise('check the input parametere corrrectly')
		except Exception as e:
			self.logger.exception(f"Historical data error for get_otm {underlying} as {e}")
			return None	

	def check_valid_instrument(self,name):
		try:
			df = self.instrument_df[self.instrument_df['Description']==name]
			if len(df) != 0:
				return f"instrument {name} is valid"
			else:
				return f"instrument {name} is invalid"

		except Exception as e:
			print(f"Got exception in check_valid_instrument as: {e}")	
			self.logger.exception(f"check_valid_instrument error for {name} as {e}")
			return None

	def get_pnl(self):
		"""
			use to get live pnl
			pnl()
		"""
			#Simulation purpose
		try:
			time.sleep(1)
			pos_book = self.xts1.get_position_daywise(clientID=self.client_code)
			pos_book_dict = pos_book['result']['positionList']
			pos_book = pd.DataFrame(pos_book_dict)
			live_pnl = []

			if pos_book.empty:
				return 0

			for pos_ in pos_book_dict:
				token = int(pos_['ExchangeInstrumentId'])
				underlying = self.instrument_df.loc[self.instrument_df['ExchangeInstrumentID']==token].iloc[0][['Description']][0]
				closePrice = self.get_ltp(underlying)
				Total_MTM = (float(pos_['SellAmount']) - float(pos_['BuyAmount'])) + (int(pos_['Quantity']) *closePrice * float(pos_['Multiplier']))
				# Total_MTM = (float(pos_['SumOfTradedQuantityAndPriceSell']) - float(pos_['SumOfTradedQuantityAndPriceBuy'])) + (int(pos_['Quantity']) *closePrice * float(pos_['Multiplier']))
				live_pnl.append(Total_MTM)
			
			return sum(live_pnl)
		except Exception as e:
			print(f"Got exception in pnl as: {e}")	
			self.logger.exception(f'got exception in pnl as {e} ')
			traceback.print_exc()
			return None

	def order_placement(self,stock,quantity,price,trigger_price,productType,order_type,transaction_type,validity_type='DAY'):
		try:
			strike_exchange = self.instrument_df.loc[self.instrument_df['Description']==stock].iloc[0][['ExchangeSegment']][0]
			exchangeInstrumentID = self.instrument_df.loc[(self.instrument_df['ExchangeSegment'] == strike_exchange) & (self.instrument_df['Description'] == stock)]
			exchangeInstrumentID = exchangeInstrumentID.iloc[0]['ExchangeInstrumentID']
			exchange = {'NSEFO': self.xts1.EXCHANGE_NSEFO, 'NSECM': self.xts1.EXCHANGE_NSECM, 'BSECM': self.xts1.EXCHANGE_BSECM,'NSECD': self.xts1.EXCHANGE_NSECD, 'MCXFO': self.xts1.EXCHANGE_MCXFO,'BSEFO': 'BSEFO'}
			self.order_Type = {'LIMIT': self.xts1.ORDER_TYPE_LIMIT, 'MARKET': self.xts1.ORDER_TYPE_MARKET,'STOPLIMIT': self.xts1.ORDER_TYPE_STOPLIMIT, 'STOPMARKET': self.xts1.ORDER_TYPE_STOPMARKET}
			product = {'MIS': self.xts1.PRODUCT_MIS, 'NRML': self.xts1.PRODUCT_NRML, 'CNC': 'CNC'}
			Validity = {'DAY': self.xts1.VALIDITY_DAY, 'IOC': 'IOC'}
			transactiontype = {'BUY': self.xts1.TRANSACTION_TYPE_BUY, 'SELL': self.xts1.TRANSACTION_TYPE_SELL}

			exchangeSegment = exchange[strike_exchange.upper()]
			product_Type = product[productType.upper()]
			order_type = self.order_Type[order_type.upper()]
			order_side = transactiontype[transaction_type.upper()]
			time_in_force = Validity[validity_type.upper()]

			order = self.xts1.place_order(exchangeSegment=exchangeSegment, exchangeInstrumentID=int(exchangeInstrumentID),
									productType=product_Type, orderType=order_type, orderSide=order_side,
									timeInForce=time_in_force, disclosedQuantity=0,
									orderQuantity=int(quantity), limitPrice=price, stopPrice=trigger_price,
									orderUniqueIdentifier="123abc")

			order_id = order['result']['AppOrderID']
			if order_id == None:
				c_orders = pd.DataFrame(self.xts1.get_order_book()['result'])
				time.sleep(1)
				order_id = c_orders.iloc[-1]['order_id']	
				return str(order_id)
			else:
				return str(order_id)

		except Exception as e:
			print(f"Got exception in place_order as: {e}")	
			self.logger.exception(f'Got exception in place_order as {e}')
			return None


	def get_order_status(self, order_id):
		try:
			flag = True
			while flag == True:
				try:
					time.sleep(1)
					order_history = self.xts1.get_order_history(appOrderID=order_id,clientID=self.client_code)
					send_order_history = order_history['result'][-1]
					flag = False
				except Exception as e:
					pass
			return send_order_history['OrderStatus']
		except Exception as e:
			print(f"Got exception in get_order_status as: {e}")	
			self.logger.exception("exception in get_order_status {0} ".format(str(e)))
			return None

	def get_executed_price(self, order_id):
		try:
			flag = True
			while flag == True:
				try:
					order_history = self.xts1.get_order_history(appOrderID=str(order_id),clientID=self.client_code)
					time.sleep(1)
					send_order_history = order_history['result'][-1]
					flag = False
				except Exception as e:
					pass
			order_price = send_order_history['OrderAverageTradedPrice']
			if order_price is None:
				order_price = 0
			elif type(order_price)==str:
				if len(order_price)==0:
					order_price = 0
			order_price = float(order_price)

			return order_price
		except Exception as e:
			print(f"Got exception in get_executed_price as: {e}")	
			self.logger.exception("exception in get_executed_price {0}".format(str(e)))
			return None
	def order_report(self):
		'''
		If watchlist has more than two stock, using order_report, get the order status and order execution price
		order_report()
		'''
		try:
			order_details= dict()
			order_exe_price= dict()
			order_placed_time = dict
			time.sleep(1)
			status_df = self.xts1.get_order_book()['result']
			status_df = pd.DataFrame(status_df)
			if not status_df.empty:
				status_df['AppOrderID'] =status_df['AppOrderID'].astype("str")
				status_df.set_index('AppOrderID',inplace=True)
				order_details = status_df['OrderStatus'].to_dict()
				order_exe_price = status_df['OrderAverageTradedPrice'].to_dict()
				order_placed_time = status_df['LastUpdateDateTime'].to_dict()
			
			return order_details, order_exe_price, order_placed_time
		except Exception as e:
			self.logger.exception(f"Exception in getting order report as {e}")
			return dict(), dict(), dict()

	def cancel_all_orders(self):
		try:
			order_details = dict()
			product_detail = {'MIS': self.xts1.PRODUCT_MIS, 'NRML': self.xts1.PRODUCT_NRML, 'CNC': 'CNC'}
			product_type = "MIS"
			product = product_detail[product_type]
			time.sleep(1)
			data = self.xts1.get_order_book()["result"]
			if data is None:
				return order_details
			orders = pd.DataFrame(data)
			if orders.empty:
				return order_details
			# trigger_pending_orders = orders.loc[(orders['OrderStatus'] == 'PendingNew') & (orders['ProductType'] == product)]
			open_orders = orders.loc[(orders['OrderStatus'] == 'New') & (orders['ProductType'] == product)]
			# for index, row in trigger_pending_orders.iterrows():
			# 	response = self.xt1.cancel_order(appOrderID=row["AppOrderID"], orderUniqueIdentifier='NA', clientID= self.clientID)
			self.xts1.cancelall_order(exchangeInstrumentID=0,exchangeSegment=self.xts1.EXCHANGE_NSEFO)

			for index, row in open_orders.iterrows():
				response = self.xts1.cancel_order(appOrderID=row["AppOrderID"], orderUniqueIdentifier="123abc", clientID= self.client_code )
			position_dict = self.xts1.get_position_netwise(clientID= self.client_code )["result"]["positionList"]
			positions_df = pd.DataFrame(position_dict)
			if positions_df.empty:
				return order_details
			positions_df['Quantity']=positions_df['Quantity'].astype(int)
			bought = positions_df.loc[(positions_df['Quantity'] > 0) & (positions_df['ProductType'] == product)]
			sold = positions_df.loc[(positions_df['Quantity'] < 0) & (positions_df['ProductType'] == product)]

			for index, row in bought.iterrows():
				qty = int(row["Quantity"])
				order = self.xts1.place_order(exchangeSegment=row["ExchangeSegment"],
									   exchangeInstrumentID=int(row["ExchangeInstrumentId"]),
									   productType=row["ProductType"], orderType=self.xts1.ORDER_TYPE_MARKET,
									   orderSide=self.xts1.TRANSACTION_TYPE_SELL, timeInForce='DAY', disclosedQuantity=0,
									   orderQuantity=qty, limitPrice=0, stopPrice=0, orderUniqueIdentifier="NA",
									   clientID=self.client_code )
				stock = row['TradingSymbol']
				sell_order_id=order['result']['AppOrderID']
				ltp = self.get_ltp(stock)
				order_details[stock]=dict({'orderid':sell_order_id,'price':ltp})				
				time.sleep(0.1)

			for index, row in sold.iterrows():
				qty = int(row["Quantity"]) * -1
				order = self.xts1.place_order(exchangeSegment=row["ExchangeSegment"],
									   exchangeInstrumentID=int(row["ExchangeInstrumentId"]),
									   productType=row["ProductType"], orderType=self.xts1.ORDER_TYPE_MARKET,
									   orderSide=self.xts1.TRANSACTION_TYPE_BUY,
									   timeInForce='DAY', disclosedQuantity=0,
									   orderQuantity=qty, limitPrice=0, stopPrice=0,
									   orderUniqueIdentifier="NA", clientID=self.client_code )
				stock = row['TradingSymbol']
				buy_order_id=order['result']['AppOrderID']
				ltp = self.get_ltp(stock)
				order_details[stock]=dict({'orderid':buy_order_id,'price':ltp})
				time.sleep(0.1)

			if len(order_details)!=0:
				_,order_price,_ = self.order_report()
				for key,value in order_details.items():
					orderid = str(value['orderid'])
					if orderid in order_price:
						if order_price is None:
							continue
						elif type(order_price)==str:
							if len(order_price)==0:
								continue 
						order_details[key]['price'] = order_price[orderid] 	
			return order_details
		except Exception as e:
			print(f"problem cancel_all_orders as: {e}")
			self.logger.exception("problem cancel_all_orders as: {e}")
			traceback.print_exc()

	def modify_order(self,appOrderID,modifiedOrderType,modifiedOrderQuantity,modifiedLimitPrice,modifiedStopPrice):
		try:
			
			self.order_Type = {'Limit': self.xts1.ORDER_TYPE_LIMIT, 'Market': self.xts1.ORDER_TYPE_MARKET,'StopLimit': self.xts1.ORDER_TYPE_STOPLIMIT, 'StopMarket': self.xts1.ORDER_TYPE_STOPMARKET}
			product = {'MIS': self.xts1.PRODUCT_MIS, 'NRML': self.xts1.PRODUCT_NRML, 'CNC': 'CNC'}
			Validity = {'DAY': self.xts1.VALIDITY_DAY, 'IOC': 'IOC'}


			product_Type = product['MIS']
			order_type = self.order_Type[modifiedOrderType]
			time_in_force = Validity['DAY']

			order = self.xts1.modify_order(appOrderID=appOrderID,modifiedProductType=product_Type,modifiedOrderType=order_type,modifiedOrderQuantity=modifiedOrderQuantity,modifiedDisclosedQuantity=0,modifiedLimitPrice=modifiedLimitPrice,modifiedStopPrice=modifiedStopPrice,modifiedTimeInForce=time_in_force,orderUniqueIdentifier="123abc")

			order_id = order['result']['AppOrderID']
			if order_id == None:
				time.sleep(1)
				c_orders = pd.DataFrame(self.xts1.get_order_book()['result'])
				print("didnt find order id from api trying to get it via wrapper")
				order_id = c_orders.iloc[-1]['order_id']
				return str(order_id)
			else:
				return str(order_id)

		except Exception as e:
			print(f"problem modify order as: {e}")
			self.logger.exception(f'Got exception in modify_order as {e}')
			traceback.print_exc()


	def cancel_order(self,OrderID):
		try:
			self.xts1.cancel_order(appOrderID=OrderID,orderUniqueIdentifier='123abc',clientID=self.client_code )	
			
		except Exception as e:
			print(f"Got exception in cancel order as: {e}")	
			self.logger.exception(f'Got exception in cancel_order as {e}')
			traceback.print_exc()


	def send_telegram_alert(self,message, receiver_chat_id, bot_token):
		"""
		Sends a message via Telegram bot to a specific chat ID.
		
		Parameters:
			message (str): The message to be sent.
			receiver_chat_id (str): The chat ID of the receiver.
			bot_token (str): The token of the Telegram bot.
		"""
		try:
			encoded_message = urllib.parse.quote(message)
			send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={receiver_chat_id}&text={encoded_message}'
			response = requests.get(send_text)
			response.raise_for_status()
			if int(response.status_code) ==200:
				print(f"Message sent successfully")
			else:
				raise Exception(response.json())
		except requests.exceptions.RequestException as e:
			print(f"Got exception in send_telegram_alert as: {e}")	
			self.logger.exception(f'Got exception in send_telegram_alert as {e}')
			print(f"Failed to send message: {e}")
	

	def get_account_balance(self):
		try:
			response = self.xts1.get_balance(clientID=self.client_code)
			balance = int(response['result']['BalanceList'][0]['limitObject']['RMSSubLimits']['cashAvailable'])
			return balance
		except Exception as e:
			self.logger.exception(f"Error at Gettting get_account_balance as {e}")
			print(f"Error at Gettting get_account_balance as {e}")
			return 0
