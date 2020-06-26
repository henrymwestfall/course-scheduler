# importing the csv module 
import csv 

# field names 
fields = ['Section ID', 'Teacher']


# data rows of csv file 
# rows = [ ['Nikhil', 'COE', '2', '9.0'], 
# 		['Sanchit', 'COE', '2', '9.1'], 
# 		['Aditya', 'IT', '2', '9.3'], 
# 		['Sagar', 'SE', '1', '9.5'], 
# 		['Prateek', 'MCE', '3', '7.8'], 
# 		['Sahil', 'EP', '2', '9.1']] 
blank_row = []
rows = ['Student', 'Student'] #Should contain additional lists within

filename = "Information.csv" #File can also be .xlsx
students = [['Pranav'], ['Jimmy'], ['Leo'], ['Henry']]
# writing to csv file 
with open(filename, 'w') as csvfile: 
	# creating a csv writer object 
	csvwriter = csv.writer(csvfile) 
	#USE WRITEROWS WHEN PARSING ARRAYS
	# writing the fields 
	csvwriter.writerow(fields) 
	csvwriter.writerow(blank_row)
	# writing the data rows 
	csvwriter.writerow(rows)
	csvwriter.writerows(students)

csvfile.close()
