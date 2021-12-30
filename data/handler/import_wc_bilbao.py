import xmltodict
import requests
import pymysql.cursors
import os 
db_host=os.getenv("DB_HOST")
db_user=os.getenv("DB_USER")
db_password=os.getenv("DB_PASSWORD")
db_name=os.getenv("DB_NAME")
connection = pymysql.connect(host=db_host,
                 user=db_user,
                 password=db_password,
                 db=db_name,
                 charset='utf8mb4',
                 cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cursor:  
    cursor.execute("CREATE TABLE IF NOT EXISTS `wc_bilbao` ( `id` int NOT NULL AUTO_INCREMENT, `name` text NOT NULL, `lat` float NOT NULL, `lon` float NOT NULL, `source` text NOT NULL,  PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1")
    connection.commit()

with connection.cursor() as cursor:  
    cursor.execute("DELETE FROM `wc_bilbao` WHERE `wc_bilbao`.`source` = 'bilbao.eus'")
    connection.commit()  
    
r = requests.get("https://www.bilbao.eus/Bilbaonet/kml/aseos_publicos.kml")

obj=xmltodict.parse(r.content)
wcs=obj["kml"]["Document"]["Folder"]["Placemark"]
for wc in wcs:
    name= wc["name"]
    coordinates=wc["ExtendedData"]['Data'][1]['value'].split(",")
    lat=coordinates[0]
    lon=coordinates[1]
    with connection.cursor() as cursor:  
        cursor.execute("""insert into wc_bilbao (name, lat, lon,source) VALUES (%s, %s, %s, 'bilbao.eus')""", (name, lat, lon,))
        connection.commit()