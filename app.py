from module.scraper import Parser

#Config
profile = 'melissagomezmx'
path = "C:\\Users\\gwall\\Documents\\Python\\InstagramParser\\InstagramParsedData"
number_posts = 100
sleep_time = 8


#Class instance
test = Parser(profile,path,sleep_time)

#Parse and generate csv
test.to_csv(number_posts)
