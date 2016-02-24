"variants_lister.py - Get variants using the CIVIC API"

import argparse
from flask import Flask, render_template, url_for
import json
import requests
requests.packages.urllib3.disable_warnings()
import sys

import civic_api_client
import utils
from variants_lister import VariantsLister, VariantDetails

class EvidenceItems:
    
    # Upstream infomation of variants and genes
    disease = {}
    #list of drugs
    drugs = []
    error = ""

    def __init__(self, variant_details, evidence_items, error_type):
        "Constructor"
        self.error = str(error_type)
        self.variant_id = None
        self.variant_name = None
        self.gene_name = None
        self.evi_id = None
        self.evi_type = None
        self.doid = None
        self.parse_variant_details(variant_details)
        self.parse_evidence_details(evidence_items)
        self.evidence_civic_url = self.define_evidence_url(variant_details,evidence_items)
        self.variant_civic_url = VariantDetails.define_civic_url(variant_details)
        

    @classmethod       
    def define_evidence_url(self, variant_details, evidence_items):
        "Define the CIVIC URL for the evidence"
        if 'gene_id' not in variant_details:
            variant_details['gene_id'] = "NA"
        return "https://civic.genome.wustl.edu/#/events/genes/" + \
               str(variant_details['gene_id']) + "/summary/variants/" + \
               str(variant_details['id']) + "/summary/evidence/" + \
               str(evidence_items['id']) + "/summary#evidence"

    def parse_variant_details(self, variant_details):
        "Parse variant details into class members"
        if 'name' in variant_details:
            self.variant_name = variant_details['name']
        if 'id' in variant_details:
            self.variant_id = variant_details['id']
        if 'entrez_name' in variant_details:
            self.gene_name = variant_details['entrez_name']

    def parse_evidence_details(self, evidence_items):
        "Parse evidence details into class members"
        if 'id' in evidence_items:
            self.evi_id = evidence_items['id']
        if 'evidence_type' in evidence_items:
            self.evi_type = evidence_items['evidence_type']
        if 'drugs' in evidence_items:
            self.drugs = evidence_items['drugs']
        if 'disease' in evidence_items:
            self.disease = evidence_items['disease']
        #if 'doid' in evidence_items['disease']:
         #   self.doid = evidence_items['disease']['doid']

        

class EvidenceItemsLister:
    """Represent the evidence-items in CIVIC"""
    valid_doids = {}
    invalid_eis = []
    def __init__(self, args):
        "Constructor"
        self.args = args
    def parse_args(self):
        "Parse command-line arguments"
        parser = argparse.ArgumentParser(description="civic-api-client version {}".format(civic_api_client.__version__),
            usage = "civic-api-client evidence-items-list",
            formatter_class = argparse.RawTextHelpFormatter,
        )
        parser.add_argument("--doid",
            action='store_true',
            help = "Print evidence-items with improper DOID (not defined"\
                    " on disease-ontology.org)."
        )
        parser.add_argument("--drug",
            action='store_true',
            help = "Print predictive evidence-items without drug defined."
        )
        parser.add_argument("--max-gene-count",
            help = "Maximum number of genes to query from CIVIC [100,000].",
            type = int,
            default = 100000
        )
        parser.add_argument("--evi-type",
            type = str,
            default = "All",
            help = "Specify one evidence_type to check (default = All)."\
                    " Chose from Predictive,Diagnostic,Prognostic or All."
        )
        parser.add_argument("--web",
            action='store_true',
            help = "Publish evidence-items to a webpage."
        )
        args = parser.parse_args(self.args)
        print "Max number of genes to query is ",args.max_gene_count
        self.args = args

    def check_doid(self, variant_id, variant_detail, evidence_items):
        "Check if DOID is valid, if not add to list of invalids"
        for evidence_item in evidence_items:
            if evidence_item['status'] == 'rejected':
                continue
            doid = evidence_item['disease']['doid']
            #Query each DOID once
            if doid not in self.valid_doids:
                url = utils.disease_ontology_api_url() + \
                        "metadata/DOID:" + str(doid)
                r = requests.get(url, verify = False)
                try:
                    r.raise_for_status()
                except requests.exceptions.HTTPError:
                    ei1 = EvidenceItems(variant_detail,evidence_item,"DOID")
                    self.invalid_eis.append(ei1)
                    continue
                self.valid_doids[doid] = 1


    def check_drug_for_pre(self, variant_id, variant_detail,evidence_items):
        "Check if predictive evidence items have drug information"
        for evidence_item in evidence_items:
            if evidence_item['status'] == 'rejected':
                continue
            doid = evidence_item['disease']['doid']
            #For the same output format add doid
            drugs = evidence_item['drugs']
            evi_type_to_check = 0

            if self.args.evi_type == evidence_item['evidence_type'] or self.args.evi_type == "All":
                evi_type_to_check = 1
            if evi_type_to_check == 0:
                continue

            if len(drugs) == 1 and drugs[0]['name'] == "N/A":
                ei1 = EvidenceItems(variant_detail,evidence_item,"Drug name is NA")
                self.invalid_eis.append(ei1)
            #if evidence_item['evidence_type'] == "Predictive":
            # For predictive evidence, check if there's "drugs"
            if not drugs:
                ei1 = EvidenceItems(variant_detail,evidence_item,"Drug was not defined")
                self.invalid_eis.append(ei1)
        return


    def display_invalid_eis(self):
        "Display the invalid evidence_items"
        if self.args.web:
            self.display_invalid_eis_web()
        else:
            for ei1 in self.invalid_eis:
                print   "Error_type: ", \
                        ei1.error, \
                        "Evidence_ID: ", \
                        ei1.evi_id, \
                        "Variant_id: ", \
                        ei1.variant_id, \
                        "Variant_name: ", \
                        ei1.variant_name, \
                        "Gene_name: ", \
                        ei1.gene_name, \
                        "Evidence_type: ", \
                        ei1.evi_type, \
                        "DOID: ", \
                        ei1.disease['doid'], \
                        "Evidence_URL: ", \
                        ei1.evidence_civic_url, \
                        "Variant_URL", \
                        ei1.variant_civic_url

    def display_invalid_eis_web(self):
        "Publish to web page"
        app = Flask("civic_api_client")
        @app.route("/")
        def template_test():
                return render_template('evidence-items.html', \
                        invalid_eis = self.invalid_eis)
        app.run(debug=True)

    def create_invalid_eis_list(self):
        "Create the list of invalid evidence items"
        vl1 = VariantsLister(self.args)
        vl1.get_civic_genes()
        variant_ids = vl1.get_variant_ids()
        for variant_id in variant_ids:
            variant_detail = vl1.get_variant_details(variant_id)
            if "evidence_items" in variant_detail:
                evidence_items = variant_detail['evidence_items']   
                if self.args.doid:
                    #If not valid, add to list of invalids
                    self.check_doid(variant_id, variant_detail, evidence_items)
                if self.args.drug:
                    #If drug doesn't exist, add to list of invalids
                    self.check_drug_for_pre(variant_id, variant_detail,evidence_items)
                # if neither of the flags were specified, do both checks
                if not (self.args.doid or self.args.drug):
                    self.check_doid(variant_id, variant_detail, evidence_items)
                    self.check_drug_for_pre(variant_id, variant_detail,evidence_items)

    def get_invalid_eis(self):
        "Return the list of invalid DOIDs"
        return self.invalid_eis

    def main(self):
        "Execution starts here"
        self.parse_args()
        self.create_invalid_eis_list()
        self.display_invalid_eis()
