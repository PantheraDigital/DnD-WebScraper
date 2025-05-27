import requests
from bs4 import BeautifulSoup
import re 
import csv



# (source/name)  H1 and/or H2
# (descrition )  p
#                (optional) tabl, ul, more p
# (content    )  ul...


# Description:
#  may hold multiple p tags, tables, or ul
#  will end with a p tag or table
#
#  if current tag is p
#    if next tag is table
#       when tag is no longer table
#         switch to content
#    if next tag is ul 
#      if next next tag is ul or if there is no next next tag
#        switch to content


# Content:
#  all tags are formatted before adding to class
#
#  if tag not table
#    name = tag.li.strong.text
#    if name is known trait (age, speed, ...)
#      add to matching class variable
#    else 
#      handle as feature
#  else if table
#    if header in table and header contains a previous feature name
#      add to matching feature
#    else
#      add to previous feature


# formatter functions take in a single tag and output the 
#  inline string form
#
# ListFormatter(ul tag)
#  handles nested lists
#  uses LinkFormatter() 
#
# TableFormatter(table tag, name='')
#  accepts optional table name arg (use for preceding p tags)
#  uses LinkFormatter() 
#
# LinkFormatter(a tag)



class RaceData:
    def __init__(self):
        self.source = ''
        self.race = ''
        self.sub_race = ''
        self.description = ''
        self.ability_score = ''
        self.age = ''
        self.alignment = ''
        self.languages = ''
        self.size = ''
        self.speed  = ''
        self.features  = {}

    def __str__(self):
        str = ''
        str += ('{: <16}'.format('source : ') + self.source + '\n')
        str += ('{: <16}'.format('race : ') + self.race + '\n')
        str += ('{: <16}'.format('sub-race : ') + self.sub_race + '\n')
        str += ('{: <16}'.format('description : ') + self.description + '\n')
        str += ('{: <16}'.format('ability-score : ') + self.ability_score + '\n')
        str += ('{: <16}'.format('age : ') + self.age + '\n')
        str += ('{: <16}'.format('alignment : ') + self.alignment + '\n')
        str += ('{: <16}'.format('languages : ') + self.languages + '\n')
        str += ('{: <16}'.format('size : ') + self.size + '\n')
        str += ('{: <16}'.format('speed : ') + self.speed + '\n')
        str += ('{: <16}'.format('features : ') + '\n'.join(self.features.values()))
        return str
    
    def toCSVformat(self):
        return {
            'Variant':self.sub_race,
            'Description':self.description,
            'Source':self.source,
            'Ability Score Increase':self.ability_score,
            'Age':self.age,
            'Alignment':self.alignment,
            'Size':self.size,
            'Speed':self.speed,
            'Languages':self.languages,
            'Features':'\n'.join(self.features.values())
        }


def scrape_webpage(url, element, identifier, css_class):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup.find(element, id=identifier, class_=css_class)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        

def extractRaceData(soup, raceName):
    data = RaceData()
    races = []

    data_source = ""
    sub_race = ""

    elmnt = soup.h1
    source_override = False

    if not elmnt:
        data_source = soup.contents[1].text[8:] # skip 'Source: '
        source_override = True
        elmnt = soup.contents[3]
        print(soup.contents[1].text[8:])


    while elmnt and ((elmnt.name == 'h1' or elmnt.name == 'h2') or source_override):
        if source_override:
            source_override = False

        # source/name
        if elmnt.name == "h1":
            data_source = elmnt.text
            sub_race = ''
            elmnt = elmnt.next_sibling.next_sibling
            
        if elmnt.name == "h2":
            sub_race = elmnt.text
            elmnt = elmnt.next_sibling.next_sibling

        print(f"\n\n{data_source} | {sub_race}")
        data.race = raceName
        data.source = data_source
        data.sub_race = sub_race


        # description
        while elmnt.name == 'p':
            # handle description text
            data.description += elmnt.text
            elmnt = elmnt.next_sibling.next_sibling

            if elmnt.name == 'ul':
                if elmnt.next_sibling.next_sibling.name == 'p':
                    # handle ul in desc
                    data.description += " " + ListFormatter(elmnt) + " "
                    elmnt = elmnt.next_sibling.next_sibling

            while elmnt.name == 'table':
                # handle tables
                data.description += " " + TableFormatter(elmnt) + " "
                elmnt = elmnt.next_sibling.next_sibling
            

        # content
        while elmnt and elmnt.name != 'h1' and elmnt.name != 'h2':
            #handle features
            if elmnt.name == 'ul':
                featureName = elmnt.li.strong.text.rstrip('.')
                print(featureName)

                
                while elmnt.ul: # has list
                    elmnt.ul.replace_with(ListFormatter(elmnt.ul))

                while elmnt.a: # no list / basic feature
                    elmnt.a.replace_with(LinkFormatter(elmnt.a))


                featureData = ' '.join(elmnt.get_text(" xx ",strip=True).split(" xx ")[1:])
                match featureName:
                    case "Ability Score Increase":
                        data.ability_score = featureData
                    case "Age":
                        data.age = featureData
                    case "Alignment":
                        data.alignment = featureData
                    case "Size":
                        data.size = featureData
                    case "Speed":
                        data.speed = featureData
                    case "Languages":
                        data.languages = featureData
                    case _:
                        data.features[featureName] = f"{featureName} | {featureData};\n"
                    

            if elmnt.name == 'table':
                title = '' 
                if elmnt.previous_sibling.previous_sibling.name == 'p':
                    title = elmnt.previous_sibling.previous_sibling.text.strip()

                tableAsStr = TableFormatter(elmnt, title)
                #print(tableAsStr)

                if tableAsStr != None:
                    addToPrevFeat = True
                    if " ||| " in tableAsStr and title == '': # title was in table
                        tableTitle = tableAsStr[:tableAsStr.index(" ||| ")]
                        for key in data.features.keys():
                            if key[:-1] in tableTitle:
                                addToPrevFeat = False
                                data.features[key] = data.features[key].rstrip(';\n') + " " + tableAsStr + ';\n'
                    
                    if addToPrevFeat:
                        data.features[featureName] = data.features[featureName].rstrip(';\n') + " " + tableAsStr + ';\n'
                

                
            elmnt = elmnt.next_sibling
            if elmnt.text == '\n':
                elmnt = elmnt.next_sibling


        #print(data)
        races.append(data)
        data = RaceData()

    return races   



def TableFormatter(tableTag, title = ""):
    if tableTag.name != 'table':
        print(f"table fail {tableTag}")
        return

    while tableTag.a: # no list / basic feature
        tableTag.a.replace_with(LinkFormatter(tableTag.a))

    tableAsStr = '['
    if title != '':
        tableAsStr += title + " ||| "

    for index, child in enumerate(tableTag.contents):
        if child.text == '\n':
            continue

        if child.th:
            if tableTag.contents[index + 2].th:
                if tableAsStr == '[': # table title
                    tableAsStr += child.text.strip() + " ||| "
            else: # column names
                tableAsStr += child.get_text(" || ",strip=True) + ";;\n"
        
        if child.td: # row data
            for index, td in enumerate(child.find_all("td")):
                if index > 0:
                    tableAsStr += " || "

                if td.strong:
                    tableAsStr += td.strong.extract().text.strip() + " | "
                    tableAsStr += td.text.strip() 
                else:
                    tableAsStr += td.text.strip() 

            tableAsStr += ";\n"

    return tableAsStr[:-2] + ']'


def ListFormatter(listTag, count = 0):
    if listTag.name != 'ul':
        return
    
    while listTag.a: # no list / basic feature
        listTag.a.replace_with(LinkFormatter(listTag.a))

    listAsStr = "["
    for child in listTag.children:
        if child.text == '\n':
            continue
        if child.name == 'ul':
            listAsStr += ListFormatter(child, count + 1) + "; "
        elif child.name == 'li':
            while child.ul:
                child.ul.replace_with(ListFormatter(child.ul, count + 1))

            if child.strong:
                liTextArray = child.get_text(" | ",strip=True).split(" | ")
                listAsStr += f"{child.strong.text.strip().rstrip('.')} | {' '.join(liTextArray[1:])};\n"
            else:
                listAsStr += child.text.strip() + ";\n"
        
    return listAsStr[:-2] + ']'


def LinkFormatter(linkTag):
    if linkTag.name != 'a':
        return
    
    linkAsMarkdown = re.search('href="http://dnd5e.wikidot.com/(.*?)"', str(linkTag))
    if linkAsMarkdown:
        linkAsMarkdown = '{' + linkAsMarkdown.groups()[0] + '}'
    else:
        linkAsMarkdown = re.search('href="/(.*?)"', str(linkTag))
        if linkAsMarkdown:
            linkAsMarkdown = '{' + linkAsMarkdown.groups()[0] + '}'
        else:
            linkAsMarkdown = f'[{linkTag.text}]({re.search('href="(.*?)"', str(linkTag)).groups()[0]})'
            print(f"markdown used {linkAsMarkdown}")
    
    return linkAsMarkdown



def main():

    url = "https://dnd5e.wikidot.com/lineage:verdan"
    target_element = "div page-content" # (html element) (id) (class)

    targets = target_element.split()
    element, identifier, css_class = [None,None,None]

    if len(targets) > 0:
        element = targets[0]
    if len(targets) > 1:
        identifier = targets[1]
    if len(targets) > 2:
        css_class = targets[2]


    raceName = re.search('https://dnd5e.wikidot.com/lineage:(.*)', str(url)).groups()[0]
    print(raceName)
    raceData = extractRaceData(scrape_webpage(url, element, identifier, css_class), raceName)
    
    #for data in raceData:
    #    print(str(raceData))
    
    for index, data in enumerate(raceData):
        raceData[index] = data.toCSVformat()

    with open(f'{raceName}.csv', 'w', newline='') as csvfile:
        columns = [
            'Variant',
            'Description',
            'Source',
            'Ability Score Increase',
            'Age',
            'Alignment',
            'Size',
            'Speed',
            'Languages',
            'Features']
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(raceData)
        print(f'{raceName}.csv DONE')
    

if __name__ == "__main__":
    main()
