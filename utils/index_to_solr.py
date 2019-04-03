#!/usr/bin/python3

""" index_to_solr.py: indexing tool for whiiif """

import whiiif.xml_constants as xc
from whiiif import app
import argparse
import json
import requests
import string
from lxml import etree

__version__ = '0.0.1'
DEBUG = False

def pipeline(alto, manifest, start_canvas = 0):
    dprint("Starting pipeline...")
    if not alto or not manifest:
        dprint("Missing ALTO or MANIFEST data")
        return False

    dprint("Loading ALTO file:", alto)
    xml = load_alto(alto)
    if xml is False:
        return False

    dprint("Identifying ALTO version by namespace")
    xmlns = find_namespace(xml)
    if xmlns is False:
        return False
    dprint("Namespace found:", xmlns)

    pages = xml.findall('./{%s}Layout/{%s}Page' % (xmlns, xmlns))
    dprint("Found %s page(s) in ALTO file" % len(pages))

    dprint("Loading manifest:", manifest)
    manifest_json = load_manifest(manifest)
    if manifest_json is False:
        return False

    # Customise this based on your way of identifying manifests
    # This turns http://myserver/iiif/manifests/myIdentifier.json -> myIdentifier
    manifest_id = manifest_json["@id"].split("/")[-1].replace(".json", "")

    canvases = manifest_json["sequences"][0]["canvases"]
    dprint("Found %s canvas(es) in manifest" % len(canvases))

    dprint("Start canvas:", start_canvas)
    if start_canvas > 0:
        if len(pages)+start_canvas != len(canvases):
            dprint("WARNING: Page/Canvas count mismatch: %s canvases (starting from Canvas #%s) != %s pages" %
                   (len(canvases)-start_canvas, start_canvas, len(pages)))
    else:
        if len(pages) != len(canvases):
            dprint("WARNING: Page count does not match Canvas count")

    for idx, page in enumerate(pages):
        canvas_idx = idx + start_canvas
        try:
            canvas = canvases[canvas_idx]
        except:
            dprint("Reached end of canvases before end of pages")
            break

        # Customise this based on your way of identifying manifests
        # This turns http://myserver/iiif/manifests/myIdentifier/page-1.json -> myIdentifier:page-1
        canvas_id = manifest_id + ":" + canvas["@id"].split("/")[-1].replace(".json", "")

        page_txt = ""
        words = {}
        annos = []
        for word in page.iterfind('.//{%s}String' % xmlns):
            x = word.attrib.get("HPOS")
            y = word.attrib.get("VPOS")
            w = word.attrib.get("WIDTH")
            h = word.attrib.get("HEIGHT")
            text = word.attrib.get("CONTENT")

            fragment = "%s,%s,%s,%s"%(x, y, w, h)
            page_txt += text + ' '

            plaintext = text.translate(str.maketrans('','', string.punctuation))

            if plaintext in words.keys():
                words[plaintext].append(fragment)
            else:
                words[plaintext] = [fragment]
            annos.append((fragment,text))

        result = add_solr_doc(manifest_id=manifest_id, manifest_url=manifest_json["@id"], canvas_id=canvas_id,
                              canvas_url=canvas["@id"], annos=annos, page_txt=page_txt, words=words)

        if result:
            dprint("Page",idx,"processed")
        else:
            dprint("Page", idx, "failed processing")
    dprint("Finished")


def load_manifest(manifest):
    try:
        manifest_json = json.load(open(manifest, 'r', encoding="UTF8"))
        return manifest_json
    except Exception as e:
        dprint("ERROR:", e)
        return False

def load_alto(alto):
    try:
        alto_file = etree.parse(alto)
        xml = alto_file.getroot()
        return xml
    except Exception as e:
        dprint("ERROR:", e)
        return False

def find_namespace(xml):
    if 'http://' in str(xml.tag.split('}')[0].strip('{')):
        xmlns = xml.tag.split('}')[0].strip('{')
    else:
        try:
            ns = xml.attrib
            xmlns = str(ns).split(' ')[1].strip('}').strip("'")
        except IndexError:
            dprint('WARNING: no namespace declaration found.')
            xmlns = 'no_namespace_found'

    if xmlns in xc.namespaces.values():
        return xmlns
    else:
        dprint('WARNING: namespace is not registered.')
        return False


def add_solr_doc(manifest_id, manifest_url, canvas_id, canvas_url, annos, page_txt, words):
    solr_doc = { "id": canvas_id,
                 "manifest_id": manifest_id,
                 "manifest_url": manifest_url,
                 "canvas_id": canvas_id,
                 "canvas_url": canvas_url,
                 "annotations": json.dumps(annos, ensure_ascii=False),
                 "page_text": page_txt,
                 "word_coords": json.dumps(words, ensure_ascii=False)
                 }

    solr_url = app.config["SOLR_URL"] + "/" + app.config["SOLR_CORE"] + "/update/json/docs"

    r = requests.post(solr_url, json=solr_doc, params=dict(softCommit="true"))
    if r.status_code == requests.codes.ok:
        return True
    else:
        dprint("ERROR posting to solr: ", r.content)
        return False

def dprint(*args):
    if DEBUG:
        print(*args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="index_to_solr: Import an ALTO XML to Solr",
        add_help=True)
    parser.add_argument('ALTO',
                        help='path to ALTO XML file')
    parser.add_argument('MANIFEST',
                        help='path to IIIF manifest')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__,
                        help='show version number and exit')
    parser.add_argument('-c',
                        action='store',
                        type=int,
                        metavar='CANVAS',
                        dest='canvas',
                        default=0,
                        help='start from specified canvas index')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='enable debug output')

    args = parser.parse_args()
    DEBUG = args.debug

    process = pipeline(args.ALTO, args.MANIFEST, args.canvas)
    if process:
        print("Completed successfully")

