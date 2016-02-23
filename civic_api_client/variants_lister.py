"variants_lister.py - Get variants using the CIVIC API"

import argparse
from flask import Flask, render_template
import json
import requests
requests.packages.urllib3.disable_warnings()

import civic_api_client
import utils

class VariantDetails:
    coordinates = {}
    args = []

    def __init__(self, args, variant_details):
        "Constructor"
        self.args = args
        self.coordinates = None
        self.name = None
        self.id = None
        self.gene_name = None
        self.ref_base = None
        self.var_base = None
        self.parse_variant_details(variant_details)
        self.civic_url = self.define_civic_url(variant_details)
        self.gene_id = None
        self.error_type = None

    @classmethod
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
        if 'entrez_name' in variant_details:
            self.gene_name = variant_details['entrez_name']
        if 'reference_bases' in variant_details['coordinates']:
            self.ref_base = variant_details['coordinates']['reference_bases']
        if 'variant_bases' in variant_details['coordinates']:
            self.var_base = variant_details['coordinates']['variant_bases']
        if 'gene_id' in variant_details:
            self.gene_id = variant_details['gene_id']

    #Returns true if the variant does not have defined coordinates
    def no_coords(self):
        "Does the variant have the chr, start and stop defined"
        if self.error_type != None:
            return True
        coord = self.coordinates['chromosome'] or \
                self.coordinates['start'] or \
                self.coordinates['stop']
        if not coord and self.error_type == None:   
            self.error_type = "No coordinate"
        return coord

    #Returns true if the variant start > stop
    def wrong_coords(self):
        "Does the variant have start > stop"
        rval = False
        if self.error_type != None:
            return True

        try:
            rval = (int(self.coordinates['start']) > \
             int(self.coordinates['stop'])) 
        except ValueError:
            self.error_type = "Wrong coordinates"
            return True

        if self.coordinates['start2'] and \
        self.coordinates['stop2'] and \
        not rval:
            rval = (int(self.coordinates['start2']) > \
             int(self.coordinates['stop2']))

        if rval and self.error_type == None:
            self.error_type = "Wrong coordinates"

        return rval

    #Returns true if ref/variant base not in [A,C,G,T,N]
    def wrong_base(self):
        "Are both the ref/variant base in [A,C,G,T,N,None]"
        if self.error_type != None:
            return True
        allowed_nucs = ['A', 'C', 'G', 'T', 'N']
        if (self.ref_base not in allowed_nucs or self.var_base not in allowed_nucs):
            if self.error_type == None:
                self.error_type = "Wrong base"
        return (self.ref_base not in allowed_nucs or
                self.var_base not in allowed_nucs)

    #Returns true if variant length within limit or coordinates undefined
    def max_var_length(self):
        "Does the variant have start - stop <= max_var_length"
        if self.error_type != None:
            return True
        if self.coordinates and self.coordinates['stop'] and \
           self.coordinates['start']:
            try:
                rval = int(self.coordinates['stop']) - \
                        int(self.coordinates['start']) < \
                        self.args.max_var_length
            except:
                if self.error_type == None:
                    self.error_type = "Max variant length"
                return True

            if rval and self.error_type == None:
                self.error_type = "Max variant length"

            return rval

    def satisfies_filters(self):
        "Does the variant satisfy any one of the conditions"
        satisfies = True

        if self.coordinates:
            nocoodrs = self.no_coords() 
            wrongcoords = self.wrong_coords()
            wrongbase = self.wrong_base()  
            maxvarlength = self.max_var_length()

            if self.error_type == None:
                return False

            if self.args.no_coords:
                if self.error_type == "No coordinate":
                    return True
            if self.args.wrong_coords:
                if self.error_type == "Wrong coordinates":
                    return True
            if self.args.wrong_base:
                if self.error_type == "Wrong base":
                    return True
            if self.args.max_var_length:
                if self.error_type == "Max variant length":
                    return True
        else:
            satisfies = False

        return satisfies

    def print1(self):
        "Print variant details"
        print   "ID: ", \
                self.id, \
                "Name: ", \
                self.name, \
                "Gene name: ", \
                self.gene_name, \
                "Error type: ", \
                self.error_type, \
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
            help = "Maximum number of genes to query from CIVIC [100,000]",
            type = int,
            default = 100000
        )
        parser.add_argument("--max-var-length",
            help = "Maximum length of the variants to query from CIVIC [INF]",
            type = int,
        )
        parser.add_argument("--web",
            action='store_true',
            help = "Publish variants to a webpage."
        )
        args = parser.parse_args(self.args)
        print "Max number of genes to query is ",args.max_gene_count
        if args.max_var_length:
            print "Max length of variants displayed is ",args.max_var_length
        self.args = args

    def get_civic_genes(self):
        "Get a list of genes from CIVIC"
        genes_url = utils.civic_api_url() + 'genes?count=' + str(self.args.max_gene_count)
        self.genes = sorted(requests.get(genes_url, verify = False).json(), \
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
        variant_url = utils.civic_api_url() + 'variants/' + str(variant_id)
        return requests.get(variant_url, verify = False).json()

    def filter_variants(self):
        "Filter the variant details"
        for variant_details in self.all_variant_details:
            vd1 = VariantDetails(self.args, variant_details)
            if vd1.satisfies_filters():
                self.filtered_variant_details.append(vd1)

    def get_filtered_variant_details(self):
        "Return the list of filtered variant details"
        return self.filtered_variant_details

    def print_variant_coordinates(self):
        "Print the details of the variants to screen"
        if self.args.web:
            self.print_variant_coordinates_web()
        else:
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

    def create_filtered_variants_list(self):
        "Get variants from CIViC and filter them"
        self.get_civic_genes()
        variant_ids = self.get_variant_ids()
        for variant_id in variant_ids:
            variant_detail = self.get_variant_details(variant_id)
            if 'id' not in variant_detail:
                variant_detail['id'] = variant_id
            self.all_variant_details.append(variant_detail)
        self.filter_variants()

    def main(self):
        "Execution starts here"
        self.parse_args()
        self.create_filtered_variants_list()
        self.print_variant_coordinates()
