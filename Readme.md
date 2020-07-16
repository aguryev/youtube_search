Youtube Search Scrapper
=======================

Requirements
------------
Install requirements:
```bash
pip install -r requirements.txt
```

Program attributes
------------------
| Attribute | Default Value | Description
|----------|---------------|-------------
| --keywords | - | The search keywords
| --target | 'video' | The search target. Aither 'video' or 'users'
| --amount | 100 | Number of results to search
| --lang | 'en' | Language code of the search results


Search for Videos
-----------------
Execute:
```bash
python search_youtube.py --keywords <several_keywords> --amount <number_of_search_results> --lang <search_language_code>
```

Search for Youtubers
--------------------
Execute:
```bash
python search_youtube.py --keywords <several_keywords> --amount <number_of_search_results> --lang <search_language_code> --target users 
```

Help
----
To access help message execute:
```bash
python search_youtube.py -h
```
