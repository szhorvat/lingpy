cogid	int	cognateid,cogid,cognateset
counterpart	str	entry,counterpart,orthography,forminsource
doculect	str	language,doculect,dialect,taxon,languages,counterpart_doculect,taxa
concept	str	gloss,concept,concepts
iso	str	iso,isocode
tokens	lambda x:x.split(" ")	tokens,tokenized_counterpart,ipatokens
ipa	str	word,ipa,words
ortho_parse	lambda x:x.split(" ")[1:-1]	orthography_tokens,tokenized_counterpart
sonars	lambda x:[int(s) for s in x.split(" ")]	
prostrings	str	
numbers	lambda x:x.split(" ")	
langid	int	
classes	str	
                          