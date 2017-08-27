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
        print ('number of listings: %d' % (len(content)))

        for c in content:
            item = json.loads(c)
            item['matched'] = False
            manufacturer_string = item['manufacturer']
            key = format_key(manufacturer_string)
            #del item['manufacturer']
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
    formatted_key = (''.join(c for c in raw_key if c.isalnum())).lower()
    return formatted_key

def tokenize(string):
    tokens = [keyword.lower() for keyword in re.split('-| ',string)]
    return tokens




def find_matches_deep(product, listings):


    #print("product name: %s" % (product.get('product_name')))

    matches = []


    # correct listing must be from same manufacturer and contain product model and family in title
    product_key = format_key(product['manufacturer'])
    product_keywords = tokenize(product['model']) + tokenize(product.get('family', ''))#+ tokenize(product['family'])


    # now we check all keys which are a subset of the product key or vice versa
    for listing_key in listings:

        if (listing_key in product_key or product_key in listing_key ):
            possible_matches = listings.get(listing_key, [])
            for listing in possible_matches:#listings[key]:
                if not listing['matched']:
                    #print("listing title: %s" % (listing.get('title')))

                    title_keywords = tokenize(listing['title'])
                    #print("listing keywords: ")
                    #print(title_keywords)

                    # all product keywords contained in (subset of) listing title
                    if set(product_keywords) < set(title_keywords):
                        #print('match found:  %s' % (listing['title']))
                        listing['matched'] = True
                        matches.append(listing)

                        #possible_matches.remove(listing) # listing can only be matched once
                else:
                    title_keywords = tokenize(listing['title'])

                    # all the cases which could potentially belong to 2 different products
                    if set(product_keywords) < set(title_keywords):
                        print('listing found with 2 or more possible products: %s' % (listing['title']))

    

    #return len(matches)
    return {'product_name' : product.get('product_name'), 'listings' : matches }


def find_matches(product, listings):

    #print("product name: %s" % (product.get('product_name')))

    matches = []


    # correct listing must be from same manufacturer and contain product model and family in title
    key = format_key(product['manufacturer'])
    #print("manufacturer key: %s" % (key))
    product_keywords = tokenize(product['model']) + tokenize(product.get('family', ''))#+ tokenize(product['family'])
    #print("product keywords: ")
    #print(product_keywords)
    possible_matches = listings.get(key, [])
    for listing in possible_matches:#listings[key]:
        #print("listing title: %s" % (listing.get('title')))

        title_keywords = tokenize(listing['title'])
        #print("listing keywords: ")
        #print(title_keywords)

        # all product keywords contained in (subset of) listing title
        if set(product_keywords) < set(title_keywords):
            #print('match found:  %s' % (listing['title']))
            matches.append(listing)
            possible_matches.remove(listing) # listing can only be matched once

    return len(matches)

    # each product can have multiple listings
    # a listing may match at most one product

    # different manufacturer does NOT guarantee they aren't a match
    # Nikon vs Nikon Electronic, Konika Minolta vs Minolta
    # tradeoff is less recall for much faster search (being able to use manufacturer as key)
    # example:
    # product:
    #{"product_name":"Nikon_Coolpix_L22","manufacturer":"Nikon","model":"L22","family":"Coolpix","announced-date":"2010-02-02T19:00:00.000-05:00"}
    #matching listing:
    # {"title":"Nikon Coolpix L22 12.1MP Digital Camera with 3.6x Optical Zoom and 3.0-Inch LCD (Black)","manufacturer":"Nikon Electronic Imaging","currency":"CAD","price":"129.99"}

    # ACCESORY bundle that doesn't match (or does it?):
    # {"title":"Nikon Coolpix L22 12.0MP Digital Camera with 3.6x Optical Zoom and 3.0-Inch LCD (Silver) 4GB BigVALUEInc Accessory Saver NiMH Bundle","manufacturer":"Nikon","currency":"USD","price":"107.95"}


    # without manufacturer as key, bestcase runtime is n^2
    # with manufacturer, bestcase runtime is n
    # determine recall while using manufacturer as key


    # match criteria:
    # same manufacturer
    # all keywords in model, family are present in listing title
    # price is within acceptable variance of other listings?

    """
    Product
    {
    "product_name": String // A unique id for the product
    "manufacturer": String
    "family": String // optional grouping of products
    "model": String
    "announced-date": String // ISO-8601 formatted date string, e.g. 2011-04-28T19:00:00.000-05:00
    }
    Listing
    {
    "title": String // description of product for sale
    "manufacturer": String // who manufactures the product for sale
    "currency": String // currency code, e.g. USD, CAD, GBP, etc.
    "price": String // price, e.g. 19.99, 100.00
    }

    """


def write_result(results):
    with open('./results.txt', 'w') as f:
        for result in results:
            f.write(str(result))



def main(products_path, listings_path):

    # test_keys(listings_path)
    start_time = time.time()
    
    products = create_list(products_path) # list

    listings = create_dict(listings_path) # dict

    n_matched_listings = 0

    results = []

    # start by mapping the manufacturer - correct listings must at least be from same manufacturer
    # since this is the best criteria, create a hashmap using manufacturer as key, then we only have the check the listing from the same manufacturer for each product
    # worst case runtime is n^2 (all listings are same manufacturer), best case is n (1 listing per manufacturer)

    
    for product in products:
    #for i in range(len(products)):
        #print("\n-------%d--------\n" % (i))
        #product = products[i]
        #n_matched_listings += find_matches_deep(product, listings)
        result = find_matches_deep(product, listings)
        n_matched_listings += len(result['listings'])
        results.append(result)

    #print results
    print("%d matches found for %d products" % (n_matched_listings, len(products)))

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

