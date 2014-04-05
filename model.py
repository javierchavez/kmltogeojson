__author__ = 'Javier Chavez'

import argparse
import json
from zipfile import ZipFile
import os
import urllib2
import xml.dom.minidom



class KML_Handler(object):
    def parse_kml_to_json(self, kml):

        doc= None
        try:
            doc = xml.dom.minidom.parse(kml)
        except Exception as e:
            print ('\033[91mFAILED:\033[0m Are you pointing to a KMZ file(use --kmz) or check Path?')
            return '{}';

        js = {"type": "FeatureCollection", "features":[]}

        for pm in doc.getElementsByTagName('Placemark'):
            geotype = ""
            # Determine if point or polygon
            if pm.getElementsByTagName("Point"):
                geotype = "Point"
                pnt = pm.getElementsByTagName("Point")[0]
                coor_tag = pnt.getElementsByTagName("coordinates")[0]
                ll = coor_tag.firstChild.nodeValue.strip(' ')
                _ll_ = [float(ll.split(",")[0]), float(ll.split(",")[1])]
            elif pm.getElementsByTagName("Polygon"):
                geotype = "Polygon"
                pnt = pm.getElementsByTagName("Polygon")[0]
                _ll_ = self.__handle_multi_coordinates__(pnt)
            elif pm.getElementsByTagName("MultiGeometry"):
                pnt = pm.getElementsByTagName("MultiGeometry")[0]
                _ll_ = self.__handle_multi_coordinates__(pnt, muli=True)
            else:
                _ll_ = ""

            # description TAG surrounding
            desctag = pm.getElementsByTagName("description")[0]
            # check make sure there is a desc available
            if desctag.firstChild is None:
                desc = ""
            else:
                # inner
                desc = desctag.firstChild.nodeValue

            # name TAG surrounding
            namtag = pm.getElementsByTagName("name")[0]
            # check make sure there is a name available
            if namtag.firstChild is None:
                name = ""
            else:
                # inner
                name = namtag.firstChild.nodeValue

            js["features"].append(
                {
                    "type":"Feature",
                    "geometry": {"coordinates": _ll_, "type": geotype},
                    "properties": {"marker-symbol": "bar", "name": name },
                    }
            )

        return json.dumps(js)

    @staticmethod
    def __handle_multi_coordinates__(parent_tag, muli=False):
        if not muli:
            coor_tag= parent_tag.getElementsByTagName("coordinates")[0]
            ll = coor_tag.firstChild.nodeValue.lstrip().split(' ')
            return [ {"lng": ll_obj.split(",")[0], "lat": ll_obj.split(",")[1]} for ll_obj in ll ]
        else:
            coor_tag= parent_tag.getElementsByTagName("coordinates")[0]
            tags = [ct for ct in parent_tag.getElementsByTagName("coordinates")]
            all = [s.firstChild.nodeValue.lstrip().split(' ') for s in tags]
            ll = sum(all, [])
            return [ {"lng": ll_obj.split(",")[0], "lat": ll_obj.split(",")[1]} for ll_obj in ll ]


class Data(object):
    def __init__(self, location='data/hello.json', kmz=False):

        if location[:4] == "http" and not kmz:
            # download file
            self.__download_file__(location=location)
            # open as file
            self.kml_data = open('tmp', 'r')
            # clean up tmp file
            self.__clean_tmp__()
            # load it and parse it
            self.__json__ =  json.loads(KML_Handler().parse_kml_to_json(self.kml_data))
        elif location[:4] == "http" and kmz:
            # download file
            self.__download_file__(location=location)
            # open as zip
            self.kmz_file = ZipFile("tmp", 'r')
            self.kml_data = self.kmz_file.open('doc.kml', 'r')
            # clean up tmp file
            self.__clean_tmp__()
            # load it and parse it
            self.__json__ =  json.loads(KML_Handler().parse_kml_to_json(self.kml_data))
        else:
            self.__init_file__(location)
            self.__json__ = json.load(self.json_file)

    def get_json_dumps(self, indent=0):
        # Do not pass indent if 0
        if indent == 0:
            return json.dumps(self.__json__)
        else:
            return json.dumps(self.__json__, indent=indent)

    def get_json(self):
        return self.__json__

    def __init_file__(self, location):
        self.json_file = open(location)

    @staticmethod
    def __clean_tmp__():
        os.unlink("tmp")

    @staticmethod
    def __download_file__(location):
        f = urllib2.urlopen(location).read()
        with open("tmp", "wb") as code:
            code.write(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turn KML/KMZ files to JSON. You can ">>" to output to file')
    parser.add_argument('--l', help='path/or/url/to json | kml | kmz', required=True, dest='loc')
    parser.add_argument('--kmz', help='Flag for KMZ', dest='is_kmz', default=False, action='store_true')
    parser.add_argument('--i', help='spaces to indent json', required=False, dest='indent_l', default=0, type=int)
    args = parser.parse_args()

    data = Data(location=args.loc, kmz=args.is_kmz)

    print data.get_json_dumps(indent=args.indent_l)
