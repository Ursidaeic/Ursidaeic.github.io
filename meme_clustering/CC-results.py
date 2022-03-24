import numpy as np
import pickle, argparse
from tqdm import tqdm
from pprint import pprint


def sort_by_values_len(dict):
    dict_len= {key: len(value) for key, value in dict.items()}
    import operator
    sorted_key_list = sorted(dict_len.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict = [{item[0]: dict[item [0]]} for item in sorted_key_list]
    return sorted_dict

def process_results(fn):
    chunk_iter = 0
    cossim = []
    with open (f"memes/raw_processed/{fn}_cosines.pickle", "rb") as f:
        while True:
            try:
                chunk = pickle.load(f)
                for x in range(chunk.shape[0]):
                    chunk[x][0]+=chunk_iter
                cossim.append(chunk)
                chunk_iter+=100
            except EOFError:
                break
    cossim = np.array(cossim, dtype=object)
    cossim=np.concatenate(cossim)

    with open (f"memes/raw_processed/{fn}_POS.pickle", "rb") as f:
        POS_dict = pickle.load(f)
    # for k, v in POS_dict.items():
    #     POS_dict[k] = set(v)

    inverted_pos = {}
    for k,values in POS_dict.items():
        for v in values:
            if v not in inverted_pos:
                inverted_pos[v] = set()
            inverted_pos[v].add(k)

    goods = []
    ke = set()
    for pair in tqdm(range(cossim.shape[0])):
        a = cossim[pair][0]
        b = cossim[pair][1]
        try:
            a_ip = inverted_pos[a]
        except KeyError:
            ke.add(a)
            continue
        
        try:
            b_ip = inverted_pos[b]
        except KeyError:
            ke.add(b)
            continue
        
        if len(inverted_pos[a].intersection(inverted_pos[b]))!=0 and b!=a:
            goods.append(tuple(cossim[pair]))

    print(sorted(list(ke)))
    goods = np.array(goods)
    print(goods.shape)
    with open (f"memes/results/{fn}.pickle", "wb") as f:
        pickle.dump(goods, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group("Required arguments")
    required.add_argument("--songname", '-sn', help="The name of the song whose results you wish to process")
    args = parser.parse_args()

    fn = args.songname
    process_results(fn)