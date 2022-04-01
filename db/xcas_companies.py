from flask import g
import requests
from bs4 import BeautifulSoup
import pandas as pd

class Get_XCAS_Companies():

    xcas_url = 'https://www.casablanca-bourse.com/Bourseweb/Liste-Societe.aspx?IdLink=20&Cat=7'
    html_text = requests.get(xcas_url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    #print(soup.title.text)

    #for link in soup.find_all("a"):
    #    print("Link Text :  {}".format(link.text).replace(' ', ''))
    #    print("Link URL  : {}".format(link.get("href")))

    # Defining the table variables
    companies_table = soup.find_all("table", id="arial11bleu")[1]
    headings = companies_table.find_all("td", class_="arial11blanc")
    companies_rows = companies_table.find_all("tr", class_="arial11gris")
    companies_data = companies_table.find_all("span")
    
    #print(headings)
    #print(companies_data)

    # Get all the column names from class: arial11blanc
    columns = []
    for heading in headings:
        columns.append(heading.text.replace('\n', ' ').strip())
    columns = list(filter(None, columns))
    #print(columns)

    # Get all the rows from class: arial11gris
    rows = []
    for row in companies_rows:
        rows.append(row.text.replace('\n', ' ').strip())
    rows = list(filter(None, rows))
    #print(rows)

    # Get all the data from tag: span
    fields = []
    for field in companies_data:
        fields.append(field.text.replace('\n', ' ').strip())
    rows = list(filter(None, rows))
    #print(fields)

    # Create a data dictionnary
    data = {}
    for field in fields:
        # Zip the row with its columns  
        zipped = list(zip(columns,field))
        #print(zipped)

        # Create a data list of tag (span) from rows of class: arial11gris 
        table_data = []
        for variable in companies_rows:
            t_row = {}
            # find all the spans in arial11gris and zip it with columns
            for td, th in zip(companies_data, columns): 
                t_row[th] = td.text.replace('\n', '').strip()
                table_data.append(t_row)
                    
    data[heading] = table_data
    #print(data)

    # Create a dataframe from the table data
    #df = pd.DataFrame(table_data)
    #print(df.info())


def main():
    Get_XCAS_Companies()
    
if __name__ == "__main__":
    main()

