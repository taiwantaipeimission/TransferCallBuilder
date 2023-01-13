import csv
import os
import base64
import json
import datetime
from datetime import date
from datetime import datetime
import pickle
from googletrans import Translator as pikachu
import pprint
from pathlib import Path

# Folder Paths
area_pics_path = Path('Pictures/area_pictures/')
mission_pics_filePath = Path('Pictures/move_card/')
tcall_folder_destination = Path('Transfer Calls Output/{}.html')

# Settings
train_station_disp = False
missionary_data_disp = False
missionary_curr_name_disp = True

#Translator
position_translator = {
	"(ZL1)":"Zone Leader",
	"(ZL2)":"Zone Leader",
	"(STL1)":"Sister Training Leader",
	"(STL2)":"Sister Training Leader",
	"(TR)":"Trainer",
	"(DL)":"District Leader",
	"(DT)":"District Leader/Trainer",
	"(AP)":"Assistant to the President",
	"(SC)":"Senior Companion",
	"(JC)":"Junior Companion",
	"(STLT)": "Sister Training Leader/Trainer",
	"":""
}
#FUNCTIONS
def csv_to_list(file_name, type=True):
	#True means use dictionaries, false means use lists.
	try:
		csv_file = open('{}.csv'.format(file_name),'r',encoding='utf-8')
	except:
		try:
			csv_file = open('{}.txt'.format(file_name),'r',encoding='utf-8')
		except:
			print("UNABLE TO OPEN FILE")
	if type:
		read_csv = csv.DictReader(csv_file)
	else:
		read_csv = csv.reader(csv_file)
	csv_data = []
	for dataLine in read_csv:
		csv_data.append(dataLine)
	csv_file.close()
	return csv_data

def make_the_call(mish_dict,moving_instr,bike_instr,translate):
	
	#Find the trainers!
	if mish_dict["Area"] == "Home":
		pass
	else:
		mish_dict['Companion'] = " ".join(mish_dict['Companion'].split(" ")[:-1])
	if mish_dict['Companion'] == "":
		mish_dict['Companion'] = "Trainee!"
	
	#FORMAT THE HTML VALUES!
	if translate == 'yes':
		mish_call = read_html_zho
	else:
		mish_call = read_html_eng
	
	#Find the area pic!

	areaPics = os.listdir()
	compare_area = mish_dict['Area']
	normal_name = mish_dict['Area']
	mish_dict['Area'] = "".join(mish_dict['Area'].split(" ")[0].lower())
	encoded_string = ""
	
	for area_pic in areaPics:

		if mish_dict['Area'] in area_pic:

			try:

				#the_pic = open(area_pics_path / area_pic,"rb") # This was in the origional code, it works without it, but if it stops working, then put the "b" back
				the_pic = open(area_pics_path / area_pic,"r")

				encoded_string = base64.b64encode(the_pic.read())
				the_pic.close()

			except:
				
				print(str(area_pic) + " Was Not Able To Be Opened")
			
			break
		
	if encoded_string == "":
		the_pic = open(area_pics_path / 'default.jpg',"rb")
		encoded_string = base64.b64encode(the_pic.read())
		the_pic.close()
	encoded_string = str(encoded_string)
	encoded_string = encoded_string[2:]
	encoded_string = encoded_string[:-1]
	encoded_string = 'data:image/jpeg;base64,'+ encoded_string
	mish_call = mish_call.replace("$area-hero-pic$", encoded_string)
	encoded_string = ""
	#
	mish_call = mish_call.replace("$miss-name$", mish_dict['Missionary Name'])
	mish_call = mish_call.replace("$area-name$", normal_name.capitalize())
	mish_call = mish_call.replace("$zone-name$", mish_dict['Zone'])
	mish_call = mish_call.replace("$comp-name$", mish_dict['Companion'])
	
	#What does their companion look like?
	mish_pics = os.listdir(mission_pics_filePath)
	first_name = mish_dict['Companion'].split(", ")[-1].split(" ")[0]
	last_name = mish_dict['Companion'].split(",")[0]
	for pic in mish_pics:
		if first_name in pic:
			if last_name in pic:
				the_pic = open(mission_pics_filePath / pic,"rb")
				encoded_string = base64.b64encode(the_pic.read())
				the_pic.close()
				break
	if encoded_string == "":
		the_pic = open(mission_pics_filePath / 'trainee.jpg',"rb")
		encoded_string = base64.b64encode(the_pic.read())
		the_pic.close()
	encoded_string = str(encoded_string)
	encoded_string = encoded_string[2:]
	encoded_string = encoded_string[:-1]
	encoded_string = "data:image/jpeg;base64,"+str(encoded_string)
	mish_call = mish_call.replace("$comp-pic$", encoded_string)
	#
	mish_call = mish_call.replace("$position$", position_translator[mish_dict['Position']])
	
	#PHONE NUMBER CHECK
	
	#does it have letters?
	escape_num = mish_dict['Area Phone']
	alpha = 'abcdefghijklmnopqrstuvwxyz'
	is_int = True
	for letter in alpha:
		if letter in mish_dict['Area Phone']:
			is_int = False
	
	#can we parse out the cell num and leave behind the old home num?
	if mish_dict['Area Phone'] != "" and is_int:
		mish_dict['Area Phone'] = mish_dict['Area Phone'].split(",")
		mish_dict['Area Phone'] = list(filter(lambda phone_num: "09" in phone_num.split(" ")[-1][:3],mish_dict['Area Phone']))
		if mish_dict['Area Phone']:
			mish_dict['Area Phone'] = mish_dict['Area Phone'][0]
		else:
			mish_dict['Area Phone'] = escape_num
	else:
		pass
	
	#Moving Instructions
	if moving_instr == "" or moving_instr == None:
		if translate == 'yes':
			moving_instr = "你不會搬家！謝謝你的服務。加油！"
		else:
			moving_instr = "You will be staying in "+mish_dict['Area'].capitalize()+" this transfer. Thank you for your service, continue to work hard and effective!"
	mish_call = mish_call.replace("$moving-instr$", moving_instr)
	
	#Bike shipping instructions
	bike_instructions = "Your bike will not be moved."
	meet_ups = csv_to_list('meetingplace')
	
	#what station do they go to?
	if compare_area == "Home":
		print("GOING HOME!")
		bike_instructions = "Get a new bike!"
	else:
		compare_area = compare_area.split(" ")
		compare_area[0] = compare_area[0].upper()
		compare_area = " ".join(compare_area)

		if "TAOYUAN" in compare_area:
			compare_area = compare_area.replace("TAOYUAN","TAO")

		# if 'FENGLIN' in compare_area:
		# 	compare_area = 'FENGLIN E'

		#what station do they leave from?
		mish_dict['Area Prior To Change'] = mish_dict['Area Prior To Change'].split(" ")
		mish_dict['Area Prior To Change'][0] = mish_dict['Area Prior To Change'][0].upper()
		mish_dict['Area Prior To Change'] = " ".join(mish_dict['Area Prior To Change'])
		if "TAOYUAN" in mish_dict['Area Prior To Change']:
			mish_dict['Area Prior To Change'] = mish_dict['Area Prior To Change'].replace("TAOYUAN","TAO")
		#
		if "in" in bike_instr or "out" in bike_instr or "mrt" in bike_instr or "train" in bike_instr:
			
			try:
				ending_station = list(filter(lambda station:station['Area'] == compare_area, meet_ups))[0]['\ufeffMeeting Place']
			except:
				raise IndexError("'" + compare_area + "' Doesn't Exist In 'meetingplace.txt'. Please Add Or Adjust Accordingly")

			# This Output Is Toggleable By Settings At The Top
			if train_station_disp: print("ENDING_STATION: "+str(ending_station))
			
			try:
				starting_station = list(filter(lambda station:station['Area'] == mish_dict['Area Prior To Change'], meet_ups))[0]['\ufeffMeeting Place']
			except:
				raise IndexError("'" + mish_dict['Area Prior To Change'] + """' Doesn't Exist In 'meetingplace.txt'. Please Add Or Adjust Accordingly""")
			
			# This Output Is Toggleable By Settings At The Top
			if train_station_disp: print("STARTING_STATION: "+str(starting_station))
			
			if "in" == bike_instr:
				bike_instructions = "On Wednesday take your bike to the "+starting_station+" and ship it to the Wanhua Train Station.\
 Write the reciever as 台北傳道部 (Taiwan Taipei Mission Office).\
 They will give you a receipt.\
 Without this receipt the Mission Office cannot legally pick up your bike so please immediately send a picture of your receipt to the Recorder.\
 Your bike will be at the Jinhua Chapel B1 by Saturday afternoon."
			elif "out" == bike_instr:
				bike_instructions = "On Saturday morning the staying missionaries need to take your bike to the Mission Office using the MRT.\
 Please put a label with your name on it so the Mission Office can know who to send it to.\
 Ask the Recorder to send you a picture of the receipt you can use to pick it up from the "+ending_station+"."
			elif "mrt" == bike_instr:
				bike_instructions = "You are responsible for your bicycle.\
 As soon as convenient, return to your previous area and grab your bicycle.\
 Take it to your new area using the MRT.\
 The MRT allows bikes on weekdays 10-4 and Saturdays all day."
			elif "train" == bike_instr:
				bike_instructions = "On Wednesday take your bike to the "+starting_station+" and ship it to the "+ending_station+"."+\
 "Do not lose the receipt.\
 You will use it to pick up your bike from the train station when it arrives."
			elif "ship" == bike_instr:
				bike_instructions = "You will be responsible for shipping your bike, if you want to use the shipping company, communicate\
 this with the office elders and we will tell the shipping comapny, and they will contact you\
 YOU are responsible to contact the office elders and say that you want the shipping! If you have another method that you want to use to\
 move your bike, you are welcome to use it (MRT, Train, Have a Member Take It). \nIf you do NOT contact the Office Elders, we will assume you\
 are moving your bike yourself, and will not arrange shipping through the shipping company!"
			else:
				print("No bike instructions applicable for this missionary")
	if translate == 'yes':
		if "in" in bike_instr or "out" in bike_instr or "mrt" in bike_instr or "train" in bike_instr:

			ending_station = list(filter(lambda station:station['Area'] == compare_area,meet_ups))[0]['\ufeffMeeting Place']
			ending_station = pikachu(ending_station,"zh-TW","auto")

			if train_station_disp: print("ENDING_STATION: " + str(ending_station))

			starting_station = list(filter(lambda station:station['Area'] == mish_dict['Area Prior To Change'],meet_ups))[0]['\ufeffMeeting Place']
			starting_station = pikachu(starting_station,"zh-TW","auto")

			if train_station_disp: print("STARTING_STATION: " + str(starting_station))


			if "in" == bike_instr:
				bike_instructions = "星期三帶著你的腳踏車去"+starting_station+"，然後把它寄到萬華火車站。\
 受貨人的部分請寫台北傳道部，而不是辦公室長老或是任何一位傳教士的名字。\
 火車站的工作人員會給您一張收據，\
 沒有這個收據，傳道部就不能合法地領取您的腳踏車，所以請盡快將這張收據的照片傳給紀錄員。\
 星期六下午您的腳踏車就會在金華街教堂的地下一樓。"
			elif "out" == bike_instr:
				bike_instructions = "留下的傳教士在星期六早上需要帶著你的腳踏車到金華街教堂的地下一樓。\
 請在車上貼一個有你的名字的標籤，讓傳道部知道這是誰的車並要送去哪裡。\
 請紀錄員把寄腳踏車的收據照片傳給你，你去"+ending_station+"的時候可以用它來領你的腳踏車。"
			elif "mrt" == bike_instr:
				bike_instructions = "你會負責你自己的腳踏車。\
 盡快回到你原本的地區拿你的腳踏車，\
 然後帶著你的車坐捷運，回到你的地區。\
 在捷運上可以帶著腳踏車的時間是 : 平日早上10點到下午4點，以及星期六整天。"
			elif "train" == bike_instr:
				bike_instructions = "星期三把你的腳踏車帶去 "+starting_station+" ，然後把它寄到 "+ending_station+"。"+\
 "請留著這張收據，\
 當你的腳踏車到火車站的時候，你要用這張收據來領你的腳踏車。"
			elif "ship" == bike_instr:
				bike_instructions = "你會需要自己負責運輸腳踏車，你如果要用運輸公司請和辦公室長老們說 他們會通知運輸公司，\
之後運輸公司會跟你聯絡。如果要用運輸公司的話你需要和辦公室長老們說， 這是你的責任。\
如果需要你也可以用其他運輸的方式 (例如: 捷運，火車，請成員送)，不用告訴辦公室長老們。\
你如果沒有和辦公室長老們說你要用運輸公司的話辦公室長老們會假設你不用幫助也不會幫你安排運輸公司嘍！(Translated By Elder Manwell)"
			else:
				print("No bike instructions applicable for this missionary")

	if "ship" in bike_instr:
		if translate == 'yes':
			bike_instructions = "你會需要自己負責運輸腳踏車，你如果要用運輸公司請和辦公室長老們說 他們會通知運輸公司，\
之後運輸公司會跟你聯絡。如果要用運輸公司的話你需要和辦公室長老們說， 這是你的責任。\
如果需要你也可以用其他運輸的方式 (例如: 捷運，火車，請成員送)，不用告訴辦公室長老們。\
你如果沒有和辦公室長老們說你要用運輸公司的話辦公室長老們會假設你不用幫助也不會幫你安排運輸公司嘍！(Translated By Elder Manwell)"
		else: 
			bike_instructions = "You will be responsible for shipping your bike, if you want to use the shipping company, communicate\
 this with the office elders and we will tell the shipping comapny, and they will contact you\
 YOU are responsible to contact the office elders and say that you want the shipping! If you have another method that you want to use to\
 move your bike, you are welcome to use it (MRT, Train, Have a Member Take It). \nIf you do NOT contact the Office Elders, we will assume you\
 are moving your bike yourself, and will not arrange shipping through the shipping company!"

	mish_call = mish_call.replace("$bike-instr$", bike_instructions)
	#other
	mish_dict['Area Phone'] = mish_dict['Area Phone'].replace("+886","")
	mish_call = mish_call.replace("$phone-number$", mish_dict['Area Phone'])
	mish_call = mish_call.replace("$address$", mish_dict['Area Address'])
	
	#make the call!
	mish_call_html = open(str(tcall_folder_destination).format(mish_dict['Missionary Name']),'w',encoding='utf-8')
	mish_call_html.write(mish_call)
	mish_call_html.close()

#DATA
transfer_data = csv_to_list('transfer_data')

#English
html_template = open('call-template-en.html','r',encoding='utf-8')
read_html_eng = html_template.read()
html_template.close()

#Chinese
html_template = open('call-template-zh.html','r',encoding='utf-8')
read_html_zho = html_template.read()
html_template.close()

#
for missionary in transfer_data:
	
	# These Outputs Are Toggleable By Settings At The Top
	if missionary_data_disp: print()
	if missionary_data_disp or missionary_curr_name_disp: print("Currently Prossessing: " + missionary['Missionary Name'])
	if missionary_data_disp: print("THIS IS THE MISSIONARY DATAAA: "+str(missionary)+"<--------")
	if missionary_data_disp: print()

	make_the_call(missionary,missionary['Moving Instructions'],missionary['Bike Instructions'],translate=missionary['Translate'])
