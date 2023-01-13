from hkpy.hkbase import HKBase, HKRepository
from hkpy.hklib import HKDataNode

hkbase = HKBase(url='http://localhost:3000', auth='')
hkrepository = hkbase.connect_repository(name='hkpy-repo')

# Add data node to hkbase
f = open("./tests/data/cat1.png")
mnode = HKDataNode(f)
hkrepository.add_entities([mnode])

# Retrieve data node from hkbase
cat = hkrepository.get_entities(["cat1.png"])[0]
assert cat.raw_data == mnode.raw_data

# Retrieve raw data with fragments api
artifact = hkrepository.resolve_fi("``cat1.png``")

assert artifact == mnode.raw_data