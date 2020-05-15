import nltk
from nltk.tree import Tree
import spacy
from nltk.chunk import RegexpParser
import warnings
import re
warnings.filterwarnings("ignore")

nlp=spacy.load(r'en_core_web_sm')


##################################################################################
######################## UTILITY FUNCTIONS #######################################
##################################################################################

def ie_preprocess(segments):
        sentences = nltk.sent_tokenize(segments) 
        prepared_sents=[]
        for sent in sentences:
            prepared_sents=prepared_sents+nltk.word_tokenize(sent)
            
        words_list=[]
        for sent in prepared_sents:
            words_list=words_list+nltk.word_tokenize(sent)
        tagged_words = nltk.pos_tag(words_list)
        return tagged_words
    
###################################################################################    

def parse_chunks(tagged_segments, grammar):
        cp = RegexpParser(grammar)
        tree = cp.parse(tagged_segments)
        return tree
    
###################################################################################

def find_chunk(chunks,chunks_list=['CLAUSE']):
    return [subtree for subtree in chunks.subtrees(filter = lambda t: t.label() in chunks_list)]

##################################################################################

def is_clause(parse_trees): 
    return any([subtree.label()=='CLAUSE' for subtree in find_chunk(parse_trees)])

##################################################################################

def is_only_VP(parse_tree):
    if is_clause(parse_tree):
        return False
    return any([Tree.fromstring(str(subtree)).label() == 'VP' for subtree in parse_tree])

##################################################################################

def find_VP_tree(parse_tree):
    words=""
    f_index=0
    for child in parse_tree:
            if not isinstance(child,tuple):
                if child.label() == "CLAUSE":
                    for phrase in child:
                        if not isinstance(phrase,tuple):
                            if phrase.label()=="VP":
                                r_index=f_index
                                for word in phrase:
                                    words=words+" "+word[0]
                                    r_index+=1
                                return (phrase,words,f_index,r_index)
                            else:
                                for word in phrase:
                                    f_index+=1
                        else:
                            f_index+=1
                elif child.label()=="VP":
                    r_index=f_index
                    for i in child:
                        words=words+" "+i[0]
                        r_index+=1
                    return (child,words,f_index,r_index)
                else:
                    for word in child:
                        f_index+=1
            else:
                f_index+=1
                
##################################################################################

def find_POS_subtree(parse_tree,POS):
    words=""
    f_index=0
    for child in parse_tree:
            if not isinstance(child,tuple):
                if child.label() == "CLAUSE":
                    for phrase in child:
                        if not isinstance(phrase,tuple):
                            if phrase.label()==POS:
                                r_index=f_index
                                for word in phrase:
                                    words=words+" "+word[0]
                                    r_index+=1
                                return (phrase,words,f_index,r_index)
                            else:
                                for word in phrase:
                                    f_index+=1
                        else:
                            f_index+=1
                elif child.label()==POS:
                    r_index=f_index
                    for i in child:
                        words=words+" "+i[0]
                        r_index+=1
                    return (child,words,f_index,r_index)
                else:
                    for word in child:
                        f_index+=1
            else:
                f_index+=1
                
##################################################################################

def find_NP_tree(parse_tree):
    words=""
    f_index=0
    for child in parse_tree:
            if not isinstance(child,tuple):
                if child.label() == "CLAUSE":
                    for phrase in child:
                        if phrase.label()=="NP":
                            r_index=f_index
                            for word in phrase:
                                words=words+" "+word[0]
                                r_index+=1
                            return (phrase,words,f_index,r_index)
                        else:
                            for word in phrase:
                                f_index+=1
                elif child.label()=="NP":
                    r_index=f_index
                    for i in child:
                        words=words+" "+i[0]
                        r_index+=1
                    return (child,words,f_index,r_index)
                else:
                    for word in child:
                        f_index+=1
            else:
                f_index+=1
                
################################################################################## 

def find_the_closest_NP_for_VP(parse_trees,POS):
    is_VP =[ is_only_VP(parse_tree) for parse_tree in parse_trees]
    closest_POS = []
    for index,truth_val in enumerate(is_VP):
        if not truth_val:
            closest_POS.append(None)
        else:
            found_POS = False
            for index_tree in reversed(range(0,index)):
                POS,_,_,_=find_POS_subtree(parse_trees[index_tree],POS)
                closest_POS.append(POS)
                found_POS=True
                break
            if not found_POS :
                closest_POS.append(None)
    return closest_POS

################################################################################## 

def enrich_VPs(parse_trees,POS):
    enrichment_data = find_the_closest_NP_for_VP(parse_trees,POS)
    enriched_parse_trees =  []
    enrichment_done =[]
    for ptree,enrich in zip(parse_trees,enrichment_data):
        if enrich :
#             print(enrich)
            VP,_,vpf_index,_=find_VP_tree(ptree)
            ptree.insert(vpf_index,Tree('CLAUSE',[enrich.copy(deep=True),VP]))
            ptree.remove(VP)
            enriched_parse_trees.append(ptree)
        else:
            enriched_parse_trees.append(ptree)
    return enriched_parse_trees , [ not not data for data in enrichment_data ]

################################################################################## 
           
def chunk_VP_NP_parts(parse_tree) :
    NP_trees=[]
    VP_trees=[]
    for subtree in parse_tree:
        if not isinstance(subtree, tuple):
            print(subtree)
            if subtree.label()=="CLAUSE":
                for phrase in subtree:
                    print(subtree)
                    if phrase.label()=="NP":
                        NP_trees.append(phrase)
                    else:
                        VP_trees.append(phrase)
            elif subtree.label()=="NP":
                NP_trees.append(subtree)
            elif subtree.label()=="VP":
                VP_trees.append(subtree)
    return NP_trees,VP_trees

##################################################################################

def verb_phrase_from_clause(identified_chunk,POS_tag="VP"):
    if len(identified_chunk)>0:
        vp_tree,vp_phrase,_,_=find_POS_subtree(identified_chunk,POS_tag)
        vp_phrase=nlp(vp_phrase.strip())
        if len(vp_phrase)>1:
            vp_tag=vp_tree.leaves()[0][1]#0-> first one, next 1-> POS Tag
            if vp_tag == "VBD" or vp_tag == "VBN":
                return "did"
            return vp_phrase[0].text
        else:
            vp_tag=vp_tree.leaves()[0][1] 
        if vp_tag == "VBD" or vp_tag == "VBN":
            return "did"
        elif vp_tag == "VBP" or vp_tag == "VB" or vp_tag == "VBG":
            if vp_phrase[0].text.lower()=='am':
                return 'are'
            elif vp_phrase[0].text.lower() =='are':
                return 'are'
            elif vp_phrase[0].text.lower()=='were':
                return 'were'
            return "do"
        elif vp_tag == "VBZ" :
            return "does"
        else :
            return None
        
##################################################################################

def words_from_tree(parse_tree,start=0,end=None):
    if str(end).lower()=="end":
        end=len(parse_tree.leaves())
    if end==None:
        sentence=parse_tree[parse_tree.leaf_treeposition(start)][0]
    else:
        sentence=""
        for i in range(start,end):
            sentence+=parse_tree[parse_tree.leaf_treeposition(i)][0]+" "
    return sentence

##################################################################################

def remove_blah(parse_tree,chunks_list=['CLAUSE','NP','VP'],other_way=False):
    bsl=[] #blah subtrees list
    for subtree in parse_tree:
        blah_stop=False
        if isinstance(subtree,nltk.tree.Tree):
            if subtree.label() in chunks_list:
                blah_stop=True
        else:
            if subtree[1] in chunks_list:
                blah_stop=True
        if blah_stop:
            break
        else:
            bsl.append(subtree)
    for blah in bsl:
        parse_tree.remove(blah) 
    return parse_tree

##################################################################################

def get_date(sentence):
    doc=nlp(sentence.strip())
    pos=[ent.pos_ for ent in doc]
    for ent in doc.ents:
        if ent.label_ in ['DATE','TIME','CARDINAL']:
            if ent.label_=='CARDINAL':
                date_format='\d{1,4}[-/]\d{1,2}[-/]\d{1,4}'
                if not ('AM' in ent.text or 'PM' in ent.text or re.findall(date_format,ent.text)):
                    continue
            sentence=sentence.replace(ent.text,"")
            doc=nlp(sentence.strip())
            if doc[-1].pos_ == 'ADP':
                Answer=doc[-1].text+" "+ent.text
                sentence=sentence.replace(doc[-1].text,"")
                return Answer,sentence 
            else:
                return ent.text,sentence 
    return None,None

##################################################################################

def subject_verb_conversion(subject,verb,type=1):
    verb='is' if (subject.strip()+verb.strip()).lower() in ['iam','youare'] else verb
    verb='was' if (subject.strip()+verb.strip()).lower() in ['youwere'] else verb
    if subject.strip().lower() in ['i','we']:
        subject='you' 
    elif subject.strip().lower() =='you':
        subject='i'
    elif subject.strip().lower() in ['my','our'] and type==3:
        subject='yours' 
    return verb,subject

##################################################################################
########################  Question Disambiguity rules   ##########################
##################################################################################

def QSD_1(noun_phrase):
    #print(ner_chunk_tags)
    sentence =  nlp(noun_phrase.strip())
    pos=dict([(word.pos_,word.text) for  word in sentence])
    if sentence.ents or "PRON" in pos.keys():
        if len(sentence.ents)==1 :
            name=sentence.ents[0].text
            not_name=noun_phrase.replace(name,"")
            ipos=dict([(word.pos_,word.text) for  word in nlp(not_name)])
            if any([pos=="NOUN" for pos in ipos.keys()]):
                return [("whom",name,not_name),("what",not_name,name)]
            else:
                return [("whom",name,not_name)]
        elif len(sentence.ents)>1:
            return [("whom",noun_phrase,"")]
        else:
            return [("whom",pos["PRON"],noun_phrase.replace(pos["PRON"],""))]
    else:
        return [("what",noun_phrase,"")]
    
##################################################################################

def QSD_2(noun_phrase):
    tags=ie_preprocess(noun_phrase)
    grammar='''CLAUSE:{(<DT>?<JJ.?|IN|DT|CC|VBN>*<NN.?|POS|VBG>+)+}
                PRON:{<PRP>|<PRP\$>}'''
    p=parse_chunks(tags,grammar)
    chunks1=find_chunk(p)
    chunks2=find_chunk(p,chunks_list=["PRON"])
    if chunks1 and chunks2:
        chunk1_text=words_from_tree(chunks1[0],end="end")
        chunk2_text=words_from_tree(chunks2[0],end="end")
        return [("Whom",chunk2_text,chunk1_text),("what",chunk1_text,chunk2_text)]
    return []+QSD_1(noun_phrase)
   
    
##################################################################################

def QSD_3(phrase,qtype=1):
    doc=nlp(phrase.strip())
    for ent in doc.ents:
        if ent.label_ in ['NORP','ORG','GPE','LOC']:
            if qtype==1:
                return "what"
            elif qtype==2:
                return "Where"
            else:
                return None
        
##################################################################################


##################################################################################################################
def QSG_1(sentence):#Questions starting with Who.
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        doc=nlp(sentence)
        grammer=r'''
                    NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
                    VP:{<RB.?|VB.?|MD|RP>+}
                    CLAUSE:{<NP>+<VP>+} 
        '''
        parse_trees=[parse_chunks(tagged_segment,grammer) for tagged_segment in tagged_segments]
        parse_trees,_=enrich_VPs(parse_trees,"NP")
        parse_trees=[remove_blah(parse_tree) for parse_tree in parse_trees]
      
        identified_chunks=[find_chunk(parse_tree) for parse_tree in parse_trees]
        
        Question_answer_pairs=[]
        for i in range(len(identified_chunks)): 
            Question=""
            if len(identified_chunks[i])==1:
                #print(identified_chunks[0][0].leaves()) #noun_phrase length
                sentence_length=len(parse_trees[i].leaves())
                _,answer,_,skip_length=find_NP_tree(identified_chunks[i][0])
                _,verb,_,skip_length=find_VP_tree(identified_chunks[i][0])
                parse_trees[i].remove(identified_chunks[i][0])
                Question=words_from_tree(parse_trees[i],end='end')
                Question+="?"
                verb,answer=subject_verb_conversion(answer,verb)
                #print(answer)
                Question="Who " +verb +" "+Question
#                 print("Question: ", Question)
#                 print("Answer: ",answer)
                Question_answer_pairs.append((Question,answer))
            else:
                None
        return Question_answer_pairs
    except:
        return None

##################################################################################################################
def QSG_21(sentence):#what questions starting with preposition or TO
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        grammar=r'''
                   VP:{<RB.?|VB.?|MD|RP>+}
                   NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
                   CLAUSE:{<NP>+<VP>+}  
        '''
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
            PREP:{<TO>+|<IN>+}
            CLAUSE:{<PREP><DT>?< RB.?>*<JJ.?>*<NN.?|PRP|PRP$|POS|VB.?|DT|CD|VBN>+}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
    #     print(parse_trees2)
        tagged_segments=[parse_tree.leaves() for parse_tree in parse_trees2]
        if len(tagged_segments)>0:
            parse_trees1=[parse_chunks(tagged_segment,grammar) for tagged_segment in tagged_segments]
            parse_trees1,_=enrich_VPs(parse_trees1,"NP")
            parse_trees1=[remove_blah(parse_tree) for parse_tree in parse_trees1]
            identified_chunks1=[find_chunk(parse_tree) for parse_tree in parse_trees1]
            verbs=[verb_phrase_from_clause(identified_chunk) for identified_chunk in identified_chunks1]
        else:
            parse_trees1=[]
            identified_chunks1=[]

        Question_answer_pairs=[]
        for i in range(len(identified_chunks1)):
            if not not identified_chunks1[i] and not not identified_chunks2[i]:
                if QSG_23(segments[i]) or QSG_22(segments[i]):
                    continue
                _,subject,_,_=find_NP_tree(identified_chunks1[i])
                _,verb_phrase,_,_=find_VP_tree(identified_chunks1[i])
                parse_trees1[i].remove(identified_chunks1[i][0])
                if not verbs[i] in verb_phrase:
                    verb_phrase=verbs[i]+" "+verb_phrase
                vp_doc=nlp(verb_phrase.strip())
                _,preposition,_,_=find_POS_subtree(identified_chunks2[i],"PREP")
                Answer=words_from_tree(identified_chunks2[i][0],end="end")
                check,_=get_date(Answer)
                if check or QSG_4(segments[i]):
                    continue
                #import pdb;pdb.set_trace()
                verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text
                v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                if not not QSD_3(Answer):
                    WH_word=QSD_3(Answer,2)
                else:
                    [(WH_word,_,_)]=QSD_1(Answer)
                    WH_word=preposition+" "+WH_word
                Question=WH_word+" "+verbs[i]+" "+subject+" "+v_rest
                remaining=words_from_tree(parse_trees1[i],end="end")
                Question=Question+" "+remaining+'?'
#                 print("Question: ",Question)
#                 print("Answer: ",Answer)
                Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None
##################################################################################################################
def QSG_22(sentence):#what questions for answers in noun form
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
            VP:{<VB.?|MD|RP|RB.?>+}
            NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN|JJ>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
            CLAUSE:{<VP>+<NP>+}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        #print(parse_trees2)
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
        verbs=[verb_phrase_from_clause(identified_chunk) for identified_chunk in identified_chunks2]
        #print(identified_chunks2)
        #print(verbs)
        Question_answer_pairs=[]
        for i in range(len(identified_chunks2)):
            if not not identified_chunks2[i]:
                if QSG_4(segments[i]):
                    continue
                NP_tree,subject,_,_=find_NP_tree(parse_trees2[i])
                VP_tree,verb_phrase,_,_=find_VP_tree(identified_chunks2[i])
                parse_trees2[i].remove(NP_tree)
                identified_chunks2[i][0].remove(VP_tree)
                if not verbs[i] in verb_phrase:
                    verb_phrase=verbs[i]+" "+verb_phrase
                vp_doc=nlp(verb_phrase.strip())
                #print(chunk_VP_NP_parts(identified_chunks2[i][0]))
                verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                Answer=words_from_tree(identified_chunks2[i][0],end="end")
                v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text
                v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                #print(Answer)
                q_list=QSD_2(Answer)
                #print(q_list)
                for q in q_list:
                    #print(q)
                    Question=q[0]+" "+verbs[i]+" "+subject+" "+v_rest+" "+q[2]
                    remaining=words_from_tree(parse_trees2[i],end="end")
                    Question=Question+" "+remaining+'?'
                    Answer=q[1]
                    check,_=get_date(Answer)
                    if check:
                        continue
#                     print("Question: ",Question)
#                     print("Answer: ",Answer)
                    Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None



##################################################################################################################
def QSG_23(sentence):#what questions for answers in verb form
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
            VP1:{<TO>+<VB|VBP|RP>+}
            VP2:{<VB.?|MD|RP|RB.?>+}
            NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
            CLAUSE:{<VP1><NP>*}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
    #     print(parse_trees2)
    #     print(identified_chunks2)
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
    #     print(parse_trees2)
        verbs=[verb_phrase_from_clause(parse_tree,"VP2") for parse_tree in parse_trees2]
        #print(identified_chunks2)
        #print(verbs)
        Question_answer_pairs=[]
        for i in range(len(identified_chunks2)):
            if not not identified_chunks2[i]:
                NP_tree,subject,_,_=find_NP_tree(parse_trees2[i])
                parse_trees2[i].remove(NP_tree)
                VP_tree1,verb_phrase1,_,_=find_POS_subtree(identified_chunks2[i],"VP1")
                VP_tree2,verb_phrase2,_,_=find_POS_subtree(parse_trees2[i],"VP2")
                identified_chunks2[i][0].remove(VP_tree1)
                parse_trees2[i].remove(VP_tree2)
                if not verbs[i] in verb_phrase2:
                    verb_phrase2=verbs[i]+" "+verb_phrase2
                vp_doc=nlp(verb_phrase2.strip())
                verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text
                v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                Question="what "+verbs[i]+" "+subject+" "+v_rest
                if not not find_NP_tree(identified_chunks2[i]):
                    Question=Question+" "+verb_phrase1
                    _,Answer,_,_=find_NP_tree(identified_chunks2[i])
                else:
                    Question=Question+" to do"
                    Answer=verb_phrase1
                check,_=get_date(Answer)
                if check:
                    continue
                sentence=nlp(words_from_tree(parse_trees2[i],end="end"))
                remaining=words_from_tree(parse_trees2[i],end="end")
                Question=Question+" "+remaining+'?'
#                 print("Question: ",Question)
#                 print("Answer: ",Answer)
                Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None

##################################################################################################################

def QSG_3(sentence): #Questions for answer's with personal pronoun
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        doc=nlp(sentence)
        grammer=r'''
                   NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
                    VP:{<RB.?|VB.?|MD|RP>+}
                    CLAUSE:{<NP>+<VP>+}             
        '''
        parse_trees=[parse_chunks(tagged_segment,grammer) for tagged_segment in tagged_segments]
        parse_trees,_=enrich_VPs(parse_trees,"NP")
        tagged_segments=[parse_tree.leaves() for parse_tree in parse_trees]
        rule_specific_grammer='''
                    PP:{<NN.?>*<PRP.?|POS>}
                    CLAUSE:{<PP>+<RB.?>*<JJ.?>*<NN.?|VBG|VBN>+<VB.?|MD|RP>+} 
                    '''
        if len(tagged_segments)>0:
            parse_trees=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
            parse_trees=[remove_blah(parse_tree) for parse_tree in parse_trees]
            identified_chunks=[find_chunk(parse_tree) for parse_tree in parse_trees]
        else:
            parse_trees1=[]
            identified_chunks1=[]
    #     print(identified_chunks)
        clause_truths=[is_clause(parse_tree) for parse_tree in parse_trees]
        Question_answer_pairs=[]
        for i in range(len(identified_chunks)):
            Question=""
            if len(identified_chunks[i])==1:
                Question+="Whose "
                #print(identified_chunks[0][0].leaves()) #noun_phrase length
                _,_,_,skip_length=find_POS_subtree(parse_trees[i],"PP")
                #print(skip_length)
                Question+=words_from_tree(parse_trees[i],skip_length,"end")
                Question+="?"
#                 print("Question: ", Question)
                answer=words_from_tree(parse_trees[i],end=skip_length)
                _,answer=subject_verb_conversion(answer,'no',type=3)
#                 print("Answer: ",answer)
                Question_answer_pairs.append((Question,answer))
            else:
                None
        return Question_answer_pairs
    except:
        return None


##################################################################################################################
def QSG_4(sentence):#Questions of Type How many
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        grammar=r'''
                   VP:{<RB.?|VB.?|MD|RP>+}
                   NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
                   CLAUSE:{<NP><VP>}
        '''
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
        NP:{<NN.?|PP|PRP|PRP\$ >+<VBG|POS|CD|RB|DT>*}
        CLAUSE:{<DT>?<JJ.?>?<RB>?<IN|TO|RP>+<DT>*<NP>+}
        
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]

        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
        #print(parse_trees2)
        tagged_segments=[parse_tree.leaves() for parse_tree in parse_trees2]
        if len(tagged_segments)>0:
            parse_trees1=[parse_chunks(tagged_segment,grammar) for tagged_segment in tagged_segments]
            parse_trees1,_=enrich_VPs(parse_trees1,"NP")
            parse_trees1=[remove_blah(parse_tree) for parse_tree in parse_trees1]
            identified_chunks1=[find_chunk(parse_tree) for parse_tree in parse_trees1]
            verbs=[verb_phrase_from_clause(parse_tree) for parse_tree in parse_trees1]
        else:
            parse_trees1=[]
            identified_chunks1=[]
        #import pdb;pdb.set_trace()
        Question_answer_pairs=[]
        for i in range(len(identified_chunks2)):
            if not not identified_chunks2[i] and not not identified_chunks1[i]:
                answer_tree,Answer,_,_=find_NP_tree(identified_chunks2[i][0])
                identified_chunks2[i][0].remove(answer_tree)
                check,_=get_date(Answer)
                if check:
                    continue
                NP_tree,subject,_,_=find_NP_tree(identified_chunks1[i])
                VP_tree,verb_phrase,_,_=find_VP_tree(identified_chunks1[i])
                parse_trees1[i].remove(identified_chunks1[i][0])
                if not verbs[i] in verb_phrase:
                    verb_phrase=verbs[i]+" "+verb_phrase
                vp_doc=nlp(verb_phrase.strip())
                verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text 
                v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                Question=" Where "+verbs[i]+" "+subject+" "+v_rest
                remaining=words_from_tree(parse_trees1[i],end="end")+words_from_tree(identified_chunks2[i][0])

                Question=Question+" "+remaining+'?'
#                 print("Question: ",Question)
#                 print("Answer: ",Answer)
                Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None

##################################################################################################################
def QSG_5(sentence):#Questions of Type How many
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        grammar=r'''
                   VP:{<RB.?|VB.?|MD|RP>+}
                   NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
                   CLAUSE:{<NP><VP>}
        '''
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
                   CLAUSE:{<DT>?<JJ.?>?<RB>?<IN|TO|RP>+<DT>*<NN.?|CD>+}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        #print(parse_trees2)
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
        #import pdb; pdb.set_trace()
        tagged_segments=[parse_tree.leaves() for parse_tree in parse_trees2]
        if len(tagged_segments)>0:
            parse_trees1=[parse_chunks(tagged_segment,grammar) for tagged_segment in tagged_segments]
            parse_trees1,_=enrich_VPs(parse_trees1,"NP")
            parse_trees1=[remove_blah(parse_tree) for parse_tree in parse_trees1]
            identified_chunks1=[find_chunk(parse_tree) for parse_tree in parse_trees1]
            verbs=[verb_phrase_from_clause(parse_tree) for parse_tree in parse_trees1]
        else:
            parse_trees1=[]
            identified_chunks1=[]
        Question_answer_pairs=[]
        for i in range(len(identified_chunks2)):
            if not not identified_chunks2[i] and not not identified_chunks1[i]:
                Answer=words_from_tree(identified_chunks2[i][0],end="end")
                Answer,rest=get_date(Answer)
                if not not Answer:
                    NP_tree,subject,_,_=find_NP_tree(identified_chunks1[i])
                    VP_tree,verb_phrase,_,_=find_VP_tree(identified_chunks1[i])
                    parse_trees1[i].remove(identified_chunks1[i][0])
                    if not verbs[i] in verb_phrase:
                        verb_phrase=verbs[i]+" "+verb_phrase
                    vp_doc=nlp(verb_phrase.strip())
                    verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                    v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text 
                    v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                    Question=" When "+verbs[i]+" "+subject+" "+v_rest
                    remaining=words_from_tree(parse_trees1[i],end="end")
                    Question=Question+" "+remaining+" " +rest+'?'
#                     print("Question: ",Question)
#                     print("Answer: ",Answer)
                    Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None
##################################################################################################################
def QSG_61(sentence):##How much Questions type-1
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        grammar=r'''
                   VP:{<RB.?|VB.?|MD|RP>+}
                   NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
                   CLAUSE:{<NP>+<VP>+}  
        '''
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
            PREP:{<IN>+}
            CLAUSE:{<PREP>+<\$>?<CD>+<NN.?>}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
    #     print(parse_trees2)
        tagged_segments=[parse_tree.leaves() for parse_tree in parse_trees2]
        if len(tagged_segments)>0:
            parse_trees1=[parse_chunks(tagged_segment,grammar) for tagged_segment in tagged_segments]
            parse_trees1,_=enrich_VPs(parse_trees1,"NP")
            parse_trees1=[remove_blah(parse_tree) for parse_tree in parse_trees1]
            identified_chunks1=[find_chunk(parse_tree) for parse_tree in parse_trees1]
            verbs=[verb_phrase_from_clause(identified_chunk) for identified_chunk in identified_chunks1]
        else:
            parse_trees1=[]
            identified_chunks1=[]
        Question_answer_pairs=[]
        for i in range(len(identified_chunks1)):
            if not not identified_chunks1[i] and not not identified_chunks2[i]:
                NP_tree,subject,_,_=find_NP_tree(identified_chunks1[i])
                VP_tree,verb_phrase,_,_=find_VP_tree(identified_chunks1[i])
                parse_trees1[i].remove(identified_chunks1[i][0])
                if not verbs[i] in verb_phrase:
                    verb_phrase=verbs[i]+" "+verb_phrase
                vp_doc=nlp(verb_phrase.strip())
                _,preposition,_,_=find_POS_subtree(identified_chunks2[i],"PREP")
                verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text 
                v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                Question=preposition+" how much "+verbs[i]+" "+subject+" "+v_rest
                Answer=words_from_tree(identified_chunks2[i][0],end="end")
                check,_=get_date(Answer)
                if check:
                    continue
                remaining=words_from_tree(parse_trees1[i],end="end")
                Question=Question+" "+remaining+'?'
#                 print("Question: ",Question)
#                 print("Answer: ",Answer)
                Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None
##################################################################################################################
def QSG_62(sentence):#How much Questions type-2
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
            CURR:{<\$>*<CD>+<NN.?>}
            CLAUSE:{<CURR><MD>?<VB|VBD|VBG|VBP|VBN|VBZ|IN>+}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
    #     print(parse_trees2)
    #     print(identified_chunks2)
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
 
        Question_answer_pairs=[]
        for i in range(len(identified_chunks2)):
            if not not identified_chunks2[i]:
                CURR_tree,Answer,_,_=find_POS_subtree(identified_chunks2[i],"CURR")
                check,_=get_date(Answer)
                if check:
                    continue
                identified_chunks2[i][0].remove(CURR_tree)
                Question="How much "+words_from_tree(identified_chunks2[i][0],end="end")
                remaining=words_from_tree(parse_trees2[i],end="end")
                Question=Question+" "+remaining+'?'
#                 print("Question: ",Question)
#                 print("Answer: ",Answer)
                Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None
##################################################################################################################
def QSG_63(sentence):#How much Questions type-3
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        grammar=r'''
                   VP:{<RB.?|VB.?|MD|RP>+}
                   NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
        '''
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
                   VP:{<MD>?<VB| VBD|VBG|VBP|VBN|VBZ>+}
                   NP:{<IN>?<NN|NNS| NNP|NNPS|PRP|PRP$>?}  
                   CURR:{<\$>*<CD>+}
                   CLAUSE:{<VP><NP><CURR>}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
    #     print(parse_trees2)
        tagged_segments=[parse_tree.leaves() for parse_tree in parse_trees2]
        if len(tagged_segments)>0:
            parse_trees1=[parse_chunks(tagged_segment,grammar) for tagged_segment in tagged_segments]
            parse_trees1,_=enrich_VPs(parse_trees1,"NP")
            parse_trees1=[remove_blah(parse_tree) for parse_tree in parse_trees1]
            verbs=[verb_phrase_from_clause(identified_chunk) for identified_chunk in identified_chunks2]
        else:
            parse_trees1=[]
            identified_chunks2=[]
        Question_answer_pairs=[]
        for i in range(len(identified_chunks2)):
            if not not identified_chunks2[i] and not not parse_trees1[i]:
                NP_tree,subject,_,_=find_NP_tree(parse_trees1[i])
                VP_tree,verb_phrase,_,_=find_VP_tree(identified_chunks2[i])
                CURR_tree,Answer,_,_=find_POS_subtree(identified_chunks2[i],"CURR")
                check,_=get_date(Answer)
                if check:
                    continue
                parse_trees1[i].remove(NP_tree)
                identified_chunks2[i][0].remove(VP_tree)
                identified_chunks2[i][0].remove(CURR_tree)
                if not verbs[i] in verb_phrase:
                    verb_phrase=verbs[i]+" "+verb_phrase
                vp_doc=nlp(verb_phrase.strip())
                verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text 
                v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                Question="How much "+verbs[i]+subject+" "+v_rest
                remaining=words_from_tree(identified_chunks2[i][0],end="end")+words_from_tree(parse_trees1[i],end="end")
                Question=Question+" "+remaining+'?'
#                 print("Question: ",Question)
#                 print("Answer: ",Answer)
                Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None

##################################################################################################################
def QSG_7(sentence):#Questions of Type How many
    try:
        segments = sentence.rstrip().rstrip(".").split(",")
        doc=nlp(sentence)
        grammar=r'''
                   VP:{<RB.?|VB.?|MD|RP>+}
                   NP:{<DT>?<JJ.?>*(<IN|DT|CC|VBN>*<NN.?|PRP|PRP\$|POS|VBG>+)+} 
                   CLAUSE:{<NP><VP>}
        '''
        tagged_segments=[ie_preprocess(segment) for segment in segments]
        rule_specific_grammer=r'''
                   PREP:{<IN>+}
                   NUM:{<CD>+}
                   CLAUSE:{<PREP>?<DT>?<NUM>< RB>?<JJ|JJR|JJS>?<NN|NNS|NNP|NNPS|VBG>+}
        '''
        parse_trees2=[parse_chunks(tagged_segment,rule_specific_grammer) for tagged_segment in tagged_segments]
        identified_chunks2=[find_chunk(parse_tree) for parse_tree in parse_trees2]
        for i in range(len(parse_trees2)):
            if not not identified_chunks2[i]:
                parse_trees2[i].remove(identified_chunks2[i][0])#remove the clauses from parse_tree
    #     print(parse_trees2)
        tagged_segments=[parse_tree.leaves() for parse_tree in parse_trees2]
        if len(tagged_segments)>0:
            parse_trees1=[parse_chunks(tagged_segment,grammar) for tagged_segment in tagged_segments]
            parse_trees1,_=enrich_VPs(parse_trees1,"NP")
            parse_trees1=[remove_blah(parse_tree) for parse_tree in parse_trees1]
            identified_chunks1=[find_chunk(parse_tree) for parse_tree in parse_trees1]
            verbs=[verb_phrase_from_clause(parse_tree) for parse_tree in parse_trees1]
        else:
            parse_trees1=[]
            identified_chunks1=[]

        Question_answer_pairs=[]
        for i in range(len(identified_chunks2)):
            if not not identified_chunks2[i] and not not identified_chunks1[i]:
                Answer=words_from_tree(identified_chunks2[i][0],end="end")
                check,_=get_date(Answer)
                if check:
                    continue
                NP_tree,subject,_,_=find_NP_tree(identified_chunks1[i])
                VP_tree,verb_phrase,_,_=find_VP_tree(identified_chunks1[i])
                parse_trees1[i].remove(identified_chunks1[i][0])
                NUM_tree,_,_,_=find_POS_subtree(identified_chunks2[i],"NUM")
                identified_chunks2[i][0].remove(NUM_tree)
                preposition=""
                if not not find_POS_subtree(identified_chunks2[i],"PREP"):
                    PREP_tree,preposition,_,_=find_POS_subtree(identified_chunks2[i],"PREP")
                    identified_chunks2[i][0].remove(PREP_tree)
                if not verbs[i] in verb_phrase:
                    verb_phrase=verbs[i]+" "+verb_phrase
                vp_doc=nlp(verb_phrase.strip())
                verbs[i],subject=subject_verb_conversion(subject,verbs[i])
                v_rest=vp_doc[1:].lemma_ if (vp_doc[0].text).strip().lower()=='did' else vp_doc[1:].text 
                v_rest="" if vp_doc[1:].text.strip() in ['am','are','were','is'] else v_rest
                Question=preposition+" How many "+words_from_tree(identified_chunks2[i][0])+" "+verbs[i]+" "+subject+" "+v_rest
                remaining=words_from_tree(parse_trees1[i],end="end")
                Question=Question+" "+remaining+'?'
#                 print("Question: ",Question)
#                 print("Answer: ",Answer)
                Question_answer_pairs.append((Question,Answer))
        return Question_answer_pairs
    except:
        return None
##################################################################################################################

##################################################################################################################



