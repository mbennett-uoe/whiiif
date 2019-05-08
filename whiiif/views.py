import json
import re

from flask import render_template, request, url_for
import requests
import bleach
from whiiif import app


@app.route('/')
def index():
    app.logger.warning('sample message')
    return render_template('index.html')

@app.route('/search/<manifest>')
def search(manifest):
    q = bleach.clean(request.args.get("q"), strip=True, tags=[])
    manifest_regexp = re.compile(r'[^A-Za-z0-9-]')
    manifest = manifest_regexp.sub("", manifest)
    unimplemented = {"motivation", "date", "user"}
    ignored = list(set(request.args.keys()) & unimplemented)

    query_url = app.config["SOLR_URL"] + "/" + app.config["SOLR_CORE"] + \
                "/select?&df=ocr_text&hl.fl=ocr_text&hl.snippets=4096&hl=on&hl.ocr.absoluteHighlights=true" + \
                "&hl.ocr.contextBlock=line&hl.ocr.contextSize=2&hl.ocr.limitBlock=page" + \
                "&fq=id:" + manifest + "&q=" + q
    solr_results = requests.get(query_url)
    results_json = solr_results.json()

    docs = results_json["response"]["docs"]

    results = []
    total_results = 0
    for doc in docs:
        snippets = results_json["ocrHighlighting"][doc["id"]]["ocr_text"]["snippets"]
        total_results +=  int(results_json["ocrHighlighting"][doc["id"]]["ocr_text"]["numTotal"])
        for fragment in snippets:
            #matches = re.findall('<em>(.*?)</em>', fragment["text"])
            canvas = fragment["page"]
            for highlight in fragment["highlights"]:
                for part in highlight:
                    x = part["ulx"]
                    y = part["uly"]
                    w = part["lrx"] - part["ulx"]
                    h = part["lry"] - part["uly"]
                    results.append({"manifest_id": doc["id"],
                                    "manifest_url": doc["manifest_url"],#.replace("https","http"),
                                    "canvas_id": canvas,
                                    "coords": "{},{},{},{}".format(x,y,w,h),
                                    "chars": part["text"]})

    response_dict = make_annotations(results, total_results, ignored)

    response = app.response_class(
        response=json.dumps(response_dict),
        mimetype='application/json',
        headers=[('Access-Control-Allow-Origin', '*')]
        )
    return response

def make_annotations(results, hit_count, ignored):

    search_id = request.url

    anno_base = {"@context": ["http://iiif.io/api/presentation/2/context.json",
                              "http://iiif.io/api/search/1/context.json"],
                 "@id": search_id,
                 "@type": "sc:AnnotationList",
                 "within": {"@type": "sc:Layer",
                            "total": hit_count,
                            "ignored": ignored
                            },
                 "resources": []}

    for idx, result in enumerate(results):
        result_base = {"@id": "uun:whiiif:%s:%s:%s"%(result["manifest_id"], result["canvas_id"], idx),
                       "@type": "oa:Annotation",
                       "motivation": "sc:painting",
                       "resource": {"@type": "cnt:ContentAsText",
                                    "chars": result["chars"]},
                       "on": "{}/canvas/{}#xywh={}".format(result["manifest_url"], result["canvas_id"], result["coords"])
                       }
        anno_base["resources"].append(result_base)

    return anno_base

