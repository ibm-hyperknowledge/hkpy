
from hkpy.hkbase import HKBase
from hkpy.hklib import HKNode, HKDataNode, HKGraphBuilder
from hkpy.hklib.fi.fi import FI
from hkpy.hklib.fi.fianchor import FIAnchor

hkbase = HKBase(url='http://localhost:3000')

repo = hkbase.delete_create_repository('data')

with open('./data/myonto-2021-6-1.json', 'r') as onto_file:
    repo.import_data(onto_file.read(), 'application/json', as_hk = True)

# add picture
with open('./data/cat1.png', 'rb') as file:
    img1 = bytes(bytearray(file.read()))
dnPicture1 = HKDataNode(id_='mypicture', mimeType='image/png', raw_data=img1)

# add text
text1 = """"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
dnText1 = HKDataNode(id_='mytext', mimeType='text/plain', raw_data=text1)
repo.add_entities([dnText1, dnPicture1])


fi = FI('mytext')
text = repo.resolve_fi(fi)

fi = FI('mytext.subtext({start: 2, end: 50})')
text_frag = repo.resolve_fi(fi)
repo.persist_fi(fi)


link = HKGraphBuilder.create_ifi_spo_hklink('depictedBy', FI('Dog'), fi)
repo.add_entities([link])

fi = FI('mytext.subtext*({start: 2, end: 50})')
node : HKNode = repo.resolve_fi(fi)

# part1 = text[:node.properties['start']]
# part3 = text[node.properties['end']:]
# print(part1 + '**' + text_frag + '**' + part3)

fi = FI('mytext.subtext({start: 2, end: 50}).subtext({start: 3, end: 10})')
text_frag_frag = repo.resolve_fi(fi)
repo.persist_fi(fi)
print(text_frag_frag)

fi = FI('mypicture', FIAnchor('rect', {"x": 20, "y": 20, "w": 800, "h": 20}))
data = repo.resolve_fi(fi)
repo.persist_fi(fi)

fi = FI('mypicture.rect({x: 20, y: 20, w: 800, h: 20}).rect({x: 2, y: 4, w: 10, h: 10})')
data = repo.resolve_fi(fi)
repo.persist_fi(fi)


# Test parse
fi = FI('file.func(["A", "B"])')