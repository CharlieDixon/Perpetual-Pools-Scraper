#!/Users/csd/PycharmProjects/tracer_pools/.venv/bin/python
"""
Script which uses selenium to run a headless chromium browser to scrape values from Perpetual Pools and Arbitrum Balancer and sends an SMS notification 
containing the token pairs for which the percentage difference is greater than X%. Allows opportunities for arbitrage to be spotted and exploited.
"""
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
from loguru import logger
import sys, time, re, os
from send_sms import price_alerts
from resources.xpaths import *
from contextlib import contextmanager

sys.path.append(
    "/Users/csd/PycharmProjects/tracer_pools/.venv/lib/python3.8/site-packages/"
)


def main():
    logger.remove()
    logger.add(
        sys.stderr,
        colorize=True,
        format="<c>{time:HH:MM:SS}</c> | {level} | <level><blue>{message}</blue></level>",
        level="DEBUG",
    )

    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(f"Time of execution: {current_time}")

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
    ADDON_PATH = os.getenv("ADDON_PATH")
    SECRET_RECOVERY_PHRASE = os.getenv("SECRET_RECOVERY_PHRASE")
    NEW_PASSWORD = os.getenv("NEW_PASSWORD")

    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    s = Service("/Users/csd/PycharmProjects/tracer_pools/.venv/bin/geckodriver")
    driver = webdriver.Firefox(
        service=s,
        options=options,
    )
    driver.install_addon(ADDON_PATH, temporary=True)
    time.sleep(1)
    # switch to second tab
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[1])

    @contextmanager
    def wait_for_new_window(driver, timeout=10):
        handles_before = driver.window_handles
        yield
        WebDriverWait(driver, timeout).until(
            lambda driver: len(handles_before) != len(driver.window_handles)
        )
    def wait_and_click(xpath):
        try:
            # elem = WebDriverWait(driver, 30).until(
            # EC.element_to_be_clickable((By.XPATH, xpath)))
            elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            # elem.click() 
            driver.execute_script("arguments[0].click();", elem)
        except Exception as e:
            print(f"exception occured: {e}")
            print(f"the error occured with this xpath: {xpath}")
            driver.quit()
            sys.exit()

    wait_and_click("/html/body/div[1]/div/div[2]/div/div/div/button")
    wait_and_click(
        "/html/body/div[1]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/button"
    )
    wait_and_click(
        "/html/body/div[1]/div/div[2]/div/div/div/div[5]/div[1]/footer/button[1]"
    )
    time.sleep(2)
    # enter recovery phrase and new password into input boxes
    inputs = driver.find_elements(By.XPATH, "//input")
    inputs[0].send_keys(SECRET_RECOVERY_PHRASE)
    inputs[1].send_keys(NEW_PASSWORD)
    inputs[2].send_keys(NEW_PASSWORD)
    time.sleep(1)
    driver.find_element(
        By.CSS_SELECTOR, ".first-time-flow__terms"
    ).click()  # toc checkbox
    wait_and_click('//button[text()="Import"]')  # click import button
    wait_and_click('//button[text()="All Done"]')  # click all done
    driver.get("https://pools.tracer.finance/")

    # click on decline tour for popup on startup
    wait_and_click("/html/body/div[3]/div/div/div/div[2]/div[2]/div[7]/button[1]")
    # select Connect Wallet
    wait_and_click("/html/body/div[1]/div/div/div[1]/nav/div/span/div[1]/button")
    # check TOCs
    wait_and_click("/html/body/aside/section/div[7]/input")
    # Continue button
    wait_and_click("/html/body/aside/section/button")
    # check participation agreement
    wait_and_click("/html/body/aside/section/div[6]/input")
    # Ok, let's connect button
    wait_and_click("/html/body/aside/section/button")
    # select MetaMask wallet option
    with wait_for_new_window(driver):
        wait_and_click("/html/body/aside/section/ul/li[1]/button/span")
    # switch to MetaMask popup window
    windows = driver.window_handles
    driver.switch_to.window(windows[2])
    # Next button
    wait_and_click("/html/body/div[1]/div/div[2]/div/div[2]/div[4]/div[2]/button[2]")
    # Connect button
    with wait_for_new_window(driver):
        wait_and_click(
            "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]"
        )
    # switch back to tracer pools window
    driver.switch_to.window(windows[1])
    # click Switch to Arbitrum Mainnet link
    with wait_for_new_window(driver):
        wait_and_click("/html/body/div[2]/div/div[2]/span/a[1]")
    # switch back to newly opened window to allow tracer pools to add a network to MetaMask
    windows = driver.window_handles
    driver.switch_to.window(windows[2])
    # Approve button
    wait_and_click("/html/body/div[1]/div/div[2]/div/div[2]/div/button[2]")
    # Switch network button
    with wait_for_new_window(driver):
        wait_and_click("/html/body/div[1]/div/div[2]/div/div[2]/div[2]/button[2]")
    # switch to homepage again
    driver.switch_to.window(windows[1])
    # close Bridge Funds to Arbirtrum modal
    wait_and_click("/html/body/div[3]/div/div/div/div[2]/div[1]/div[2]")
    time.sleep(1)
    driver.refresh()
    time.sleep(20)
    driver.refresh()
    time.sleep(4)
    # click dropdown menu for trading pairs
    while True:
        try:
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/nav/div/span/div[1]/button/span')
            break
        except:
            driver.refresh()
    wait_and_click(SELECT_DROPDOWN)
    time.sleep(1)
    counter = 0
    xpaths = []
    for i in range(3,20):
        if counter < 2:
            try:
                elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f'//*[@id="headlessui-menu-item-{i}"]'))
                    )
                driver.execute_script("arguments[0].click();", elem)
                counter += 1
                xpaths.append(f'//*[@id="headlessui-menu-item-{i}"]')
            except:
                print(f'//*[@id="headlessui-menu-item-{i}"] does not exist')
    print(xpaths)
    BTC_OPTION = xpaths[0]
    ETH_OPTION = xpaths[1]
    # wait for dropdown options to appear and click first option
    wait_and_click(BTC_OPTION)
    # select input
    amount_input = driver.find_elements(By.XPATH, "//input")[0]
    # add 1000 to input field
    amount_input.send_keys(1000)

    def get_inner_html(xpath) -> float:
        """Extracts inner html from a given element as identified by its xpath. Removes html elements and replaces any characters that aren't numeric or decimal.
        Args:
            xpath (str): xpath of the element of interest e.g. '/html/body/div[1]'.
        Returns:
            float: cleaned numeric string converted into a float e.g. 1.3.
        """
        time.sleep(1)
        innerHtml = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(By.XPATH, xpath).get_attribute(
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

    # 1L-BTC/USD
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["1L-BTC/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"1L-BTC/USD: {percent_diff}")

    driver.find_element(By.XPATH, POWER_LEV_3_XPATH).click()  # click leverage 3 button

    # 3L-BTC/USD
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["3L-BTC/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"3L-BTC/USD: {percent_diff}")

    driver.find_element(By.XPATH, SHORT_XPATH).click()  # click Short button

    # 3S-BTC/USD
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["3S-BTC/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"3S-BTC/USD: {percent_diff}")

    driver.find_element(
        By.XPATH, POWER_LEV_1_XPATH
    ).click()  # click power leverage button 1

    # 1S-BTC/USD
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["1S-BTC/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"1S-BTC/USD: {percent_diff}")

    wait_and_click(SELECT_DROPDOWN)  # click on dropdown menu
    wait_and_click(ETH_DROPDOWN)  # select ETH/USDC pair option

    # 1S-ETH/USD
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["1S-ETH/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"1S-ETH/USD: {percent_diff}")

    driver.find_element(By.XPATH, POWER_LEV_3_XPATH).click()  # click leverage 3 button

    # 3S-ETH/USD
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["3S-ETH/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"3S-ETH/USD: {percent_diff}")

    driver.find_element(By.XPATH, LONG_XPATH).click()  # click Long button

    # 3L-ETH/USD
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["3L-ETH/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"3L-ETH/USD: {percent_diff}")

    # 1L-ETH/USD
    driver.find_element(
        By.XPATH, POWER_LEV_1_XPATH
    ).click()  # click power leverage 1 button
    token_rate = get_inner_html(TOKEN_RATE_XPATH)
    balancer_pools = get_inner_html(BALANCER_POOLS_XPATH)
    try:
        percent_diff = ((token_rate - balancer_pools) / balancer_pools) * 100
    except ZeroDivisionError:
        percent_diff = 0
    PAIRS["1L-ETH/USD"] = token_rate, balancer_pools, percent_diff
    logger.debug(f"1L-ETH/USD: {percent_diff}")

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
    print("message: ", message)
    driver.close()
    driver.quit()
    sys.exit()


if __name__ == "__main__":
    main()
