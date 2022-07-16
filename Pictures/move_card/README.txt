The individual missionary pictures are supposed to be downloaded from IMOS and stored in here, 
and should be stored in the format of having both first name and last name. 
The code that pulls them out so you know what your companion looks like, looks like this:



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



The "Tyler A Chartrand" is an example
