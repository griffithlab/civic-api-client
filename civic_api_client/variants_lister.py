"variants_lister.py - Get variants using the CIVIC API"

import argparse
import json
import requests

import civic_api_client

class VariantsLister:
    """Represent the variants in CIVIC"""
    #Flag to select variants with no co-ordinates
    no_coords = False
    #URL to the CIVIC API
    civic_url = 'https://civic.genome.wustl.edu/api/'
    #Max number of genes to query
    max_gene_count = 100000
    #List of genes that were queried for
    genes = []
    #Arguments to this tool
    args = []
    def __init__(self, args):
        "Constructor"
        self.args = args
    def parse_args(self):
        "Parse command-line arguments"
        parser = argparse.ArgumentParser(description="civic-api-client version {}".format(civic_api_client.__version__),
            usage = "civic-api-client variants-list",
            formatter_class = argparse.RawTextHelpFormatter,
        )
        parser.add_argument("--no-coords",
            action='store_true',
            help = "Print variants with no coordinates defined"
        )
        return parser.parse_args(self.args)
    def get_civic_genes(self):
        "Get a list of genes from CIVIC"
        genes_url = self.civic_url + 'genes?count=' + str(self.max_gene_count)
        self.genes = sorted(requests.get(genes_url).json(), key=lambda key: int(key['id']))
    def get_variant_ids(self):
        "Get a list of variants using a list of genes"
        variant_ids = []
        for gene in self.genes:
            for variant in gene['variants']:
                variant_id = variant['id']
                if variant_id in variant_ids:
                    continue
                variant_ids.append(variant_id)
        return variant_ids
    def get_variant_details(self, variant_id):
        "Get the details for a variant given an ID"
        variant_url = self.civic_url + 'variants/' + str(variant_id)
        return requests.get(variant_url).json()
    def parse_variant_details(self, variant_id, variant_details):
        "Parse the details of the variants"
        if 'coordinates' in variant_details:
            print "ID: ", variant_details['id'], \
                    "Name: ", variant_details['name'], \
                    "Coordinate1: ", \
                    variant_details['coordinates']['chromosome'],\
                    variant_details['coordinates']['start'], \
                    variant_details['coordinates']['stop'], \
                    "Coordinate2: ", \
                    variant_details['coordinates']['chromosome2'],\
                    variant_details['coordinates']['start2'],\
                    variant_details['coordinates']['stop2']
        elif self.args.no_coords:
            print "coordinates unavailable: ", \
                  variant_id
    def main(self):
        "Execution starts here"
        self.args = self.parse_args()
        self.get_civic_genes()
        variant_ids = self.get_variant_ids()
        for variant_id in variant_ids:
            variant_details = self.get_variant_details(variant_id)
            self.parse_variant_details(variant_id, variant_details)
