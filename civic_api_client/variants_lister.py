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
        self.civic_url = self.define_civic_url(variant_details)

    def define_civic_url(self, variant_details):
        "Define the CIVIC URL for the variant"
        if 'gene_id' not in variant_details:
            variant_details['gene_id'] = "NA"
        return "https://civic.genome.wustl.edu/#/events/genes/" + \
               str(variant_details['gene_id']) + "/summary/variants/" + \
               str(variant_details['id']) + "/summary#variant"

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
        try:
            rval = (int(self.coordinates['start']) > \
             int(self.coordinates['stop'])) or \
            (int(self.coordinates['start2']) > \
             int(self.coordinates['stop2']))
        except ValueError:
            return True
        return rval

    #Returns true if ref/variant base not in [A,C,G,T,N]
    def wrong_base(self):
        "Are both the ref/variant base in [A,C,G,T,N,None]"
        allowed_nucs = ['A', 'C', 'G', 'T', 'N']
        return (self.ref_base not in allowed_nucs or
                self.var_base not in allowed_nucs)

    #Returns true if variant length within limit or coordinates undefined
    def max_var_length(self):
        "Does the variant have start - stop <= max_var_length"
        if self.coordinates and self.coordinates['stop'] and \
           self.coordinates['start']:
            try:
                rval = int(self.coordinates['stop']) - \
                        int(self.coordinates['start']) < \
                        self.args.max_var_length
            except:
                return True
            return rval

    def satisfies_filters(self):
        "Does the variant satisfy any one of the conditions"
        satisfies = True
        if self.coordinates:
            if self.args.no_coords:
                satisfies = self.no_coords()
            if not satisfies and self.args.wrong_coords:
                satisfies = self.wrong_coords()
            if not satisfies and self.args.wrong_base:
                satisfies = self.wrong_base()
            if self.args.max_var_length:
                satisfies = satisfies and self.max_var_length()
        else:
            satisfies = False
        return satisfies

    def print1(self):
        "Print variant details"
        print   "ID: ", \
                self.id, \
                "Name: ", \
                self.name, \
                "Ref base: ", \
                self.ref_base, \
                "Var base: ", \
                self.var_base, \
                "Coordinate1: ", \
                self.coordinates['chromosome'], \
                self.coordinates['start'], \
                self.coordinates['stop'], \
                "Coordinate2: ", \
                self.coordinates['chromosome2'], \
                self.coordinates['start2'], \
                self.coordinates['stop2'], \
                "URL: ", \
                self.civic_url

class VariantsLister:
    """Represent the variants in CIVIC"""
    #Flag to select variants with no co-ordinates
    no_coords = False
    #URL to the CIVIC API
    civic_url = 'https://civic.genome.wustl.edu/api/'
    #List of variant details
    all_variant_details = []
    #Details of variants satisfying filters
    filtered_variant_details = []
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
        parser.add_argument("--wrong-base",
            action='store_true',
            help = "Print variants where ref/var base is not in [A,C,G,T,N,None]",
        )
        parser.add_argument("--max-gene-count",
            help = "Maximum number of genes to query from CIVIC",
            type = int,
            default = 100000
        )
        parser.add_argument("--max-var-length",
            help = "Maximum length of the variants to query from CIVIC",
            type = int,
        )
        parser.add_argument("--web",
            action='store_true',
            help = "Publish variants to a webpage."
        )
        args = parser.parse_args(self.args)
        if args.max_gene_count:
            print "Max number of genes to query is ",args.max_gene_count
        if args.max_var_length:
            print "Max length of variants displayed is ",args.max_var_length
        return args

    def get_civic_genes(self):
        "Get a list of genes from CIVIC"
        genes_url = self.civic_url + 'genes?count=' + str(self.args.max_gene_count)
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

    def filter_variants(self):
        "Filter the variant details"
        for variant_details in self.all_variant_details:
            vd1 = VariantDetails(self.args, variant_details)
            if vd1.satisfies_filters():
                self.filtered_variant_details.append(vd1)

    def print_variant_coordinates_screen(self):
        "Print the details of the variants to screen"
        for vd1 in self.filtered_variant_details:
            vd1.print1()

    def print_variant_coordinates_web(self):
        "Publish to web page"
        app = Flask("civic_api_client")
        @app.route("/")
        def template_test():
                return render_template('variants.html', \
                        filtered_variant_details = self.filtered_variant_details)
        app.run(debug=True)

    def main(self):
        "Execution starts here"
        self.args = self.parse_args()
        self.get_civic_genes()
        variant_ids = self.get_variant_ids()
        for variant_id in variant_ids:
            variant_detail = self.get_variant_details(variant_id)
            if 'id' not in variant_detail:
                variant_detail['id'] = variant_id
            self.all_variant_details.append(variant_detail)
        self.filter_variants()
        if self.args.web:
            self.print_variant_coordinates_web()
        else:
            self.print_variant_coordinates_screen()
