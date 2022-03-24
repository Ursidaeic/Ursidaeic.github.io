import re

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import sent_tokenize

from emoji import UNICODE_EMOJI

import pkg_resources
from symspellpy import SymSpell, Verbosity

from NEW_NAMES import new_names
from contractions import CONTRACTION_MAP
from abbreviations import abbrev_map



def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    text = re.sub(r"’", "'", text)
    if text in abbrev_map:
        return(abbrev_map[text])
    text = re.sub(r"\bluv", "lov", text)
    
    contractions_pattern = re.compile('({})'.format('|'.join(contraction_mapping.keys())), 
                                      flags=re.IGNORECASE|re.DOTALL)
    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = contraction_mapping.get(match)\
                                if contraction_mapping.get(match)\
                                else contraction_mapping.get(match.lower())
        if expanded_contraction != None:
                
            expanded_contraction = first_char+expanded_contraction[1:]
            return expanded_contraction
        else:
            return 0
    try:    
        expanded_text = contractions_pattern.sub(expand_match, text)
        return expanded_text
    except TypeError:
        return 0
    
def reduce_lengthening(text):
    pattern = re.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1", text)

def lemmatize_sentence(tokens, POS_list):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    
    for word, tag in POS_list:
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence


def prsr(comment, return_POS=False, combine_neg=False, sent_tokenizer=False):
    if type(comment) == list:
        comment = comment[0]
##    cleaned = []
##    for p_com in comments_list:
        
    p_com = comment.lower()
    
    #expand out contractions
    tok = p_com.split(" ")
    z = []
    for w in tok:
        wx = expand_contractions(w)
        if wx == 0:
            continue
        z.append(wx)
    st = " ".join(z)

    if combine_neg == True:
        if "not" in st:
            r = re.findall(r"not \w+\b", st)
            for match in r:
                st = re.sub(match, re.sub(" ", "_", match), st)
    
    if sent_tokenizer==True:
        st = sent_tokenize(st)
        pos_list = []
    else:
        st = [st]
    cleaned = []
    POS_list = []
    for sent in st:
        tokenized = tokenizer.tokenize(sent)
        tokenized = [reduce_lengthening(token) for token in tokenized]
        #clean and spellcheck the data
        clean = []
        
        flag = False
        for w in tokenized:
            if w == "i":
                w = "I"
            if flag == True:
                flag = False
                continue
            if w in emoji_set and w not in clean:
                clean.append(w)
                continue
            elif re.match(r"[^a-zA-Z]", w):
                continue
            elif w in new_names:
                try:                    
                    if tokenized[tokenized.index(w)+1] in new_names:
                        flag = True
                    if f"{w} {tokenized[tokenized.index(w)+1]}" in new_names:
                        flag = True

                    if f"{tokenized[tokenized.index(w)+1]} {w}" in new_names:
                        clean.pop(-1)
                except IndexError:
                    pass
                clean.append("Artist_name")
            else:
                suggestions = sym_spell.lookup(w, Verbosity.CLOSEST,
                               max_edit_distance=0, include_unknown=True)
                sug = str(suggestions[0])
                sug = sug.split(", ")[0]
                clean.append(sug)
                    
                
        cleaned.append(clean)
        
        #generate pos_list
        if sent_tokenizer == True:
            POS = pos_tag(clean)
            POS_list.append(POS)
            lemmatized = lemmatize_sentence(clean, POS)
            
        else:
            POS_list = pos_tag(clean)
            lemmatize_sentence(clean, POS_list)   
#     sw = set(("be", "I", "this", "the", "it", "a", "and", "to", "you", "of", "do", "in", "my", "me", "that", "with", "for", "have", "on"))
    
    processed = []
    for item in cleaned:
        stop = [l for l in item if l not in sw]
        processed.append(stop)
    if sent_tokenizer == False:
        processed = processed[0]
    
    if return_POS == True:
        return (processed, POS_list)
    else:
        return processed

tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True)

sw = set(stopwords.words('english'))
sw.add("I")

emoji_set = set()
for emoji in UNICODE_EMOJI["en"].keys():
    emoji_set.add(emoji)


sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt")

sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)


if __name__ == "__main__":
    pass
