import SimpleITK as sitk
import typing
import numpy as np


def getLabelShapeStatistics(image: typing.Union[np.ndarray, sitk.Image, str]) -> (list, list):
    """
    Calculates shape statistics of an image
    :param image: Three options
    1. numpy ndarray, image read in using scikit-image/matplotlib/pillow
    2. SimpleITK.Image, image read using SimpleITK
    3. str, path to a file containing an image
    :return: measureNames, measureValues
    measureNames: list of strings, names of measures
    measureValues: list of lists, with one list per label. Each list consists of floats, with one float per measure.
    Measure values are ordered according to measure names in <measureNames>.
    """

    if type(image) == sitk.Image:
        pass
    elif type(image) == np.ndarray:
        image = sitk.GetImageFromArray(image)
    elif type(image) == str:
        image = sitk.ReadImage(image)
    else:
        raise(TypeError(f"Argument Image is of unknown type {type(image)}"))

    labelStats = sitk.LabelShapeStatisticsImageFilter()
    labelStats.ComputeFeretDiameterOn()
    labelStats.Execute(image)

    labels = labelStats.GetLabels()

    funcs = {"Centroid": "GetCentroid",
             "Surface Area\n(pixels)": "GetPerimeter",
             "Sphericity": "GetRoundness",
             "Volume\n(number of pixels)": "GetNumberOfPixels",
             "Principal Moments": "GetPrincipalMoments"}

    measureValues = []
    for label in labels:
        labelMeasureValues = [label]
        for x, v in funcs.items():
            measureVal = getattr(labelStats, v)(label)
            if hasattr(measureVal, "__iter__"):
                measureVal = tuple(round(x, 6) for x in measureVal)
            else:
                measureVal = round(measureVal, 6)
            labelMeasureValues.append(measureVal)

        measureValues.append(labelMeasureValues)

    return ["Label Value"] + list(funcs.keys()), measureValues




