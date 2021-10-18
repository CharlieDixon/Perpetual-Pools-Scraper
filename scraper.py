"""
Script which uses selenium to run a headless chromium browser to scrape values from Perpetual Pools and Arbitrum Balancer and sends an SMS notification 
containing the token pairs for which the percentage difference is greater than X%. Allows opportunities for arbitrage to be spotted and exploited.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from loguru import logger
import sys, time, re
from send_sms import price_alerts


def main():
    logger.remove()
    logger.add(
        sys.stderr,
        colorize=True,
        format="<c>{time:HH:MM:SS}</c> | {level} | <level><blue>{message}</blue></level>",
        level="DEBUG",
    )

    X = 2  # percentage difference to send alert at
    PAIRS = {
        "1L-BTC/USD": None,
        "3L-BTC/USD": None,
        "3S-BTC/USD": None,
        "1S-BTC/USD": None,
        "1S-ETH/USD": None,
        "3S-ETH/USD": None,
        "3L-ETH/USD": None,
        "1L-ETH/USD": None,
    }

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # driver = webdriver.Firefox()
    driver.get("https://pools.tracer.finance/")

    def wait_and_click(xpath):
        try:
            elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", elem)
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

    def get_inner_html(xpath) -> float:
        """Extracts inner html from a given element as identified by its xpath. Removes html elements and replaces any characters that aren't numeric or decimal.

        Args:
            xpath (str): xpath of the element of interest e.g. '/html/body/div[1]'.

        Returns:
            float: cleaned numeric string converted into a float e.g. 1.3.
        """
        time.sleep(1)
        innerHtml = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_xpath(xpath).get_attribute(
                "innerHTML"
            )
        )
        try:
            cleantext = BeautifulSoup(innerHtml, "lxml").text
            rate = float(re.sub("[^0-9,.]", "", cleantext))
            logger.debug(rate)
            return rate
        except Exception as e:
            logger.debug(e)

    # will likely break once site changes but accurate as of 18/10/21
    token_rate_xpath = "/html/body/div[1]/div/div/div[2]/div/div[6]/div/div/div/div[1]/div[1]/span/div/span[2]"
    balancer_pools_xpath = (
        "/html/body/div[1]/div/div/div[2]/div/div[6]/div/div/div/div[1]/div[3]/div[2]/a"
    )

    # 1L-BTC/USD
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["1L-BTC/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(percent_diff)

    driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[2]"
    ).click()  # click leverage 3 button

    # 3L-BTC/USD
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["3L-BTC/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(percent_diff)

    driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[2]"
    ).click()  # click Short button

    # 3S-BTC/USD
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["3S-BTC/USD"] = token_rate, balancer_pools, percent_diff

    driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[1]"
    ).click()  # click power leverage button 1

    # 1S-BTC/USD
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["1S-BTC/USD"] = token_rate, balancer_pools, percent_diff

    wait_and_click('//*[@id="headlessui-menu-button-3"]')  # click on dropdown menu
    wait_and_click('//*[@id="headlessui-menu-item-19"]')  # select ETH/USDC pair option

    # 1S-ETH/USD
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["1S-ETH/USD"] = token_rate, balancer_pools, percent_diff

    driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[2]"
    ).click()  # click leverage 3 button

    # 3S-ETH/USD
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["3S-ETH/USD"] = token_rate, balancer_pools, percent_diff

    driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[3]/span[2]/span/button[1]"
    ).click()  # click Long button

    # 3L-ETH/USD
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["3L-ETH/USD"] = token_rate, balancer_pools, percent_diff

    # 1L-ETH/USD
    driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/span/button[1]"
    ).click()  # click power leverage 1 button
    token_rate = get_inner_html(token_rate_xpath)
    balancer_pools = get_inner_html(balancer_pools_xpath)
    percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    PAIRS["1L-ETH/USD"] = token_rate, balancer_pools, percent_diff

    # extract key value pairs for trading pairs that have over X% difference
    over_x_percent = {k: v for k, v in PAIRS.items() if v[2] >= X}

    # create list of lists for trading pairs and their percentage differences
    pair_percentages = [
        [item[0], round(item[1][2], 2)] for item in over_x_percent.items()
    ]

    message = ""
    for pair in pair_percentages:
        message += "(" + pair[0] + ": " + str(pair[1]) + ") "
    logger.debug(message)
    if message:
        price_alerts(message)
    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()
