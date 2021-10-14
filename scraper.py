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
from send_sms import price_alerts

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<c>{time:HH:MM:SS}</c> | {level} | <level><blue>{message}</blue></level>",
    level="DEBUG",
)

pairs = {
    "1L-BTC/USD": None,
    "3L-BTC/USD": None,
    "3S-BTC/USD": None,
    "1S-BTC/USD": None,
    "1S-ETH/USD": None,
    "3S-ETH/USD": None,
    "3L-ETH/USD": None,
    "1L-ETH/USD": None,
}

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

# click dropdown menu for trading pairs
wait_and_click('//*[@id="headlessui-menu-button-3"]')

# wait for dropdown options to appear and click first option
wait_and_click('//*[@id="headlessui-menu-item-11"]')

# select input
amount_input = driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[5]/div[1]/input"
)
# add 1 to input field
ActionChains(driver).click(amount_input).send_keys("1").perform()


def get_inner_html(xpath):
    time.sleep(1)
    innerHtml = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element_by_xpath(xpath).get_attribute("innerHTML")
    )
    try:
        logger.debug(innerHtml)
        logger.debug(BeautifulSoup(innerHtml, "lxml").text)
        cleantext = BeautifulSoup(innerHtml, "lxml").text
        rate = float(re.sub("[^0-9,.]", "", cleantext))
        logger.debug(rate)
        return rate
    except Exception as e:
        logger.debug(e)


token_rate_xpath = "/html/body/div[1]/div/div/div[2]/div/div[6]/div/div/div/div[1]/div[1]/span/div/span[2]"
balancer_pools_xpath = (
    "/html/body/div[1]/div/div/div[2]/div/div[6]/div/div/div/div[1]/div[3]/div[2]/a"
)

# 1L-BTC/USD
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["1L-BTC/USD"] = token_rate, balancer_pools, percent_diff
logger.debug(percent_diff)

driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[2]"
).click()  # click leverage 3 button

# 3L-BTC/USD
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["3L-BTC/USD"] = token_rate, balancer_pools, percent_diff
logger.debug(percent_diff)


def get_rates(func):
    def wrapper(*args, **kwargs):
        get_inner_html(token_rate_xpath)
        get_inner_html(balancer_pools_xpath)
        return func(*args, **kwargs)

    return wrapper


driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[2]"
).click()  # click Short button

# 3S-BTC/USD
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["3S-BTC/USD"] = token_rate, balancer_pools, percent_diff

driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[1]"
).click()  # click power leverage button 1

# 1S-BTC/USD
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["1S-BTC/USD"] = token_rate, balancer_pools, percent_diff

wait_and_click('//*[@id="headlessui-menu-button-3"]')  # click on dropdown menu
wait_and_click('//*[@id="headlessui-menu-item-19"]')  # select ETH/USDC pair option

# 1S-ETH/USD
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["1S-ETH/USD"] = token_rate, balancer_pools, percent_diff

driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[2]"
).click()  # click leverage 3 button

# 3S-ETH/USD
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["3S-ETH/USD"] = token_rate, balancer_pools, percent_diff

driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[1]"
).click()  # click Long button

# 3L-ETH/USD
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["3L-ETH/USD"] = token_rate, balancer_pools, percent_diff

# 1L-ETH/USD
driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[1]"
).click()  # click power leverage 1 button
token_rate = get_inner_html(token_rate_xpath)
balancer_pools = get_inner_html(balancer_pools_xpath)
percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
pairs["1L-ETH/USD"] = token_rate, balancer_pools, percent_diff

over_two_percent = {k: v for k, v in pairs.items() if pairs[k][2] >= 2}
# for item in over_one_percent.items():
#     item[0], round(item[1][2], 2)

# create list of lists for trading pairs and their percentage differences
pair_percentages = [
    [item[0], round(item[1][2], 2)] for item in over_two_percent.items()
]

message = ""
for pair in pair_percentages:
    message += pair[0] + ": " + str(pair[1]) + "; "


# f"{ex[0]}: {ex[1]}%"

price_alerts(message)
driver.close()

# BTC/USDC dropdown - //*[@id="headlessui-menu-item-11"]
# ETH/USDC dropdown - //*[@id="headlessui-menu-item-12"]
# power leverage 1 button - /html/body/div[1]/div/div/div[2]/div/div[4]/span/button[1]
# power leverage 3 button - /html/body/div[1]/div/div/div[2]/div/div[4]/span/button[2]
# amount input - /html/body/div[1]/div/div/div[2]/div/div[5]/div[1]/input
# long button - /html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[1]
# short button - /html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[2]
# connect wallet button - /html/body/div[1]/div/div/div[2]/div/button
