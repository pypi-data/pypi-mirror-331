from PGLW.main.hawc2_planform import HAWC2InputReader

# read htc file and extract c12 and ae axes
r = HAWC2InputReader("main_h2.htc")

# convert to PGL dict format
pf = r.toPGL()
