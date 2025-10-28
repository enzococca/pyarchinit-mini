"""
SVG Resources for Extended Matrix Nodes
Contains SVG definitions for CON, Extractor, and Combinar nodes
"""

from xml.etree.ElementTree import Element, SubElement


class SVGResources:
    """SVG resource definitions for yEd special nodes"""

    @staticmethod
    def create_resources_section(parent: Element):
        """
        Create y:Resources section with SVG definitions

        Args:
            parent: Parent element (graphml root)
        """
        # Find or create data element for resources (key d14)
        resources_data = SubElement(parent, 'data')
        resources_data.set('key', 'd14')

        # Create y:Resources container
        resources = SubElement(resources_data, '{http://www.yworks.com/xml/graphml}Resources')

        # Add SVG resource for Extractor (refid="1")
        SVGResources._add_extractor_svg(resources)

        # Add SVG resource for Combinar (refid="2")
        SVGResources._add_combinar_svg(resources)

        # Add SVG resource for CON (refid="3")
        SVGResources._add_con_svg(resources)

        return resources

    @staticmethod
    def _add_extractor_svg(resources: Element):
        """Add Extractor SVG (complex symbol - refid=1 from EM palette)"""
        resource = SubElement(resources, '{http://www.yworks.com/xml/graphml}Resource')
        resource.set('id', '1')
        resource.set('xml:space', 'preserve')

        # SVG from EM palette (Extractor symbol)
        svg_content = '''
<svg
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:cc="http://creativecommons.org/ns#"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:svg="http://www.w3.org/2000/svg"
xmlns="http://www.w3.org/2000/svg"
xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
width="48px"
height="48px"
id="svg4192"
version="1.1"
inkscape:version="0.48.4 r9939"
sodipodi:docname="New document 20">
<defs id="defs4194" />
<sodipodi:namedview
 id="base"
 pagecolor="#ffffff"
 bordercolor="#666666"
 borderopacity="1.0"
 inkscape:pageopacity="0.0"
 inkscape:pageshadow="2"
 inkscape:zoom="14"
 inkscape:cx="24.612064"
 inkscape:cy="28.768962"
 inkscape:current-layer="layer1"
 showgrid="true"
 inkscape:grid-bbox="true"
 inkscape:document-units="px"
 inkscape:window-width="1920"
 inkscape:window-height="1025"
 inkscape:window-x="-2"
 inkscape:window-y="-3"
 inkscape:window-maximized="1" />
<metadata id="metadata4197">
<rdf:RDF>
  <cc:Work
     rdf:about="">
    <dc:format>image/svg+xml</dc:format>
    <dc:type
       rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
    <dc:title></dc:title>
  </cc:Work>
</rdf:RDF>
</metadata>
<g
 id="layer1"
 inkscape:label="Layer 1"
 inkscape:groupmode="layer">
<g
   transform="matrix(0.40828104,0,0,0.41346794,-201.56174,97.998396)"
   id="g3922">
  <path
     sodipodi:type="arc"
     style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
     id="path3912"
     sodipodi:cx="374.7666"
     sodipodi:cy="906.90021"
     sodipodi:rx="55.558392"
     sodipodi:ry="55.558392"
     d="m 430.32499,906.90021 c 0,30.68405 -24.87434,55.55839 -55.55839,55.55839 -30.68405,0 -55.55839,-24.87434 -55.55839,-55.55839 0,-30.68405 24.87434,-55.55839 55.55839,-55.55839 30.68405,0 55.55839,24.87434 55.55839,55.55839 z"
     transform="translate(177.55723,-1085.7479)" />
  <path
     sodipodi:nodetypes="ccsccc"
     inkscape:connector-curvature="0"
     id="path3914"
     d="m 543.53146,-169.98986 63.36579,-17.50001 c 0,0 0.71429,3.97312 0.71429,11.68875 0,7.71563 -2.93748,15.70661 -2.93748,15.70661 l -61.1426,17.05358 z"
     style="fill:#7b7b7b;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
  <path
     sodipodi:nodetypes="ccccsc"
     inkscape:connector-curvature="0"
     id="path3916"
     d="m 501.52478,-201.54471 54.88091,-14.27148 0,26.94893 -59.23348,15.97426 c 0,0 -0.15898,-6.266 0.10274,-12.48413 0.34368,-8.16509 4.24983,-16.16758 4.24983,-16.16758 z"
     style="fill:#7b7b7b;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
</g>
</g>
</svg>'''
        resource.text = svg_content

    @staticmethod
    def _add_combinar_svg(resources: Element):
        """Add Combinar SVG (aggregation symbol - refid=2 from EM palette)"""
        resource = SubElement(resources, '{http://www.yworks.com/xml/graphml}Resource')
        resource.set('id', '2')
        resource.set('xml:space', 'preserve')

        # SVG from EM palette (Combinar = aggregation symbol)
        svg_content = '''
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="48px"
   height="48px"
   id="svg4050"
   version="1.1"
   inkscape:version="0.48.4 r9939"
   sodipodi:docname="New document 13">
 <defs
     id="defs4052" />
 <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="9.8994949"
     inkscape:cx="18.095997"
     inkscape:cy="17.278115"
     inkscape:current-layer="layer1"
     showgrid="true"
     inkscape:grid-bbox="true"
     inkscape:document-units="px"
     inkscape:window-width="1920"
     inkscape:window-height="1025"
     inkscape:window-x="-2"
     inkscape:window-y="-3"
     inkscape:window-maximized="1" />
 <metadata
     id="metadata4055">
   <rdf:RDF>
     <cc:Work
         rdf:about="">
       <dc:format>image/svg+xml</dc:format>
       <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
       <dc:title></dc:title>
     </cc:Work>
   </rdf:RDF>
 </metadata>
 <g
     id="layer1"
     inkscape:label="Layer 1"
     inkscape:groupmode="layer">
   <g
       transform="matrix(0.41470954,0,0,0.41438764,-58.075087,96.197996)"
       id="g3932">
     <path
         transform="translate(-176.7767,-1080.8632)"
         d="m 430.32499,906.90021 c 0,30.68405 -24.87434,55.55839 -55.55839,55.55839 -30.68405,0 -55.55839,-24.87434 -55.55839,-55.55839 0,-30.68405 24.87434,-55.55839 55.55839,-55.55839 30.68405,0 55.55839,24.87434 55.55839,55.55839 z"
         sodipodi:ry="55.558392"
         sodipodi:rx="55.558392"
         sodipodi:cy="906.90021"
         sodipodi:cx="374.7666"
         id="path2996-3"
         style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
         sodipodi:type="arc" />
     <path
         inkscape:connector-curvature="0"
         id="path3795"
         d="m 195.82737,-229.48049 c -29.75104,1.0602 -53.53125,25.52148 -53.53125,55.53125 0,30.00977 23.78021,54.4398 53.53125,55.5 l 0,-38.875 -18.1875,0 0,-32.8125 18.1875,0 0,-39.34375 z"
         style="fill:#7d7d7d;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
     <rect
         y="-187.49332"
         x="212.49696"
         height="27.142857"
         width="26.071428"
         id="rect3805"
         style="fill:#7d7d7d;fill-opacity:1;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
     <path
         inkscape:connector-curvature="0"
         id="path3807"
         d="m 180.35416,-173.20759 c 29.28571,0 29.28571,0 29.28571,0"
         style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" />
   </g>
 </g>
</svg>'''
        resource.text = svg_content

    @staticmethod
    def _add_con_svg(resources: Element):
        """Add CON SVG (black diamond - refid=3)"""
        resource = SubElement(resources, '{http://www.yworks.com/xml/graphml}Resource')
        resource.set('id', '3')
        resource.set('xml:space', 'preserve')

        # SVG for diamond (CON - continuity)
        svg_content = '''
<svg
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:cc="http://creativecommons.org/ns#"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:svg="http://www.w3.org/2000/svg"
xmlns="http://www.w3.org/2000/svg"
width="48px"
height="48px">
<g>
  <path
     d="M 24,5 L 43,24 L 24,43 L 5,24 Z"
     style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:1;stroke-opacity:1" />
</g>
</svg>'''
        resource.text = svg_content
