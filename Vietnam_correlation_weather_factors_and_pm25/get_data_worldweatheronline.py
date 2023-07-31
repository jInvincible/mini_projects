# import libraries
import bs4
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import sys 

# define URL
area = 'hai-phong'

# Done: 'bac-giang', 'ho-chi-minh-city', 'ha-noi', 'binh-dinh', 'lang-son', 'Ha-Tinh', 'Bac-Lieu', 'Ben-Tre', 'Rach-Gia', 'Soc-Trang', 'Tra-Vinh', 'Vinh-Long', 'Long-Xuyen', 'Vung-Tau', 'Bien-Hoa', 'Ca-Mau', 'Can-Tho', 'Chau-Doc', 'Da-Lat', 'Dien-Bien', 'Bac-Giang', 'Cao-Bang', 'Dong-Hoi', 'Ha-Giang', 'Hai-Duong', 'Lao-Cai', 'My-Tho', 'Nam-Dinh', 'Nha-Trang', 'Ninh-Binh', 'Phan-Rang', 'Phan-Thiet', 'Son-Tay', 'Tam-Ky', 'Tan-An', 'Tay-Ninh', 'Thai-Binh', 'Thai-Nguyen', 'Thanh-Hoa', 'Tuy-Hoa', 'Tuyen-Quang', 'Uong-Bi', 'Viet-Tri', 'Vinh', 'Yen-Bai', 'Bac-Ninh', 'Buon-Me-Thuot', 'Cam-Pha', 'Cam-Ranh', 'Hoa-Binh', 'Hoi-An', 'Hong-Gai', 'Hue', 'Kon-Tum', 'Phu-Ly', 'Play-Cu', 'Quang-Ngai', 'Qui-Nhon'

# Pending: 

url = f'https://www.worldweatheronline.com/{area}-weather-history/vn.aspx'

# load dates table
dates =  pd.read_csv('dates_01012011_03312023.csv')
dd_list = dates['Day']
mm_list = dates['Month']
yyyy_list = dates['Year']


# function get data
def get_data(df_csv):
    # get page source (HTML)
    r = driver.page_source

    # parse HTML Code
    soup = bs4.BeautifulSoup(r, 'html.parser')
    
    # find table of page
    section = bs4.BeautifulSoup(str(soup.find_all("section")), 'html.parser')

    table = section.find_all(name='table', attrs={"class":"days-details-table"})

    # find all trs tag (AKA rows) of above table
    rows_tr = table[0].find_all(name='tr')

    df_data = pd.DataFrame(None)
    df_col_name = ["Time", "Forecast", "Rain", "Rain %", "Cloud", "Pressure", "Wind", "Gust", "Dir"]

    temp_data = []
    # get data from each tr (AKA row)
    for row in rows_tr[2:]:
        row_data = []
        for cell in row.find_all('td'):
            if cell.text.strip() != '':
                if re.match(pattern='[\d]{2}:[\d]{2}', string=cell.text.strip()) == None:
                    row_data.append(cell.text.strip())
                else:
                    times = cell.text.strip()[0:5]
                    temperature = cell.text.strip()[5:-1]
                    row_data.append(f'{times} {temperature}')
            elif cell.find('img') != None:
                row_data.append(cell.find('img').attrs['alt'])
        temp_data.append(row_data)
    df_row = pd.DataFrame(temp_data)
    df_data = pd.concat([df_data, df_row])
    df_data

    # correct columns name and add column Date with date_value
    df_data.columns = df_col_name
    date_value = f'{mm}/{dd}/{yyyy}'
    df_data['Date'] = date_value
    df_data['Area'] = area
    print(df_data)
    df_csv = pd.concat([df_csv, df_data])  
    return df_csv

# function input_date and get data
def input_date_get_data(mm, dd, yyyy, df_csv):
    
    ele_input = driver.find_element(by=By.ID, value='ctl00_MainContentHolder_txtPastDate')
    ele_input.clear()
    ele_input.send_keys(mm)
    sleep(0.5)
    ele_input.send_keys(dd)
    sleep(0.5)
    ele_input.send_keys(yyyy)
    # check if send_keys input_value work properly
    count = 1
    input_value = f'{yyyy}-{mm}-{dd}'
    # retry inputing 10 times
    while count < 11 and ele_input.get_attribute("value") != input_value:
        try:
            ele_ad_close = driver.find_element(by=By.CLASS_NAME, value='ad-close bold')
            ele_ad_close.click()
        except:
            pass
        
        finally:
            ele_input.clear()
            ele_input.send_keys(mm)
            sleep(0.5)
            ele_input.send_keys(dd)
            sleep(0.5)
            ele_input.send_keys(yyyy)
            count = count + 1
        
    try:
        ele_ad_close = driver.find_element(by=By.CLASS_NAME, value='ad-close bold')
        ele_ad_close.click()
        sleep(0.5)
        driver.find_element(by=By.ID, value="ctl00_MainContentHolder_butShowPastWeather").click()
        
    except:        
        driver.find_element(by=By.ID, value="ctl00_MainContentHolder_butShowPastWeather").click()

    # check if new page with new date is loaded completely
    count = 0 # timeout
    while (driver.find_element(by=By.NAME, value=f'{yyyy}{mm}{dd}').get_attribute('name') != f'{yyyy}{mm}{dd}'):
        print(driver.find_element(by=By.NAME, value=f'{yyyy}{mm}{dd}').get_attribute('name'))
        sleep(1)
        count = count + 1
        # exit if timeout 15s
        if count == 15: 
            exit()
            
    df_csv = get_data(df_csv)
    return df_csv
    
# Main
# open browser and navigate to URL
driver = webdriver.Chrome()
driver.get(url)
print(driver.session_id)
# driver.implicitly_wait(5)

# get data by dates list
df_csv = pd.DataFrame(None)
#start = 0 # main loops start at this index in dates list, can start over where we left from last run or from the begining (zero)
with open('current_index.txt') as f:
        start = int(f.readline())
end = 4472 # loops end at this index in dates list
try:
    for i in range(start, len(yyyy_list)):
        if mm_list[i] < 10:
            mm = '0'+ str(mm_list[i])
        else:
            mm = str(mm_list[i])
        if dd_list[i] < 10:
            dd = '0' + str(dd_list[i])
        else:
            dd = str(dd_list[i])
        yyyy = str(yyyy_list[i])
        print(f'trying ... index {i}.. area: {area}, Dates: {mm}/{dd}/{yyyy}')
        df_csv = input_date_get_data(mm, dd, yyyy, df_csv)
        if i == end-1: # loop stopped at (end - 1)
            break           

except Exception:
    error_shot = f'C:\\Users\\Nam Invincible\\PycharmProjects\\Group7-mini-project\\functions\\{area}_{mm_list[i]}{dd_list[i]}{yyyy_list[i]}_error_at_{i}.png'
    driver.save_screenshot(error_shot)
    print(f'[error] detail at: {error_shot}')
    print(sys.exc_info())
    sleep(1)
    driver.quit()
    
finally:
    print(f'stopped at {i}, {area}_{mm_list[i]}{dd_list[i]}{yyyy_list[i]}')   
    if i == len(yyyy_list)-1:
            driver.save_screenshot(f'C:\\Users\\Nam Invincible\\PycharmProjects\\Group7-mini-project\\functions\\{area}_{mm_list[i]}{dd_list[i]}{yyyy_list[i]}_DONE.png')
            with open('current_index.txt', 'w') as f:
                f.write('0')
    else:
        with open('current_index.txt', 'w') as f:
            f.write(str(i))
            
    file_name = f'{area}_weather_{mm_list[start]}{dd_list[start]}{yyyy_list[start]}_{mm_list[i]}{dd_list[i]}{yyyy_list[i]}_{i}.csv'
    
        
    df_csv.to_csv(file_name)
    print(f'exported to {file_name}')        
    driver.quit()
    