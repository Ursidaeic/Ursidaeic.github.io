import requests, time, random, json, configparser
from bs4 import BeautifulSoup

def get_chart(url, fromweek, agent):
    

    url = url+fromweek
    
    week_data = {}

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Accept-Language": "en,de;q=0.9,en-US;q=0.8,fr-FR;q=0.7,fr;q=0.6,es;q=0.5",  
        "authority": "acharts.co", 
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": agent
    }   
    
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
 
    e = r.status_code
    if e == 400:
        return 400
    elif e == 404:
        return 404
    elif e == 410:
        return 410
    elif e >= 500:
        return 500
    

    
    week_data.update({fromweek: []})
    
    soup = BeautifulSoup(r.text, 'html.parser')
    charts = soup.find(id='chart_sheet')
    for item in charts.select("td"):
        if item['class'][0] == 'cPrinciple':
            song = item.a.span.get_text()
            e = item.find("span", {"class": "Sub"})
            if e is not None:
                results = e.find_all("span",{"itemprop":"name"})
                artists = [x.text for x in results]
            week_data[fromweek].append((song, artists))
    return(week_data)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    c = config.read('acharts/acharts_config.ini')
    c_args = config['variables']

    if c_args['from_week'] == "today":
        x = time.time() - 604800
        gmweek = time.gmtime(x)

        fromweek = "{}/{}".format(
            time.strftime("%Y", gmweek),
            time.strftime("%U", gmweek)
            )
    else:
        fromweek = c_args['from_week']

    toweek = c_args['to_week']
    output = c_args['output']
    email = c_args['email_address']
    project = c_args['project_title']
    agent = f"{project}. Please contact me at {email} for more information"
    url = c_args['url']
    if url[-1] != "/":
        url = url+"/"
    
    check_r = requests.get(url+toweek)
    if check_r.status_code == 404:
        print("The week you asked to scrape back to is not contained within the Acharts archive")
        exit()
    #-----------------------------------------------------------------------------------#

    #single-digit week numbers are zero padded, thus we need to add them to the list manually
    weeklist = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
    for i in range(10, 53):
        weeklist.append(str(i))
    chart_data = {}

    while toweek != fromweek:
        print("Scraping week of:", fromweek, end="\r")
        week_data = get_chart(url, fromweek, agent)
        chart_data[list(week_data.keys())[0]] = week_data.values()
        if type(week_data) == int:
            if week_data == 400:
                print('Error', week_data, ': the request was not encoded correctly')
            elif week_data == 404:
                print('Error', week_data, ': page not found. Ensure that the information you have supplied is valid and correctly formatted')
            elif week_data == 410:
                print('Error', week_data, ': the page you have requested is missing/no longer exists')
            elif week_data >= 500:
                print('Error', week_data, ': there is a problem with the server')
        else:
            chart_data[list(week_data.keys())[0]] = list(week_data.values())[0]



        splitdate = fromweek.split("/")   #separates supplied date into week and year  
        year = splitdate[0]     
        year = int(year)
        week = splitdate[1]

        w = weeklist.index(week) 

        if w == 0:
            year-=1
            week = weeklist[11]
        else:
            week = weeklist[w-1]

        year = str(year)
        fromweek = year + "/" + week

        with open (f'acharts/chart_data/{output}.json', "w", encoding='utf8') as f:
            json.dump(chart_data, f, ensure_ascii=False, indent=4)


        time.sleep(random.randint(5,10))

    with open (f'acharts/chart_data/{output}.json', "w", encoding='utf8') as f:
        json.dump(chart_data, f, ensure_ascii=False,  indent=4)