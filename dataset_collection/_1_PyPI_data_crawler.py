import requests
from bs4 import BeautifulSoup
import pandas as pd



def spider_package_info(url_1):
    res = requests.get(url_1)
    content = res.text
    soup = BeautifulSoup(content, "html.parser")
    All_package_info = soup.find('main',{"id":"content"}).find('form',{"action":"/search/"}).find('ul',attrs={"class":"unstyled"}).findAll('li')

    list_1 = []
    for i in range(len(All_package_info)):

        package_info = All_package_info[i]
        package_name_bef = package_info.find('a',{'class':'package-snippet'}).find('h3',{'class':'package-snippet__title'}).find('span',{'class':'package-snippet__name'}).text
        package_name_version = package_info.find('a',{'class':'package-snippet'}).find('h3',{'class':'package-snippet__title'}).find('span',{'class':'package-snippet__version'}).text

        package_name = package_name_bef + package_name_version
        package_href = 'https://pypi.org' + package_info.find('a',{'class':'package-snippet'}).get('href')
        package_des = package_info.find('p').text

        list_1.append((package_name,package_des,package_href))

    return list_1

def spider_history_info(url_2):
    res = requests.get(url_2)
    content = res.text
    soup = BeautifulSoup(content, "html.parser")
    all_his = soup.find('div',{"id":"history"}).find('div',attrs={"class":"release-timeline"}).find_all('div',attrs={"class":"release"})
    list_info = []

    for i in range(len(all_his)):
        release_version_bef = all_his[i].find('a').find('p',attrs={"class":"release__version"}).text.strip()

        release_version = ''.join([i.strip(' ') for i in release_version_bef])
        release_time = all_his[i].find('a').find('time')['datetime'].split('T')[0]

        list_info.append((release_version, release_time))

    github_href = ""

    if soup.find('div', attrs={"class": "vertical-tabs__tabs"}).findAll('div', attrs={"class": "sidebar-section"}) is not None:
        github_info = soup.find('div', attrs={"class": "vertical-tabs__tabs"}).findAll('div', attrs={"class": "sidebar-section"})
        for n in range(len(github_info)):
            https = github_info[n].findAll('a')
            for m in range(len(https)):
                if "github.com" in https[m]['href'] and github_href == "":
                    github_href = https[m]['href'].split(".com")[1]
                    break
            else:
                continue
            break
    if github_href != "":
        new_url_stars = "https://img.shields.io/github/stars" + github_href + "?style=social"
        res_2 = requests.get(new_url_stars)
        content_2 = res_2.text
        soup = BeautifulSoup(content_2, "html.parser")
        stars = soup.find('text',{"id":"rlink"}).text

        new_url_forks = "https://img.shields.io/github/forks" + github_href + "?style=social"
        res_3 = requests.get(new_url_forks)
        content_3 = res_3.text
        soup = BeautifulSoup(content_3, "html.parser")
        forks = soup.find('text',{"id":"rlink"}).text

        new_url_issues = "https://img.shields.io/github/issues" + github_href + "?style=social"
        res_4 = requests.get(new_url_issues)
        content_4 = res_4.text
        soup = BeautifulSoup(content_4, "html.parser")
        issues = soup.find('text',{"id":"rlink"}).text.replace(" open",'')

    else:
        stars = ""
        forks = ""
        issues = ""

    return list_info, stars, forks, issues

def spider_files_info(url_3):
    res = requests.get(url_3)
    content = res.text
    soup = BeautifulSoup(content, "html.parser")
    file_href = soup.find('div',{"class":"file"}).find('div',{"class":"card file__card"}).find('a')['href']
    return file_href

if __name__ == '__main__':
    out = []
    for i in range(500):
        print("pages", i+1)
        page_url = 'https://pypi.org/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3&o=-created&q=&page=' + str(i+1)

        list_1 = spider_package_info(page_url)
        print(list_1)


        for j in range(len(list_1)):
            try:
                print("items", (j+1) + (i)*20)
                task = {"package_name":None,"package_des":None,"package_href":None,"stars":None,"forks":None,"issues":None,"release_info":None,"file_href":None}
                task['package_name'] = list_1[j][0]
                task['package_des'] = list_1[j][1]
                task['package_href'] = list_1[j][2]

                list_2, stars, forks, issues = spider_history_info(list_1[j][2]+ '#history')

                task['stars'] = stars
                task['forks'] = forks
                task['issues'] = issues
                task['release_info'] = list_2

                file_href = spider_files_info(list_1[j][2]+ '#files')
                task['file_href'] = file_href

                out.append(task)

            except Exception as e:
                print(e)

            df = pd.DataFrame(out)
            df.to_csv('./code_repos.csv',index=False)