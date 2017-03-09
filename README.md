### Spelling corrector project (MA Ling 2016, Computer Linguistics, HSE) ###
The project is done only for study purposes. 

#### Contributors: ####
* Danilova Veronika
* Moiseev George
* Nasedkin Alexander
* Prisyazhnaya Angelina

#### Dictionaries ####
Dictionaries are formed basing on OpenCorpora (http://www.opencorpora.org/) resource
* __dict.opcorpora.xml__ (http://www.opencorpora.org/dict.php)
* __bigram.opcorpora.json__ and __trigram.opcorpora.json__ (bi/trigram frequencies of morphological tags counted upon http://www.opencorpora.org/?page=downloads corpora)

#### PrefixTree ####
PrefixTree (or trie) realization is based upon http://fiber-space.de/wordpress/2011/01/07/fuzzy-string-matching-ii-matching-wordlists/. Trie is serialized with pickle and stored in archive __pt.pkl.zip__.
