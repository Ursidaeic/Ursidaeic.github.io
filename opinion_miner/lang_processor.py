import os, json, re, emoji, pkg_resources
import pycld2 as cld2
import tqdm
from symspellpy import SymSpell, Verbosity
import multiprocessing as mp


def formatter(text):
    for cha in text:
        if cha in bads:
            text = text.replace(cha,'')
    
    text = re.sub(r"http\S*\b", '', text)
    return emoji.get_emoji_regexp().sub(r'', text)

def check_eng(string):
    if len(string) <= 440:
        formatted = formatter(string)
        details = cld2.detect(formatted)
        code = details[2][0][1] 
        if code == "en":
            return True

        if code =="un":
            wds = re.findall(r'\w+', formatted)
            if len(wds) <= 10:
                a = 0
                for word in wds:
                    suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=0)
                    if len(suggestions)!=0:
                        a+=1
                try:
                    perc = ((a/len(wds))*100)
                    if perc >= 50:
                        return True
                except:
                    return False



def process_lang(filename):
    eng_com = []
    count = 0 
    with open(f"opinion_miner/comments/{filename}", "r", encoding="utf8") as f:
        comments = json.load(f)
        
    for item in comments:
        if 'total_comments' not in item:
            if check_eng(item['text']) == True:
                if 'replies' in item:
                    reps = []
                    for reply in item['replies']:
                        if check_eng(reply['text']) == True:
                            reps.append(reply)
                            count+=1
                    item.update({'replies': reps})
                eng_com.append(item)
                count+=1
                
    eng_com.append({'total_comments': count})
    nn = filename.split("_")
    new_name = f"{nn[0]}_{nn[1]}_{eng_com[-1]['total_comments']}"
    with open(f"opinion_miner/english_lang_comments/{new_name}.json", "w", encoding='utf8') as f:
        json.dump(eng_com, f, indent=4)


#variables
#====================================================================#    
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

bads = set()
for i in range(100000):
    try:
        sentence = f"try {chr(i)} it"

        cld2.detect(sentence)
    except:
        bads.add(chr(i))
#====================================================================#
                 
if __name__ == '__main__':
    flist = os.listdir("opinion_miner/comments")
    p = mp.Pool()
    mapped_values = list(tqdm.tqdm(p.imap_unordered(process_lang, flist), total=len(flist)))
    p.close()
    p.join()
        
        
            
    
            
