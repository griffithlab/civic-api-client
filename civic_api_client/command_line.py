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

def main():
    "Everything starts here"
    if len(sys.argv) >= 2:
        if sys.argv[1] == "variants-list":
            vl1 = VariantsLister(sys.argv[2:])
            return vl1.main()
        if sys.argv[1] == "evidence-items-list":
            eil1 = EvidenceItemsLister(sys.argv[2:])
            return eil1.main()
    return usage()

if __name__ == '__main__':
    main()
