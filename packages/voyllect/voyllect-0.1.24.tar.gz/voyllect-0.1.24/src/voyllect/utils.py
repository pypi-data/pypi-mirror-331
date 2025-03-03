#!/usr/bin/env python

import glob
import os
import sys

sys.path.append('..')

from math import ceil


def convert_n_reviews_to_int(n_reviews):
    """Converts the `n_reviews` to int.
    
    Args:
        n_reviews: value of reviews count.
        
    Return:
        int, Reviews count in integer.
    """

    if isinstance(n_reviews, int):
        return n_reviews
    elif isinstance(n_reviews, float):
        return int(n_reviews)
    else:
        try:
            # Remove non-numeric characters
            n_reviews = ''.join(filter(str.isdigit, n_reviews))  
            return int(n_reviews)
        except Exception as e:
            print(f"[LOG] [EXCEPTION]\n{e}")
            return 0


def check_n_reviews_limit(n_reviews, n_reviews_max):
    """Compare number of reviews loaded/saved to the limit 'n_reviews_max'.
    
    Args:
        n_reviews: value of reviews count.
        n_reviews_max: limit of reviews to load/save.
        
    Return:
        Bool, if the limit has been exceeded or not.
    """

    if n_reviews >= n_reviews_max:
        print("[LOG] [LIMIT] The reviews limit has been reached.")
        return True
    else:
        return False


def get_rating_from_colors(colors):
    """Evaluates the rating value based on the number of occurrences 
    of the color "#3cbeaf" in a list of colors.

    Args:
        colors (list): list of color codes in string 
                       format, such as "#3cbeaf" or "#E6E6E6".

    Returns:
        int, The rating value corresponding to the number of consecutive 
             occurrences of the color "#3cbeaf" in the list.
             The rating value starts at 1 and increases by 1 for 
             each group of consecutive "#3cbeaf" colors.
    """

    return colors.count("#3cbeaf")


def get_most_recent_json_file(folder_path):
    """Returns path to the most recent json file in a the specified folder.

    Args:
        folder_path (str): path of folder containing json files.

    Returns:
        str, most recently created json file path.
    """
    
    most_recent_json_file = \
        sorted(glob.glob(os.path.join(folder_path, '*.json')))[-1]
    
    return most_recent_json_file


def n_pages(n_reviews, n_reviews_per_page):
    """Determines the number of reviews pages per product.

    Args:
        n_reviews (int): number of reviews.
        n_reviews_per_page (int): number of reviews per page.

    Returns:
        int, Number of reviews pages.
    """

    return ceil(int(n_reviews) / n_reviews_per_page) + 1


def delete_files_after_transfer(aggregated_urls_folder_path,
                                aggregated_urls,
                                filtered_urls_folder_path,
                                filtered_urls,
                                reviews_folder_path,
                                reviews,
                                products_folder_path,
                                products,
                                urls_to_collect_anchor_folder_path,
                                urls_to_collect_anchor,
                                aggregated_products_folder_path,
                                aggregated_products,
                                aggregated_reviews_folder_path,
                                aggregated_reviews,
                                counts_per_urls_folder_path,
                                counts_per_urls,
                                counts_per_collect_date_products_folder_path,
                                counts_per_collect_date_products,
                                counts_per_collect_date_reviews_folder_path,
                                counts_per_collect_date_reviews,
                                samples_products_folder_path,
                                samples_products,
                                samples_reviews_folder_path,
                                samples_reviews):
    """Deletes files after ransferrind data to S3.

    Args:
        aggregated_urls_folder_path (str): folder path to aggregated URLs.
        aggregated_urls (bool): delete aggregated URLs.
        filtered_urls_folder_path (str): folder path to filtered URLs.
        filtered_urls (bool): delete filtered URLs.
        reviews_folder_path (str): folder path to the reviews.
        reviews (bool): delete reviews files.
        products_folder_path (str): folder path to the products.
        products (bool): delete products files.
        aggregated_products_folder_path (str): folder path to aggregated products.
        aggregated_products (bool): delete aggregated products.
        aggregated_reviews_folder_path (str): folder path to aggregated reviews.
        aggregated_reviews (bool): delete aggregated reviews.
        counts_per_urls_folder_path (str): folder path to KPIs files.
        counts_per_urls (bool): delete KPIs files.
        counts_per_collect_date_products_folder_path (str): folder path to the products KPIs files.
        counts_per_collect_date_products (bool): delete KPIs files.
        counts_per_collect_date_reviews_folder_path (str): folder path to the reviews KPIs files.
        counts_per_collect_date_reviews (bool): delete KPIs files.
        samples_products_folder_path (str): folder path to the samples products KPIs files.
        samples_products (bool): delete KPIs files.
        samples_reviews_folder_path (str): folder path to the samples reviews KPIs files.
        samples_reviews (bool): delete KPIs files.
    """

    print("[LOG] Deleting files that have been transfered to S3...")
    confirm_transfer = input("[LOG] Confirm transfer (yes/no) : ")
    confirm_operation = input("[LOG] Confirm operation (yes/no) : ")

    if confirm_transfer == 'yes' and confirm_operation ==  'yes':
        # reviews
        if reviews:
            print(f"[LOG] Deleting content of : {reviews_folder_path} ...")
            files = glob.glob(os.path.join(reviews, '*.json'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # products
        if products:
            print(f"[LOG] Deleting content of : {products} ...")
            files = glob.glob(os.path.join(products, '*.json'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # Filtered URLs
        if filtered_urls:
            print(f"[LOG] Deleting content of : {filtered_urls_folder_path} ...")
            files = glob.glob(os.path.join(filtered_urls_folder_path, '*.json'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # Aggregated products
        if aggregated_products:
            print(f"[LOG] Deleting content of : {aggregated_products_folder_path} ...")
            files = glob.glob(os.path.join(aggregated_products_folder_path, '*.json'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # Aggregated reviews
        if aggregated_reviews:
            print(f"[LOG] Deleting content of : {aggregated_reviews_folder_path} ...")
            files = glob.glob(os.path.join(aggregated_reviews_folder_path, '*.json'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # counts_per_urls
        if counts_per_urls:
            print(f"[LOG] Deleting content of : {counts_per_urls_folder_path} ...")
            files = glob.glob(os.path.join(counts_per_urls_folder_path, '*.xlsx'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # counts_per_collect_date_products
        if counts_per_collect_date_products:
            print(f"[LOG] Deleting content of : {counts_per_collect_date_products_folder_path} ...")
            files = glob.glob(os.path.join(counts_per_collect_date_products_folder_path, '*.xlsx'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # counts_per_collect_date_reviews
        if counts_per_collect_date_reviews:
            print(f"[LOG] Deleting content of : {counts_per_collect_date_reviews_folder_path} ...")
            files = glob.glob(os.path.join(counts_per_collect_date_reviews_folder_path, '*.xlsx'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # samples_products
        if samples_products:
            print(f"[LOG] Deleting content of : {samples_products_folder_path} ...")
            files = glob.glob(os.path.join(samples_products_folder_path, '*.xlsx'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")

        # samples_reviews
        if samples_reviews:
            print(f"[LOG] Deleting content of : {samples_reviews_folder_path} ...")
            files = glob.glob(os.path.join(samples_reviews_folder_path, '*.xlsx'))
            for file in files:
                os.remove(file)
            print("[LOG] Files deleted.")
    else:
        print("[LOG] Operation cancelled.")
