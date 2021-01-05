data = {'FB': [[278.7699890136719, 297.5155132625356, 302.77615753396924, 314.4955994634929, 341.0929116976553, 365.31218862739615, 353.48634482248286, 366.80059929560645, 365.9352283939074, 365.71201910203666, 372.31726670511216, 375.4354810408592, 396.45492171478105, 408.6640443057517, 411.75449095169284, 419.68905074300545, 426.0960379443087, 450.56813790725766, 448.6242583382001, 455.13703616724524, 442.4406968008913, 402.7844056951178, 413.61620454954027], [278.7699890136719, 296.1002734379986, 290.44789231299393, 285.7855989900315, 275.54043293386695, 285.0709290408847, 262.12459630591206, 279.5675526233687, 272.71249797707867, 276.7307019275137, 275.09221174317815, 290.5720675343136, 269.7318330254881, 267.41880465338147, 264.5266475979439, 276.2558166631469, 266.08201676993184, 265.25052981419697, 257.62215297373217, 258.82649013482285, 265.1209995304733, 255.35025392515843, 266.7741845892228]], 'SPY': [[354.55999755859375, 363.60402735341313, 366.0280341391365, 371.3937314102098, 383.3135905616745, 393.6391407241909, 388.7731403577834, 394.3183986083418, 393.9429567565599, 393.82984197041924, 396.5121578665069, 397.7526865868964, 406.1963410720281, 410.9292975663563, 412.08795294838944, 415.08398731900127, 417.4699741341177, 426.56175469185257, 425.83858400795555, 428.16516933275426, 423.6009664582733, 409.1439720654486, 413.30414070680166], [354.55999755859375, 362.9197468912711, 360.2660111172743, 358.0476635095172, 353.1483293075355, 357.7723412433242, 346.8047572762932, 355.55878981768683, 352.22481281734986, 354.17826157384843, 353.36148970831243, 360.9010330435907, 351.0410438456877, 349.8772765543531, 348.4194577125884, 354.27321487481333, 349.29376860343643, 348.8595237830704, 345.02619447447245, 345.6202959838677, 348.7965081118359, 343.89053173480295, 349.72023801666774]]}

new_data = {}
for key,val in data.items():
	l = []
	for i in zip(*val):
		print (list(i))
		data = list(i)
		import numpy as np
		Q1 = np.quantile(data,0.25)
		Q3 = np.quantile(data,0.75)
		IQR = Q3 - Q1
		l.append(IQR)
	new_data[key] = l

	print("---------------")

print("new_data", new_data)



def remove_outliers(data):
	import numpy as np
	Q1 = np.quantile(data,0.25)
	Q3 = np.quantile(data,0.75)
	IQR = Q3 - Q1
	return IQR