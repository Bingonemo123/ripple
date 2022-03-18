from PackageDependencies.Means.BuildMeansFiles.Exp12.PackageDependencies.Means.BuildMeansFiles import MeanFunctions
from PackageDependencies.Constans import *
from PackageDependencies.Means.BuildMeansFiles.MeanFunctions import meanv1
import time
import multiprocessing as mp

tst = time.perf_counter()
with mp.Pool(processes=mp.cpu_count()) as pool:
    print(pool.map(meanv1, list(cd.keys())))
print(time.perf_counter() - tst)

tst = time.perf_counter()
for f in cd:
    MeanFunctions.meanv1(f)
print(time.perf_counter() - tst)

