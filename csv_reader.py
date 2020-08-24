import csv
import Download_File

Download_File.download()

def get_request():
    request_list = []
    with open("Requests.csv", 'r') as csvfile: #open csv file
        csvreader = csv.reader(csvfile)
        next(csvreader) #ignore heading
        for row in csvreader:
            modified_row = row
            del(modified_row[0]) #remove name
            request_list.append(modified_row)
    for i in range(0, len(request_list)):
        for x in range(0, len(request_list[i])):
            request_list[i][x] = int(request_list[i][x])
    return request_list

def get_qualifs():
    qualif_list = []
    with open ("Teacher Qualifications.csv", 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            modified_row = row
            del(modified_row[0])
            qualif_list.append(modified_row)
    for i in range(0, len(qualif_list)):
        for x in range(0, len(qualif_list[i])):
            qualif_list[i][x] = int(qualif_list[i][x])
    return qualif_list

