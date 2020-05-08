IIIF = {
    "responseHeader": {
        "status": 0,
    },
    "response": {"numFound": 1, "start": 0, "docs": [
        {
            "id": "test-manifest",
            "manifest_url": "http://mytestserver/manifests/test-manifest",
            "ocr_text": "/test/manifests/test-manifest"
        }]
                 },
    "ocrHighlighting": {
        "test-manifest": {
            "ocr_text": {
                "snippets": [{
                    "text": "this is a <em>test response</em>",
                    "score": 3.373848E8,
                    "regions": [{
                        "ulx": 455,
                        "uly": 1054,
                        "lrx": 506,
                        "lry": 1272,
                        "page": "page_1069"}],
                    "highlights": [[{
                        "ulx": 466,
                        "uly": 1206,
                        "lrx": 497,
                        "lry": 1272,
                        "text": "test response",
                        "page": "page_1069"}]]},
                    {
                        "text": "and another <em>test response</em>",
                        "score": 3.59115616E8,
                        "regions": [{
                            "ulx": 5087,
                            "uly": 3579,
                            "lrx": 5123,
                            "lry": 3860,
                            "page": "page_1073"}],
                        "highlights": [[{
                            "ulx": 5099,
                            "uly": 3600,
                            "lrx": 5108,
                            "lry": 3656,
                            "text": "test response",
                            "page": "page_1073"}]]},
                    {
                        "text": "this one is a multiline <em>test response</em>",
                        "score": 7587345.5,
                        "regions": [{
                            "ulx": 615,
                            "uly": 948,
                            "lrx": 3950,
                            "lry": 1904,
                            "page": "page_537"}],
                        "highlights": [[{
                            "ulx": 3133,
                            "uly": 1319,
                            "lrx": 3436,
                            "lry": 1442,
                            "text": "test",
                            "page": "page_537"},
                            {
                                "ulx": 622,
                                "uly": 1419,
                                "lrx": 1166,
                                "lry": 1580,
                                "text": "response",
                                "page": "page_537"}]]},
                ],
                "numTotal": 3}}},
}
IIIF_SCALED = {
    "responseHeader": {
        "status": 0,
        "QTime": 11,
    },
    "response": {"numFound": 1, "start": 0, "docs": [
        {
            "id": "test-scaled-manifest",
            "manifest_url": "http://mytestserver/manifests/test-scaled-manifest",
            "ocr_text": "/test/manifests/test-scaled-manifest",
            "scale": 2.90625,
        }]
                 },
    "ocrHighlighting": {
        "test-scaled-manifest": {
            "ocr_text": {
                "snippets": [{
                    "page": "1",
                    "text": "Scaled <em>test</em>",
                    "score": 1.1692171E7,
                    "regions": [{
                        "ulx": 51,
                        "uly": 93,
                        "lrx": 670,
                        "lry": 141}],
                    "highlights": [[{
                        "text": "test",
                        "page": "1",
                        "ulx": 109,
                        "uly": 125,
                        "lrx": 141,
                        "lry": 141}]]}],
                "numTotal": 1}}}
}
SOLR_ERROR = {
    "responseHeader": {
        "status": 400,
        "QTime": 1,
    },
    "error": {
        "metadata": [
            "error-class", "org.apache.solr.common.SolrException",
            "root-error-class", "org.apache.solr.common.SolrException"],
        "msg": "undefined field errorfield",
        "code": 400}}

COLLECTION = {
    "responseHeader": {
        "status": 0,
        "QTime": 26,
    },
    "response": {"numFound": 2, "start": 0, "docs": [
        {
            "id": "collection-manifest",
            "manifest_url": "http://mytestserver/manifests/collection-manifest",
            "ocr_text": "/test/manifests/collection-manifest",
        },
        {
            "id": "collection-another",
            "manifest_url": "http://mytestserver/manifests/collection-another",
            "ocr_text": "/test/manifests/collection-another"}
    ]
                 },
    "ocrHighlighting": {
        "collection-manifest": {
            "ocr_text": {
                "snippets": [{
                    "text": "this is a multi-part collection <em>test response</em> with some context",
                    "score": 2.4530088E7,
                    "regions": [{
                        "ulx": 1752,
                        "uly": 2897,
                        "lrx": 4774,
                        "lry": 3107,
                        "page": "page_0"}],
                    "highlights": [[{
                        "ulx": 2861,
                        "uly": 6,
                        "lrx": 3022,
                        "lry": 86,
                        "text": "test",
                        "page": "page_0"},
                        {
                            "ulx": 0,
                            "uly": 102,
                            "lrx": 799,
                            "lry": 205,
                            "text": "response",
                            "page": "page_0"}]]},
                    {
                        "text": "this is a single part collection <em>test response</em> with some context",
                        "score": 2.4740064E7,
                        "regions": [{
                            "ulx": 951,
                            "uly": 3626,
                            "lrx": 3969,
                            "lry": 3852,
                            "page": "page_1"}],
                        "highlights": [[{
                            "ulx": 742,
                            "uly": 94,
                            "lrx": 1646,
                            "lry": 226,
                            "text": "test response",
                            "page": "page_1"}]]}],
                "numTotal": 8}},
        "collection-another": {
            "ocr_text": {
                "snippets": [{
                    "text": "this is the second collection <em>test response</em> with some different context",
                    "score": 7.24624E7,
                    "regions": [{
                        "ulx": 697,
                        "uly": 2690,
                        "lrx": 3829,
                        "lry": 3910,
                        "page": "page_1"}],
                    "highlights": [[{
                        "ulx": 1031,
                        "uly": 135,
                        "lrx": 1806,
                        "lry": 246,
                        "text": "test response",
                        "page": "page_1"}]]},
                    {
                        "text": "and a second <em>test response</em> for the second collection result",
                        "score": 9.0326496E7,
                        "regions": [{
                            "ulx": 881,
                            "uly": 4194,
                            "lrx": 3193,
                            "lry": 4420,
                            "page": "page_1"}],
                        "highlights": [[{
                            "ulx": 321,
                            "uly": 101,
                            "lrx": 1138,
                            "lry": 209,
                            "text": "test response",
                            "page": "page_1"}]]}],
                "numTotal": 2}}},
    "highlighting": {}}
