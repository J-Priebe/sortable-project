# https://sortable.com/project/

import json
import sys
import time

DEFAULT_PRODUCTS_PATH = './products.txt'
DEFAULT_LISTINGS_PATH = './listings.txt'

# read products and listings input files; create a dictionary and list, respectively
def process_input(products_path, listings_path, products, listings):

    with open(products_path) as f:
        content = f.readlines()
        print('Number of products: %d' % (len(content)))
        for c in content:
            item = json.loads(c)
            manufacturer_string = item['manufacturer']
            key = format_string(manufacturer_string)
            products.setdefault(key,[]).append(item)


    with open(listings_path) as f:
        content = f.readlines()
        print('Number of listings: %d' % (len(content)))
        for c in content:
            listings.append(json.loads(c))


# strip whitespace, special characters (except '.') from string and convert to lowercase
def format_string(raw_key):
    formatted_string = (''.join(c for c in raw_key if c.isalnum() or c == '.')).lower()
    return formatted_string

# create list of keywords from string
def tokenize(string):
    tokens = [format_string(token) for token in string.split(' ')]
    return tokens

# output results to file
def write_results(results):
    with open('./results.txt', 'w') as f:
        for product_key in results:
            json_result = json.dumps({'product_name': product_key, 'listings': results[product_key]})
            f.write(json_result + '\n')

# True if set(a) < set(b)
def is_subset(a, b):
    for item in a:
        if item not in b: return False
    return True


# Find the closest matching product (if any) for a listing
# some loss of precision due to listings for product accessories such as batteries 
# could be improved with a tailored keyword dictionary, more info about the data
def find_best_match(listing, products):


    manufacturer_key = format_string(listing['manufacturer'])

    # extract keywords from listing title
    title_keywords = (tokenize(listing['title']))

    # track the highest-scoring product match
    best_score = 0
    best_match = None

    # only consider products from the same manufacturer
    # check for manufacturers that are substrings as well (e.g., Minolta = Konica Minolta)
    # increased recall but slightly slower than just checking products with the exact same manufacturer name
    for key in products:
        if key in manufacturer_key or manufacturer_key in key:

            possible_matches = products.get(key, [])

            for product in possible_matches:

                score = 0

                # at minimum, product model and family must be included in listing title
                product_keywords = (tokenize(product.get('model')) + tokenize(product.get('family', '')))
                if is_subset(product_keywords, title_keywords):

                    # two ways methods of reducing false positives:
                    # 1. product models with suffixes (e.g., WG-1 GPS) will score higher than those without (WG-1)
                    # 2. products with 2 or more same-score matches will be discarded (likely to be accessories for the product)
                    score = len(product_keywords)

                    # no clear best match; discard this listing
                    if score == best_score:
                        return None

                    if score > best_score:
                        best_score = score
                        best_match = product.get('product_name')

    # return product name of the best match for this listing
    return best_match


def main(products_path, listings_path):
    start_time = time.time()
    
    # manufacturer is only shared key between products and listings
    # improves best-case runtime to O(n) by only checking for matches from same manufacturer; worst-case is still O(n^2)
    products = {} 
    listings = []
    results = {} 

    # create a dictionary of products using manufacturer as key 
    # listings are just stored as a list
    process_input(products_path, listings_path, products, listings)

    num_matched_listings = 0
    
    # iterate each listing and find its best product match
    for listing in listings:
        product_name = find_best_match(listing, products)
        if product_name:
            num_matched_listings+=1

            # append the listing to the product it belongs to
            results.setdefault(product_name, []).append(listing)

    # results are written to results.txt
    write_results(results)
    print('Results written to results.txt')

    print('%d listings found for %d products.' % (num_matched_listings, len(results)))
    print('Runtime: %d seconds.' % (time.time() - start_time))


if __name__ == '__main__':
    main(DEFAULT_PRODUCTS_PATH, DEFAULT_LISTINGS_PATH)
