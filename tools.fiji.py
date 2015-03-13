# hiroutil.py

from ij import ImageStack, IJ


def load_stack(w,h,paths):
	stk = ImageStack(w,h)
	for path in paths:
		ip = IJ.openImage(path).getProcessor()
		stk.addSlice(ip)
	return stk


# Loading a tab-separate file (TSV) with n skipping rows.
# n (>= 1) must be put in the first column in the first row.
def load_tsv(path):
	import csv
	f = open(path,'rU')
	rows = []
	reader = csv.reader(f,delimiter='\t')
	skipping = int(reader.next()[0])
	for _ in range(skipping-1):
		reader.next()
	for row in reader:
		rows.append(row)
	f.close()
	return rows


def write_tsv(path,rows):
	import csv
	f = open(path,'wb')
	print('Writing: %s'%path)
	writer = csv.writer(f,delimiter='\t')
	for row in rows:
		writer.writerow(row)
	f.close()


def read_sequence(path):
	from ij.plugin import FolderOpener
	return FolderOpener().openFolder(path)


# imp: ImagePlus
# slices: a list of slice indices (1-based)
def remove_slices(imp,slices):
	stk = imp.getStack()
	slices = sorted(slices, reverse=True)
	num_slices = stk.getSize()
	for s in slices:
		if s <= num_slices:
			stk.deleteSlice(s)
	return imp


# imp: ImagePlus
# slices: a list of slice indices (1-based)
def take_slices(imp,slices):
	stk = imp.getStack()
	num_slices = stk.getSize()
	slices = diff(range(1,num_slices+1), slices)
	slices = sorted(slices, reverse=True)
	remove_slices(imp,slices)
	return imp


def map_slices(func,imp,slices=None):
	stk = imp.getStack()
	num_slices = stk.getSize()
	if slices is None:
		slices = range(1,num_slices+1)
	res = []
	for s in slices:
		imp.setSlice(s)
		res.append(func(imp))
	return res


def linescan(x1,y1,x2,y2):
	from ij.gui import Line,ProfilePlot
	def f(imp):
		line = Line(x1,y1,x2,y2)
		imp.setRoi(line)		
		vs = ProfilePlot(imp).getProfile()
		imp.killRoi()
		return vs
	return f


def linescan_poly(xs,ys):
	def f(imp):
		from ij.gui import Line, Roi, ProfilePlot, PolygonRoi
		if len(xs) > 1:
			print(xs,ys)
			line = PolygonRoi(xs,ys,len(xs),Roi.POLYLINE)
			imp.setRoi(line)
		else:
			line = Line(xs[0],ys[0],xs[1],ys[1])
			imp.setRoi(line)
		vs = ProfilePlot(imp).getProfile()
		imp.killRoi()
		return vs
	return f


def remove_scale(imp):
	IJ.run(imp,"Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");


def crop(imp,w,h,x,y):
	IJ.run(imp,"Specify...", "width=%d height=%d x=%d y=%d"%(w,h,x,y))
	IJ.run(imp,"Crop","")
	return imp


#
# List functions
#

def transpose(xss):
	return [list(i) for i in zip(*xss)]


def diff(a, b):
	b = set(b)
	return [aa for aa in a if aa not in b]


#
# Utility
#


def mayint(s):
	try:
		r = int(s)
	except:
		r = None
	return r