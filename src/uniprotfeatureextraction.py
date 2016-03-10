#!/usr/bin/env python2
#encoding: UTF-8

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "jgao"
__date__ = "$March 9, 2016$"


import urllib2

from xml.dom import Node
from xml.dom import minidom

def readUniportAccs(uniprot_url):
    f = urllib2.urlopen(uniprot_url)
    myfile = f.read().strip()
    return myfile.split("\n");

def parseUniprotEntry(uniprot_acc, out_file):
    uniprot_xml_url = "http://www.uniprot.org/uniprot/"+uniprot_acc+".xml"
    xmlstr=urllib2.urlopen(uniprot_xml_url).read()
    parseUniprotXML(xmlstr, out_file)
    

def parseUniprotXML(xmlstr, out_file):
    exludingFeatureTypes = set([
        'sequence variant',
        'mutagenesis site',
        'splice variant',
        'sequence conflict',
        'chain',
        'repeat',
        'region of interest',
        'strand',
        'helix',
        'turn',
        'disulfide bond',
        'site'
        ])
    dom=minidom.parseString(xmlstr)
    
    entries = findElementByPath(dom, "uniprot/entry")
    for entry in entries:
        gene = getGeneName(entry)
        name = findChildrenByName(entry, "name", True)[0].firstChild.data
        print(gene+" - "+name)
        
        features = findChildrenByName(entry, "feature", False)
        for feature in features:
            f_type = feature.getAttribute("type")
            if f_type in exludingFeatureTypes:
                continue

            f_desc = feature.getAttribute("description")
            if not f_desc:
                f_desc = ''

            location = findChildrenByName(feature, "location", True)
            if not location:
                continue

            begin_pos = 0
            end_pos = 0
    #        position_el = location[0].findChildrenByName("position")
    #        if position_el:
    #            begin_pos = position_el[0].getAttribute('position')
    #            end_pos = begin_pos
    #        else:
            begin_pos_el = findChildrenByName(location[0], "begin", True)
            end_pos_el = findChildrenByName(location[0], "end", True)
            if begin_pos_el and end_pos_el:
                begin_pos = begin_pos_el[0].getAttribute('position')
                end_pos = end_pos_el[0].getAttribute('position')

            if not begin_pos or not end_pos:
                continue

            out_file.write('\t'.join([name, gene, f_type, f_desc, begin_pos, end_pos])+'\n')
                    
def getGeneName(entry):
    gene = findChildrenByName(entry, "gene", True)
    if not gene:
        print "### No gene symbol"
        return ""
    
    names = findChildrenByName(gene[0], "name", True)
    for name in names:
        type = name.getAttribute("type")
        if type=="primary":
            return name.firstChild.data
   
    print "### No primary gene symbol"
    return ""

def findElementByPath(el, path):
    if not el:
        return []
    els = []
    parts = path.split('/',1)
    children = findChildrenByName(el, parts[0], False)
    if len(parts)==1:
        els.extend(children)
    else:
        for child in children:
            els.extend(findElementByPath(child, parts[1]))
            
    return els
    
        
def findChildrenByName(el, name, firstOnly):
    if not el:
        return None
    els = []
    children = el.childNodes
    for child in children:
        if child.nodeType == Node.ELEMENT_NODE and child.tagName == name:
            els.append(child)
            if firstOnly:
                return els
    
    return els

def main(input_dir, output_dir):
#    parseUniprotXML('EGFR_HUMAN')
#    parseUniprotXML('ERBB2_HUMAN')
#    parseUniprotXML('ERBB3_HUMAN')
#    parseUniprotXML('MTOR_HUMAN')
#    parseUniprotXML('PTEN_HUMAN')
#    parseUniprotXML('AKT1_HUMAN')
#    parseUniprotXML('AKT2_HUMAN')
#    parseUniprotXML('AKT3_HUMAN')
#    parseUniprotXML('P53_HUMAN')
#    parseUniprotXML('RASK_HUMAN')
#    parseUniprotXML('RASN_HUMAN')
#    parseUniprotXML('RASH_HUMAN')
#    parseUniprotXML('BRAF_HUMAN')
#    parseUniprotXML('MP2K1_HUMAN')
    
    in_file = open(input_dir, 'r')
    
    out_file = open(output_dir, 'w+')

    i = 1
    oneentry = []
    for line in in_file:
        if line.startswith('<entry'):
            print(str(i))
            i = i + 1
            oneentry = []
            oneentry.append('<uniprot>')
        oneentry.append(line)
        if line.startswith('</entry'):
            oneentry.append('</uniprot>')
            parseUniprotXML(''.join(oneentry), out_file)

#    parseUniprotEntry('MP2K2_HUMAN', out_file)
    
    out_file.close()
    in_file.close()

        


if __name__ == "__main__":
    input_dir = "/Users/jgao/projects/UniProtPyUtils/test_in_file.xml"#"test_in_file.xml uniprot-all-human.xml
    output_dir = "/Users/jgao/projects/UniProtPyUtils/uniprot-features-test.tsv" #sys.argv[2]
    main(input_dir, output_dir)
