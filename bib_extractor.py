import os
import re
import shutil
import bibtexparser



target = "related_papers"
source = "files"
paper_dict = {}

if os.path.exists(target):
	shutil.rmtree(target)

os.mkdir(target)

for i in os.listdir(source):
	ip = source + os.sep + i
	if os.path.isdir(ip):
		for j in os.listdir(ip):
			jp = ip + os.sep + j
			if j[-4:] == '.pdf':
				# shutil.copy(jp, target + os.sep + j)
				paper_dict[j] = jp


with open("Location Hierarchy Embedded Timeline Visualization of Epidemiological Investigation Data.bib", "r", encoding="utf-8") as f:
	data = bibtexparser.load(f)

with open("related_work.txt", "r", encoding="utf-8") as f:
	tex = f.readlines()

category_dict = {}
cur_category = ""
count = 0
for i in tex:
	r = re.match(r'^\\subsection{(.*)}$', i)
	if r:
		cur_category = r.group(1)
	else:
		r = re.findall(r'(?<=\\cite\{).*?(?=\})', i)
		for j in r:
			assert(cur_category != "")
			category_dict[j] = cur_category

for i in data.entries:
	id = i['ID']
	try:
		# print(i['file'])
		r = re.search(r'(?<=/)[^/]*(?=:application/pdf)', i['file']).group(0)
	except Exception as ex:
		print(id + " not found\n", ex)
		continue
	filename = r
	subfile_name = category_dict[id]
	if not os.path.exists(target + os.sep + subfile_name):
		os.mkdir(target + os.sep + subfile_name)
	try:
		shutil.copy(paper_dict[filename], os.path.join(target, subfile_name, filename))
	except Exception as ex:
		print(id, paper_dict[filename])
		print(ex)
	

# print(count)
# print(data.entries[6])


