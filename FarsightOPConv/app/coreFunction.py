from FarsightOPConv.core import FarsighOutputConverter, replaceLabels
from FarsightOPConv import tifffile
import pandas as pd
from skimage import measure, io
import numpy as np
import pathlib as pl


def farsightOPConvAndMetricsGen(farsightOPImageFile: str, farsightOPSeedsFile: str):
    """

    :param farsightOPImageFile:
    :param farsightOPSeedsFile:
    :return:
    """

    foc = FarsighOutputConverter(farsightOPImageFile, farsightOPSeedsFile)

    yield 0

    relabelledImage, newOldLabelDict = foc.separateMultipleLabels()

    yield 0

    regProps = measure.regionprops(relabelledImage)

    yield 0

    newLabels = np.unique(relabelledImage)[1:]
    labelsDone = {x: False for x in newLabels}
    statsList = []

    for ind, (x, y, z) in enumerate(foc.seeds):

        # print(f"Doing {ind} of {foc.seeds.shape[0]}")
        newLabel = relabelledImage[z, y, x]
        oldLabel = foc.labelImage[z, y, x]

        if newLabel:
            if not labelsDone[newLabel]:

                labelsDone[newLabel] = True

                centroid = regProps[newLabel - 1].centroid

                volume = regProps[newLabel - 1].filled_area

                statsList.append([newLabel, oldLabel, f"({x:d},{y:d}, {z:d})",
                                  f"({centroid[2]:0.5g}, {centroid[1]:0.5g}, {centroid[0]:0.5g})",
                                  volume])

            else:
                statsList.append([np.nan, oldLabel, f"({x:d},{y:d}, {z:d})", np.nan, np.nan])
        else:
            statsList.append([np.nan, oldLabel, f"({x:d},{y:d}, {z:d})", np.nan, np.nan])

    yield 0

    labels2Remove = [x for x, v in labelsDone.items() if not v]

    yields = []
    for ret in replaceLabels(relabelledImage, labels2Remove, 0, makeGenerator=True):

        yield 0
        yields.append(ret)

    relabelledImageFiltered = yields[-1]

    statsDF = pd.DataFrame(columns=("New Label", "Farsight Output Label", "Farsight Output Seed",
                                    "Centroid", "Volume (number of pixels)"),
                           data=statsList)

    ipImagePath = pl.Path(farsightOPImageFile)
    opImagePath = ipImagePath.parent / f"{ipImagePath.stem}_corrected32Bit{ipImagePath.suffix}"
    opXLPath = ipImagePath.parent / f"{ipImagePath.stem}_corrected32Bit.xlsx"

    yield 0

    relabelledImageUInt32 = relabelledImageFiltered.astype(np.uint32)

    yield 0
    tifffile.imsave(str(opImagePath), relabelledImageUInt32, compress=9)

    statsDF.to_excel(opXLPath)

    yield str(opImagePath), str(opXLPath)


def farsightOPConvAndMetrics(farsightOPImageFile: str, farsightOPSeedsFile: str):

    yields = []

    for ret in farsightOPConvAndMetricsGen(farsightOPImageFile, farsightOPSeedsFile):
        yields.append(ret)

    return yields[-1]





