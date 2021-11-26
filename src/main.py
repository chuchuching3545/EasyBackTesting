import csv
import matplotlib.pyplot as plt


class True_Data:
	file_name = '../MTX_from2014.csv'
	

	def __init__(self):
		with open(self.file_name, newline='') as fp:
			yesterday = None
			reader = csv.reader(fp)
			self.date_info_map = {}
			for row in reader:
				self.date_info_map[row[0]] = [int(row[i]) for i in range(1, 5)] + [yesterday]
				yesterday = row[0]
		

	def get_open(self, date):
		return self.date_info_map[date][0]

	def get_high(self, date):
		return self.date_info_map[date][1]

	def get_low(self, date):
		return self.date_info_map[date][2]

	def get_close(self, date):
		return self.date_info_map[date][3]

	def get_yesterday(self, date):
		
		return self.date_info_map[date][4]

def calculate_mdd(cum):
	cummax = [max(cum[:i+1]) for i in range(len(cum))]
	cumdiff = [cummax[i] - cum[i] for i in range(len(cum))]
	return max(cumdiff)

#calculate profit/mdd with different schemes
def calculate(data, time, turn_threashold, upper_offset, lower_offset, persent = 0.3):
	table = {}   		# map: date -> profit (skip)
	complete_table = {} # map: date -> profit (complete)

	for row in data:
		if row[1][:5] == "08:46":
			day_data = []
		modified_row = [row[0], row[1], int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6])]
		day_data.append(modified_row)
		if row[1][:5] == "13:45":
			profit = calculate_in_day(day_data, time, turn_threashold, upper_offset, lower_offset, persent)
			if profit != 'bad case' and profit != 'filted out':
				table[row[0]] = profit
				complete_table[row[0]] = profit
			else:
				complete_table[row[0]] = 0
	
	# table -> two dim array			
	lst = [[key, value] for key, value in table.items()]
	lst.sort(key = lambda x : x[0])	

	# complete_table -> two dim array
	complete_lst = [[key, value] for key, value in complete_table.items()]
	complete_lst.sort(key = lambda x : x[0])	

	
	#write_file(complete_lst, f'profit_{time}_{turn_threashold}_{upper_offset}_{lower_offset}.csv')
	return risk_reward_ratio(lst), avg_return(lst), win_rate(lst), lose_rate(lst), return_rate(lst)



def write_file(rows, file_name):
	with open(file_name, 'w', newline = '') as fp:
		writer = csv.writer(fp)
		writer.writerows(rows)
	

# rows : [[date, profit],
#		  [date, profit]]
def win_rate(rows):
	return round(len([rows[i][1] for i in range(len(rows)) if rows[i][1] > 0]) * 100 / len(rows), 4)

def lose_rate(rows):
	return round(len([rows[i][1] for i in range(len(rows)) if rows[i][1] <= 0. ]) * 100 / len(rows), 4)

def risk_reward_ratio(rows):
	profits = [rows[i][1] for i in range(len(rows))]	#profit of every day
	accu = [sum(profits[:i + 1]) for i in range(len(profits))]
	return round(accu[-1] / calculate_mdd(accu), 4)

def avg_return(rows):
	profits = [rows[i][1] for i in range(len(rows))]	#profit of every day
	return round(sum(profits) / len(profits), 4)

def plot_accu(rows):
	profits = [rows[i][1] for i in range(len(rows))]	#profit of every day
	accu = [sum(profits[:i + 1]) for i in range(len(profits))]
	plt.plot([lst[i][0] for i in range(len(lst))], accu)
	plt.show()


def return_rate(rows):
	rates = [rows[i][1] / true_data.get_close(true_data.get_yesterday(rows[i][0])) for i in range(len(rows))]
	return round(sum(rates) * 100, 4)

# data_yesterday = [["2020/08/20","08:46:00","21255","21258","21240","21245","2119"], 
#		  			["2020/08/20","08:47:00","21245","21250","21241","21247","866"],
#		 			,[...],
#		  			["2020/08/20","13:45:00","20845","20870","20843","20865","2348"]]
#
# data_today = [["2020/08/21","08:46:00","21255","21258","21240","21245","2119"],
#				["2020/08/21","08:47:00","21245","21250","21241","21247","866"],
#					,[...],
#		  		["2020/08/21","13:45:00","20845","20870","20843","20865","2348"]]


def filter_jump_big(data_yesterday, data_today):
	highest_in_minutes = [data_yesterday[i][3] for i in range(len(data_yesterday))]
	lowest_in_minutes = [data_yesterday[i][4] for i in range(len(data_yesterday))]
	highest_between_minutes = max(highest_in_minutes)
	lowest_between_minutes = min(lowest_in_minutes)
	open_price = data_today[0][2]
	if open_price > highest_between_minutes or open_price < lowest_between_minutes:
		return True
	else:
		return False

def filter_jump_persent(data_today, persent):
	yesterday = true_data.get_yesterday(data_today[0][0])
	jump_persent = (true_data.get_open(data_today[0][0]) - true_data.get_close(yesterday)) / true_data.get_close(yesterday)
	if (jump_persent > persent or jump_persent < -persent):
		return True
	else:
		return False





# data = [["2020/08/20","08:46:00","21255","21258","21240","21245","2119"], 
#		  ["2020/08/20","08:47:00","21245","21250","21241","21247","866"],
#		 	,[...],
#		  ["2020/08/20","13:45:00","20845","20870","20843","20865","2348"]]	

# time : define upper and lower
# turn : current turn
# turn_threashold : if turn excesses turn_threashold, then calculate profit
# upper_offset
# lower_offset

BUY = 0
SELL = 1
NONE = 2
none_cnt = 0
data_yesterday = [["2016/01/04","08:46:00",13586,13585,13584,13596,1959]]
def calculate_in_day(data, time, turn_threashold, upper_offset, lower_offset, persent = 0.3):
	global data_yesterday, none_cnt
	state = NONE
	first_data = [data[i] for i in range(time)]
	upper, lower = get_upper_lower_bound(first_data)
	upper += upper_offset
	lower -= lower_offset
	profit = 0
	turn = 0
	buy_price = 0
	sell_price = 0

	
#	if data[0][2] <= pre_high and data[0][2] >= pre_low:
#		pre_high = max(data[0][2], data[-1][5]) 
#		pre_low = min(data[0][2], data[-1][5]) 
#		return 0
#	else:
#		pre_high = max(data[0][2], data[-1][5]) 
#		pre_low = min(data[0][2], data[-1][5]) 
	
#	if not filter_jump_persent(data, persent):
#		return 'filted out'
	
	if filter_jump_big(data_yesterday, data):
		data_yesterday = data 
	else:
		data_yesterday = data 
		return 'filted out'

	for i in range(time, len(data), 1):
		if upper <= lower: 
			return 'bad case'
		if state == NONE:
			if data[i][3] > upper and data[i][4] < lower:
				state = NONE
				none_cnt += 1
				if none_cnt >= 1:
					profit -= upper - (lower - 1)
					break
			elif data[i][3] > upper:
				state = BUY
				profit -= 1
				buy_price = max(upper + 1, data[i][2])
			elif data[i][4] < lower:
				state = SELL
				profit -= 1
				sell_price = min(lower - 1, data[i][2])
		if state == BUY:
			if data[i][4] < lower:
				turn += 1
				profit -= buy_price - (lower - 1) 
				if turn > turn_threashold:
					break
				state = SELL
				profit -= 1
				sell_price = lower - 1
		if state == SELL:
			if data[i][3] > upper:
				turn += 1
				profit -= (upper + 1) - sell_price
				if turn > turn_threashold:
					break
				state = BUY
				profit -= 1
				buy_price = upper + 1
	else:
		if state == BUY:
			profit += data[-1][5] - buy_price 
		elif state == SELL:
			profit += sell_price - data[-1][5] 

	return profit







# first_data in the range from first minute to time-th minute

def get_upper_lower_bound(first_data):
	upper = -1
	lower = 100000
	for i in range(len(first_data)):
		if first_data[i][3] > upper:
			upper = first_data[i][3]
		if first_data[i][4] < lower:
			lower = first_data[i][4]

	return upper, lower


true_data = True_Data()

with open("../day_1_2016.csv", newline='') as fp:
	reader = csv.reader(fp)
	data = [row for row in reader]
	max_ratio = -10000
	max_scheme = None

##### Following is brute testing to determine which set of hyperparameters is best.
#	with open("Result_big.csv", 'w', newline='') as write_file:
#		writer = csv.writer(write_file)
#
#		for time in range(1, 10, 1):
#			for turn_threashold in range(1, 4):
#				for upper_offset in range(-5, 5):
#					for lower_offset in range(-5, 5):
#						data_yesterday = [["2016/01/04","08:46:00",13586,13585,13584,13596,1959]]
#						ratio, avg_profit, win, lose, return_accu = calculate(data, time, turn_threashold, upper_offset, lower_offset)
#						content = [f'{time}_{turn_threashold}_{upper_offset}_{lower_offset}', f'{ratio}', f'{avg_profit}', f'{win}%', f'{lose}%', f'{return_accu}%']
#						writer.writerow(content)
#						print(content)
#						if ratio > max_ratio:
#							max_ratio = ratio
#							max_scheme = [time, turn_threashold, upper_offset, lower_offset]
#		writer.writerow(['max_ratio', max_ratio])
#		writer.writerow(['max_scheme', max_scheme])


##### Following is usage	
	print(calculate(data, 3, 1, -4, -3)) 
















