import csv
import Download_File

def get_download():
    Download_File.download()
    
def csv_line_parse(line):
    return line.split(",")

def get_request(zf):
    request_list = []
    name_list = []
    with zf.open("temporary_files/requests.csv", "r") as f: #open csv file
        for bytes_line in f.readlines()[1:]: # iterate over all non-header lines
            line = csv_line_parse(bytes_line.decode())
            modified_row = line
            name_list.append(modified_row[0])
            del modified_row[0] # remove name
            request_list.append(modified_row)

        # csvreader = csv.reader(csvfile)
        # next(csvreader) #ignore heading
        # for row in csvreader:
        #     modified_row = row
        #     name_list.append(modified_row[0])
        #     del(modified_row[0]) #remove name
        #     request_list.append(modified_row)
    for i in range(0, len(request_list)):
        for x in range(0, len(request_list[i])):
            request_list[i][x] = int(request_list[i][x])
    return request_list, name_list

def get_qualifs(zf):
    qualif_list = []
    name_list = []
    with zf.open("temporary_files/qualifications.csv", "r") as f:
        for bytes_line in f.readlines()[1:]: # iterate over non-header lines
            line = csv_line_parse(bytes_line.decode())
            modified_row = line
            name_list.append(modified_row[0])
            del modified_row[0] # remove name
            qualif_list.append(modified_row)

        # csvreader = csv.reader(csvfile)
        # next(csvreader)
        # for row in csvreader:
        #     modified_row = row
        #     del(modified_row[0])
        #     qualif_list.append(modified_row)

    for i in range(0, len(qualif_list)):
        for x in range(0, len(qualif_list[i])):
            qualif_list[i][x] = int(qualif_list[i][x])
    return qualif_list, name_list

