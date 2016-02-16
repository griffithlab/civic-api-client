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
    variant_id = ""
    doid = ""
    variant_civic_url = ""
    evi_id = ""
    error = ""

    def __init__(self, variant_id, doid, variant_civic_url,evidence_id, error_type, evidence_type):
        "Constructor"
        self.variant_id = variant_id
        self.doid = doid
        self.variant_civic_url = variant_civic_url
        self.evi_id = evidence_id
        self.error = str(error_type)
        self.evi_type = evidence_type

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
            help = "Print evidence-items with improper DOID.(not defined"\
                    "on disease-ontology.org)"
        )
        parser.add_argument("--drug",
            action='store_true',
            help = "Print predictive evidence-items without drug defined."
        )
        parser.add_argument("--max-gene-count",
            help = "Maximum number of genes to query from CIVIC [100,000]",
            type = int,
            default = 100000
        )
        parser.add_argument("--evi_type",
            type = str,
            default = "All",
            help = "Speicify one evidence_type to check (default = All)"\
                    "Chose from Predictive,Diagnostic,Prognostic or All"
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
            doid = evidence_item['disease']['doid']
            #Query each DOID once
            if doid not in self.valid_doids:
                url = utils.disease_ontology_api_url() + \
                        "metadata/DOID:" + str(doid)
                r = requests.get(url, verify = False)
                try:
                    r.raise_for_status()
                except requests.exceptions.HTTPError:
                    ei1 = EvidenceItems(variant_id, doid, \
                                        VariantDetails.define_civic_url(variant_detail), \
                                        evidence_item['id'],"DOID",evidence_item['evidence_type'])
                    self.invalid_eis.append(ei1)
                    continue
                self.valid_doids[doid] = 1


    # New function added by Lei
    def check_drug_for_pre(self, variant_id, variant_detail,evidence_items):
        "Check if predictive evidence items have drug information"
        for evidence_item in evidence_items:
            doid = evidence_item['disease']['doid']
            #For the same output format add doid
            drugs = evidence_item['drugs']
            evi_type_to_check = 0

            if self.args.evi_type == evidence_item['evidence_type'] or self.args.evi_type == "All":
                evi_type_to_check = 1
            if evi_type_to_check == 0:
                continue

            if len(drugs) == 1 and drugs[0]['name'] == "N/A":
                ei1 = EvidenceItems(variant_id, doid, \
                                    VariantDetails.define_civic_url(variant_detail), \
                                    evidence_item['id'],"NA_drug_names",evidence_item['evidence_type'])
                self.invalid_eis.append(ei1)
            #if evidence_item['evidence_type'] == "Predictive":
            # For predictive evidence, check if there's "drugs"
            if not drugs:
                ei1 = EvidenceItems(variant_id, doid, \
                                    VariantDetails.define_civic_url(variant_detail), \
                                    evidence_item['id'],"No drug",evidence_item['evidence_type'])
                self.invalid_eis.append(ei1)
        return


    def display_invalid_eis(self):
        "Display the invalid evidence_items"
        if self.args.web:
            self.display_invalid_eis_web()
        else:
            sys.stderr.write("Printing invalid DOIDs\n")
            print "\nDOID\tvariant_ID\tvariant_civic_url"
            for ei1 in self.invalid_eis:
                if ei1.error == "DOID":
                    print str(ei1.evi_id) + "\t" + str(ei1.doid) + "\t" + str(ei1.variant_id) + "\t" + ei1.variant_civic_url + "\n"
            sys.stderr.write("Pringting invalid drug names\n")
            print "\nEvidence_ID\tvariant_ID\tvariant_civic_url"
            for ei1 in self.invalid_eis:
                if ei1.error == "NA_drug_names":
                    print str(ei1.evi_id) + "\t" + str(ei1.variant_id) + "\t" + ei1.variant_civic_url + "\n"
            sys.stderr.write("Pringting predictive evidence without any drug\n")
            print "\nEvidence_ID\tvariant_ID\tvariant_civic_url"
            for ei1 in self.invalid_eis:
                if ei1.error == "No drug":
                    print str(ei1.evi_id) + "\t" + str(ei1.variant_id) + "\t" + ei1.variant_civic_url + "\n"

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

    def get_invalid_eis(self):
        "Return the list of invalid DOIDs"
        return self.invalid_eis

    def main(self):
        "Execution starts here"
        self.parse_args()
        self.create_invalid_eis_list()
        self.display_invalid_eis()
