These are the scripts I use to make CSVs that are used in Google Sheets to act as a database for my [Character Sheet](https://pantheradigital.github.io/CharacterSheet/) project.

## DnDWebScrape-Races
Pulls a specified webpage for DnD races found on wikidot.com, parses the page elements to determine what data they hold, formats the data into plain text with Markdown-Like elements for lists/tables/links, then places data into a CSV. 

A custom Markdown-like format was used for special elements in text to allow for easy adding and reparsing of this data again later, easy nested elements, and adding extra data to elements such as names for tables and organizational tags to links.

<details>

<summary>Custom Format</summary><br>
  
**Links:** \
`{spell:spell name}` \
`{feat:feat name}` \
`{item:item name}`
- Curly braces enclose the link with a colon separating the two main parts
- Part one is the specifier of what the element type is (such as a spell or item like a sword)
- Part two is the name of the item
- This works with wikidot links as the site uses this format without the curly braces for their links
- This same format for data lookup is planned to be used in [Character Sheet](https://pantheradigital.github.io/CharacterSheet/) for adding and finding items, spells, etc.
- As a fallback normal Markdown format may be used if a non-wikidot link is used


**Unordered Lists:**
```
\n[item1;\n
item2]\n
```
- ‘;\n’ separates items
- Lists start and end on their own lines unless they are within another element, such as a list or table, in which the outer newlines are removed

**Table:** \
_With name_
```
\n[optional table name ||| column name || column name;;\n
row 1 data || row 1 other data;\n
row 2 data || row 2 other data]\n
```
_Without name_
```
\n[column name || column name;;\n
row 1 data || row 1 other data;\n
row 2 data || row 2 other data]\n
```
- ‘ || ‘ separates columns
- ‘ ||| ‘ separates the name of the table from the rest of the table
- ‘;;\n’ separates the header row containing the names of the columns from the rest of the rows containing data
- ‘;\n’ separates rows of the table
- Similar to list, a table starts and ends on its own line
- Similar to list syntax but with the addition of column separators and a name separator

**Feat:** \
`Name | Description;\n` \
These are elements that have a name and a description and are used in DnD to describe many aspects of a character
<br><br>

All above elements, except Links, may contain themselves or other above elements making it a goal for this format to allow for containment of other elements while still being easy to format and add to entries, and parse later.

</details>

<details>

<summary>Example Output of Text Pre-CSV:</summary><br>

Pulled from https://dnd5e.wikidot.com/lineage:hexblood \
(The script will pull all data for a race from a page including different sub-races and sources. This is just the data of the first entry to demonstrate the formatting of the output.)

```
source :        Van Richten's Guide to Ravenloft
race :          hexblood
sub-race :      
description :   Where wishing fails, ancient magic can offer a heart’s desire—at least, for a time. Hexbloods are individuals infused with eldritch magic, fey energy, or mysterious witchcraft. Some who enter into bargains with hags gain their deepest wishes but eventually find themselves transformed. These changes evidence a hag’s influence: ears that split in forked points, skin in lurid shades, long hair that regrows if cut, and an irremovable living crown. Along with these marks, hexbloods manifest hag-like traits, such as darkvision, and a variety of magical methods to beguile the senses and avoid the same.
While many hexbloods gain their lineage after making a deal with a hag, others reveal their nature as they age—particularly if a hag influenced them early in life or even before their birth. Many hexbloods turn to lives of adventure, seeking to discover the mysteries of their magic, to forge a connection with their fey natures, or to avoid a hag that obsesses over them.
###Heir of Hags
One way hags create more of their kind is through the creation of hexbloods. Every hexblood exhibits features suggestive of the hag whose magic inspires their powers. This includes an unusual crown, often called a eldercross or witch’s turn. This living, garland-like part of a hexblood’s body extends from their temples and wraps behind the head, serving as a visible mark of the bargain between hag and hexblood, a debt owed, or a change to come.
###Hexblood Origins
A bargain with a hag or other eerie forces transformed your character into a magical being. Roll on or choose an option from the Hexblood Origins table to determine how your character gained their lineage.
[Hexblood Origins ||| d8 || Origin;;
1 || Seeking a child, your parent made a bargain with a hag. You are the result of that arrangement.;
2 || Fey kidnappers swapped you and your parents’ child.;
3 || A coven of hags lost one of its members. You were created to replace the lost hag.;
4 || You were cursed as a child. A deal with the spirits of the forest transformed you into a hexblood, now free of the curse.;
5 || You began life as a fey creature, but an accident changed you and forced you from your home.;
6 || A slighted druid transformed you and bound you to live only so long as a sacred tree bears fruit.]
ability-score :  Increase one ability score by 2 and increase a different one by 1, or increase three different ability scores by 1. If you are replacing your race with this lineage, replace any Ability Score Increase you previously had with this.
age :           
alignment :     
languages :      You can speak, read, and write Common and one other language that you and your DM agree is appropriate for the character. If you are replacing your race with this lineage, you retain any languages you had and gain no new languages.
size :           You are Medium or Small. You choose the size when you gain this lineage.
speed :          Your walking speed is 30 feet
features :      Creature Type |  You are a Fey.;

Ancestral Legacy |  If you replace a race with this lineage, you can keep the following elements of that race: any skill proficiencies you gained from it and any climbing, flying, or swimming speed you gained from it.
[If you don't keep any of those elements or you choose this lineage at character creation, you gain proficiency in two skills of your choice.];

Darkvision |  You can see in dim light within 60 feet of you as if it were bright light and in darkness as if it were dim light. You discern colors in that darkness as shades of gray.;

Eerie Token |  As a bonus action, you can harmlessly remove a lock of your hair, one of your nails, or one of your teeth. This token is imbued with magic until you finish a long rest. While the token is imbued this way, you can take these actions:
[[Telepathic Message | As an action, you can send a telepathic message to the creature holding or carrying the token, as long as you are within 10 miles of it. The message can contain up to twenty-five words.;
Remote Viewing | If you are within 10 miles of the token, you can enter a trance as an action. The trance lasts for 1 minute, but it ends early if you dismiss it (no action required) or are incapacitated. During this trance, you can see and hear from the token as if you were located where it is. While you are using your senses at the token's location, you are blinded and deafened in regard to your own surroundings. When the trance ends, the token is harmlessly destroyed.];
Once you create a token using this feature, you can't do so again until you finish a long rest, at which point your missing part regrows.];

Hex Magic |  You can cast the {spell:disguise-self} and {spell:hex} spells with this trait. Once you cast either of these spells with this trait, you can’t cast that spell with it again until you finish a long rest. You can also cast these spells using any spell slots you have.
[Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose the ability when you gain this lineage).];
```

</details>

<details>

<summary>Looking Back</summary><br>

This was good practice in data parsing and code adaptability. The core problem to solve with this project was taking data from web elements and storing the data in a defined format for use later. 

The web elements had multiple formats and variations that would need to be read from. Additionally one webpage would hold all the data related to one race which included sub-races and variants from different sources. The data itself is text, having to be formatted based on the content and intended use of the text. The text would need to be parsed into main categories before being converted to CSV. These are the main categories used to organize race data in DnD and this project: \
Source, race, sub-race, description, ability score, age, alignment, languages, size, speed, features.

This project had 3 main phases of development, each coinciding with the different versions of the program.

1 : Brute force method. \
Identified a common format across a few pages that organized the data in a specific order and with consistent HTML element usage. This was only usable for some races in Common and Exotic groups. This stage was very rigid but acted as a starting point

2 : Good for all races under Common, Exotic and Monstrous groups. \
Common formats were identified based on their use of HTML elements and organization of data, with some deviation that would need to be handled. This, and the previous version, operated on ‘assumptions’. For example if the current element was the source then the next would be the description, and after that would be the features, unless it was an HTML table in which case it was still part of the description. This worked well since a format was known with known variations that could be handled, however it would expand version 1 greatly to cover the variations and was still rigid. In this phase test cases were used during production. Three main pages were used for testing as they were complicated and covered all main variations and elements. Once the program could properly read these pages it was complete.

3 : Good for all previous races and extends to Setting Specific group. \
New formats were introduced that were so different from the previous formats that the previous version of the program would not be usable. This version rebuilt the program to no longer operate on ‘assumptions’ but would assess each element individually, only looking at past or future elements for context when necessary (such as if the table name was the previous element). This greatly improved the flexibility of the program, only needing minor changes to work on the previous formats once it worked on the Setting Specific formats. Test cases were again identified among the Setting Specific races to help during development before moving back to the previous groups to ensure full compatibility with the rest of the groups.

</details>
