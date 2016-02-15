from flask import Flask, render_template
import sys

import civic_api_client
from variants_lister import VariantsLister
from evidence_items_lister import EvidenceItemsLister

def usage():
    "Defines usage for the tool"
    print "civic-api-client command options"
    print "Commands:"
    print "\tvariants-list"
    print "\tevidence-items-list"
    print "\taction-items-web-view"

def main():
    "Everything starts here"
    if len(sys.argv) >= 2:
        if sys.argv[1] == "variants-list":
            vl1 = VariantsLister(sys.argv[2:])
            return vl1.main()
        elif sys.argv[1] == "evidence-items-list":
            eil1 = EvidenceItemsLister(sys.argv[2:])
            return eil1.main()
        elif sys.argv[1] == "action-items-web-view":
            web_view()
        else:
            return usage()

def web_view():
    "Setup the webview"
    app = Flask("civic_api_client")
    @app.route("/")
    def template_home():
        return render_template('home.html')
    @app.route("/evidence-items")
    def evidence_items():
        eil1 = EvidenceItemsLister(sys.argv[2:])
        eil1.parse_args()
        eil1.create_invalid_eis_list()
        invalid_eis = eil1.get_invalid_eis()
        return render_template('evidence-items.html', \
                invalid_eis = invalid_eis)
    @app.route("/variants")
    def variants():
        vl1 = VariantsLister(sys.argv[2:])
        vl1.parse_args()
        vl1.create_filtered_variants_list()
        filtered_variant_details = vl1.get_filtered_variant_details()
        return render_template('variants.html', \
                filtered_variant_details= filtered_variant_details)
    app.run(debug=True)

if __name__ == '__main__':
    main()
