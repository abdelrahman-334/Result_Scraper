import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/71.0.3578.98 Safari/537.36'
}

URL = "https://g12.emis.gov.eg/"
STUDENT_RESULTS = []


def scrape_movie_data(movie_link):
    response = requests.get(url=movie_link, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        title = soup.find('span', class_='hero__primary-text', attrs={'data-testid': 'hero__primary-text'}).text
    except:
        print("couldnt find title")
    try:
        rating = soup.find('span', class_='sc-bde20123-1 cMEQkK').text
    except:
        print("couldnt find rating")

    try:
        genre_div = soup.find('div', {'class': 'ipc-chip-list__scroller'})
        genres = [chip.find('span', {'class': 'ipc-chip__text'}).get_text() for chip in genre_div.find_all('a')]
    except:
        print("couldnt find genre")

    try:
        year_div = soup.find('div', class_="sc-b7c53eda-0 dUpRPQ")
        year_link = year_div.find('a', class_="ipc-link ipc-link--baseAlt ipc-link--inherit-color")
        year = year_link.text
    except:
        print("couldnt find year")

    try:
        directors_ul = soup.select_one('span:-soup-contains("Directors") + div ul').find_all('li')
        directors = [director.text for director in directors_ul]
    except:
        directors = [soup.find('a', class_="ipc-metadata-list-item__list-content-item "
                                           "ipc-metadata-list-item__list-content-item--link").text]


    try:
        cast_links = soup.find_all('a', {'data-testid': 'title-cast-item__actor'})
        cast = [actor.get_text() for actor in cast_links]
    except:
        print("couldnt find cast members")

    first_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.ipc-lockup-overlay.ipc-focusable'))
    )

    first_link.click()
    link_for_img = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="mv-gallery-button"]').get_attribute('href')


    second_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-testid="mv-gallery-button"]'))
    )

    second_link.click()
    response = requests.get(url=f'{link_for_img}', headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    img_src = soup.find('img', class_='poster').get('src')

    movie_data = {
        "title": title,
        "rating": rating,
        "genres": genres,
        "release_year": year,
        "director(s)": directors,
        "cast": cast,
        "image": img_src
    }

    return movie_data


def scrape_student_results():
    df = pd.read_html(driver.page_source)[0]
    df.columns = ['Date', 'Value']
    return df


chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    driver.get(URL)

    for i in range(102000, 990100):
        driver.find_element(By.CLASS_NAME, 'form-control').send_keys(str(i))
        time.sleep(0.25)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        Current_Student_Data = scrape_student_results()
        print(Current_Student_Data)
        STUDENT_RESULTS.append(Current_Student_Data)
        time.sleep(0.25)

        driver.back()

except Exception as e:
    print(f'Error has occurred: {e}')

finally:
    df = pd.concat(STUDENT_RESULTS)
    df.to_csv("Student_Results_2024.csv")
    driver.quit()