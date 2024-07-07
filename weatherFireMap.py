import numpy as np
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests
import time
import datetime
from bs4 import BeautifulSoup

ref_points = np.array([[137, 1296],
                      [137, 1319],
                      [137, 1337],
                      [137, 1360],
                      [137, 1385]], dtype=int)

key_points = np.array([[362, 368],
                      [389, 385],
                      [457, 523],
                      [467, 562],
                      [445, 610],
                      [571, 701],
                      [587, 753],
                      [591, 1218],
                      [501, 644]], dtype=int)

def download_image(url, save_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        
        # Open the file in binary mode and write the content
        with open(save_path+'.jpg', 'wb') as file:
            file.write(response.content)
        
        print(f"Image successfully downloaded: {save_path}")
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        print(f"An error occurred: {err}")
        return False

def get_robust_color(img, points, window=3):
    rob_colors = np.zeros((points.shape[0], 3))
    max_height, max_width = img.shape[0], img.shape[1]
    for i, point in enumerate(points):
        ys = np.arange(max([0, point[1]-int(window/2)]), 
                       min([point[1]+int(window/2)+1, max_height - 1]))
        xs = np.arange(max([0, point[0]-int(window/2)]), 
                       min([point[0]+int(window/2)+1, max_width - 1]))
        xv, yv = np.meshgrid(ys, xs)
        rob_color = img[xv.reshape(-1, ), yv.reshape(-1, )].mean(axis=0)
        rob_colors[i] = rob_color
    return rob_colors

def find_closest_rows(n, m):
    distances = np.linalg.norm(n[:, np.newaxis] - m, axis=2)
    closest_indices = np.argmin(distances, axis=1)
    return closest_indices

def write_number_on_image(number, position, font_size=40):
    # font = ImageFont.load_default()
    font = ImageFont.truetype("arialbd.ttf", font_size, encoding="unic")
    draw = ImageDraw.Draw(img)
    draw.text(tuple([position[0] - font_size/2, position[1] - font_size/2]), str(number), font=font, fill=(0, 0, 0))

downloaded = False
day = 1
today_date = str(datetime.date.today() + datetime.timedelta(days=day))
todays_map = today_date[2:].replace('-','')
while(not downloaded):
    html_maps_page = 'https://civilprotection.gov.gr/arxeio-imerision-xartwn'
    html_text = requests.get(html_maps_page).text
    soup = BeautifulSoup(html_text, 'lxml')
    maps = soup.find('div', class_ ="col-6 col-md-4 col-lg-3").find(href=True).get("href")
    img_name = maps.split('/')[-1].split('.')[0]
    url = 'https://civilprotection.gov.gr'+ maps.replace('/','//')
    print(todays_map,img_name)
    if (todays_map in img_name): downloaded = download_image(url, todays_map)
    if(not downloaded): time.sleep(10)

img = Image.open(f'./{todays_map}.jpg').convert('RGB')
img_np = np.asarray(img)

ref_colors = get_robust_color(img_np, ref_points, window=3)
key_colors = get_robust_color(img_np, key_points, window=3)

idxs = find_closest_rows(key_colors, ref_colors)

for i in range(idxs.shape[0]):
    write_number_on_image(idxs[i] + 1, key_points[i], 20)
img.save(todays_map+'.jpg')
img.close()

try:
    from playsound import playsound
    playsound(r'C:\Users\ΓΕΠ\Desktop\Ημερήσιοι Χάρτες Πρόβλεψης Κινδύνου Πυρκαγιάς\files\sound2.mp3')
except:
    print("no sound found")


