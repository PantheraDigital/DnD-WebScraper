import requests
from bs4 import BeautifulSoup
import re 
import csv


class RaceData:
    def __init__(self, race = ''):
        self.source = ''
        self.race = race
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



## soup - 'page-content' web element containing DnD race info extracted from BeautifulSoup
## raceName - string
## defaultSource - string
## 
## return - RaceData array
#
# fills an array with RaceData objects created from a DnD race web page from https://dnd5e.wikidot.com
def extract_race_data(soup, raceName, defaultSource):
    data = RaceData(raceName)
    races = []

    sourcePrefix = False
    sourceFinal = False
    baseDescUsed = False
    inContent = False

    baseDesc = ""
    tableHeader = ""
    lastFeature = ""


    def AddTextToBody(body, text, preappend = False):
        if not text:
            return body
        if body:
            if preappend:
                body = text + "\n" + body
            else:
                body += "\n" + text
        else:
            body = text
        return body

    def NewEntry(keepSource = False):
        nonlocal sourcePrefix
        nonlocal sourceFinal
        nonlocal inContent
        nonlocal baseDescUsed
        nonlocal tableHeader
        nonlocal lastFeature
        nonlocal data
        nonlocal races

        if (data.description == "" and 
            (not data.ability_score and not data.features and not data.languages)):
            '''
            print("######## description not set ########")
            print(data)
            print("#####################################")
            '''
            return

        tempSource = ""

        if data.source == "":
            data.source = defaultSource

        if keepSource:
            tempSource = data.source
        else:
            sourcePrefix, sourceFinal=False,False
            lastFeature, tableHeader = "", ""

        baseDescUsed = False
        inContent  = False
        races.append(data)
        data = RaceData(raceName)
        data.source = tempSource
        print(f"Add Entry\n")

    def AddFeature(data, elmnt):
        while elmnt.ul: # has list
            elmnt.ul.replace_with(list_formatter(elmnt.ul).strip('\n'))

        while elmnt.a: # has link
            elmnt.a.replace_with(link_formatter(elmnt.a))
            
            
        featureName = elmnt.li.strong.extract().text.rstrip('.')
        featureData = "\n".join(FilterStrings(elmnt.strings))

        #print(FilterStrings(elmnt.strings))
        
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
        #print(f"\t{featureName}")

        return featureName

    def SetSource(data, source):
        if not data.source:
            data.source = source
        else: 
            if data.source not in source:
                data.source += " - " + source
            else:
                data.source = source
        print(f"Source: {data.source}")

    # strings - BeautifulSoup PageElement.strings
    # return  - array of strings
    #   filters out newlines and appends strings together that contain an intext link
    #   without this filter all links would be on their own line since PageElement.strings places links as their own element
    #     before: ["some text with ", "{link}", " in the sentence"]
    #     after:  ["some text with {link} in the sentence"]
    def FilterStrings(strings):
        result = ['']
        i = 0
        for string in strings:
            if string == '\n':
                i += 1
                continue

            if i == 0:
                result.append(string.strip('\n'))
            elif string.startswith("{") and string.endswith("}"):
                # is a spell
                if not result[len(result) - 1].endswith("]"):
                    result[len(result) - 1] += string.strip('\n')
                else:
                    result.append(string.strip('\n'))
            else:
                if not string.startswith("[") and not string.endswith("]"):
                    result[len(result) - 1] += string.strip('\n')
                else:
                    result.append(string.strip('\n'))
            i += 1
        return result

    def LookAhead(elmnt):
        if elmnt.next_sibling:
            if elmnt.next_sibling.next_sibling:
                return elmnt.next_sibling.next_sibling
        return None
        
    # loop over each element in the page checking each one 
    elmnt = soup.contents[0]
    while elmnt:
        if elmnt.text == '\n' or elmnt.find("div", {"id": "toc-action-bar"}):
            elmnt = elmnt.next_sibling
            continue
        
        match elmnt.name:
            case "p" if not inContent:
                if elmnt.text.lower().startswith("source:"): # source final
                    if sourceFinal == True: # new entry
                        NewEntry()
                        
                    sourceFinal = True
                    SetSource(data, elmnt.text[7:].strip())
                    
                else: # desc
                    # table in desc
                    nextelmnt = LookAhead(elmnt)
                    if nextelmnt and nextelmnt.name == 'table':
                        tempTable = nextelmnt
                        if tempTable.contents[1].th and not tempTable.contents[3].th:
                            tableHeader = elmnt.text
                            elmnt = elmnt.next_sibling
                            continue
                    
                    if sourceFinal == False and sourcePrefix == False: # base desc
                        baseDesc = AddTextToBody(baseDesc, elmnt.text)
                    else: # race desc
                        data.description = AddTextToBody(data.description, elmnt.text)

            case "h1" | "h2" | "h3" | "h4" | "h5" if (elmnt.text.lower().endswith("features") or elmnt.text.lower().endswith("traits")):
                #print("separator")
                elmnt = elmnt.next_sibling
                continue

            case "h1": # source prefix
                NewEntry()
                data.source = elmnt.text.strip()
                sourcePrefix = True
                print(f"Source: {data.source}")
                    
            case "h2":# subclass
                NewEntry(True)
                data.sub_race = elmnt.text
                print(f"Subclass: {elmnt.text}")

            case "h3": # desc title
                data.description = AddTextToBody(data.description, f"###{elmnt.text}")

            case "h4": # desc title
                data.description = AddTextToBody(data.description, f"####{elmnt.text}")

            case "h5":# table name
                tableHeader = elmnt.text

            case "ul": # content 
                nextelmnt = LookAhead(elmnt)
                if inContent == False and nextelmnt and nextelmnt.name == 'p':
                    data.description = AddTextToBody(data.description, list_formatter(elmnt).strip())
                else:
                    if not inContent and not baseDescUsed:
                        data.description = AddTextToBody(data.description, baseDesc, True) 
                        baseDescUsed = True

                    lastFeature = AddFeature(data, elmnt)
                    inContent = True

            case "p" if inContent and not elmnt.text.lower().startswith("see also"):
                tableHeader = elmnt.text
            
            case "table": # add table to desc or feature
                if inContent:
                    #print("\tadd table to feature")
                    tableAsStr = table_formatter(elmnt, tableHeader)
                    tableHeader = ""

                    if tableAsStr != None:
                        addToPrevFeat = True
                        if " ||| " in tableAsStr: # title was in table
                            tableTitle = tableAsStr[:tableAsStr.index(" ||| ")]
                            for key in data.features.keys():
                                if key[:-1] in tableTitle:
                                    addToPrevFeat = False
                                    data.features[key] = data.features[key].rstrip(';\n') + " " + tableAsStr.rstrip() + ';\n'
                        
                        if addToPrevFeat:
                            data.features[lastFeature] = data.features[lastFeature].rstrip(';\n') + " " + tableAsStr.rstrip() + ';\n'
                else:
                    #print("add table to desc")
                    data.description = AddTextToBody(data.description, table_formatter(elmnt, tableHeader).strip())
                    tableHeader = ""
                

            case _:
                print(f"!!! Unknown Element {elmnt.name} :\n{elmnt.text}\n!!!")

        elmnt = elmnt.next_sibling

    races.append(data)
    return races


## url        - string
## element    - string
## identifier - string
## css_class  - string
##
## return     - BeautifulSoup PageElement
def scrape_webpage(url, element, identifier, css_class):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup.find(element, id=identifier, class_=css_class)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        

## tableTag - BeautifulSoup tag element with name "table"
## title    - title for table (optional)
##
## return   - string form of table element and all its contained elements 
##            "\n[{title} ||| {column1} || {column2};;\n
##                {row1 data column1} || {row1 data column2};
##                {row2 data column1} || {row2 data column2}]\n"
#
# replaces links using link_formatter 
# if table starts with two th rowns, the text in the first row will be used as the title
#  setting a title with the 'title' arg will prevent this
def table_formatter(tableTag, title = ""):
    if tableTag.name != 'table':
        print(f"table fail {tableTag}")
        return

    while tableTag.a: # no list / basic feature
        tableTag.a.replace_with(link_formatter(tableTag.a))

    tableAsStr = '\n['
    if title != '':
        tableAsStr += title + " ||| "

    for index, child in enumerate(tableTag.contents):
        if child.text == '\n':
            continue

        if child.th:
            if tableTag.contents[index + 2].th:
                if tableAsStr == '\n[': # table title
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

    return tableAsStr[:-2] + ']\n'


## listTag - BeautifulSoup tag element with name "ul"
## count   - recursion count
##
## return  - string form of ul element and all its contined elements
##           "\n[{item1};\n
##               {item2}]\n"
#
# supports nested lists (uses recursion for this)
# replaces links using link_formatter 
# if a list element contains strong text the element is added in the Feature format
#  "{strong text} | {following text}"
def list_formatter(listTag, count = 0):
    if listTag.name != 'ul':
        return
    
    while listTag.a:
        listTag.a.replace_with(link_formatter(listTag.a))

    listAsStr = "\n["
    for child in listTag.children:
        if child.text == '\n':
            continue
        if child.name == 'ul':
            listAsStr += list_formatter(child, count + 1).strip() + ";\n"
        elif child.name == 'li':
            while child.ul:
                child.ul.replace_with(list_formatter(child.ul, count + 1).strip())

            if child.strong:
                liTextArray = child.get_text(" | ",strip=True).split(" | ")
                listAsStr += f"{child.strong.text.strip().rstrip('.')} | {' '.join(liTextArray[1:])};\n"
            else:
                listAsStr += child.text.strip() + ";\n"
        
    return listAsStr[:-2] + ']\n'


## linkTag - BeautifulSoup tag element with name "a"
## 
## return - string form of hyperlink in custom format or markdown if link does not go to dnd5e.wikidot.com
##          custom format examples: "{spell:true-strike}" or "{feat:rune-shaper}"
##          markdown examples: "[true-strike](https://dnd5e.wikidot.com/spell:true-strike)" or "[rune-shaper](https://dnd5e.wikidot.com/feat:rune-shaper)"
def link_formatter(linkTag):
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
    # provide the setting specific source. EX: Eberron
    # only use for races under Setting Specific Lineages: https://dnd5e.wikidot.com/lineage#toc4
    source = ""
    # provide the url to the race's main page EX: https://dnd5e.wikidot.com/lineage:deep-gnome
    # note: all races have the same url but change the race name at the end
    #  https://dnd5e.wikidot.com/lineage:deep-gnome  https://dnd5e.wikidot.com/lineage:eladrin
    url = "https://dnd5e.wikidot.com/lineage:custom"

    target_element = "div page-content"# target element in the format "{html element} {id} {class}"

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
    raceData = extract_race_data(scrape_webpage(url, element, identifier, css_class), raceName, source)

    print(f"\n\nnum entries: {len(raceData)}\n")
    for data in raceData:
        print("########################")
        print(str(data))
    for index, data in enumerate(raceData):
        raceData[index] = data.toCSVformat()

    filePath = "CSVs/SettingSpecific/" if source else "CSVs/"
    with open(f'{filePath}{raceName}.csv', 'w', newline='') as csvfile:
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


## web page pattern/format notes ##
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


    
## Identified patterns in Setting Specific race pages ##

## THEROS, Ravnica, Plane Shift, Dragonlance
# (desc)    p
# (titile)  h2   ('Features'/'Traits')
# (source)  p    ('Source: ...')
# (content) ul
## ##


## Plane Shift ##
# (desc)    p
# (source)  h1
# (desc)    p
# (content) ul
#
# (source)  h1
# (desc)    p
# (content) ul

# (desc)    p
# (titile)  h1   ('Features'/'Traits')
# (content) ul
#
# (source)  h1
# (sub race)h2
# (desc)    p
# (content) ul
## Plane Shift ##


## SPELLJAMMER ##
# (source)  p    ('Source: ...')
# (desc)    p
# (titile)  h5   ('Features'/'Traits')
# (content) ul

# (source)  p    ('Source: ...')
# (desc)    p
# (table h) h5
# (table)   table
# (titile)  h5   ('Features'/'Traits')
# (content) ul
## SPELLJAMMER ##


## Ravnica, Plane Shift ##
# (desc)    p
# (source)  h1
# (content) ul
#
# (source)  h1
# (content) ul
## Ravnica, Plane Shift ##


## Ravenloft ##
# (desc)          p
# (source)        h1
# (desc cont.)    h3, p, table
# (title)         h2
# (content)       ul
#
# (source prefix) h1
# (source final)  p   ('Source:...')
# (desc cont.)    h3, p, table
# (title)         h2
# (content)       ul
## Ravenloft ##


## Eberron ##
# (desc)          p
# (source)        h1
# (content)       ul
#
# (source prefix) h1
# (title)         h2  ('Features'/'Traits')
# (source final)  p   ('Source:...')
# (content)       ul
#
# (sub race)      h2
# (desc)          p
# (content)       ul

# (desc)    p
# (source)  h1
# (content) ul
#
# (source prefix) h1
# (source final)  p   ('Source: ...')(may hold prefix already)
# (content)       ul
## Eberron ##


# p     desc/source final ("Source: ...")(source final may contain source prefix)
# h1    separator ('Features'/'Traits')/source prefix (prefix + final = full source)
# h2    subclass/separator ('Features'/'Traits')
# h3    subsection title in description
# h5    table name/separator ('Features'/'Traits')
# ul    content

# source - marks a new entry
