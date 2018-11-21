import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime
import re
import pandas as pd
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class Parser(object):

    '''
    App: Creates a webscraper for https://inkphy.com/, a webpage using Instagram API.
    Args:
    - insta_user (type=string): Username in instagram. E.g. insta_user = velvetoak --- in https://www.instagram.com/velvetoak/
    - main_directory (type=string): Path in PC to which csv and images will be saved
    Callable Methods:
    - to_csv()
    Background Methods:
    - current_date()
    - parse_posts()
    - get_noPages()
    - download_img()
    '''


    def __init__(self, insta_user,main_directory,sleep_time):
        #Hardcoded web url
        self.url = "https://inkphy.com/"
        #Name of user in instagram
        self.insta_user = insta_user
        #Generates route for each user: E.g. https://inkphy.com/user/sexyrevolver
        self.profile_url = self.url + '/' + self.insta_user
        #Home url -used for building dynamic image urls
        self.generic_url = "https://inkphy.com"
        #Main directory in PC where output files (csv and photos) will be saved. E.g. C:\Imagenes\
        self.main_directory = main_directory
        self.counter = 1
        self.sleep_time = sleep_time


    def download_img(self,link,root_dir,directory,img_code):

        '''
        App: Downloads images from http link (E.g.
        https://scontent.cdninstagram.com/t51.2885-15/s640x640/sh0.08/e35/23280180_130199887607263_396194665583345664_n.jpg)
        to a specific route in PC directory
        Args:
        - link: Image link
        - root_dir: Root dir. E.g. C:\SocialAnalytics
        - directory: Name of parsed page (type=string). E.g. sexyrevolver
        - img_code: Image identifier (type=string). E.g. While parsing each post, each image will be named after the number of each
                    iteration, for instance, the first downloaded image will be named "1.jpg"
        Output: Downloaded Image to specified directory
        '''
        imgs_directory = directory + "FOTOS"

        #Path of directory where images will be saved
        path = "{}\\Instagram\\{}\\{}".format(root_dir,directory,imgs_directory)

        #Creates path if it doesn't exists
        if not os.path.exists(path):
            os.makedirs(path)

        #Img link
        url = link
        #gets http data
        response = requests.get(url)
        #If something is returned after http GET, download image
        if response.status_code == 200:
            with open("{}\\{}.jpg".format(path,img_code), 'wb') as f:
                f.write(response.content)

    @staticmethod
    def get_noPages(posts_amount):

        '''
        App: Gets number of pages to display (each containing 12 posts before continue button)
             needed according to the amount of posts requested.
        Args:
        - posts_amount (int): number of posts that need to be parsed
        Output: E.g. 3
        '''

        integer = int(posts_amount/12)

        if integer == 0:
            return 1
        elif posts_amount%12 == 0:
            return integer
        else:
            return integer + 1

    def parse_posts(self,posts_amount):

        #Headless configuration for Chrome webdriver
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)

        #Times the next button has to be clicked
        pages_to_parse = self.get_noPages(posts_amount)

        data = []
        img_code = 1

        #Connects to webpage and fetches page source
        driver.get(self.profile_url)

        #Clicks next button the number of times set in posts_amount
        for i in range(1,pages_to_parse+1):
            time.sleep(self.sleep_time)
            try:
                siguiente = driver.find_element_by_xpath('//*[@id="click4more"]')
                #siguiente  = WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="click4more"]')))
                siguiente.click()                
            except:
                break


        webpage = driver.page_source
        #Creates BeautifulSoup object
        soup = BeautifulSoup(webpage,'html.parser')
        #finds all divs that contain images, post text, comments, likes and publishing time
        the_divs = soup.findAll('div',{'class':'item'})

        #loops within each div and searches the tags containing images, post text, comments, likes and publishing time
        for div in the_divs:
            #If img code (# of iteration) <= to posts amount, keep fetching data; else, break loop
            if img_code <= posts_amount:
                #Contains images url
                img_attr = div.find('a',{'class':'mask'})
                #Converts img code (originally int) into string
                str_img_code = str(img_code)
                #While parsing the page source, some blank advertising divs may break the code, so this line checks if <a href>
                #containing the img url exists and downloads image; else continue to next iteration
                if img_attr:
                    img = re.findall('[htps]{5}.+\.jpg',img_attr['style'])[0]
                    self.download_img(link=img,root_dir=self.main_directory,directory=self.insta_user,img_code=str_img_code)
                else:
                    continue
                #Contains post text
                post_text = div.find('p',{'class':'caption'}).text
                #Contains # of comments
                comments = div.find('span',{'class':'comments'}).text
                #Contains # of likes
                likes = div.find('span',{'class':'likes'}).text
                #Contains time of post
                hour = div.find('span',{'class':'created_time'}).text

                str_img_code = str(img_code)

                #Creates tuple for list
                complete_data = (str_img_code,post_text,comments,likes,hour)
                #Appends to data empty list
                data.append(complete_data)

                img_code += 1
            else:
                break


        return data



    @staticmethod
    def current_date():

        '''
        App: Gets current date.
        Args: None
        Output: 2017-09-08 18:10
        '''

        today = datetime.datetime.now()
        return today.strftime("%Y-%m-%d--%H:%M")


    def to_csv(self,number_posts):

        '''
        App: Converts list to pandas dataframe and then converts it to csv.
        Args:
        - data_list: A list of tuples
        - root_dir: Root dir. E.g. C:\\SocialAnalytics
        - filename = filename
        Output: .csv file
        '''

        #Dir config
        root_dir = self.main_directory
        directory = self.insta_user
        filename = self.insta_user
        #Number of posts config
        data_list = self.parse_posts(number_posts)
        #Columns names
        labels = ['ID','Post','# Comentarios','# Likes','Fecha de Publicación']
        #Converts list to pandas dataframe
        df = pd.DataFrame.from_records(data_list, columns=labels)
        #Creates full path
        file = filename + '.csv'
        path = "{}\\Instagram\\{}\\{}".format(root_dir,directory,file)
        #Converts dataframe to .csv file
        df.to_csv(path,index=False)
        return "Done"
