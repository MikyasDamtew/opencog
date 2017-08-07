import re
__author__ = 'Mikyas Damtew'
# sample string:
# string = '(GeneNode "SERPINA5")(EquivalenceLink(PredicateNode "LOC285484")(LambdaLink(VariableNode "$X")(EvaluationLink(PredicateNode "overexpressed")(ListLink(GeneNode "LOC285483")(VariableNode "$X")))))(AndLink(GeneNode "CCR6")(ConceptNode "GO:0009986"))(MemberLink(GeneNode "CCR6")(ConceptNode "GO:0010634"))(EquivalenceLink(PredicateNode "ACSM5")(LambdaLink(VariableNode "$X")(EvaluationLink(PredicateNode "overexpressed")(ListLink(GeneNode "ACSM5")(VariableNode "$X")))))'

json = {"result":{"atoms":[]}}
handle = 1
links = {}

compile_re = re.compile(r"(?P<open>\()|(?P<close>\))")
compile_re2 = re.compile(r"(\((?P<node>\w+)\s+\"(?P<name>\$?.+?)\")\s*(?P<tv_node>\(stv\s+.+?\s+.+?\))?\)|(\((?P<link>\w+)\s*(?P<tv_link>\(stv\s+.+?\s+.+?\))?(?P<inner>\(.+))")

count = 0
count_brackets = 0
start = 0


def map() :
    for h in links:
	    for x in json["result"]["atoms"]:
				if x["handle"] == h:
					x["outgoing"] = links[h]["outgoing"]		

# a method to find the nth occurence of s in string
def find_nth(string, s, n):
    start = string.find(s)
    while start >= 0 and n > 1:
        start = string.find(s, start+len(s))
        n -= 1
    return start
def extract_tv(tv):
	# cast to string
	st = str(tv)
	# extract and set strength
	strengthstart = st.index(" ")
	strengthlast = st.index(" ",strengthstart+1,len(st)-1)
	strengthstring = st[strengthstart+1:strengthlast]
	strength = float(strengthstring[:2])
	# extract and set count
	countstring = st[strengthlast+1:st.index(")")]
	count = float(countstring[:2])
	# set confidence
	confidnce = count
	return [strength, count, confidnce]

def extract(string,parent,handle,parent_handle):
	count = 0
	count_brackets = 0
	start = 0
	inner = None
	pos = 0
	for match in compile_re.finditer(string):
		try:
			if match.group("open") in match.group():
				count += 1
				count_brackets += 1
		except Exception as e:
			if match.group("close") in match.group():
				count -= 1
				count_brackets += 1
				if count == 0:
					inner = string[start:find_nth(string,")",count_brackets/2)+1]
					for match2 in compile_re2.finditer(inner):
						if match2.group("node") is not None:
							if match2.group("tv_node") is not None:
								tv_list = extract_tv(match2.group("tv_node"))
								strength = tv_list[0]
								tv_count = tv_list[1]
								confidence = tv_list[2]
							else:
								strength = 1.0
								tv_count = 0.0
								confidence = 0.0
							node_type = match2.group("node")
							name = match2.group("name")
							av = {'lti':0,'sti':0,'vlti':False}

							num = 0
							if len(json["result"]["atoms"]) is not 0:
								if parent_handle is None:
									handle = len(json["result"]["atoms"]) +1
									json["result"]["atoms"].append({"name":name,"type":node_type,"attentionvalue":av,"handle":handle,"truthvalue":{"details":{"confidence":confidence,"count":tv_count,"strength":strength},"type":"simple"},"outgoing":[],"incoming":[]})
								else:
									for an_atom in json["result"]["atoms"]:
										if (an_atom["name"] == name) and (an_atom["type"] == node_type):
											num += 1			
									if num == 1:
										for an_atom in json["result"]["atoms"]:
											if (an_atom["name"] == name) and (an_atom["type"] == node_type):
												an_atom["incoming"].append(parent_handle)
												links[parent_handle]["outgoing"].append(an_atom["handle"])
									elif num == 0:
										handle = len(json["result"]["atoms"]) +1
										links[parent_handle]["outgoing"].append(handle)
										json["result"]["atoms"].append({"name":name,"type":node_type,"attentionvalue":av,"handle":handle,"truthvalue":{"details":{"confidence":confidence,"count":tv_count,"strength":strength},"type":"simple"},"outgoing":[],"incoming":[parent_handle]})	
		
							else:
								handle = len(json["result"]["atoms"]) +1
								# links[parent_handle]["outgoing"].append(handle)
								json["result"]["atoms"].append({"name":name,"type":node_type,"attentionvalue":av,"handle":handle,"truthvalue":{"details":{"confidence":confidence,"count":tv_count,"strength":strength},"type":"simple"},"outgoing":[],"incoming":[]})
						elif match2.group("link") is not None:
							if match2.group("tv_link") is not None:
								tv_list = extract_tv(match2.group("tv_link"))
								strength = tv_list[0]
								tv_count = tv_list[1]
								confidence = tv_list[2]
							else:
								strength = 1.0
								tv_count = 0.0
								confidence = 0.0
							link_type = match2.group("link")
							my_handle = len(json["result"]["atoms"]) +1
							handle = my_handle + 1
							links[my_handle] = {"name":link_type,"outgoing":[]}
								
							if parent is None:
								json["result"]["atoms"].append({"name":"","type":link_type,"attentionvalue":{'lti': 0, 'sti': 0, 'vlti': False},"handle":my_handle,"truthvalue":{"details":{"confidence":confidence,"count":tv_count,"strength":strength},"type":"simple"},"outgoing":[],"incoming":[]})
							else:	
								json["result"]["atoms"].append({"name":"","type":link_type,"attentionvalue":{'lti': 0, 'sti': 0, 'vlti': False},"handle":my_handle,"truthvalue":{"details":{"confidence":confidence,"count":tv_count,"strength":strength},"type":"simple"},"outgoing":[],"incoming":[parent_handle]})
								links[parent_handle]["outgoing"].append(my_handle)
							
							pos = find_nth(inner,"(",2)
							st = inner[pos:len(inner)-1]
							extract(st,match2.group("link"),handle,my_handle)
					start = find_nth(string,")",count_brackets/2)+1
	return


def parse(string,parent,handle,parent_handle):
	s = string.replace('\n', '')
	extract(s,parent,handle,parent_handle)
	map()
	return json
# print the result of the sample string sample:
# print parse(string,None,handle,None)

