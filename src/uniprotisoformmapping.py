# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "jgao"
__date__ = "$Jun 8, 2015 10:59:01 AM$"


import urllib2
from xml.dom import minidom

def readUniportAccs(uniprot_url):
    f = urllib2.urlopen(uniprot_url)
    myfile = f.read().strip()
    return myfile.split("\n");

def parseUniprotXML(uniprot_acc):
    uniprot_xml_url = "http://www.uniprot.org/uniprot/"+uniprot_acc+".xml"
    u1=urllib2.urlopen(uniprot_xml_url)
    dom=minidom.parse(u1)
    gene = getGeneName(dom)
    canonical_isoform = getCanonicalIsoform(dom)
    delimiter = ";"
    enst = delimiter.join(getDbRefs(dom, canonical_isoform, "Ensembl"))
    ccds = delimiter.join(getDbRefs(dom, canonical_isoform, "CCDS"))
    refseqp = delimiter.join(getDbRefs(dom, canonical_isoform, "RefSeq"))
    refseqm = delimiter.join(getRefSeqMrnas(dom, canonical_isoform))
    return [uniprot_acc, gene, enst, ccds, refseqp, refseqm]

def getGeneName(dom):
    gene = dom.getElementsByTagName("gene")
    if not gene:
        print "### No gene symbol"
        return ""
    
    names = gene[0].getElementsByTagName("name")
    for name in names:
        type = name.getAttribute("type")
        if type=="primary":
            return name.firstChild.data
   
    print "### No primary gene symbol"
    return ""

def getCanonicalIsoform(dom):
    isoforms = dom.getElementsByTagName("isoform")
    
    if not isoforms:
        return None
    
    for isoform in isoforms:
        sequence_type = isoform.getElementsByTagName("sequence")[0].getAttribute("type")
        if sequence_type == "displayed":
            return isoform.getElementsByTagName("id")[0].firstChild.data
        
    return None

def getDbRefs(dom, canonical_isoform, db):
    ensts = []
    ensts_no_mol_id = []
    db_refs = dom.getElementsByTagName("dbReference")
    for db_ref in db_refs:
        type = db_ref.getAttribute("type")
        if type == db:
            if canonical_isoform == None:
                ensts.append(db_ref.getAttribute("id"))
            else:
                mols = db_ref.getElementsByTagName("molecule")
                if not mols:
                    ensts_no_mol_id.append(db_ref.getAttribute("id"))
                else:
                    mol_id = mols[0].getAttribute("id")
                    if mol_id == canonical_isoform:
                        ensts.append(db_ref.getAttribute("id"))
    if not ensts:
        print "Cound not match the isoform"
    return ensts;

def getRefSeqMrnas(dom, canonical_isoform):
    ensts = []
    db_refs = dom.getElementsByTagName("dbReference")
    for db_ref in db_refs:
        type = db_ref.getAttribute("type")
        if type == "RefSeq":
            match = False
            if canonical_isoform == None:
                match = True
            else:
                mols = db_ref.getElementsByTagName("molecule")
                if not mols:
                    match = False
                else:
                    mol_id = mols[0].getAttribute("id")
                    if mol_id == canonical_isoform:
                        match = True
                
            if match:
                db_ref_properties = db_ref.getElementsByTagName("property");
                for prop in db_ref_properties:
                    if prop.getAttribute("type")=="nucleotide sequence ID":
                        ensts.append(prop.getAttribute("value"))
    if not ensts:
        print "Cound not match the isoform"
        
    return ensts;
            

def main(uniprot_url, output_dir):
    print ','.join(parseUniprotXML('P63000'))+'\n'
#    
#    file = open(output_dir, 'w+')
#    accs = readUniportAccs(uniprot_url)
#    i = 1
#    for acc in accs:
#        print str(i)+":"+acc
#        i = i+1
#        row = '"'+'","'.join(parseUniprotXML(acc))+'"\n'
#        file.write(row)
#    file.close()

    
#        
#    parseUniprotXML("A8MXY4")
    


if __name__ == "__main__":
    uniprot_url = "http://www.uniprot.org/uniprot/?sort=&desc=&compress=no&query=&fil=organism:%22Homo%20sapiens%20(Human)%20[9606]%22%20AND%20reviewed:yes&format=list&force=yes" #sys.argv[1]
    output_dir = "/Users/jgao/projects/UniProtIsoformMapping/mapping.csv" #sys.argv[2]
    main(uniprot_url, output_dir)
