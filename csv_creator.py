# importing the csv module 
import csv 

# field names 
fields = ['Name', 'ID', 'Grade']

for i in range(1, 9):
	exec("fields.append('Period %s')" % i)

# data rows of csv file 
# rows = [ ['Nikhil', 'COE', '2', '9.0'], 
# 		['Sanchit', 'COE', '2', '9.1'], 
# 		['Aditya', 'IT', '2', '9.3'], 
# 		['Sagar', 'SE', '1', '9.5'], 
# 		['Prateek', 'MCE', '3', '7.8'], 
# 		['Sahil', 'EP', '2', '9.1']] 

rows = [] #Should contain additional lists within

filename = "Courses.csv" #File can also be .xlsx

# writing to csv file 
with open(filename, 'w') as csvfile: 
	# creating a csv writer object 
	csvwriter = csv.writer(csvfile) 
	
	# writing the fields 
	csvwriter.writerow(fields) 
	
	# writing the data rows 
	csvwriter.writerows(rows)

csvfile.close()
