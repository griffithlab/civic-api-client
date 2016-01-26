"variants_lister.py - Get variants using the CIVIC API"

import argparse
from flask import Flask, render_template
import json
import requests

import civic_api_client

class VariantDetails:
    coordinates = {}
    args = []

    def __init__(self, args, variant_details):
        "Constructor"
        self.args = args
        self.coordinates = None
        self.name = None
        self.id = None
        self.ref_base = None
        self.var_base = None
        self.parse_variant_details(variant_details)

    def parse_variant_details(self, variant_details):
        "Parse variant details into class members"
        if 'coordinates' in variant_details:
            self.coordinates = variant_details['coordinates']
        if 'name' in variant_details:
            self.name = variant_details['name']
        if 'id' in variant_details:
            self.id = variant_details['id']
        if 'reference_bases' in variant_details:
            self.ref_base = variant_details['reference_bases']
        if 'variant_bases' in variant_details:
            self.var_base = variant_details['variant_bases']

    #Returns true if the variant does not have defined coordinates
    def no_coords(self):
        "Does the variant have the chr, start and stop defined"
        return self.coordinates['chromosome'] == None or \
               self.coordinates['start'] == None or \
               self.coordinates['stop'] == None

    #Returns true if the variant start > stop
    def wrong_coords(self):
        "Does the variant have start > stop"
        return (self.coordinates['start'] > \
               self.coordinates['stop']) or \
               (self.coordinates['start2'] > \
               self.coordinates['stop2'])

    def satisfies_filters(self):
        "Does the variant satisfy any one of the conditions"
        satisfies = True
        if self.coordinates:
            if self.args.no_coords:
                satisfies = satisfies and self.no_coords()
            if self.args.wrong_coords:
                satisfies = satisfies and self.wrong_coords()
        else:
            satisfies = False
        return satisfies

    def print1(self):
        "Print variant details"
        print   "ID: ", \
                self.id, \
                "Name: ", \
                self.name, \
                "Coordinate1: ", \
                self.coordinates['chromosome'], \
                self.coordinates['start'], \
                self.coordinates['stop'], \
                "Coordinate2: ", \
                self.coordinates['chromosome2'], \
                self.coordinates['start2'], \
                self.coordinates['stop2']

class VariantsLister:
    """Represent the variants in CIVIC"""
    #Flag to select variants with no co-ordinates
    no_coords = False
    #URL to the CIVIC API
    civic_url = 'https://civic.genome.wustl.edu/api/'
    #Max number of genes to query
    max_gene_count = 100000
    #List of variant details
    all_variant_details = []
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
        parser.add_argument("--wrong-coords",
            action='store_true',
            help = "Print variants where start > stop",
        )
        parser.add_argument("--max-gene-count",
            help = "Maximum number of genes to query from CIVIC",
            type = int,
        )
        parser.add_argument("--web",
            action='store_true',
            help = "Publish variants to a webpage."
        )
        args = parser.parse_args(self.args)
        if args.max_gene_count:
            self.max_gene_count = args.max_gene_count
            print "Max number of genes to query is ",args.max_gene_count
        return args

    def get_civic_genes(self):
        "Get a list of genes from CIVIC"
        genes_url = self.civic_url + 'genes?count=' + str(self.max_gene_count)
        self.genes = sorted(requests.get(genes_url).json(), \
                            key=lambda key: int(key['id']))

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

    def print_variant_coordinates_screen(self):
        "Parse the details of the variants"
        for variant_details in self.all_variant_details:
            vd1 = VariantDetails(self.args, variant_details)
            if vd1.satisfies_filters():
                vd1.print1()

    def add_variant_detail(self, variant_id, variant_detail):
        "Append variant detail to list of variant details"
        if 'id' not in variant_detail:
            variant_detail['id'] = variant_id
        self.all_variant_details.append(variant_detail)

    def print_variant_coordinates_web(self):
        "Publish to web page"
        app = Flask("civic_api_client")
        @app.route("/")
        def template_test():
                return render_template('variants.html', \
                        all_variant_details = self.all_variant_details)
        app.run(debug=True)

    def main(self):
        "Execution starts here"
        self.args = self.parse_args()
        self.get_civic_genes()
        variant_ids = self.get_variant_ids()
        for variant_id in variant_ids:
            variant_detail = self.get_variant_details(variant_id)
            self.add_variant_detail(variant_id, variant_detail)
        if self.args.web:
            self.print_variant_coordinates_web()
        else:
            self.print_variant_coordinates_screen()
