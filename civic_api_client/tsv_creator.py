"tsv_creator.py - Get tsv file for UCSC genome browser track(special mission)"

import argparse
from flask import Flask, render_template, url_for
import json
import requests
requests.packages.urllib3.disable_warnings()
import sys
import time

import civic_api_client
import utils
from variants_lister import VariantsLister, VariantDetails
from evidence_items_lister import EvidenceItems, EvidenceItemsLister

class TsvEvidenceItmes:
    """What will be listed in tsv file"""

    def __init__(self, variant_details, evidence_items):
        "Constructor"
        # Exist columns
        self.gene_name = None 
        self.entrez_id = None 
        self.variant_name = None
        self.disease_name = None
        self.doid = None 
        self.drug_names = None  
        self.evi_type = None
        self.evi_dir = None
        self.cli_sig = None
        self.evi_summary = None 
        self.pub_id = None
        self.citation = None 
        self.rating = None

        # Added columns
        self.evi_status = None
        self.evi_id = None
        self.var_id = None     
        self.gene_id = None
        self.coordinates = None 
        self.var_summary = None 
        self.var_ori = None
        self.evidence_civic_url = EvidenceItems.define_evidence_url(variant_details,evidence_items)
        self.variant_civic_url = VariantDetails.define_civic_url(variant_details)
        self.gene_civic_url = self.define_gene_url(variant_details)

        self.parse_variant_details(variant_details)
        self.parse_evidence_details(evidence_items)

    def define_gene_url(self, variant_details):
        "Define the CIVIC URL for the gene"
        if 'gene_id' not in variant_details:
            variant_details['gene_id'] = "NA"
        return "https://civic.genome.wustl.edu/#/events/genes/" + \
               str(variant_details['gene_id']) + "/summary#gene/" 

    def parse_variant_details(self, variant_details):
        "Parse Variant Details into class members"
        if 'entrez_id' in variant_details:
            self.entrez_id = variant_details['entrez_id']
        if 'entrez_name' in variant_details:
            self.gene_name = variant_details['entrez_name']
        if 'name' in variant_details:
            self.variant_name = variant_details['name']       
        if 'id' in variant_details:
            self.var_id = variant_details['id']
        if 'gene_id' in variant_details:
            self.gene_id = variant_details['gene_id']
        if 'coordinates' in variant_details:
            self.coordinates = variant_details['coordinates'] 
        if 'description' in variant_details:
            self.var_summary = variant_details['description']

    def parse_evidence_details(self, evidence_items):
        "Parse evidence details into class members"
        if 'id' in evidence_items:
            self.evi_id = evidence_items['id']
        if 'evidence_type' in evidence_items:
            self.evi_type = evidence_items['evidence_type']
        if 'drugs' in evidence_items:
            self.drug_names = self.list_all_drugs(evidence_items['drugs'])
        if 'disease' in evidence_items:
            self.disease_name = evidence_items['disease']['name']
        if 'doid' in evidence_items['disease']:
            self.doid = evidence_items['disease']['doid']
        if 'evidence_direction' in evidence_items:
            self.evi_dir = evidence_items['evidence_direction']
        if 'clinical_significance' in evidence_items:
            self.cli_sig = evidence_items['clinical_significance']
        if 'description' in evidence_items:
            self.evi_summary = evidence_items['description']
        if 'pubmed_id' in evidence_items:
            self.pub_id = evidence_items['pubmed_id']
        if 'citation' in evidence_items:
            self.citation = evidence_items['citation']
        if 'rating' in evidence_items:
            self.rating = evidence_items['rating']
        if 'status' in evidence_items:
            self.evi_status = evidence_items['status']
        if 'variant_origin' in evidence_items:
            self.var_ori = evidence_items['variant_origin']

    def list_all_drugs(self,drugs_list):
        drugs = []
        drug_string = ""
        if drugs_list == None:
            return drug_string 
        for drug in drugs_list:
            if drug['name'] != None:
                drugs.append(drug['name'])
        drug_string= ','.join(drugs)
        return drug_string

    def list_all_pubchem_id(self,drugs_list):
        pubchem_ids = []
        pubchem_id_str = ""
        for drug in drugs_list:
            if drug['pubchem_id'] != None:
                pubchem_ids.append(drug['pubchem_id'])
        pubchem_id_str.join(pubchem_ids)
        return pubchem_id_str

    def make_str_for_print(self):
        "give row string for print out"
        row_string= self.gene_name+"\t"+  \
                    repr(self.entrez_id)+"\t"+ \
                    repr(self.variant_name)+"\t"+ \
                    repr(self.disease_name)+"\t"+ \
                    repr(self.doid)+"\t"+ \
                    repr(self.drug_names)+"\t"+ \
                    repr(self.evi_type)+"\t"+ \
                    repr(self.evi_dir)+"\t"+\
                    repr(self.cli_sig)+"\t"+ \
                    repr(self.evi_summary)+"\t"+\
                    repr(self.pub_id)+"\t"+ \
                    repr(self.citation)+"\t"+ \
                    repr(self.rating)+"\t"+ \
                    repr(self.evi_status)+"\t"+ \
                    repr(self.evi_id)+"\t"+ \
                    repr(self.var_id)+"\t"+ \
                    repr(self.gene_id)+"\t"+ \
                    repr(self.coordinates['chromosome'])+"\t"+ \
                    repr(self.coordinates['start'])+"\t"+ \
                    repr(self.coordinates['stop'])+"\t"+ \
                    repr(self.coordinates['reference_bases'])+"\t"+ \
                    repr(self.coordinates['variant_bases'])+"\t"+ \
                    repr(self.coordinates['representative_transcript'])+"\t"+ \
                    repr(self.coordinates['chromosome2'])+"\t"+ \
                    repr(self.coordinates['start2'])+"\t"+ \
                    repr(self.coordinates['stop2'])+"\t"+ \
                    repr(self.coordinates['representative_transcript2'])+"\t"+ \
                    repr(self.coordinates['ensembl_version'])+"\t"+ \
                    repr(self.coordinates['reference_build'])+"\t"+ \
                    repr(self.var_summary)+"\t"+ \
                    repr(self.var_ori)+"\t"+ \
                    repr(self.evidence_civic_url)+"\t"+ \
                    repr(self.variant_civic_url)+"\t"+ \
                    repr(self.gene_civic_url)+"\n"
        row_u_remove = row_string.replace('u\'','')
        row = row_u_remove.replace('\'','')
        return row         
    

class TsvFileLister:
    """List the evidence-items in CIVIC to tsv file"""
    def __init__(self, args):
        "Constructor"
        self.args = args
    def parse_args(self):
        "Parse command-line arguments"
        parser = argparse.ArgumentParser(description="civic-api-client version {}".format(civic_api_client.__version__),
            usage = "civic-api-client tsv_creator",
            formatter_class = argparse.RawTextHelpFormatter,
        )
        parser.add_argument("--max-gene-count",
            help = "Maximum number of genes to query from CIVIC [100,000].",
            type = int,
            default = 100000
        )
        args = parser.parse_args(self.args)
        print "Max number of genes to query is ",args.max_gene_count
        self.args = args

    def make_header(self):
        """Returen a header string for tsv file"""
        return  'gene'+'\t'+ \
                'entrez_id'+'\t'+ \
                'variant'+'\t'+ \
                'disease'+'\t'+ \
                'doid'+'\t'+ \
                'drugs'+'\t'+ \
                'evidence_type'+'\t'+ \
                'evidence_direction'+'\t'+ \
                'clinical_significance'+'\t'+ \
                'evidence_statement'+'\t'+ \
                'pubmed_id'+'\t'+ \
                'citation'+'\t'+ \
                'rating'+'\t'+ \
                'evidence_status'+'\t'+ \
                'evidence_id'+'\t'+ \
                'variant_id'+'\t'+ \
                'gene_id'+'\t'+ \
                'chromosome'+'\t'+ \
                'start'+'\t'+ \
                'stop'+'\t'+ \
                'reference_bases'+'\t'+ \
                'variant_bases'+'\t'+ \
                'representative_transcript'+'\t'+ \
                'chromosome2'+'\t'+ \
                'start2'+'\t'+ \
                'stop2'+'\t'+ \
                'representative_transcript2'+'\t'+ \
                'ensembl_version'+'\t'+ \
                'reference_build'+'\t'+ \
                'variant_summary'+'\t'+ \
                'variant_origin'+'\t'+ \
                'evidence_civic_url'+'\t'+ \
                'variant_civic_url'+'\t'+ \
                'gene_civic_url'+'\n'

    def get_info_and_print(self):
        "Get variants and evidence items "
        vl1 = VariantsLister(self.args)
        vl1.get_civic_genes()
        variant_ids = vl1.get_variant_ids()

        file_name = 'ClinicalEvidenceSummary_'+time.strftime('%d%m%Y')+'.tsv'
        output = open(file_name,'w')
        header = self.make_header()
        output.write(header)

        for variant_id in variant_ids:
            variant_detail = vl1.get_variant_details(variant_id)
            if "evidence_items" in variant_detail:
                evidence_items = variant_detail['evidence_items'] 
                for evidence_item in evidence_items:
                    tsv_item = TsvEvidenceItmes(variant_detail, evidence_item)
                    output.write(tsv_item.make_str_for_print())
        output.close()

    def main(self):
        "Execution starts here"
        self.parse_args()
        self.get_info_and_print()



