COLLECTION_ONE = """
{
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": "http://mytestserver/manifests/collection-manifest",
    "@type": "sc:Manifest",
    "label": "Whiiif Test Manifest 1",
    "viewingHint": "individuals",
    "service": [
        {
            "@context": "http://iiif.io/api/search/1/context.json",
            "@id": "http://testserver:5000/search/collection-manifest",
            "profile": "http://iiif.io/api/search/1/search"
        }
    ],
    "sequences": [
        {
            "@type": "sc:Sequence",
            "label": "Current Page Order",
            "viewingHint": "individuals",
            "canvases": [
                {
                    "@id": "http://mytestserver/manifests/collection-manifest/canvas/page_0",
                    "@type": "sc:Canvas",
                    "label": "p. 0",
                    "height": 6171,
                    "width": 5535,
                    "images": [
                        {
                            "@type": "oa:Annotation",
                            "motivation": "sc:painting",
                            "resource": {
                                "@id": "https://test-iiif-endpoint/iiif/collectionimage0/full/full/0/default.jpg",
                                "@type": "dcTypes:Image",
                                "format": "image/jpeg",
                                "height": 6171,
                                "width": 5535,
                                "service": {
                                    "@context": "http://iiif.io/api/image/2/context.json",
                                    "@id": "https://test-iiif-endpoint/iiif/collectionimage0",
                                    "profile": "http://iiif.io/api/image/2/level2.json"
                                }
                            },
                            "on": "http://mytestserver/manifests/collection-manifest/canvas/page_0"
                        }
                    ]
                },
                {
                    "@id": "http://mytestserver/manifests/collection-manifest/canvas/page_1",
                    "@type": "sc:Canvas",
                    "label": "p. 1",
                    "height": 6059,
                    "width": 5233,
                    "images": [
                        {
                            "@type": "oa:Annotation",
                            "motivation": "sc:painting",
                            "resource": {
                                "@id": "https://test-iiif-endpoint/iiif/collectionimage1/full/full/0/default.jpg",
                                "@type": "dcTypes:Image",
                                "format": "image/jpeg",
                                "height": 6059,
                                "width": 5233,
                                "service": {
                                    "@context": "http://iiif.io/api/image/2/context.json",
                                    "@id": "https://test-iiif-endpoint/iiif/collectionimage1",
                                    "profile": "http://iiif.io/api/image/2/level2.json"
                                }
                            },
                            "on": "http://mytestserver/manifests/collection-manifest/canvas/page_1"
                        }
                    ]
                }
            ]
        }
    ]
}
"""

COLLECTION_TWO = """
{
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": "http://mytestserver/manifests/collection-another",
    "@type": "sc:Manifest",
    "label": "Whiiif Test Manifest 2",
    "viewingHint": "individuals",
    "service": [
        {
            "@context": "http://iiif.io/api/search/1/context.json",
            "@id": "http://testserver:5000/search/collection-another",
            "profile": "http://iiif.io/api/search/1/search"
        }
    ],
    "sequences": [
        {
            "@type": "sc:Sequence",
            "label": "Current Page Order",
            "viewingHint": "individuals",
            "canvases": [
                {
                    "@id": "http://mytestserver/manifests/collection-another/canvas/page_0",
                    "@type": "sc:Canvas",
                    "label": "p. 0",
                    "height": 6171,
                    "width": 5535,
                    "images": [
                        {
                            "@type": "oa:Annotation",
                            "motivation": "sc:painting",
                            "resource": {
                                "@id": "https://test-iiif-endpoint/iiif/collectionimage2/full/full/0/default.jpg",
                                "@type": "dcTypes:Image",
                                "format": "image/jpeg",
                                "height": 6171,
                                "width": 5535,
                                "service": {
                                    "@context": "http://iiif.io/api/image/2/context.json",
                                    "@id": "https://test-iiif-endpoint/iiif/collectionimage2",
                                    "profile": "http://iiif.io/api/image/2/level2.json"
                                }
                            },
                            "on": "http://mytestserver/manifests/collection-another/canvas/page_0"
                        }
                    ]
                },
                {
                    "@id": "http://mytestserver/manifests/collection-another/canvas/page_1",
                    "@type": "sc:Canvas",
                    "label": "p. 1",
                    "height": 6059,
                    "width": 5233,
                    "images": [
                        {
                            "@type": "oa:Annotation",
                            "motivation": "sc:painting",
                            "resource": {
                                "@id": "https://test-iiif-endpoint/iiif/collectionimage3/full/full/0/default.jpg",
                                "@type": "dcTypes:Image",
                                "format": "image/jpeg",
                                "height": 6059,
                                "width": 5233,
                                "service": {
                                    "@context": "http://iiif.io/api/image/2/context.json",
                                    "@id": "https://test-iiif-endpoint/iiif/collectionimage3",
                                    "profile": "http://iiif.io/api/image/2/level2.json"
                                }
                            },
                            "on": "http://mytestserver/manifests/collection-another/canvas/page_1"
                        }
                    ]
                }
            ]
        }
    ]
}
"""