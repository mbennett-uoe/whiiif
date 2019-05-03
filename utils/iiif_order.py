#!/usr/bin/python3

""" iiif_order.py: tools for ordering the json structure of IIIF objects """

from collections import OrderedDict

start_keys = ["@context", "@id", "@type"]
descriptive_keys = ["label", "metadata", "description", "thumbnail", "attribution", "license", "logo"]
linking_keys = ["seeAlso", "service", "related", "rendering", "within"]
paging_keys = ["first", "last", "total", "next", "prev", "startIndex"]

object_keys = {"collection": start_keys
                             + descriptive_keys
                             + ["viewingHint", "navDate"]
                             + linking_keys
                             + paging_keys
                             + ["collections", "manifests", "members"],
               "manifest": start_keys
                           + descriptive_keys
                           + ["viewingDirection", "viewingHint", "navDate"]
                           + linking_keys
                           + ["sequences", "structures"],
               "sequence": start_keys
                           + descriptive_keys
                           + ["viewingDirection", "viewingHint"]
                           + linking_keys
                           + ["startCanvas", "canvases"],
               "canvas": start_keys
                         + descriptive_keys
                         + ["height", "width", "viewingHint"]
                         + linking_keys
                         + ["images", "otherContent"],
               "image": start_keys
                         + ["motivation", "resource", "on"],
               "resource": start_keys
                           + descriptive_keys
                           + ["format", "height", "width", "viewingHint"]
                           + linking_keys,
               "service": start_keys + ["profile"]
               }

recursive_keys = {"collection": [("collections", "collection"),
                                 ("manifests", "manifest"),
                                 ("service", "service")],
                  "manifest": [("sequences", "sequence"),
                               ("service", "service")],
                  "sequence": [("canvases", "canvas"),
                               ("service", "service"),],
                  "canvas": [("images", "image"),
                             ("service", "service")],
                  "image": [("resource", "resource"),
                            ("service", "service")],
                  "resource": [("service", "service")]
                  }

def order_object(object, object_type, recursive = False):
    ordered = OrderedDict()
    for key in object_keys[object_type]:
        if key in object:
            ordered[key] = object[key]

    # copy over any other keys that might exist
    for key in set(object.keys()) - set(object_keys[object_type]):
        ordered[key] = object[key]

    if recursive and object_type in recursive_keys:
        for key, subtype in recursive_keys[object_type]:
            if key in ordered:
                if type(ordered[key]) == list:
                    for idx, val in enumerate(ordered[key]):
                        ordered[key][idx] = order_object(ordered[key][idx], subtype, recursive=True)
                elif type(ordered[key]) == dict:
                    ordered[key] = order_object(ordered[key], subtype, recursive=True)

    return ordered