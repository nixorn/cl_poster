#stolen from http://pymotw.com/2/xml/etree/ElementTree/create.html

from xml.etree import ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

"""
from rss_render import render
print render(replymail="bolik@lelik.com",
            title="title",
            description="many\nline\ndescription",
            username="bolik",
            password="lelik",
            accountID="1",
            category="npo",
            area="atl",
            image="base/64/image")
""" 
def render(replymail,
            title,
            description,
            username,
            password,
            acountID,
            category,
            area,
            image=None):
    #root elem
    rdf = Element('rdf:RDF')
    rdf.attrib = {"xmlns":"http://purl.org/rss/1.0/", 
                  "xmlns:rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                  "xmlns:cl":"http://www.craigslist.org/about/cl-bulk-ns/1.0"}
    #channel elem. auth and title here
    channel = SubElement(rdf, "channel")
    items = SubElement(channel, "items")
    rdf_li = SubElement(items, "rdf:li")
    rdf_li.attrib = {"rdf:resource":title}
    auth = SubElement(channel,"cl:auth")

    auth.attrib = {"username":username,
                   "password":password,
                   "accountID":acountID}

    #item(s?).
    item = SubElement(rdf, "item")
    item.attrib = {"rdf:about":title}
    cl_category = SubElement(item,"cl:category")
    cl_category.text = category
    cl_area = SubElement(item, "cl:area")
    cl_area.text = area

    cl_replyEmail = SubElement(item, "cl:replyEmail")
    cl_replyEmail.attrib = {"privacy":"A"}
    cl_replyEmail.text = replymail

    cl_title = SubElement(item, "title")
    cl_title.text = title

    cl_description = SubElement(item, "description")
    cl_description.text = "<![CDATA[" + description + "]]>"

    if image:
        cl_image = SubElement(item, "cl:image")
        cl_image.attrib = {"position":"1"}
        cl_image.text = image
    return prettify(rdf)
