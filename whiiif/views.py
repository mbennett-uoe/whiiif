import json
import re
from os import path
from flask import render_template, request, url_for
import requests
import bleach
from whiiif import app


@app.route('/')
def index():
    app.logger.debug('Index page loaded - this should (currently) only occur when tests are being run')
    return render_template('index.html')


@app.route('/search/<manifest>')
def search(manifest):
    app.logger.info("Processing IIIF Search request for document {}".format(manifest))

    q = bleach.clean(request.args.get("q", default=""), strip=True, tags=[])
    manifest_regexp = re.compile(r'[^A-Za-z0-9-_]')
    manifest = manifest_regexp.sub("", manifest)
    unimplemented = {"motivation", "date", "user"}
    ignored = list(set(request.args.keys()) & unimplemented)

    app.logger.debug("Request original q: {}".format(request.args.get("q", default="")))
    app.logger.debug("Request bleached q: {}".format(q))
    app.logger.debug("Regexed manifest ID: {}".format(manifest))

    query_url = "{}/{}".format(app.config["SOLR_URL"], app.config["SOLR_CORE"])
    query_url += "/select?hl=on&hl.ocr.absoluteHighlights=true"
    query_url += "&df={}".format(app.config["OCR_TEXT_FIELD"])
    query_url += "&hl.fl={}".format(app.config["OCR_TEXT_FIELD"])
    query_url += "&hl.snippets={}".format(app.config["WITHIN_MAX_RESULTS"])
    query_url += "&fq={0}:{1}".format(app.config["DOCUMENT_ID_FIELD"], manifest)
    query_url += "&q={}".format(q)

    app.logger.info("Built query: {}".format(query_url))

    try:
        solr_results = requests.get(query_url)
        app.logger.debug("Solr request response code: {}".format(solr_results.status_code))
        results_json = solr_results.json()
        app.logger.debug("Solr JSON response code: {}".format(results_json["responseHeader"]["status"]))
        docs = results_json["response"]["docs"]
    except (requests.exceptions.ConnectionError, KeyError, ValueError) as e:
        app.log_exception(e)
        results_json = {}
        docs = []

    results = []
    total_results = 0
    for doc in docs:
        snippets = results_json["ocrHighlighting"][doc[app.config["DOCUMENT_ID_FIELD"]]][app.config["OCR_TEXT_FIELD"]]["snippets"]
        total_results += int(results_json["ocrHighlighting"][doc[app.config["DOCUMENT_ID_FIELD"]]][app.config["OCR_TEXT_FIELD"]]["numTotal"])
        for fragment in snippets:
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
                    grouped_hls.append({"manifest_id": doc[app.config["DOCUMENT_ID_FIELD"]],
                                        "manifest_url": doc[app.config["MANIFEST_URL_FIELD"]],
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
                suffix = chr(97 + in_idx)
            else:
                suffix = ""
            x, y, w, h = result_part["coords"].split(",")
            if result_part["scale"] != 1:
                x, y, w, h = int(x), int(y), int(w), int(h)
                x, y, w, h = int(x * result_part["scale"]), int(y * result_part["scale"]), int(
                    w * result_part["scale"]), int(h * result_part["scale"])
                x, y, w, h = str(x), str(y), str(w), str(h)
            result_base = {
                "@id": "uun:whiiif:%s:%s:%s%s" % (result_part["manifest_id"], result_part["canvas_id"], idx, suffix),
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "resource": {"@type": "cnt:ContentAsText",
                             "chars": result_part["chars"]},
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
    app.logger.info("Processing Collection Search request")

    q = bleach.clean(request.args.get("q"), strip=True, tags=[])

    app.logger.debug("Request original q: {}".format(request.args.get("q", default="")))
    app.logger.debug("Request bleached q: {}".format(q))

    query_url = "{0}/{1}".format(app.config["SOLR_URL"], app.config["SOLR_CORE"])
    query_url += "/select?hl=on&rows={}".format(app.config["COLLECTION_MAX_RESULTS"])
    query_url += "&df={}".format(app.config["OCR_TEXT_FIELD"])
    query_url += "&hl.fl={}".format(app.config["OCR_TEXT_FIELD"])
    query_url += "&hl.snippets={}".format(app.config["COLLECTION_MAX_DOCUMENT_RESULTS"])
    query_url += "&hl.ocr.contextBlock={}".format(app.config["COLLECTION_SNIPPET_CONTEXT"])
    query_url += "&hl.ocr.contextSize={}".format(app.config["COLLECTION_SNIPPET_CONTEXT_SIZE"])
    query_url += "&hl.ocr.limitBlock={}".format(app.config["COLLECTION_SNIPPET_CONTEXT_LIMIT"])
    query_url += "&q={}".format(q)

    app.logger.info("Built query: {}".format(query_url))

    try:
        solr_results = requests.get(query_url)
        app.logger.debug("Solr request response code: {}".format(solr_results.status_code))
        results_json = solr_results.json()
        app.logger.debug("Solr JSON response code: {}".format(results_json["responseHeader"]["status"]))
        docs = results_json["response"]["docs"]
    except (requests.exceptions.ConnectionError, KeyError, ValueError) as e:
        app.log_exception(e)
        results_json = {}
        docs = []

    results = []
    for doc in docs:

        try:
            manifest_path = path.join(app.config["MANIFEST_LOCATION"], doc[app.config["DOCUMENT_ID_FIELD"]]) + ".json"
            mani_json = json.load(open(manifest_path, 'r'))
            cvlist = mani_json["sequences"][0]["canvases"]
        except FileNotFoundError as e:
            app.log_exception(e)
            continue

        result = {"id": doc[app.config["DOCUMENT_ID_FIELD"]],
                  "manifest_url": doc[app.config["MANIFEST_URL_FIELD"]],
                  "total_results": results_json["ocrHighlighting"][doc[app.config["DOCUMENT_ID_FIELD"]]][app.config["OCR_TEXT_FIELD"]]["numTotal"],
                  "canvases": []
                  }
        snippets = results_json["ocrHighlighting"][doc[app.config["DOCUMENT_ID_FIELD"]]][app.config["OCR_TEXT_FIELD"]]["snippets"]

        for fragment in snippets:
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
    app.logger.info("Processing Snippet Search request for document {}".format(id))

    q = bleach.clean(request.args.get("q", default=""), strip=True, tags=[])
    snips = bleach.clean(request.args.get("snips", default=str(app.config["SNIPPETS_MAX_RESULTS"])), strip=True, tags=[])

    app.logger.debug("Request original q: {}".format(request.args.get("q", default="")))
    app.logger.debug("Request bleached q: {}".format(q))
    app.logger.debug("Request snips: {}".format(snips))

    query_url = "{0}/{1}".format(app.config["SOLR_URL"], app.config["SOLR_CORE"])
    query_url += "/select?hl=on"
    query_url += "&hl.snippets={}".format(snips)
    query_url += "&df={}".format(app.config["OCR_TEXT_FIELD"])
    query_url += "&hl.fl={}".format(app.config["OCR_TEXT_FIELD"])
    query_url += "&hl.ocr.contextBlock={}".format(app.config["SNIPPET_CONTEXT"])
    query_url += "&hl.ocr.contextSize={}".format(app.config["SNIPPET_CONTEXT_SIZE"])
    query_url += "&hl.ocr.limitBlock={}".format(app.config["SNIPPET_CONTEXT_LIMIT"])
    query_url += "&fq={0}:{1}".format(app.config["DOCUMENT_ID_FIELD"], id)
    query_url += "&q={}".format(q)

    app.logger.info("Built query: {}".format(query_url))

    try:
        solr_results = requests.get(query_url)
        app.logger.debug("Solr request response code: {}".format(solr_results.status_code))
        results_json = solr_results.json()
        app.logger.debug("Solr JSON response code: {}".format(results_json["responseHeader"]["status"]))
        docs = results_json["response"]["docs"]
    except (requests.exceptions.ConnectionError, KeyError, ValueError) as e:
        app.log_exception(e)
        results_json = {}
        docs = []

    results = []
    for doc in docs:
        result = {"id": doc[app.config["DOCUMENT_ID_FIELD"]],
                  #                  "manifest_url": doc["manifest_url"],
                  "total_results": results_json["ocrHighlighting"][doc[app.config["DOCUMENT_ID_FIELD"]]][app.config["OCR_TEXT_FIELD"]]["numTotal"],
                  "canvases": []
                  }
        snippets = results_json["ocrHighlighting"][doc[app.config["DOCUMENT_ID_FIELD"]]][app.config["OCR_TEXT_FIELD"]]["snippets"]

        for fragment in snippets:
            x = fragment["region"]["ulx"]
            y = fragment["region"]["uly"]
            w = fragment["region"]["lrx"] - fragment["region"]["ulx"]
            h = fragment["region"]["lry"] - fragment["region"]["uly"]
            if "scale" in doc and doc["scale"] != 1:
                x, y, w, h = int(x), int(y), int(w), int(h)
                x, y, w, h = int(x * doc["scale"]), int(y * doc["scale"]), int(w * doc["scale"]), int(h * doc["scale"])
                x, y, w, h = str(x), str(y), str(w), str(h)

            canvas_doc = {"canvas": fragment["page"],
                          "region": "{},{},{},{}".format(x, y, w, h),
                          "highlights": []}

            for highlight in fragment["highlights"]:
                for part in highlight:

                    x = int(part["ulx"])
                    y = int(part["uly"])
                    w = int((part["lrx"] - part["ulx"]))
                    h = int((part["lry"] - part["uly"]))
                    if "scale" in doc and doc["scale"] != 1:
                        x, y, w, h = int(x), int(y), int(w), int(h)
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
