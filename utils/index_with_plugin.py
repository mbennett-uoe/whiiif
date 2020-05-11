#!/usr/bin/python3

""" index_with_plugin.py: indexing tool for whiiif, using solr-ocrhighlighting """

import argparse
import json
from collections import OrderedDict
from os import path

import requests
from iiif_order import order_object

from whiiif import app

__version__ = '0.3.0'
DEBUG = True

def dprint(*args):
    if DEBUG:
        print(*args)


def pipeline(alto, manifest, identifier, modify):
    dprint("Starting pipeline...")
    dprint("Loading ALTO file:", alto)
    try:
        with open(alto, "r", encoding="utf8") as alto_file:
            alto_in = alto_file.read()
    except FileNotFoundError:
        print("ERROR: File {} not found".format(alto))
        return False

    if not identifier:
        identifier = path.splitext(path.basename(alto))[0]
        dprint("No identifier supplied, using", identifier)

    dprint("Escaping non-ASCII characters in ALTO")
    alto_out = alto_in.replace("encoding=\"UTF-8\"", "encoding=\"ASCII\"").encode('ascii', 'xmlcharrefreplace')
    out_path = path.join(app.config["XML_LOCATION"], identifier) + "_escaped.xml"
    dprint("Writing escaped file to:", out_path)
    try:
        with open(out_path, 'wb') as out_file:
            out_file.write(alto_out)
    except Exception as e:
        print("ERROR:", e)
        return False

    dprint("Loading manifest:", manifest)
    manifest_json = load_manifest(manifest)
    if manifest_json is False:
        return False

    solr_doc = {app.config["DOCUMENT_ID_FIELD"]: identifier,
                app.config["MANIFEST_URL_FIELD"]: manifest_json["@id"],
                app.config["OCR_TEXT_FIELD"]: out_path }

    solr_url = "{}/{}/update/json/docs".format(app.config["SOLR_URL"], app.config["SOLR_CORE"])

    dprint("Posting to SOLR:", solr_url)
    dprint("Document:", json.dumps(solr_doc, indent=4))

    r = requests.post(solr_url, json=solr_doc, params=dict(softCommit="true"))
    if r.status_code == requests.codes.ok:
        dprint("Successfully added to SOLR")
    else:
        print("ERROR posting to solr: ", r.content)
        return False

    if modify:
        dprint("Adding IIIF service to manifest file")
        app.app_context().push()
        search_url = "{}/search/{}".format(app.config["SERVER_NAME"], identifier)
        service_doc = {"@context": "http://iiif.io/api/search/1/context.json",
                       "@id": search_url,
                       "profile": "http://iiif.io/api/search/1/search"
                       }
        if "service" in manifest_json:
            if type(manifest_json["service"]) == list:
                manifest_json["service"].append(service_doc)
            elif type(manifest_json["service"]) == dict or type(manifest_json["service"]) == OrderedDict:
                manifest_json["service"] = [manifest_json["service"], service_doc]
            else:
                manifest_json["service"] = [manifest_json["service"], service_doc]
        else:
            manifest_json["service"] = service_doc

        ordered_manifest = order_object(manifest_json, "manifest", recursive=True)
        try:
            json.dump(ordered_manifest,open(manifest, 'w', encoding="UTF8"), indent=2)
            dprint("Added!")
        except Exception as e:
            dprint("ERROR:", e)

    return True

def load_manifest(manifest):
    try:
        manifest_json = json.load(open(manifest, 'r', encoding="UTF8"), object_pairs_hook=OrderedDict)
        return manifest_json
    except Exception as e:
        dprint("ERROR:", e)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import an ALTO XML / IIIF manifest pair to Solr, using the solr-ocrhighlighting plugin",
        add_help=True)
    parser.add_argument('ALTO',
                        help='path to ALTO XML file')
    parser.add_argument('MANIFEST',
                        help='path to IIIF manifest file')
    parser.add_argument('-i',
                        metavar='<ID>',
                        help='identifier for the document (if not supplied, truncated filename will be used)')
    parser.add_argument('-m','--modify',
                        help='modify the IIIF manifest to include the search service (this will overwrite \
                        the existing file)',
                        action='store_true')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__,
                        help='show version number and exit')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='enable debug output')

    args = parser.parse_args()
    DEBUG = args.debug

    process = pipeline(args.ALTO, args.MANIFEST, args.i, args.modify)
    if process:
        print("Completed successfully")


