from FarsightOPConv.core import FarsighOutputConverter, replaceLabels
from FarsightOPConv.img32bit16bitIO import labelConv32bitTo16bit
from FarsightOPConv import tifffile
from FarsightOPConv.sitkFuncs import getLabelShapeStatistics
import pandas as pd
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

    newLabelsAll = np.unique(relabelledImage)[1:]
    labelsDone = {x: False for x in newLabelsAll}

    newLabels = []
    oldLabels = []
    farsightOPSeeds = []

    for ind, (x, y, z) in enumerate(foc.seeds):

        # print(f"Doing {ind} of {foc.seeds.shape[0]}")
        newLabel = relabelledImage[z, y, x]
        oldLabel = foc.labelImage[z, y, x]

        if newLabel:
            if not labelsDone[newLabel]:

                labelsDone[newLabel] = True
                newLabels.append(newLabel)
                oldLabels.append(oldLabel)
                farsightOPSeeds.append((round(x, 6), round(y, 6), round(z, 6)))

    yield 0

    labels2Remove = [x for x, v in labelsDone.items() if not v]

    yields = []
    for ret in replaceLabels(relabelledImage, labels2Remove, 0, makeGenerator=True):

        yield 0
        yields.append(ret)

    relabelledImageFiltered = yields[-1]

    relabelledImageUInt32 = relabelledImageFiltered.astype(np.uint32)

    yield 0

    statsDF = pd.DataFrame()
    statsDF["New Label"] = newLabels
    statsDF["Farsight Output Label"] = oldLabels
    statsDF["Farsight Output Seed"] = farsightOPSeeds

    statsDF.set_index("New Label", inplace=True)
    statsDF.sort_index(inplace=True)

    imgs16bit, labelMapDF = labelConv32bitTo16bit(relabelledImageUInt32)

    for imgInd, img16bit in enumerate(imgs16bit):

        yield 0
        measureNames, measureValues = getLabelShapeStatistics(img16bit)
        imgStatsDF = pd.DataFrame(data=measureValues, columns=measureNames)
        imgStatsDF.sort_values(by="Label Value", inplace=True)
        imgLabelMap = labelMapDF[labelMapDF["Output Image Index"] == imgInd].copy()
        imgLabelMap.sort_values(by="Output Label", inplace=True)
        imgStatsDF["New Label"] = imgLabelMap["Input Label"].values
        imgStatsDF.rename(columns={"Label Value": "Temporary\nInternal Label"}, inplace=True)
        imgStatsDF.set_index("New Label", inplace=True)
        statsDF = statsDF.combine_first(imgStatsDF)

    ipImagePath = pl.Path(farsightOPImageFile)
    opImagePath = ipImagePath.parent / f"{ipImagePath.stem}_corrected32Bit{ipImagePath.suffix}"
    opXLPath = ipImagePath.parent / f"{ipImagePath.stem}_corrected32Bit.xlsx"

    yield 0

    tifffile.imsave(str(opImagePath), relabelledImageUInt32, compress=9)

    statsDF.to_excel(opXLPath)

    yield str(opImagePath), str(opXLPath)


def farsightOPConvAndMetrics(farsightOPImageFile: str, farsightOPSeedsFile: str):

    yields = []

    for ret in farsightOPConvAndMetricsGen(farsightOPImageFile, farsightOPSeedsFile):
        yields.append(ret)

    return yields[-1]





