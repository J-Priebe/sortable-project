# sortable-project
Sortable take-home record linking project

## Usage (Requires Python 2.7)
Clone repository and run:

`python feature_match.py`

The results will be stored in `results.txt`.

## About
https://sortable.com/project/

Finds the best product match (if any) for each listing. A match must meet the following criteria:
- The manufacturer is the same for product and listing (exact match or substring)
- Keywords from product model and family must be present in the listing title

A scoring system reduces false positives:
- Longer keywords matches are scored higher
- Listings with two or more equal-scoring products are discarded due to ambiguity
