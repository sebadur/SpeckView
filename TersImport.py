import gwy
import zipfile

plugin_type = "FILE"
plugin_desc = "Importing Ters-Files (.ters)"

def detect_by_name(filename):
    if (filename.endswith(".ters")):
        return 100
    else:
        return 0

#def detect_by_content(filename, head, tail, filesize):
#    return 100



def load(filename, mode=None):
    if not (zipfile.is_zipfile(filename)):
        return
    with zipfile.Zipfile(filename) as zp:
        filenames = zp.namelist()
        print filenames
        
    c = gwy.Container()
    d = gwy.DataField(100, 100, 100, 100, 1)
    for i in range(100):
        for j in range(100):
            d.set_val(i, j, i) # draws linear gradient
    c.set_object_by_name("/0/data", d)
    return c

def save(data, filename, mode=None):
    f = open(filename, "w")
    datafield_num = 1
    for key in data.keys():
        if isinstance(data.get_object(key), gwy.DataField):
            d = data.get_object(key)
            f.write("Datafield "+ str(datafield_num) + '\n')
            datafield_num += 1
            for row in range(d.get_yres()):
                for col in range(d.get_xres()):
                    f.write(str(d.get_val(col, row))+'\n')
                f.close()
    return True
