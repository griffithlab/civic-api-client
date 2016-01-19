import sys

import civic_api_client
from variants_lister import VariantsLister

def usage():
    "Defines usage for the tool"
    print "civic-api-client command options"
    print "Commands:"
    print "\tvariants-list"

def main():
    "Everything starts here"
    if len(sys.argv) >= 2:
        if sys.argv[1] == "variants-list":
            vl1 = VariantsLister(sys.argv[2:])
            return vl1.main()
    return usage()

if __name__ == '__main__':
    main()
