```
         _     _       _   _______ 
        | |   | |     | | / /  __ \
 _______| | __| | __ _| |/ /| |  \/
|_  / _ \ |/ _` |/ _` |    \| | __ 
 / /  __/ | (_| | (_| | |\  \ |_\ \
/___\___|_|\__,_|\__,_\_| \_/\____/

a TLOZ inspired knowledge graph.                                   
```

- Step 0: Gather a lot of wiki pages (check if you can use a tool like [HTTrack](https://www.httrack.com/)), in this case I downloaded a copy of the whole [Zeldapedia](http://zelda.wikia.com/wiki/)  and [Zelda Wiki](https://zelda.gamepedia.com/Main_Page).  

- Step 1: If you did not configure your crawlers/copiers correctly, the previous step may have got you a lot of useles sites, such as User pages, templates or even forum pages. The purpose of this step is to reduce the number of files to be procesed by filtering out the documents whose name starts with "User_", "Category_Zeldapedians_", "Message_Wall_" and similar. In this cleaning stage the real content of the site (in wikia that is  the tag `article`) is extracted discarding the templated website out. 
	- Here are the **[Zeldapedia notebook](html_cleaning/zelda.wikia.ipynb)** and the **[Zelda Wiki notebook](html_cleaning/zelda.gamepedia.ipynb)**.
  - Download the "clean" data here: [zelda-wikia2-clean.zip](https://github.com/fferegrino/zeldaKG/releases/download/data/zelda-wikia2-clean.zip) and [zelda-gamepedia-clean.zip](https://github.com/fferegrino/zeldaKG/releases/download/data/zelda-gamepedia-clean.zip)

 - Step 2: Information extraction
	-  Title-Link relationship: extract a relationship between each file and the title of the article it represents into two dataframes. **[Title-Link relationship notebook](relation_extraction/title-link-relationship.ipynb)**.
	- Infobox extraction: extract *raw* relationships between entities extracted from the infobox of each page. The relationships are generated as json objects that are interpreted in the next step. **[for gamepedia](relation_extraction/infobox_extraction.gamepedia.ipynb)** and **[for wikia](relation_extraction/infobox_extraction.wikia.ipynb)**.
	- Merge infobox sources: In this step we can extract information from the infoboxes. Information such as Gender, Race, Appereances, and many more. **[Merge sources notebook](relation_extraction/merge_sources_infoboxes.ipynb)**.
	- Text extraction using spaCy. In this step the text of each article is analysed using the spaCy package to extract *raw* relationships between a `Resource` and names in the notebook **[text_extraction](relation_extraction/text_extraction.ipynb)**, and then processed again to ground them to only relationships between `Resource`s existing in our graph, his happens in **[text_extraction_processing](relation_extraction/text_extraction_processing.ipynb)**.  

- Step 3: Insertion into neo4j  

 **The graph is not accurate nor complete. I'm just playing around since I want to learn a bit more about neo4j while performing information extraction and building a knowledge graph**.
