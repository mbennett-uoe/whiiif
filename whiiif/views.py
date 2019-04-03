import json
import re

from flask import render_template, request
import requests

from whiiif import app


@app.route('/')
def index():
    app.logger.warning('sample message')
    return render_template('index.html')

@app.route('/search/<manifest>')
def search(manifest):
    q = request.args.get("q")
    unimplemented = {"motivation", "date", "user"}
    ignored = list(set(request.args.keys()) & unimplemented)

    query_url = app.config["SOLR_URL"] + "/" + app.config["SOLR_CORE"] + \
                "/select?&df=page_text&fl=canvas_id%2Ccanvas_url%2Cword_coords&hl.fl=page_text&hl.snippets=50&hl=on" + \
                "&fq=manifest_id:" + manifest + "&q=" + q
    solr_results = requests.get(query_url)
    results_json = solr_results.json()

    docs = results_json["response"]["docs"]

    results = []
    for doc in docs:
        hltext = results_json["highlighting"][doc["canvas_id"]]["page_text"]
        coords = json.loads(doc["word_coords"][0])
        for fragment in hltext:
            matches = re.findall('<em>(.*?)</em>', fragment)
            for match in matches:
                xywh = coords[match].pop()
                results.append({"canvas_id": doc["canvas_id"],
                                "canvas_url": doc["canvas_url"],
                                "coords": xywh,
                                "chars": match})

    response_dict = make_annotations(results, results_json["response"]["numFound"], ignored)

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
        result_base = {"@id": "uun:whiiif:%s:%s"%(result["canvas_id"], idx),
                       "@type": "oa:Annotation",
                       "motivation": "sc:painting",
                       "resource": {"@type": "cnt:ContentAsText",
                                    "chars": result["chars"]},
                       "on": result["canvas_url"] + "#xywh=" + result["coords"]
                       }
        anno_base["resources"].append(result_base)

    return anno_base

