# https://sortable.com/project/


import json
import os, sys
import optparse
import re
import time
DEFAULT_PRODUCTS_PATH = "./products.txt"
DEFAULT_LISTINGS_PATH = "./listings.txt"



# return manufacturer map
def create_dict(fname):

    item_dict = {}

    with open(fname) as f:
        content = f.readlines()
        #print ('number of listings: %d' % (len(content)))

        for c in content:
            item = json.loads(c)
            manufacturer_string = item['manufacturer']
            key = format_key(manufacturer_string)
            item_dict.setdefault(key,[]).append(item)
    print('number of unique manufacturers: %d' % (len(item_dict)))   
    return item_dict


def create_list(fname):


    with open(fname) as f:
        lines = f.readlines()
        return [json.loads(line) for line in lines]





def format_key(raw_key):
    # strip whitespace, special characters from key and convert to lowercase
    # helps with formatting mismatches between product and listing manufacturers
    formatted_key = (''.join(c for c in raw_key if c.isalnum() or c == '.')).lower()
    return formatted_key

def tokenize(string):
    #token = (''.join(c for c in string if c.isalnum())).lower()
    #return token

    # #tokens = [format_key(token) for token in re.split('-| |_',string)]
    tokens = [format_key(token) for token in string.split(' ')]

    return tokens




def write_result(results):
    with open('./results.txt', 'w') as f:
        for result in results:
            f.write(json.dumps(result) + "\n\n")

# True if set(a) < set(b)
def is_subset(a, b):
    for item in a:
        if item not in b: return False

    return True

def find_best_match(listing, products):

    # a possible match will be from the same manufacturer and have all tokenized (see tokenize()) keywords from the product group and family in the listing title
    # two ways methods of reducing false positives:
    #   1. product models with suffixes (e.g., WG-1 GPS) will score higher than those without (WG-1)
    #   2. products with 2 or more same-score matches will be discarded (likely to be accessories for the product)



    manufacturer_key = format_key(listing['manufacturer'])

    title_keywords = (tokenize(listing['title']))

    threshold_score = 0#2 # minimum score needed for a match

    # product must be from same manufacturer

    for key in products:
        if key in manufacturer_key or manufacturer_key in key:

            possible_matches = products.get(key, [])

            for product in possible_matches:
                #model = format_key(product.get('model'))
                #family = format_key(product.get('family'), '')

                score = 0

                product_keywords = (tokenize(product.get('model')) + tokenize(product.get('family', '')))
                # model = tokenize(product.get('model'))
                # family = tokenize(product.get('family', ''))

                # model and family must be mentioned in the title 
                #if model_string in title_string and family_string in title_string:
                #if product_keywords < title_keywords:
                if is_subset(product_keywords, title_keywords):
                    #longer matches are scored higher (due to model suffixes and stuff being a better match)
                    #score = len(model_string) + len(family_string)
                    score = len(product_keywords)
                    if score > threshold_score:
                        threshold_score = score


                        #listing['best_match'] = product.get('product_name')
                        #listing['shared_keywords'] = shared_keywords

                        # find the problem listings
                    listing.setdefault('best_match', []).append("SCORE="+str(score)+product.get('product_name'))
                        #listing.setdefault('shared_keywords', []).append(shared_keywords)


                    #product_keywords = tokenize(product.get('model')) + tokenize(product.get('family', '')) #+ tokenize(product.get('product_name'))
                    #shared_keywords = set(product_keywords).intersection(`)
                    #if set(product_keywords) < set(title_string):

                        #score +=2
                    # if product.get('family', False): # bonus to score if optinional family name is included and matched
                    #     score +=1
                    #score = len(shared_keywords)
                    # if score >= threshold_score:
                    #     threshold_score = score

def main(products_path, listings_path):

    # test_keys(listings_path)
    start_time = time.time()
    
    # start by mapping the manufacturer - correct listings must at least be from same manufacturer
    # since this is the best criterion, create a hashmap using manufacturer as key, then we only have the check the listing from the same manufacturer for each product
    # worst case runtime is n^2 (all listings are same manufacturer), best case is n (1 listing per manufacturer)

    products = create_dict(products_path) 

    listings = create_list(listings_path) 

    results = [] #dict by product name

    n = 0
    
    # iterate each listing and find its best product match
    for listing in listings:
        find_best_match(listing, products)
        # if listing.get('best_match'):
        #     n+=1
        #     results.append({'listing' : listing['title'], 'product' :  listing.get('best_match'), 'keywords' : listing.get('shared_keywords')})

        # find out which ones are finding matches for multiple products.. likely to be problem areas
        if len(listing.get('best_match', [])) > 1:
            n+=1
            results.append({'listing' : listing['title'], 'product_matches' :  listing.get('best_match'), 'keywords' : listing.get('shared_keywords')})

    print("%d product listings matched" % (n))
    # for product in products:
    # #for i in range(len(products)):
    #     #print("\n-------%d--------\n" % (i))
    #     #product = products[i]
    #     #n_matched_listings += find_matches_deep(product, listings)
    #     result = find_matches_deep(product, listings)
    #     n_matched_listings += len(result['listings'])
    #     results.append(result)

    #print results
    #print("%d matches found for %d products" % (n_matched_listings, len(products)))

    write_result(results)

    print("runtime: %d seconds." % (time.time() - start_time))


if __name__ == "__main__":

    parser = optparse.OptionParser(usage="%prog [options] ")
    parser.add_option("-p", "--products", dest="products_path",
                      help="Location of product txt file (default: current directory)",
                      default=DEFAULT_PRODUCTS_PATH, metavar="PRODUCTS_PATH")
    
    parser.add_option("-l", "--listings", dest="listings_path",
                      help="Location of listings txt file (default: current directory)",
                      default=DEFAULT_LISTINGS_PATH, metavar="LISTINGS_PATH")


    options, args = parser.parse_args()
    if len(args) != 0:
        parser.error("Unknown Argument")
    else:
        main(options.products_path, options.listings_path)

