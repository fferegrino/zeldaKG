```
         _     _       _   _______ 
        | |   | |     | | / /  __ \
 _______| | __| | __ _| |/ /| |  \/
|_  / _ \ |/ _` |/ _` |    \| | __ 
 / /  __/ | (_| | (_| | |\  \ |_\ \
/___\___|_|\__,_|\__,_\_| \_/\____/
                                   
```
a TLOZ inspired knowledge graph.


- Step 0: Gather a lot of wiki websites using a tool like [HTTrack](https://www.httrack.com/), in this case I downloaded a copy of the whole website at [http://zelda.wikia.com/wiki/](http://zelda.wikia.com/wiki/)  
- Step 1: a cleaning stage that helps reducing the number of files to be procesed by filtering out the documents whose name starts with "User_", "Category_Zeldapedians_", "Message_Wall_" and similar. In this cleaning stage the tag `article` is extracted from each page. Here is the **[Notebook ](https://github.com/fferegrino/zeldaKG/blob/master/html_cleaning/notebook.ipynb)**.
  - Download the "clean" data here: [zelda-wikia2-clean.zip](https://github.com/fferegrino/zeldaKG/releases/download/data/zelda-wikia2-clean.zip)

- Step 2: Information extraction. This is performed over a series of individual tasks:
  - Infobox extraction. Extracting basic relationships between nodes from each page from the [infobox](https://en.wikipedia.org/wiki/Help:Infobox) they contain.  Here is the **[notebook ](https://github.com/fferegrino/zeldaKG/blob/master/relation_extraction/merge_info.ipynb)**.
  - spaCy extraction. Extracting basic information and relationships between entities using natural language processing in the first paragraph of each article: Here is the **[notebook ](https://github.com/fferegrino/zeldaKG/blob/master/relation_extraction/spacy_exctraction.ipynb)** .
  - Merging the information: in a series of handcrafted rules all the information obtained on the previous two steps is collected into a single result to be inserted into the database. Here is the **[notebook ](https://github.com/fferegrino/zeldaKG/blob/master/relation_extraction/merge_info.ipynb)**. 
 - Step 3: Inserting to the database. Connection to the database and programatic creation of nodes and relationships. Here is the **[notebook](https://github.com/fferegrino/zeldaKG/blob/master/database/insert.ipynb)**.
 
 
 **The graph is not accurate nor complete, I'm just playing around since I want to learn a bit more about neo4j**.
