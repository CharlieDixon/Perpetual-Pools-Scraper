from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re
from loguru import logger
import sys
import time 

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<c>{time:HH:MM:SS}</c> | {level} | <level><blue>{message}</blue></level>",
    level="DEBUG",
)

pairs = {"1L-BTC/USD": None, "3L-BTC/USD": None, "3S-BTC/USD": None, "1S-BTC/USD": None, "1S-ETH/USD": None, "3S-ETH/USD": None, "3L-ETH/USD": None, "1L-ETH/USD": None}

driver = webdriver.Firefox()
driver.get("https://pools.tracer.finance/")
def wait_and_click(xpath):
    try:
        elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", elem)
        # elem.click()
    except Exception as e:
        print(f"exception occured: {e}")
# click on decline tour for popup on startup
wait_and_click("/html/body/div[3]/div/div/div/div[2]/div[2]/div[6]/button[1]")
# try:
#     popup = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div[2]/div[6]/button[1]"))
#     )
#     popup.click()
# except Exception as e:
#     print("exception occured: {e}")

# click dropdown menu for trading pairs
wait_and_click('//*[@id="headlessui-menu-button-3"]')
# dropdown = driver.find_element(By.XPATH, '//*[@id="headlessui-menu-button-3"]')
# driver.execute_script("arguments[0].click();", dropdown)

# wait for dropdown options to appear and click first option
wait_and_click('//*[@id="headlessui-menu-item-11"]')
# try:
#     btc = WebDriverWait(driver, 15).until(
#         EC.presence_of_element_located((By.XPATH, '//*[@id="headlessui-menu-item-11"]'))
#     )
#     btc.click()
# except Exception as e:
#     print(f"exception occured: {e}")

# select input
amount_input = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[5]/div[1]/input')
# add 1 to input field
ActionChains(driver).click(amount_input).send_keys("1").perform()


def get_inner_html(xpath):
    time.sleep(1)
    innerHtml = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(xpath).get_attribute("innerHTML"))
    try:
        logger.debug(innerHtml)
        logger.debug(BeautifulSoup(innerHtml, "lxml").text)
        cleantext = BeautifulSoup(innerHtml, "lxml").text
        rate = float(re.sub('[^0-9,.]', '', cleantext))
        logger.debug(rate)
        return rate
    except Exception as e:
        logger.debug(e)

token_rate_xpath = '/html/body/div[1]/div/div/div[2]/div/div[6]/div/div/div/div[1]/div[1]/span/div/span[2]'
token_rate = get_inner_html(token_rate_xpath)

balancer_pools_xpath = '/html/body/div[1]/div/div/div[2]/div/div[6]/div/div/div/div[1]/div[3]/div[2]/a'
balancer_pools = get_inner_html(balancer_pools_xpath)

percent_diff = ((balancer_pools - token_rate)/token_rate) * 100
logger.debug(percent_diff)

power_leverage_3 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[2]')
power_leverage_3.click()

token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((balancer_pools - token_rate)/token_rate) * 100
logger.debug(percent_diff)

# click Short button
driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[2]').click()
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)

breakpoint()
assert "No results found." not in driver.page_source
driver.close()

# BTC/USDC dropdown - //*[@id="headlessui-menu-item-11"]
# ETH/USDC dropdown - //*[@id="headlessui-menu-item-12"]
# power leverage 3 button - /html/body/div[1]/div/div/div[2]/div/div[4]/span/button[2]
# amount input - /html/body/div[1]/div/div/div[2]/div/div[5]/div[1]/input
# short button - /html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[2]
# connect wallet button - /html/body/div[1]/div/div/div[2]/div/button