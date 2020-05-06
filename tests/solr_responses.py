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
                    "text": "this is a <em>test</em> response",
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
                        "text": "test",
                        "page": "page_1069"}]]},
                    {
                        "text": "and another <em>test</em> response",
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
                            "text": "test",
                            "page": "page_1073"}]]}],
                "numTotal": 2}}},
}
