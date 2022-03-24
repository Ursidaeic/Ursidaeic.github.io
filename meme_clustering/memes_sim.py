import pickle, os, argparse

from tqdm import tqdm
import numpy as np
import pandas as pd


def lcs(POS_tags_list):
    pairs_count = {}
    # Iterate through all POS_tags
    for idx, POS_tags in enumerate(POS_tags_list):
        # Iterate through each consecutive tag pair in a POS_tag
        for tag_idx in range(2, len(POS_tags)):
            # Combining the pair of strings into a single key
            tag_pair = str(POS_tags[tag_idx-2]) + " " + str(POS_tags[tag_idx-1]) + " " + str(POS_tags[tag_idx])
            if tag_pair == "NN NN NN":
                continue
            if tag_pair not in pairs_count:
                pairs_count[tag_pair] = []
            pairs_count[tag_pair].append(idx) 
    
    return pairs_count
    
#function to turn vocab-count vectors into unit vectors as we do not care about their magnitude 
def normalise(A):
    lengths = (A**2).sum(axis=1, keepdims=True)**.5
    lengths = lengths.astype(np.float32)
    return A/lengths


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group("Required arguments")
    required.add_argument("--songname", '-sn', help="The name of the song whose results you wish to process")
    args = parser.parse_args()

    fn = args.songname

    #LOAD DATA
    print("Loading from file")
    for f in os.listdir("memes/raw"):
        if fn in f:
            fn = f



    name = fn.split("_")[0]
    with open (f"memes/raw/{fn}", "rb") as f:
        df = pickle.load(f)
    print("Removing bad data")
    df = [df.iloc[i] for i in range(len(df)) if len(df.iloc[i]['POS']) > 2]
    df = pd.DataFrame(df, columns = ['KW', 'POS'])
    KW = df['KW']
    KW = np.array(KW, dtype=object)
    size = len(KW)

    POS = df['POS']
    POS = [[x[1] for x in P] for P in list(POS)] #get just the POS seqeuence cos atm each entry is a word and a POS tag
    POS = np.array(POS, dtype=object)

    print("Comments to compare:", size)

    print("Creating count matrix")
    vocab = set()
    for comment in KW:
        for keyword in comment:
            vocab.add(keyword)
    vocab=list(vocab)
    vocab = np.array(vocab, dtype=str)
    
    count_matrix = np.zeros((size, vocab.size), dtype=np.int8)
    for i in tqdm(range(size)):
        for keyword in KW[i]:
            vocab_index = np.where(vocab==keyword)[0][0]
            count_matrix[i][vocab_index]=KW[i].count(keyword)

    count_matrix = normalise(count_matrix)


    #calculate cosine
    
    rows_in_slice = 100
    slice_start = 0
    slice_end = slice_start + rows_in_slice

    pbar = tqdm(total=int(size/rows_in_slice))
    #based on code from https://www.py4u.net/discuss/208543
    while slice_end <= count_matrix.shape[0]:
        cosine_matrix = count_matrix[slice_start:slice_end].dot(count_matrix.T)
        cos = np.transpose(np.nonzero(cosine_matrix))
        cosine_matrix = (np.argwhere(cosine_matrix >= 0.5))

        slice_start += rows_in_slice
        slice_end = slice_start + rows_in_slice
        with open (f"memes/raw_processed/{name}_cosines.pickle", "ab+") as f:
            pickle.dump(cosine_matrix, f)
        pbar.update(1)



    print("Calculating LCS results")
    lcs_result = lcs(POS)
    with open (f"memes/raw_processed/{name}_POS.pickle", "wb") as f:
        pickle.dump(lcs_result, f)


