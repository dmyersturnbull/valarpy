from valarpy.Valar import Valar

with Valar('/home/dmyerstu/desktop/repos/valarpy/config/dangerous.json'):
	from valarpy.model import *  # you MUST import this AFTER setting global_connection.db
	print("Found {}".format(len(PlateRuns.select())))

