from svg import SimpleXMLReader
from io import StringIO

test_svg_1 = StringIO("""<?xml version="1.0" standalone="no"?>
<svg width="5cm" height="4cm" version="1.1"
     xmlns="http://www.w3.org/2000/svg">
  <desc>Four separate rectangles
  </desc>
    <rect x="0.5cm" y="0.5cm" width="2cm" height="1cm"/>
    <rect x="0.5cm" y="2cm" width="1cm" height="1.5cm"/>
    <rect x="3cm" y="0.5cm" width="1.5cm" height="2cm"/>
    <rect x="3.5cm" y="3cm" width="1cm" height="0.5cm"/>

  <!-- Show outline of viewport using 'rect' element -->
  <rect x=".01cm" y=".01cm" width="4.98cm" height="3.98cm"
        fill="none" stroke="blue" stroke-width=".02cm" />

</svg>""")

test_svg_2 = StringIO("""<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1" />
            <stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect x="10" y="10" width="280" height="180" fill="url(#gradient)" />
    <circle cx="150" cy="100" r="80" fill="white" stroke="blue" stroke-width="5" />
    <ellipse cx="200" cy="60" rx="40" ry="20" fill="green" />
</svg>""")

r = SimpleXMLReader()

print("Test SVG 1")
tags = r.get_all_tags(test_svg_1)
for tag in tags:
    print(f"{tag.name}: {tag.attributes}")

print("\nTest SVG 2")
tags = r.get_all_tags(test_svg_2)
for tag in tags:
    print(f"{tag.name}: {tag.attributes}")