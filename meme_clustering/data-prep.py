import json, pickle, random
from tqdm import tqdm

import pandas as pd
from utils.PRSR import prsr
from multiprocessing import Pool

#This is a tool to extract and process comments over a like-threshhold for meme-clustering using POS tags and cosine similarities
#The threshhold for likes has been pre-calculated as 0.026 of the total corpus based off the processing capabilities of my hardware and can be found in the thresh dictionary. 


def process(fn):
    thresh = {'J.Balvin_MiGente_118933_2017_es': 1, 'PSY_GangnamStyle_2993360_2012_ko': 3, 'PSY_Gentleman_524723_2013_ko': 1, 'LuisFonsi_Despacito_1631443_2017_es': 10}
    perc = 0.026
    n = thresh[fn]
    count_target = int(int(fn.split("_")[2])*perc)
    print(fn, count_target)
    count= 0
    the_bin = []

    kw_list = []
    entire_pos_list = []
    author_list = []

    with open (f"comments/{fn}.json", "r", encoding="utf8") as f:
        data = json.load(f)            
    for item in data[:-1]:
        #get tokens and POS tags from PRSR
        if item['likes'] >= n:
            toks, tags = prsr(item['text'], return_POS=True, sent_tokenizer=False)
            if len(tags) > 2:
                kw_list.append(toks)
                entire_pos_list.append(tags)
                author_list.append(item['author'])
                count+=1
        else:
            the_bin.append(item)
        #repeat above steps for replies
        if 'replies' in item:
            for reply in item['replies']:
                if reply['likes']>=n:
                    toks, tags = prsr(reply['text'], return_POS=True, sent_tokenizer=False)
                    if len(tags) > 2:
                        kw_list.append(toks)
                        entire_pos_list.append(tags)
                        author_list.append(reply['author'])
                        
                        count+=1
                else:
                    the_bin.append(reply)
            if count>=count_target:
                break
    #If we have not got enough comments to go past the threshold, fish some comments out the bin  
    repeats = set()
    if count < count_target:
        pbar = tqdm(total=count_target)
        while count <= count_target:
            r = random.randint(0, len(the_bin))
            if r not in repeats:
                item = the_bin[r]
                toks, tags = prsr(item['text'], return_POS=True, sent_tokenizer=False)
                repeats.add(r)
                if len(tags)>2:
                    kw_list.append(toks)
                    entire_pos_list.append(tags)
                    author_list.append(item['author'])
                    count+=1
                    pbar.update(1)
    df = pd.DataFrame(list(zip(kw_list, entire_pos_list, author_list)),
           columns =['KW', 'POS', 'Artist'])
    name = fn.split("_")[1]
    with open (f"saves/memes/raw/{name.lower()}_{count}.pickle", "wb") as f:
        pickle.dump(df, f)



if __name__ == "__main__":
    fn_list = [
        'J.Balvin_MiGente_118933_2017_es',
        'PSY_GangnamStyle_2993360_2012_ko',
        'PSY_Gentleman_524723_2013_ko',
        'LuisFonsi_Despacito_1631443_2017_es'
               ]
    
    pool = Pool(3)
    mapped_values = list(tqdm(pool.imap_unordered(process, fn_list), total=len(fn_list)))

