import time

from selenium.common import NoSuchElementException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

stores = {
"Company Name": ("https://dutchie.com/url/products","PDF_File_Name"),
}

for storeURL, storeInvFile in stores.values():
    print(f'current store URL {storeURL} \n current store pdf {storeInvFile}')

#while dispoNumber < len(stores):

    browser = webdriver.Chrome()
    browser.get(storeURL)

    # sleep so button fully loads before click
    time.sleep(2)
    browser.find_element(By.XPATH, '//button[@aria-label="yes button"]').click()
    # Required to generate the current date/time to append to the file name
    current_date_time_final = time.strftime("%m%d%Y-%H%M%S")

    itemHolder = open(f"{storeInvFile} - {current_date_time_final}.csv", "a+")
    def click_over21_button(window_popup):
        try:
            time.sleep(2)
            window_popup.find_element(By.XPATH, '//button[@aria-label="yes button"]').click()
        except NoSuchElementException:
            print("Yes Button didn't appear attempting to skip click")
            pass


    def scroll_down(self):
        page_height = self.execute_script("return document.body.scrollHeight")
        total_scrolled = 0
        for i in range(page_height):
            self.execute_script(f'window.scrollBy(0,{i});')
            total_scrolled += i
            if total_scrolled >= page_height / 2:
                last_no = i
                break
        for i in range(last_no, 0, -1):
            self.execute_script(f'window.scrollBy(0,{i});')
        # Done scrolling in initial scroll down should jump once more momentarily to grab last few elements missed in scan
        next_button = self.find_element(By.XPATH, '//button[@aria-label="go to next page"]')
        self.execute_script(
            "arguments[0].scrollIntoView({ behavior: 'smooth'})",
            next_button
        )
        time.sleep(2)

    def extractInvAmt(stockBrowserWindow,productBrand, productName, productPrice):
        # Test from 10 - 1, skip if there's an error then the first time it finds a value stop, break out & return that value to be included on the spreadsheet
        # if out of stock message exists give 0 move on otherwise check stock number
        # Starts checking from 10 so first one (highest number) that returns a value & not an error is the highest stock

        potentialQuantity = 10
        while potentialQuantity > 0:
            try:
                stockBrowserWindow.find_element(By.XPATH, f'//li[@data-value="{potentialQuantity}"]')
            except NoSuchElementException:
                potentialQuantity -= 1
            else:
                print(f"Quantity in stock: {potentialQuantity}")
                actualQuantity = potentialQuantity
                itemHolder.write(productBrand + "," + productName + "," + productPrice + "," + str(actualQuantity) + "\n")
                break
        stockBrowserWindow.quit()
    def scanForItems(browserWindow):

        time.sleep(2)
        scroll_down(browserWindow)
        time.sleep(1)
        menu = browserWindow.find_elements(By.XPATH, '//*[@data-testid="product-list-item"]')
        for items in menu:

            #########
            # Code to pull the URL of the item from the source code to check stock
            #########
            itemTag = items.get_attribute('innerHTML')
            soup = BeautifulSoup(itemTag, 'html.parser')
            time.sleep(2)
            productName = soup.find('div', attrs={"class": re.compile("desktop-product-list-item__ProductNameContainer")}).get_text()
            try:
                productBrand = soup.find('span', attrs={"class": re.compile("desktop-product-list-item__ProductBrand")}).get_text()
            except:
                productBrand = "N/A"

            productPrice = soup.find('span', attrs={"class": re.compile("weight-tile__PriceText")}).get_text()

            print(productBrand + '\n' + productName)

            for link in soup.find_all('a'):
                urlEnding = link.get('href')
                url = "https://dutchie.com" + urlEnding
                stockBrowserWindow = webdriver.Chrome()
                # Run the stock window minimized
                stockBrowserWindow.minimize_window()
                stockBrowserWindow.get(url)
                click_over21_button(stockBrowserWindow)
                time.sleep(1)
                # Check if it's out of stock
                try:
                    stockBrowserWindow.find_element(By.XPATH, '//div[@aria-label="Quantity"]').click()
                except:
                    pass
                finally:
                    extractInvAmt(stockBrowserWindow, productBrand, productName, productPrice)

        # Once done scanning locates the next button to click next page unless it's not enabled meaning it's at the end
        next_button = browserWindow.find_element(By.XPATH, '//button[@aria-label="go to next page"]')
        try:
            next_button_enabled = next_button.is_enabled()
            if next_button_enabled == False:
                print('next button not enabled so at the end of the list')
                return False
            time.sleep(2)
            print('Clicking Next after 5 seconds')
            browserWindow.execute_script("arguments[0].click();", next_button)
            time.sleep(5)

        except:
            print('next button not found')


    while scanForItems(browser) != False:
        scanForItems(browser)

    itemHolder.close()
