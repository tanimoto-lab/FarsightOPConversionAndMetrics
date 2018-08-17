from funcs import getDesiredLabelsDF


def test_getDesiredLabelDF():

    testLabelFile = "tests/files/funcs/getDesiredLabelDF/Act5C_no5_med1_C428_dec1_label.tif"
    testSeedsFile = "tests/files/funcs/getDesiredLabelDF/Act5C_no5_med1_C428_dec1_seedPoints.txt"

    expectedXL = "tests/funcs/getDesiredLabelDF/expectedOP.xlsx"

    desiredLabelDF = getDesiredLabelsDF(testLabelFile, testSeedsFile)

    desiredLabelDF.to_excel(expectedXL)

    assert False


if __name__ == "__main__":

    test_getDesiredLabelDF()

