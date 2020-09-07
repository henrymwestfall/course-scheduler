import csv

def write_file(raw_results):
    ordered_results = []
    for i in raw_results:
        ordered_results.append([i["Name"], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]])
    header = ["Name", "Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6", "Period 7", "Period 8"]

    filename = "Output.csv"

    with open(filename, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header) 
        csvwriter.writerows(ordered_results) 
