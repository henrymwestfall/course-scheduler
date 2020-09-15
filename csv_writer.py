import csv

def write_file(filename, raw_results):
    ordered_results = []
    for i in raw_results:
        ordered_results.append([i["Name"], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]])
    header = ["Student Name", "Period 1 Course Code", "Period 2 Course Code", "Period 3 Course Code", "Period 4 Course Code", "Period 5 Course Code", "Period 6 Course Code", "Period 7 Course Code", "Period 8 Course Code"]

    with open(filename, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header) 
        csvwriter.writerows(ordered_results) 
