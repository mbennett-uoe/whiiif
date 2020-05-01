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
@app.route('/search-v1/<manifest>')
def search(manifest):
    q = bleach.clean(request.args.get("q"), strip=True, tags=[])
    manifest_regexp = re.compile(r'[^A-Za-z0-9-_]')
    manifest = manifest_regexp.sub("", manifest)
    unimplemented = {"motivation", "date", "user"}
    ignored = list(set(request.args.keys()) & unimplemented)

    query_url = app.config["SOLR_URL"] + "/" + app.config["SOLR_CORE"] + \
                "/select?hl=on&hl.ocr.absoluteHighlights=true" + \
                "&df=" + app.config["OCR_TEXT_FIELD"] + \
                "&hl.fl=" + app.config["OCR_TEXT_FIELD"] + \
                "&hl.snippets=" + app.config["WITHIN_MAX_RESULTS"] + \
                "&fq=" + app.config["DOCUMENT_ID_FIELD"] + manifest + \
                "&q=" + q
    #    return(query_url)
    solr_results = requests.get(query_url)
    results_json = solr_results.json()

    docs = results_json["response"]["docs"]

    results = []
    total_results = 0
    for doc in docs:
        snippets = results_json["ocrHighlighting"][doc["id"]]["ocr_text"]["snippets"]
        total_results += int(results_json["ocrHighlighting"][doc["id"]]["ocr_text"]["numTotal"])
        for fragment in snippets:
            # matches = re.findall('<em>(.*?)</em>', fragment["text"])
            canvas = fragment["page"]
            for highlight in fragment["highlights"]:
                grouped_hls = []
                for part in highlight:
                    x = part["ulx"]
                    y = part["uly"]
                    w = part["lrx"] - part["ulx"]
                    h = part["lry"] - part["uly"]
                    if "scale" in doc:
                        scale = doc["scale"]
                    else:
                        scale = 1
                    grouped_hls.append({"manifest_id": doc["id"],
                                        "manifest_url": doc["manifest_url"],  # .replace("https","http"),
                                        "canvas_id": canvas,
                                        "coords": "{},{},{},{}".format(x, y, w, h),
                                        "chars": part["text"],
                                        "scale": scale})
                results.append(grouped_hls)

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
                 "resources": [],
                 "hits": []}

    for idx, result in enumerate(results):
        part_ids = []
        part_chars = []
        for in_idx, result_part in enumerate(result):
            if in_idx > 0:
                suff = chr(97 + in_idx)
            else:
                suff = ""
            x, y, w, h = result_part["coords"].split(",")
            if result_part["scale"] != 1:
                x, y, w, h = int(x), int(y), int(w), int(h)
                x, y, w, h = int(x * result_part["scale"]), int(y * result_part["scale"]), int(
                    w * result_part["scale"]), int(h * result_part["scale"])
                x, y, w, h = str(x), str(y), str(w), str(h)
            result_base = {
                "@id": "uun:whiiif:%s:%s:%s%s" % (result_part["manifest_id"], result_part["canvas_id"], idx, suff),
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "resource": {"@type": "cnt:ContentAsText",
                             "chars": result_part["chars"]},
                #                           "on": "{}/canvas/{}#xywh={}".format(result_part["manifest_url"], result_part["canvas_id"], result_part["coords"])
                "on": "{}/canvas/{}#xywh={}".format(result_part["manifest_url"], result_part["canvas_id"],
                                                    ",".join([x, y, w, h]))
            }
            anno_base["resources"].append(result_base)
            part_ids.append(result_base["@id"])
            part_chars.append(result_part["chars"])

        hit_base = {"@type": "search:Hit",
                    "annotations": part_ids,
                    "match": " ".join(part_chars)}
        anno_base["hits"].append(hit_base)
    return anno_base


@app.route("/collection/search")
def collection_search():
    q = bleach.clean(request.args.get("q"), strip=True, tags=[])
    query_url = app.config["SOLR_URL"] + "/" + app.config["SOLR_CORE"] \
                + "/select?hl=on&rows=" + app.config["COLLECTION_MAX_RESULTS"] \
                + "&df=" + app.config["OCR_TEXT_FIELD"] \
                + "&hl.fl=" + app.config["OCR_TEXT_FIELD"] \
                + "&hl.snippets=" + app.config["COLLECTION_MAX_DOCUMENT_RESULTS"] \
                + "&hl.ocr.contextBlock=" + app.config["COLLECTION_SNIPPET_CONTEXT"] \
                + "&hl.ocr.contextSize=" + app.config["COLLECTION_SNIPPET_CONTEXT_SIZE"] \
                + "&hl.ocr.limitBlock=" + app.config["COLLECTION_SNIPPET_CONTEXT_LIMIT"] \
                + "&q=" + q

    solr_results = requests.get(query_url)
    results_json = solr_results.json()
    docs = results_json["response"]["docs"]

    results = []
    for doc in docs:

        manifest_path = app.config["MANIFEST_LOCATION"] + "/{}.json".format(doc["id"])
        mani_json = json.load(open(manifest_path, 'r'))
        cvlist = mani_json["sequences"][0]["canvases"]

        result = {"id": doc["id"],
                  "manifest_url": doc["manifest_url"],
                  "total_results": results_json["ocrHighlighting"][doc["id"]][app.config["OCR_TEXT_FIELD"]]["numTotal"],
                  "canvases": []
                  }
        snippets = results_json["ocrHighlighting"][doc["id"]]["ocr_text"]["snippets"]

        for fragment in snippets:
            # matches = re.findall('<em>(.*?)</em>', fragment["text"])

            x = fragment["region"]["ulx"]
            y = fragment["region"]["uly"]
            w = fragment["region"]["lrx"] - fragment["region"]["ulx"]
            h = fragment["region"]["lry"] - fragment["region"]["uly"]

            cv = cvlist[int(fragment["page"].replace("page_", ""))]
            img = cv["images"][0]["resource"]["@id"]
            frag = img.replace("/full/full", "/{},{},{},{}/{},".format(x, y, w, h, int(w / 4)), 1)
            canvas_doc = {"canvas": fragment["page"],
                          "region": "{},{},{},{}".format(x, y, w, h),
                          "url": frag,
                          "highlights": []}

            for highlight in fragment["highlights"]:
                for part in highlight:
                    x = int(part["ulx"] / 4)
                    y = int(part["uly"] / 4)
                    w = int((part["lrx"] - part["ulx"]) / 4)
                    h = int((part["lry"] - part["uly"]) / 4)
                    canvas_doc["highlights"].append({"coords": "{},{},{},{}".format(x, y, w, h),
                                                     "chars": part["text"]})
            result["canvases"].append(canvas_doc)
        results.append(result)

    response = app.response_class(
        response=json.dumps(results),
        mimetype='application/json',
        headers=[('Access-Control-Allow-Origin', '*')]
    )
    return response


@app.route("/snippets/<id>")
def snippet_search(id):
    q = bleach.clean(request.args.get("q", default=""), strip=True, tags=[])
    snips = bleach.clean(request.args.get("snips", default="10"), strip=True, tags=[])
    query_url = app.config["SOLR_URL"] + "/" + app.config["SOLR_CORE"] + \
                "/select?&df=ocr_text&hl.fl=ocr_text&hl.snippets=" + snips + "&hl=on&rows=50" + \
                "&hl.ocr.contextBlock=word&hl.ocr.contextSize=5&hl.ocr.limitBlock=block" + \
                "&fq=id:" + id + "&q=" + q

    solr_results = requests.get(query_url)
    results_json = solr_results.json()
    docs = results_json["response"]["docs"]

    results = []
    for doc in docs:

        #        manifest_path = "resources/manifests/{}.json".format(doc["id"]) #.replace("00","0"))
        #        mani_json = json.load(open(manifest_path,'r'))
        #        cvlist = mani_json["sequences"][0]["canvases"]

        result = {"id": doc["id"],
                  #                  "manifest_url": doc["manifest_url"],
                  "total_results": results_json["ocrHighlighting"][doc["id"]]["ocr_text"]["numTotal"],
                  "canvases": []
                  }
        snippets = results_json["ocrHighlighting"][doc["id"]]["ocr_text"]["snippets"]

        for fragment in snippets:
            # matches = re.findall('<em>(.*?)</em>', fragment["text"])

            x = fragment["region"]["ulx"]
            y = fragment["region"]["uly"]
            w = fragment["region"]["lrx"] - fragment["region"]["ulx"]
            h = fragment["region"]["lry"] - fragment["region"]["uly"]
            if doc["scale"] != 1:
                x, y, w, h = int(x), int(y), int(w), int(h)
                x, y, w, h = int(x * doc["scale"]), int(y * doc["scale"]), int(w * doc["scale"]), int(h * doc["scale"])
                x, y, w, h = str(x), str(y), str(w), str(h)

            # cv = cvlist[int(fragment["page"].replace("page_",""))]
            # img = cv["images"][0]["resource"]["@id"]
            # frag = img.replace("/full/full", "/{},{},{},{}/{},".format(x,y,w,h,int(w/4)), 1)
            canvas_doc = {"canvas": fragment["page"],
                          "region": "{},{},{},{}".format(x, y, w, h),
                          #                          "url": frag,
                          "highlights": []}

            for highlight in fragment["highlights"]:
                for part in highlight:

                    x = int(part["ulx"])
                    y = int(part["uly"])
                    w = int((part["lrx"] - part["ulx"]))
                    h = int((part["lry"] - part["uly"]))
                    if doc["scale"] != 1:
                        x, y, w, h = int(x), int(y), int(w), int(h)
                        # x,y,w,h = int(x*6.46), int(y*6.46), int(w*6.46), int(h*6.46)
                        x, y, w, h = int(x * doc["scale"]), int(y * doc["scale"]), int(w * doc["scale"]), int(
                            h * doc["scale"])
                        x, y, w, h = str(x), str(y), str(w), str(h)

                    canvas_doc["highlights"].append({"coords": "{},{},{},{}".format(x, y, w, h),
                                                     "chars": part["text"]})
            result["canvases"].append(canvas_doc)
        results.append(result)

    response = app.response_class(
        response=json.dumps(results),
        mimetype='application/json',
        headers=[('Access-Control-Allow-Origin', '*')]
    )
    return response
