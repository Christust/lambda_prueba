import json
# Selenium imports
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

# Normal imports
import requests
import os
import re
import csv
import time

def lambda_handler(event, context):
    # event = {code, price, discount, price_with_discount}
    # Crear directorio para guardar archivos
    path = os.getcwd()
    path = os.path.join(path, 'products_truper_test')

    # Crear driver para scraping
    driver = webdriver.Chrome()

    # Creacion de csv
    with open(os.path.join(path, 'products_truper_sheet.csv'), 'w', encoding='UTF8') as f:
        # Iniciar escritura de archivo csv
        writer = csv.writer(f)

        # Colocar headers
        writer.writerow(['code', 'key', 'title', 'description', 'sheet'])

    product_codes = [
        40732, 40730, 40733, 40731, 40737, 40736, 40735, 40734, 49222, 40722, 40721, 40720, 40719, 40718, 40717, 40716, 40729, 40728, 40727, 40726, 40725, 40724, 40723, 48377, 48398, 48399, 46907, 46908, 46581, 46584, 46582, 46585, 46583, 46586, 102885, 102989, 103060, 102774, 102775, 102776, 102777, 102778, 102779, 102790, 102791, 102873, 102970, 40740, 40741, 40738, 40739, 40245
    ]

    ## BUSQUEDA POR CATALOGO (Encuentra pocos)
    # Productos no encontrados
    products_not_exists = []

    # Contar cuantos codigos son
    products_count = len(product_codes)

    # Abrir archivo csv
    with open(os.path.join(path, 'products_truper_sheet.csv'), 'a', encoding='UTF8') as f:
        # Iniciar escritura de archivo csv
        writer = csv.writer(f)

        for n in range(0, products_count):
            code = product_codes[n]
            if code not in []:
                driver.get("https://www.truper.com/catalogsearch/result/?q=" + str(code))

                try:
                    # driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[contains(@class, 'CatVigenteIframe')]"))
                    # product_exists = driver.find_element(By.XPATH, "//tbody").text
                    driver.find_element(By.XPATH, "//div[contains(@class, 'category-products')]")
                    product_exists = driver.find_element(By.XPATH, "//div[contains(@class, 'category-products')]/ul/li").text
                except NoSuchElementException:
                    product_exists = ""

                if product_exists != "":
                    # url = driver.find_element(By.XPATH, "//ul[contains(@class, 'products-grid')]/li/a").get_attribute('href')
                    # url = driver.find_element(By.XPATH, "//td/a[contains(@class, 'ficha-pdf')]").get_attribute('href')
                    url = driver.find_element(By.XPATH, "//div[contains(@class, 'category-products')]/ul/li/a").get_attribute('href')
                    driver.get(url)
                    time.sleep(3)

                    # Validar si hay select
                    try:
                        select_element = driver.find_element(By.XPATH, "//select[contains(@class, 'required-entry')]")
                        # select_element = driver.find_element(By.XPATH, "//select[contains(@id, 'sons')]")
                    except NoSuchElementException:
                        select_element = None

                    if select_element != None:
                        # Existe select, recorrer opciones
                        select = Select(select_element)
                        for n in range(1, len(select.options)):
                            select.select_by_index(n)
                            time.sleep(3)
                            prod_code = select.first_selected_option.text.split(" - ")[0]
                            if prod_code == str(code):
                                key = select.first_selected_option.text.split(" - ")[1]

                                # title = driver.find_element(By.XPATH, "//h1").text
                                try:
                                    title = driver.find_element(By.XPATH, "//div[contains(@class, 'product-name')]/span").text
                                except NoSuchElementException:
                                    title = ""

                                try:
                                    # description = driver.find_element(By.XPATH, "//section[contains(@id, 'caracteristicas')]/div/ul").text
                                    description = driver.find_element(By.XPATH, "//div[contains(@class, 'short-description')]").text
                                except NoSuchElementException:
                                    description = ""

                                    # sheet = driver.find_element(By.XPATH, "//div[contains(@class, 'ver-ficha-tecnica')]/a").get_attribute("href")
                                try:
                                    sheet = driver.find_element(By.XPATH, "//ul[contains(@class, 'descargables-list')]/li/a").get_attribute("href")
                                except NoSuchElementException:
                                    sheet = ""

                                try:
                                    image = driver.find_element(By.XPATH, "//img[contains(@id, 'image-main')]").get_attribute("src")
                                except NoSuchElementException:
                                    image = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, "//div[@class='zoomWindowContainer']/div"))
                                    )
                                    image = image.get_attribute("style")
                                    image = re.search('url\("(.+)"\)', image).group(1)

                                # Descargar imagen
                                with open(os.path.join(path, str(prod_code)) + '.jpg', 'wb') as handle:
                                    response = requests.get(image, stream=True)
                                    if not response.ok:
                                        print(response)
                                    for block in response.iter_content(1024):
                                        if not block:
                                            break
                                        handle.write(block)

                                # Escribir renglon de datos
                                writer.writerow([prod_code, key, title, description, sheet])
                    else:
                        time.sleep(3)
                        try:
                            # prod_code = driver.find_element(By.XPATH, "//div[contains(@id, 'info')]/div[contains(@class, 'code-label')]").text
                            # prod_code = prod_code.split(': ')[1]
                            prod_code = driver.find_element(By.XPATH, "//div[contains(@class, 'clave-sku')]/p[1]").text
                            prod_code = prod_code.split(':   ')[1]
                        except NoSuchElementException:
                            # prod_code = driver.find_elements(By.XPATH, "//div[contains(@class, 'columna-2')]/section[contains(@class, 'producto')]/div[contains(@class, 'codigo')]/div/p")[0].text
                            prod_code = ""

                        try:
                            # key = driver.find_element(By.XPATH, "//div[contains(@id, 'info')]/div[contains(@class, 'sku-label')]").text
                            # key = key.split(': ')[1]
                            key = driver.find_element(By.XPATH, "//div[contains(@class, 'clave-sku')]/p[2]").text
                            key = key.split(':   ')[1]
                        except NoSuchElementException:
                            # key = driver.find_elements(By.XPATH, "//div[contains(@class, 'columna-2')]/section[contains(@class, 'producto')]/div[contains(@class, 'codigo')]/div/p")[1].text
                            key = ""

                        try:
                            # title = driver.find_element(By.XPATH, "//div[contains(@class, 'columna-2')]/section[contains(@class, 'producto')]/div[contains(@class, 'titulo-producto')]/h1").text
                            title = driver.find_element(By.XPATH, "//div[contains(@class, 'product-name')]/span").text
                        except NoSuchElementException:
                            # title = driver.find_element(By.XPATH, "//h1").text
                            title = ""

                        try:
                            # description = driver.find_element(By.XPATH, "//div[contains(@class, 'columna-2')]/section[contains(@id, 'caracteristicas')]/div/ul").text
                            description = driver.find_element(By.XPATH, "//div[contains(@class, 'short-description')]").text
                        except NoSuchElementException:
                            # try:
                            # description = driver.find_element(By.XPATH, "//section[contains(@id, 'caracteristicas')]/div/ul").text
                            # except NoSuchElementException:
                            # description = ""
                            description = ""
                        
                        try:
                            # sheet = driver.find_element(By.XPATH, "//div[contains(@class, 'columna-1')]/section[contains(@id, 'descargables')]/div/ul/li/a").get_attribute("href")
                            sheet = driver.find_element(By.XPATH, "//ul[contains(@class, 'descargables-list')]/li/a").get_attribute("href")
                        except NoSuchElementException:
                            # sheet = driver.find_element(By.XPATH, "//div[contains(@class, 'ver-ficha-tecnica')]/a").get_attribute("href")
                            sheet = ""

                        try:
                            # image = driver.find_element(By.XPATH, "//img[contains(@class, 'img-responsive')]").get_attribute("src")
                            image = driver.find_element(By.XPATH, "//img[contains(@id, 'image-main')]").get_attribute("src")
                        except NoSuchElementException:
                            image = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@class='zoomWindowContainer']/div"))
                            )
                            image = image.get_attribute("style")
                            image = re.search('url\("(.+)"\)', image).group(1)

                        # Descargar imagen
                        with open(os.path.join(path, str(prod_code)) + '.jpg', 'wb') as handle:
                            response = requests.get(image, stream=True)
                            if not response.ok:
                                print(response)
                            for block in response.iter_content(1024):
                                if not block:
                                    break
                                handle.write(block)

                        # Escribir renglon de datos
                        writer.writerow([prod_code, key, title, description, sheet])
                else:
                    products_not_exists.append(code)

    # Mostrar productos no encontrados
    products_not_exists

    ## BUSQUEDA POR FICHA TECNICA (Encuentra mas)
    # Productos no encontrados
    products_not_exists = []

    # Contar cuantos codigos son
    products_count = len(product_codes)

    # Abrir archivo csv
    with open(os.path.join(path, 'products_truper_sheet.csv'), 'a', encoding='UTF8') as f:
        # Iniciar escritura de archivo csv
        writer = csv.writer(f)

        for n in range(0, products_count):
            code = product_codes[n]
            if code not in []:
                driver.get("https://www.truper.com/ficha_tecnica/controllers/index.php?codigo=" + str(code))
                time.sleep(3)

                # Validar si hay select
                try:
                    select_element = driver.find_element(By.XPATH, "//select[contains(@id, 'sons')]")
                except NoSuchElementException:
                    select_element = None

                if select_element != None:
                    # Existe select, recorrer opciones
                    select = Select(select_element)
                    for n in range(1, len(select.options)):
                        select.select_by_index(n)
                        time.sleep(3)
                        prod_code = select.first_selected_option.text.split(" - ")[0]
                        if prod_code == str(code):
                            key = select.first_selected_option.text.split(" - ")[1]

                            try:
                                title = driver.find_element(By.XPATH, "//h1").text
                            except NoSuchElementException:
                                title = ""

                            try:
                                description = driver.find_element(By.XPATH, "//section[contains(@id, 'caracteristicas')]/div/ul").text
                            except NoSuchElementException:
                                description = ""

                            try:
                                sheet = driver.find_element(By.XPATH, "//div[contains(@class, 'ver-ficha-tecnica')]/a").get_attribute("href")
                            except NoSuchElementException:
                                sheet = ""

                            try:
                                image = driver.find_element(By.XPATH, "//img[contains(@class, 'img-responsive')]").get_attribute("src")
                            except NoSuchElementException:
                                image = ""

                            # Descargar imagen
                            with open(os.path.join(path, str(prod_code)) + '.jpg', 'wb') as handle:
                                response = requests.get(image, stream=True)
                                if not response.ok:
                                    print(response)
                                for block in response.iter_content(1024):
                                    if not block:
                                        break
                                    handle.write(block)

                            # Escribir renglon de datos
                            writer.writerow([prod_code, key, title, description, sheet])
                else:
                    # No existe selector
                    # Tiempo de espera de carga
                    time.sleep(3)
                    
                    # Codigo de producto
                    try:
                        prod_code = driver.find_element(By.XPATH, "//div[contains(@class, 'code-label')]/span[2]").text
                    except NoSuchElementException:
                        try:
                            prod_code = driver.find_element(By.XPATH, "//div[contains(@id, 'wrapper')]/div[2]//div[contains(@class, 'codigo')]/div[1]/p").text
                        except NoSuchElementException:
                            prod_code = ""

                    # Clave de producto
                    try:
                        key = driver.find_element(By.XPATH, "//div[contains(@class, 'sku-label')]/span[2]").text
                    except NoSuchElementException:
                        try:
                            key = driver.find_element(By.XPATH, "//div[contains(@id, 'wrapper')]/div[2]//div[contains(@class, 'codigo')]/div[2]/p").text
                        except NoSuchElementException:
                            key = ""

                    # Nombre de producto
                    try:
                        title = driver.find_element(By.XPATH, "//h1[contains(@class, 'main-title')]").text
                    except NoSuchElementException:
                        try:
                            title = driver.find_element(By.XPATH, "//div[contains(@id, 'wrapper')]/div[2]//div[contains(@class, 'titulo-producto')]").text
                        except NoSuchElementException:
                            title = ""

                    # Descripcion de producto
                    try:
                        description = driver.find_element(By.XPATH, "//div[contains(@id, 'wrapper')]/div[2]//section[contains(@id, 'caracteristicas')]//ul[contains(@class, 'fa-ul')]").text
                    except NoSuchElementException:
                        try:
                            description = driver.find_element(By.XPATH, "//section[contains(@id, 'caracteristicas')]").text
                        except NoSuchElementException:
                            description = ""

                    # Ficha tecnica de producto
                    try:
                        sheet = driver.find_element(By.XPATH, "//div[contains(@class, 'ver-ficha-tecnica')]/a").get_attribute("href")
                    except NoSuchElementException:
                        try:
                            sheet = driver.find_element(By.XPATH, "//div[contains(@id, 'wrapper')]/div[1]//section[contains(@id, 'descargables')]//a").get_attribute("href")
                        except NoSuchElementException:
                            sheet = ""

                    # Imagen de producto
                    try:
                        image = driver.find_element(By.XPATH, "//img[contains(@class, 'img-responsive')]").get_attribute("src")
                    except NoSuchElementException:
                        try:
                            image = driver.find_element(By.XPATH, "//div[contains(@id, 'wrapper')]/div[1]//section[contains(@id, 'galeria')]//img[1]").get_attribute("src")
                        except NoSuchElementException:
                            image = ""

                    # Descargar imagen
                    with open(os.path.join(path, str(prod_code)) + '.jpg', 'wb') as handle:
                        response = requests.get(image, stream=True)
                        if not response.ok:
                            print(response)
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)

                    # Escribir renglon de datos
                    writer.writerow([prod_code, key, title, description, sheet])

    # Mostrar productos no encontrados
    products_not_exists
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }