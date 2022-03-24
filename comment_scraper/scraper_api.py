import argparse,os
import requests
import json
import time
import re

#this is code heavily based on the following with some minor changes:
#https://github.com/ashleve/youtube_multi_video_comment_downloader/blob/master/yt-comment-scraper.py

start_time = time.time()
class YouTubeApi():
    er = 0
    params = {
        'part': 'snippet,replies',
        'maxResults': 100,
        'textFormat': 'plainText'
        }

    YOUTUBE_COMMENTS_URL = 'https://www.googleapis.com/youtube/v3/commentThreads'
    total_comment_counter = 0
    comment_counter = 0
    author_dict = {}
    author_num = 1

    def is_error_response(self, response):
        error = response.get('error')
        if error is None:
            return False
        if error['code'] == 400:
            self.er+=1
            return True
        if error['code'] == 403:            
            print("Quota reached. Writing continuation token to file, try again tomorrow.")
            with open("c_token.txt", "w") as f:
                print(self.params['pageToken'], file=f)
                return True
                
        print("API Error: "
            f"code={error['code']} "
            f"domain={error['errors'][0]['domain']} "
            f"reason={error['errors'][0]['reason']} "
            f"message={error['errors'][0]['message']!r}")
        
        with open('params.txt', "w") as f:
            print(self.params['pageToken'], file=f)
            
        print(self.total_comment_counter)
        
    def format_comments(self, results, likes_required):
        comments_list = []
        for item in results["items"]:
            
            comment = item["snippet"]["topLevelComment"]      
            author = comment['snippet']["authorDisplayName"]     
            text = comment['snippet']["textDisplay"]
            likes = comment['snippet']["likeCount"]
            reply_count = item['snippet']['totalReplyCount']
            date = comment['snippet']['publishedAt']
            
            
            #some logic to anonomise authors of comments to "User n"
            if author not in self.author_dict:
                self.author_dict[author] = self.author_num
                author = f"User {self.author_num}"
                self.author_num+=1
            else:
                author = f"User {self.author_dict[author]}"

            comments_list.append({    #appends comment as a dictionary
                "author" : author,
                "text": text,
                "likes": likes,
                "reply_count": reply_count,
                "date": date
                })
            
            self.total_comment_counter+=1
            self.comment_counter+=1
 
            if 'replies' in item.keys():     #checks if a comment has any replies
                comments_list[-1].update({"replies":[]}) #appends replies to latest entry in comments_list (aka its parent)
                for reply in item['replies']["comments"]:
                    
                    rep_author = reply['snippet']["authorDisplayName"]     
                    rep_text = reply['snippet']["textDisplay"]
                    rep_likes = reply['snippet']["likeCount"]

                    comments_list[-1]['replies'].append({    
                        "author" : rep_author,
                        "text": rep_text,
                        "likes": rep_likes
                        })
                    
                    self.total_comment_counter+=1
                    self.comment_counter+=1
                
        print("Total comments downloaded:", self.total_comment_counter, ". Total 400 errors:", self.er, end="\r")
        return comments_list
    
    def get_video_comments(self, video_id, likes_required, video_name, c_token, key):
        comments_list = []
        self.params.update({"key": key})
        self.params.update({"videoId": video_id})
        
        #clearing key from previous video if downloading comments from multiple videos 
        if 'pageToken' in self.params.keys():
            self.params.pop('pageToken')
            
        if c_token != None:
            self.params.update({'pageToken': c_token})
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        comments_data = requests.get(self.YOUTUBE_COMMENTS_URL, params=self.params, headers=headers)
        results = comments_data.json()
        
        if self.is_error_response(results):
            comments_data = requests.get(self.YOUTUBE_COMMENTS_URL, params=self.params, headers=headers)
            results = comments_data.json()
            if self.is_error_response(results):
                return(comments_list)
        
        nextPageToken = results.get("nextPageToken")
        comments_list += self.format_comments(results, likes_required)

        while nextPageToken:
            self.params.update({'pageToken': nextPageToken})
             
            comments_data = requests.get(self.YOUTUBE_COMMENTS_URL, params=self.params, headers=headers)
            results = comments_data.json()
            
            if self.is_error_response(results):
                comments_data = requests.get(self.YOUTUBE_COMMENTS_URL, params=self.params, headers=headers)
                results = comments_data.json()
                if self.is_error_response(results):
                    return(comments_list)

            
            nextPageToken = results.get("nextPageToken")

            try:
                comments_list += self.format_comments(results, likes_required)

            except KeyError as e:
                print(e)
                with open("c_token.txt", "w") as f:
                    print(self.params['pageToken'], file=f)
                comments_data = requests.get(self.YOUTUBE_COMMENTS_URL, params=self.params, headers=headers)
                results = comments_data.json()                    
                comments_list += self.format_comments(results, likes_required)
                

        print(self.comment_counter, " comments downloaded for", video_name)
        comments_list.append({"total_comments": self.comment_counter})
        self.comment_counter = 0
        return comments_list


    def get_video_id_list(self, filename):
        print(os.listdir("comment_scraper"))
        try:
            with open(f"comment_scraper/{filename}", 'r', encoding="utf8") as file:
                URL_list = file.readlines()
        except FileNotFoundError:
            exit("File \"" + filename + "\" not found")
        urllist = []
        for url in URL_list:
            if url == "\n":     # ignore empty lines
                continue
            if url[-1] == '\n':     # delete '\n' at the end of line
                url = url[:-1]
            url = url.split("|")
            urllist.append(url)
        return urllist


def main():
    yt = YouTubeApi()

    parser = argparse.ArgumentParser(add_help=False, description=("Download youtube comments from many videos into txt file"))
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")
    required.add_argument("--key", '-k', help="Developer API key needed for authentication")
    optional.add_argument("--likes", '-l', help="The amount of likes a comment needs to be saved", type=int)
    optional.add_argument("--input", '-i', help="URL list file name")
    optional.add_argument("--c_token", '-c', help="Continuation token for continuing from where you left off")
    optional.add_argument("--help", '-h', help="Help", action='help')
    args = parser.parse_args()

    # --------------------------------------------------------------------- #



    likes = 0
    if args.likes:
        likes = args.likes

    input_file = "URL_list.txt"
    if args.input:
        input_file = args.input

    if not args.c_token:
        c_token = None

    urllist = yt.get_video_id_list(input_file)

    if not urllist:
        exit("All videos downloaded")
    try:
        while len(urllist) != 0:
            video_id = urllist[0][0]
            video_name = urllist[0][1]
            nvideo_name = video_name.split("-")
           
            new_name = f'{re.sub(" ", "", nvideo_name[0])}_{re.sub(" ", "", nvideo_name[1])}'

            print("Downloading comments for ", new_name)
            comments = yt.get_video_comments(video_id, likes, video_name, c_token, args.key)
            try:
                new_name = f"{new_name}_{comments[-1]['total_comments']}"
            except:
                new_name = f"{new_name}_0"
            if comments:
                with open(f"comment_scraper/comments/{new_name}.json", "w", encoding="utf8") as f:
                    json.dump(comments, f, ensure_ascii=False, indent=4)
                    
                    
            urllist.pop(0)     
            with open(input_file, "w", encoding="utf8") as f:    #removes urls for which the comments have been downloaded
                for item in urllist:
                    print(item[0]+'|'+item[1], file=f)

    except KeyboardInterrupt:
        exit("User Aborted the Operation")

    # --------------------------------------------------------------------- #


if __name__ == '__main__':
    main()
