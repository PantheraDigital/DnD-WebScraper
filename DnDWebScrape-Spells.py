import requests
from bs4 import BeautifulSoup
import pandas as pd

"""
    Web Scraper by: Panthera (https://github.com/PantheraDigital/)

    Creates a csv file loaded with D&D spells.
"""

def scrape_table(table_num, url, table_class):
    try:
        data = []
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tab = soup.find('div', id=f"wiki-tab-0-{table_num}")
            tables = tab.find_all('table', class_=table_class) if table_num != -1 else soup.find_all('table', class_=table_class)

            count = 0
            for table in tables:
                rows = table.find_all('tr')
                columns = ""
                
                for row in rows[1:]:
                    cols = row.find_all('td')
                    link = cols[0].find('a')['href']  # Get the link for each spell
                    link = url[:-7] + link
                    spell_data = get_spell_data(link)
                    #print(spell_data)

                    if columns == "": # Create columns on first loop from spell data keys
                        columns = [key.title() for key, data in spell_data.items()]
                        
                    cols = [data for key, data in spell_data.items()]
                    data.append(cols)

                if table_num == -1:
                    print("Table " + str(count) + " finished")
                count += 1
        else:
            print(f"Failed to scrape {url} with status code {response.status_code}")
            data = None
        
        return data, columns
    
    except Exception as e:
        print(f"Error occurred while scraping table data: {e}")
        return [],''


def get_spell_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', id='page-content')
            target_elements = div.find_all(recursive=False)
            additional_data = {"name":"", "cast time":"", "range":"", "components":"", "duration":"", "description":"", "level":"", "school":"", "spell books":"", "up casting":"", "sources":"", "extra":""}

            additional_data["name"] = soup.find('div', class_='page-header').text.strip()
            additional_data["sources"] = target_elements[1].text[8:].strip()
            
            if target_elements[2].text.endswith("cantrip"):
                additional_data["level"] = "Cantrip"
                additional_data["school"] = target_elements[2].text[:-7].strip().capitalize()
            else:
                split = target_elements[2].text.split()
                additional_data["level"] = split[0].strip()
                additional_data["school"] = split[1].strip().capitalize()


            broken_extra_block = False
            if "Duration:" in target_elements[3].text:
                text = target_elements[3].text.replace('\n', ' ')
                castIdx = text.index("Casting Time:")
                rangeIdx = text.index("Range:")
                compIdx = text.index("Components:")
                durIdx = text.index("Duration:")
                
                additional_data["cast time"] = text[len("Casting Time:") + castIdx + 1: rangeIdx].strip()
                additional_data["range"] = text[len("Range:") + rangeIdx + 1: compIdx].strip()
                additional_data["components"] = text[len("Components:") + compIdx + 1: durIdx].strip()
                additional_data["duration"] = text[len("Duration:") + durIdx + 1:].strip()
            else:
                additional_data["cast time"] = target_elements[3].text.split(':')[1].strip()
                additional_data["range"] = target_elements[4].text.split(':')[1].strip()
                additional_data["components"] = target_elements[5].text.split(':')[1].strip()
                additional_data["duration"] = target_elements[6].text.split(':')[1].strip()
                broken_extra_block = True


            description_start = 4 if broken_extra_block == False else 7
            upcast_index = -1
            classes_index = -1
            for index, elmnt in enumerate(target_elements[description_start:]):
                if elmnt.text.startswith("At Higher Levels"):
                    upcast_index = index + description_start
                elif elmnt.text.startswith("Spell Lists"):
                    classes_index = index + description_start
                    break
                else:
                    additional_data["description"] += elmnt.text + " "
                    
            additional_data["description"] = additional_data["description"].strip()


            if upcast_index > -1:
                additional_data["up casting"] = target_elements[upcast_index].text[17:].strip()

            # classes index should always become non-negative
            if classes_index > -1:
                additional_data["spell books"] = target_elements[classes_index].text[13:].strip()
                for elmnt in target_elements[classes_index + 1: -1]:
                    additional_data["extra"] += elmnt.text + " "
                additional_data["extra"] = additional_data["extra"].strip()
            else:
                print(f"Error gathering spell:{additional_data['name']}. Invalid Spell Book Index.")
            
            return additional_data
        else:
            print(f"Failed to scrape additional data from {url} with status code {response.status_code}")
            return ''
    except Exception as e:
        print(f"Error occurred while scraping additional data: {e}")
        return ''


def main():
    url = "http://dnd5e.wikidot.com/spells"
    table_class = "wiki-content-table"
    table_num = 0

    while table_num != 'q':
        valid = True
        while True:
            table_num = input("input spell level (0 = cantrip)(-1 for all tables)(9 is max)(q to end): ")
            try:
                table_num = int(table_num)
                if table_num > 9 or table_num < -1:
                    print("number out of range")
                else:
                    if table_num == -1:
                        print("Gathering all spells...")
                    break
            except ValueError:
                if table_num == "q":
                    valid = False
                    break
                else:
                    print("invalid input")

        if valid:
            data, columns = scrape_table(table_num, url, table_class)

            if data:
                # Convert the data to a pandas DataFrame and print a formatted table
                df = pd.DataFrame(data, columns=columns)
                print(df.to_string(index=False,max_rows=10))

                with open("spellList.txt", "w", encoding="utf-8") as f:
                    f.write(df.to_csv())
                    f.close()
                    print("spellList.txt saved")
            else:
                print("Failed to scrape the table.")


if __name__ == "__main__":
    main()
