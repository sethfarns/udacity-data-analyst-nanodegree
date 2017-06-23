import csv, sqlite3, pprint
from io import TextIOWrapper

# method converts strings that look like byte strings into regular strings
# also fixes encoding so Portuguese accent characters show correctly
def bytes_to_string(item):
    # credit to http://stackoverflow.com/questions/26865276/converting-utf-8-encoded-string-to-just-plain-text-in-python-3 for
    # encoding solution
    return item.replace("b'","").replace("'","").replace("\n","").encode('latin1').decode('unicode_escape').encode('latin1').decode('utf-8')

# grabs CSV data, formats it, and inserts it into database
def csv_to_db(filename, cur):
    to_db = []
    row_headers = []
    counter = 0
    with open(filename + '.csv') as csv_file:
        for row in csv.reader(csv_file):
            if counter == 0:
                row_headers = [bytes_to_string(i) for i in row]
            elif row != []:
                to_db.append([bytes_to_string(i) for i in row])
            counter += 1
    table_columns = ",".join(row_headers)
    question_marks = ",".join(len(row_headers) * ["?"])
    cur.executemany("INSERT INTO {0} ({1}) VALUES ({2});".format(filename, table_columns, question_marks), to_db)

# imports all specified CSV files into the database
def import_csv_files(filenames, cur, preview=False):
    for filename in filenames:
        csv_to_db(filename, cur)
        if preview == True:
            cur.execute("SELECT * FROM {0} LIMIT 5".format(filename))
            print("Sample of records from {0}".format(filename))
            pprint.pprint([dict(i) for i in cur.fetchall()])
            print("\n")