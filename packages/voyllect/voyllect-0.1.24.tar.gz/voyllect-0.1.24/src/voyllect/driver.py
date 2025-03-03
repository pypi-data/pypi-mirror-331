#!/usr/bin/env python

import sys
import random

sys.path.append('..')

from fake_useragent import UserAgent as ua


def get_random_user_agent(browsers=['Chrome'], min_version=120.0):
    """Generates random user agent.
    
    Args:
        browsers (list): list of web browsers.
        min_version (float): minimum version of the selected web browsers.

    Returns:
        str, Random user agent.
    s"""

    user_agents = ua(browsers=browsers, min_version=min_version)

    return user_agents.random


def get_driver_dict(driver_path, 
                    options, 
                    args):
    """Gets the driver parameters dictionary.
    
    Args:
        driver_path (str): path to the driver.
        options (dict): options of the driver.
        args (dict): parsed arguments.

    Returns:
        dict, Driver parameters dictionary.
    """

    return {
        'driver_path': driver_path,
        'options': options,
        'headless': args.headless,
        'delete_cookies': args.delete_cookies,
        'use_driver': args.use_driver,
        'use_proxy': args.use_proxy,
        'proxy_url': args.proxy_url
    }


def quit_driver(driver, 
                delete_cookies):
    """Quit the driver.

    Args:
        driver (WebDriver): selenium webdriver.
        delete_cookies (bool): to delete cookies or not.
    """
    
    try:
        driver.quit()
        if delete_cookies:
            driver.delete_all_cookies()
    except Exception as e:
        print(f"[LOG] [EXCEPTION]\n{e}")
        